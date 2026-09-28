# AXV-60 preflight - the three skipped arms, the guard arithmetic, and a batch that reuses the baseline

Written 2026-09-28 by Lens, on the retry heartbeat for AXV-60, after the previous
run (`2d3844e0`) died on an upstream `invalid_request_error` before it provisioned
anything.

**Status: no arm ran. No pod was created. Nothing is running.** The Runpod
connection reports `state: ready` and `connections_search` says it is "installed
and usable by this agent", but this run's tool surface is only `connections_search`
and `connection_request`; `connection_request` for `runpod` returned "Runpod is
connected. Use its installed tools; a native continuation will refresh tools if
needed." There is no `list-pods`, no `create-pod`, no `execute` in this run, so
the batch could not be launched.

**Pod state is UNVERIFIED, not empty.** I could not call `list-pods` to check
for a leaked pod, because that tool is not bound to this run. The evidence that
nothing leaked is circumstantial: the prior run's continuation summary records
zero completed actions, zero commands run and zero files touched, and it failed
inside the model call. That is the best available answer, and it is not the same
as a read of the pod list. **Whoever runs the batch must call `list-pods` first
and terminate anything found, before provisioning.**

## 1. The guard fix is real, and the arithmetic in the issue is right

The issue asked for this to be checked before trusting it. It checks out.

`dustin-dev-35/autoresearch` branch `experiment/2609.31098-seedvar` is at
`dc64e08`, which contains the fix `e9702dd`. The changed line in
`run_batch_2609_31098_seedvar.sh` is:

```bash
local need=$(( iters * MS_PER_ITER * 115 / 100000 + MEASURE_RESERVE_SEC ))
```

`MS_PER_ITER` is milliseconds per iteration and `BUDGET_MIN * 60` is seconds, so
the conversion is `/1000`, and `115 / 100000` is the 15 percent margin. The
number is checkable from AXV-43's own log, and it is:

```
guard_update: ms_per_iter=138 (measured train_seconds=691 over 5000 iters)
AXV_ARM_END 2609.31098-a00-s1337 rc=0 took_sec=703
```

from `experiments/runs/2609.31098-a00-s1337/train.log`, with
`metrics.json` giving `train_seconds: 691.7154836654663`,
`measure_seconds: 7.78547739982605`, `total_seconds: 701.4729423522949`. So the
138 and the 703 in the issue are read from the run, not assumed.

```
5000 * 138 * 115 / 100000 = 793   (bash truncates 793.5)
        + MEASURE_RESERVE_SEC 150 = need_sec 943
```

against the `remaining_sec 856` the guard saw. `dc64e08` is right and
`e9702dd`'s own message is wrong: the units bug was real and the figure it
printed, 793650, was off by a factor of about 842, but 943 against 856 means
AXV-43's decision to skip those three arms was **correct** even with the guard
fixed. Fixing the guard does not retroactively justify the trim. This issue
exists because the *design* asked for those arms, not because the guard owed
them.

## 2. The existing batch script cannot run this issue, and would have wasted the whole envelope

This is the finding that matters.

`run_batch_2609_31098_seedvar.sh` at `dc64e08` runs, in order: tier 1
`a00-s1337`, `a00-s1338`, `a00-s1339`; tier 5a `a03-s1337` untrained; tier 2
`a00-s1340`; tier 3 `a01-s1337`; tier 4 `a02-s1337`; tier 5b `prop3`.

Every one of the tier 1 arms, and both tier 5 arms, is **already measured in
this cohort and already in the leaderboard**. The issue requires the baseline to
be reused, not re-run. Two problems follow:

1. Tier 1 is deliberately unguarded (`[ "$tier" -gt 1 ]`). At a 45 minute
   envelope the script would spend roughly 3 x 703 = 2109 s plus about 180 s of
   startup re-deriving three numbers that are already published, and **every new
   arm would then be trimmed by the guard**. That is the AXV-43 failure mode
   repeating itself, and it would have cost about $0.38 to produce nothing.
2. The tier order is wrong for this issue. It runs the fourth seed at tier 2 and
   the between-architecture arm at tier 3, so under any budget pressure the
   `L=16` comparison is trimmed first. The issue asks for the opposite: `a01` is
   the deliverable and "tier the arms so the `L=16` comparison is never the
   thing cut".

So the script was not reused. A delta script was added instead, at
`run_batch_2609_31098_axv60.sh`, committed as **`e674e81`** on
`experiment/2609.31098-seedvar`. The AXV-43 script is left byte-for-byte
untouched, because every seed-series `run.json` records
`harness_commit: f1e09f3` and `diff.patch` is generated from that commit; editing
it in place would break the provenance of results already on the leaderboard.

## 3. The 45 minute envelope is about one minute short, and the reason is L=16

The issue states 703 s per arm, which is right for the two L=12 arms and wrong
for the first one. `a01-s1337` is 16 layers, not 12.

`metrics.json` gives `num_params: 21376128` at `n_layer: 12`. Block parameters
are constant in depth: attn `3*384*384 + 3*384 + 384*384 + 384 = 591360`, mlp
`384*1536 + 1536 + 1536*384 + 384 = 1181568`, two layer norms `1536`, total
**1774464 per layer**. So

```
L=12:  12 * 1774464 + 82560 = 21376128   (matches the run exactly)
L=16:  16 * 1774464 + 82560 = 28473984   ratio 1.332
```

Training cost scales roughly with that, so arm 1 is about `691.7 * 1.332 = 921` s
of training plus about 12 s of D_eff measurement on 16 layers, i.e. **about 933 s,
not 703 s**. The 1.332 factor is an estimate, not a measurement; it is the one
number in this document that is not read from a run, and the guard exists to
cope with it being wrong.

Simulating the guard as written, with `MS_PER_ITER_L12=138` and the measured
rate substituted after each arm:

| envelope | a01 (L=16) | s1340 (L=12) | a02 gamma=0.5 |
| --- | --- | --- | --- |
| 44 min | run | run | **trimmed** |
| 45 min (the issue's figure) | run | run | **trimmed** |
| 46 min | run | run | run |
| **50 min (new default)** | run | run | run |

45 minutes trims the `gamma=0.5` control, because the third arm's pre-flight
test needs `remaining >= need_sec 943` at an elapsed of about 1815 s, which needs
a 2758 s envelope. Total wall clock for all three is about
`180 + 933 + 703 + 703 = 2519 s`.

The default is therefore **50 minutes**, not 45. It is a real deviation from the
issue text and it is deliberate: 46 is the first envelope where all three arms
survive, and 50 leaves slack for a worse-than-estimated L=16 rate. The guard
still trims the tail and says so in its own `AXV_ARM_SKIPPED` line if the rate
comes in high.

Cost, stated before provisioning as section 10.2 requires:

| | seconds | cost at $0.59/hr |
| --- | --- | --- |
| expected finish, 3 arms | 2519 | **$0.41** |
| whole 50 min envelope | 3000 | $0.49 |

Against the $0.54 AXV-43 already spent and the $3.25 company budget, that leaves
**about $2.30 expected, $2.22 worst case**. It is not a material share, so no
board escalation is needed.

## 4. One more guard change: price an arm at its own depth

The AXV-43 guard carried one global `MS_PER_ITER`. After the L=16 arm it would
hold 184, and it would then charge 184 to the two L=12 arms, giving
`need_sec 1208` instead of `943` and trimming the `gamma=0.5` control **even at a
50 minute envelope**. Simulated and confirmed. That is the safe direction, but
it is still a trim that is not necessary.

The delta script tracks the rate per depth. `MS_PER_ITER_L12` is seeded at the
measured 138; `MS_PER_ITER_L16` starts at 0 and is learned from arm 1. The guard
update writes back to whichever key matches the arm's own `n_layer`, and
`rate_for` prices each arm from its own depth. With that, all three arms fit at
50 minutes.

## 5. What the batch will and will not tell us

Stated before the run, so it cannot be read back into the result.

- `a01-s1337` gives the **same-cohort** between-architecture comparison that
  AXV-43 had to make against the paper's published between-model spread (about
  0.027 absolute for its 7B+ models, Table 2). That is what the issue is for.
- `a00-s1340` makes `n=4`. Still a small number. The 95 percent interval on a
  sigma from three normal draws spans roughly 0.0005 to 0.0044; from four it is
  narrower but still wide, and the third significant figure of
  `sigma(D_eff/L)` is not resolvable at this budget.
- `a02-s1337` is the estimator positive control. The paper's Table S14 arm, which
  should raise `D_eff/L` to about 0.124 against a baseline of 0.0979. If the
  estimator does not respond to a known effect of that size, that is a finding
  about the estimator and it is worth more than the seed number.
- **This is still a 21,376,128 parameter char-level nanoGPT, not a 7B+ model.**
  It does not verify the paper's regime claim and must not be written up as if
  it did. `L=16` is 28.5M parameters, which is still three orders of magnitude
  from Mistral-7B.

## 6. Verification done in this heartbeat

- [x] Guard fix `e9702dd` present at `dc64e08`; `/100000` conversion is correct
- [x] `138` and `703` read from `train.log` and `metrics.json`, not assumed
- [x] `5000 * 138 * 115 / 100000 + 150 = 943` reproduced
- [x] `dc64e08`'s correction of `e9702dd` confirmed: 943 vs 856, trim was right
- [x] `train.py` knobs confirmed single-variable: `AXV_SEED`, `AXV_N_LAYER`,
      `AXV_GAMMA`, `AXV_MAX_ITERS`, `AXV_N_PASSAGES`, `AXV_TRAIN`
- [x] L=16 parameter count derived from the L=12 count and the per-layer block
      size; 21376128 reproduces exactly
- [x] Guard simulated for 44/45/46/47/50 minute envelopes and for per-arch vs
      single-rate
- [x] `run_batch_2609_31098_axv60.sh` passes `bash -n`
- [x] Delta script committed and pushed: `e674e81`
- [ ] **No arm run.** No pod created.
- [ ] `list-pods` not callable in this run; pod state unverified.

## 7. Next action

Provision one pod on the board-set instance, `1x PRO 6000 MIG 24GB`, run
`run_batch_2609_31098_axv60.sh` at `e674e81` with `AXV_BUDGET_MINUTES=50`, push
`experiments/runs/2609.31098-a01-s1337/`, `...-a00-s1340/` and
`...-a02-s1337/` plus the merged `leaderboard.jsonl` in the same commit, then
terminate the pod and verify `list-pods` is empty. Call `list-pods` **before**
provisioning in case the retry left something behind.
