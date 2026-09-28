# AXV-4 - RunPod access and cost preflight

Recorded 2026-09-28. Nothing was provisioned. No pod was created, and none existed at
the time of the read.

## 1. Access

`RUNPOD_API_KEY` does **not** resolve as a process environment variable in the agent
runtime. It resolves as a Paperclip tool connection instead.

| probe | result |
| --- | --- |
| `RUNPOD_API_KEY` in agent env | absent |
| `GET /api/agents/me/secrets` | `{ "secrets": [] }` - no agent-scoped secrets injected |
| `connections_search("runpod")` | `state: ready`, `reason: "Connection is installed and usable by this agent"` |
| connection id | `181f5481-f505-40bf-aee0-102105ac7638` |
| org secret catalog entry | `99bb861b-bc8d-40a4-b662-2e4a141f01ff`, key `tool_app.8288eda8-79a7-4d77-ac57-080b958f39f7.credentials_authorization`, status `active` |
| RunPod tools reachable by this agent | 77, via `POST /api/tool-gateway/tools/call` |

The credential is an org-level tool-app credential, not an agent-injected secret. Any
harness that reads `os.environ["RUNPOD_API_KEY"]` will fail. It must call RunPod through
the Paperclip tool gateway, or the board must bind the org credential to the agent as an
injected secret.

**Account identity is not reportable.** The 77-tool RunPod surface has no account, user, or
whoami read. The authenticated identity is established only as far as "the org RunPod tool
connection, connection `181f5481-f505-40bf-aee0-102105ac7638`". No account email or name
was read, and none is guessed here.

## 2. Template

Matched the board spec exactly. Both halves resolve.

| field | board spec | RunPod record | match |
| --- | --- | --- | --- |
| template | Runpod Pytorch 2.8.0 | `runpod-torch-v280`, name `Runpod Pytorch 2.8.0` | yes |
| image | - | `runpod/pytorch:1.0.2-cu1281-torch280-ubuntu2404` | - |
| GPU | 1x PRO 6000 MIG 24GB | `NVIDIA RTX PRO 6000 Blackwell Server Edition MIG 1g.24gb`, display name `PRO 6000 MIG 24GB`, `memory: 24` | yes |
| CUDA | 13.0 | `allowedCudaVersions` includes `13.0`; GPU `cudaVersions` lists `13.0` with `available: true` | yes |

Template is public (`public: true`, `serverless: false`), so no custom template has to be
built first. `list-templates` returns zero private templates on the account.

**Storage note.** The board row says 70 GB. The template actually provisions 30 GB
container disk (`disk: 30`) plus a 50 GB persistent `/workspace` mount
(`mounts.persistent: { path: /workspace, size: 50 }`) = **80 GB**, and the 50 GB mount is
a network volume. `list-network-volumes` currently returns `[]`, so that volume is
auto-provisioned by the template on first pod. �4 step 3 "on a network volume" is
satisfied by the template; no separate `create-network-volume` call is needed.

## 3. Rate

`get-gpu-type` and `list-gpu-types` agree, both `include=[AVAILABILITY], product=[POD],
cloud=SECURE, count=1`:

| field | value |
| --- | --- |
| `price.secure` | **$0.59 / hr** |
| `price.community` | $0.50 / hr - **unreachable**, `community: false`, `maxCount.community: 0` |
| `price.serverless` | $0.69 / hr |
| `secure` | `true` |
| availability | `LOW` |
| data centers | `EUR-IS-2`, `US-NE-1` - only these two |
| `maxCount.secure` | 32 |
| pool | `AMPERE_24` |

There is no cheaper cloud for this GPU. `community` is `false`, so a Community Cloud
substitution is not available and must not be assumed as a fallback. Availability is `LOW`
in both regions, so a provisioning queue is a real risk and is a wall-clock cost, not just
a delay.

## 4. Cost of a 60-minute run

```
1.0 h x $0.59/h = $0.59
$3.25 / $0.59  = 5.508... h = 5 h 30 m 30 s of total pod time, company-wide, for all time
```

A 60-minute run is **18.2 %** of the entire AXV budget. Five such runs exhaust it.

Realistic per-session cost including image pull, boot, push, and terminate overhead of
roughly 10 minutes (0.167 h, $0.098):

| session shape | wall clock | cost | share of $3.25 |
| --- | --- | --- | --- |
| 1 x 60-min run, own pod | 1.00 h | $0.59 | 18.2 % |
| 1 x 45-min run, own pod | 0.92 h | $0.54 | 16.6 % |
| 6 sessions (3 seeds x 2 arms), each own pod | 5.5 h | $3.25 | 100 % - the whole budget |
| 1 pod held for the whole batch, 6 x 45-min runs | 4.75 h | $2.80 | 86.2 % |

The minimum-powering rule (3 seeds, 2 arms) is **not affordable** as six separate pods. It
is affordable as one long-lived pod running the six runs sequentially, which also removes
five rounds of image-pull overhead. That changes the batch plan, and it is the reason this
number was needed first.

## 5. Pod-leak state at finish

| check | result |
| --- | --- |
| `list-pods` | `pods: []` - **0 pods, idle count zero** |
| `list-network-volumes` | `[]` |
| `list-billing` Sept 2026 | `totalAmount` $0.015108741819858551, all `podGpuAmount` |
| `list-pod-billing` Sept 2026 | `uniquePodCount: 1`, pod `vffgglkhl2pn25`, $0.0151 |
| `get-pod vffgglkhl2pn25` | 404 `pod not found` - deleted, not billing |

The one historical pod is deleted and not billing. It predates this session; this session
provisioned nothing. Total lifetime RunPod spend on the account is $0.0151.

## 6. Open items for the board

1. **Binding.** Decide whether the org RunPod credential is bound to the agent as an
   injected `RUNPOD_API_KEY`, or whether the harness calls RunPod through the Paperclip
   tool gateway. The experiment skill's preflight expects an env var; the current topology
   is a tool connection. One of the two has to change.
2. **Storage row.** Confirm 70 GB is the intended total. The template gives 80 GB
   (30 + 50). If 70 GB is a hard ceiling, the pod must be created with a smaller
   `diskSize`, which the board must approve as a deviation from the template default.
3. **Data-center pin.** `EUR-IS-2` and `US-NE-1` are the only regions, both `LOW`
   availability. Pinning one is a latency-versus-availability choice the batch plan should
   make deliberately.

## Sources

Every number above is a verbatim field from a RunPod read through the Paperclip tool
gateway, in this heartbeat:

- `list-pods {}` -> `pods: []`
- `list-templates {"limit":100}` -> `templates: []`
- `list-public-templates {}` -> `runpod-torch-v280` and 13 others
- `get-template {"id":"runpod-torch-v280"}` -> disk 30, persistent /workspace 50, CUDA 13.0 allowed
- `list-gpu-types {"include":["AVAILABILITY"],"product":["POD"],"cloud":"SECURE","count":1}` -> 48 GPU types
- `get-gpu-type {"id":"NVIDIA RTX PRO 6000 Blackwell Server Edition MIG 1g.24gb", ...}` -> `price.secure: 0.59`
- `list-billing {"lastN":1,"bucketSize":"month"}` -> $0.015108741819858551
- `list-pod-billing {"lastN":1,"bucketSize":"month"}` -> pod `vffgglkhl2pn25`
- `get-pod {"id":"vffgglkhl2pn25"}` -> 404
- `list-network-volumes {}` -> `[]`

No credential, session token, or API key is recorded in this file.
