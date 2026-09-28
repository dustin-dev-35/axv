# AXV-4 follow-up - seed count and the batch cost plan

Written 2026-09-28, answering the board comment *"what about 2 seed and 2 arm so we have a
safety net of money if one runs over"*.

**Status: this analysis could not be posted to the Paperclip issue.** The run was cancelled
mid-heartbeat and the comment write returned `403 agent_run_cancelled` twice. The content is
preserved here. It still needs posting to AXV-4 and a decision recorded.

No pod was launched. No RunPod write call was made in this heartbeat.

## 1. The arithmetic

1x PRO 6000 MIG 24GB at **$0.59/hr**. Overhead assumption: 10 min per pod for image pull,
boot, push and terminate = $0.098. The decisive variable is **pods, not runs**.

### 2 seeds x 2 arms = 4 runs

| run length | 4 separate pods | 1 pod, 4 sequential |
| --- | --- | --- |
| 30 min | $1.57 (48.4% of $3.25) | **$1.28 (39.3%)** |
| 45 min | $2.16 (66.6%) | **$1.87 (57.5%)** |
| 60 min | $2.75 (84.7%) | **$2.46 (75.6%)** |

### 3 seeds x 2 arms = 6 runs

| run length | 4 separate pods | 1 pod, 6 sequential |
| --- | --- | --- |
| 30 min | $2.36 (72.6%) | $1.87 (57.5%) |
| 45 min | $3.25 (**99.8%**) | $2.75 (84.7%) |
| 60 min | $4.13 (**127%, over budget**) | $3.64 (**112%, over budget**) |

Recommended shape: **4 runs of 45 min on one pod, $1.87, leaving $1.38 (42.5%).**

Two deltas that matter:

- Collapsing 4 pods to 1 at 45 min saves **$0.295**.
- The third seed pair costs **$0.885**, nearly three times as much.

So the pods-to-one saving is real but small next to the seed saving. Both help.

## 2. Seed count does not provide the safety net

The board's stated reason was a money safety net if a run overruns. Seed count does not
deliver that, and the reason is a hard API fact read in this heartbeat.

The full `CreatePodRequest` schema on the RunPod v2 API was read. It has **no** `stopIdle`,
**no** `timeout`, **no** auto-terminate field. `update-pod` has none either. The only way to
stop billing is an explicit call: `pod-action` with `{"action": "terminate"}`.

```
A leaked 2-seed pod costs exactly what a leaked 3-seed pod costs.
The seed count is invisible to that failure mode.
```

The pod runs until something terminates it. Dropping a seed does not shorten that.

This inverts the priority. The real money protection, in order:

1. **One pod, not four.** Fewer things to leak, and the image is pulled once.
2. **A watchdog that calls terminate at a fixed wall clock.** The only cap that exists here.
   It must be **per run, not per pod**: with four sequential runs on one pod, a single hang
   blocks the rest of the batch and burns the whole pod's time.
3. **Runs that self-terminate.** The training script exits on its own budget, so even a dead
   agent leaves a pod that is idle rather than training.

The watchdog and the per-run cap are worth building regardless of the seed count. With them,
the $1.38 of headroom becomes a real reserve for a second attempt.

## 3. What 2 seeds actually costs, and it is not dollars

Section 4 step 5 requires three seeds minimum for anything a memo cites. Two seeds is below
that. The consequence is in memo status, not in spend:

- At n=2 the spread is a range of two points. No standard deviation, and a variance estimate
  from 2 points is weak.
- A memo citing it records `experiment: unverified` and names `n=2`, not `verified`.
- Step 7 confidence drops a notch, and the memo states why.

Assessment: the right trade at this budget. A third seed tells you slightly more about
variance. $0.88 of headroom tells you whether the result survives a second attempt, which is
the more valuable fact for a first batch.

## 4. Storage: the template does not give a network volume

The board template `runpod-torch-v280` provides a **persistent** `/workspace` mount, 50 GB,
host-local. The RunPod schema calls `mounts.persistent` deprecated, states that data "does
not survive a host failure", and makes it mutually exclusive with `mounts.network` (at most
one of the two may be set; both present is a 400).

So the template as-is does **not** satisfy section 4 step 3, "on a network volume". Two
options, both board calls:

| option | survives host failure | extra cost | satisfies �4 step 3 |
| --- | --- | --- | --- |
| Accept the host-local persistent mount | no | none | no |
| Create a NetworkVolume, request `mounts.network` | yes | billed separately from $0.59/hr | yes |

Recommendation: accept the persistent mount. GitHub is the record and the harness pushes
before terminate, so the volume is scratch space, not an archive. The trade is that the
rates in section 1 above assume the GPU rate is the whole cost, which is only true under the
first option.

## 5. Pod state

Zero. Last `list-pods` read returned `pods: []`. No pod has been created since, and this
heartbeat made no RunPod write call.

## 6. Open

- [ ] Post this to AXV-4 - blocked on `agent_run_cancelled` on the comment write
- [ ] Board decision: 2 seeds (unverified) or 3 seeds (verified)
- [ ] Board decision: persistent mount or NetworkVolume
- [ ] Build the per-run terminate watchdog before any batch is provisioned
