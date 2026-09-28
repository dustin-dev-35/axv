# AXV-19 — connector service surface evidence

- **Run:** `5b62bc61-6f0f-403b-8d36-ad40057b25dc`
- **Agent:** Loom `2b4555f5-1c0b-4ce7-8835-1ed2c311d7c6`
- **Date:** 2026-09-28
- **OpenAPI:** `/api/openapi.json`, 704 paths
- **MCP:** `http://127.0.0.1:3100/mcp/runtime-tools`

## 1. Tool surface is still two tools

`tools/list` (JSON-RPC over `PAPERCLIP_RUNTIME_TOOLS_MCP_URL`):

```
COUNT: 2
  connection_request
  connections_search
```

Matches `PAPERCLIP_RUNTIME_TOOLS_AVAILABLE`.

## 2. All six connections report `ready`

| query | connectionId | state |
| --- | --- | --- |
| notion | `64ec3dca-e04d-49ce-8211-11a82976d774` | ready |
| supabase | `a37146be-a0df-49eb-828d-60a2edeca8bb` | ready |
| posthog | `4c59b2fa-b1dd-4691-9da0-5579c073e72e` | ready |
| github | `f9680aa4-e2ee-4649-a385-aa5f617beca4` | ready |
| netlify | `2e483ebf-c270-4747-bddb-b96a744d75fb` | ready |
| runpod | `181f5481-f505-40bf-aee0-102105ac7638` | ready |

Each returns `reason: "Connection is installed and usable by this agent"` and
`instruction: "Use the installed connection. Do not create another connection request."`
The instruction and the tool surface still contradict each other.

## 3. No service routes exist in the API at all

Zero paths in the 704-path document match `notion|supabase|posthog|netlify|runpod|cloudflare`.
These services are reachable only through the tool gateway, and the gateway is what is broken.

## 4. The tool gateway mints a token it then refuses — this is the precise defect

`POST /api/tool-gateway/sessions` is declared `x-paperclip-authorization.actor = board_or_agent`,
so an agent is allowed to call it. It succeeds:

```
HTTP 201
{"sessionId":"0a4ac21d-...","token":"pcgt_0a4ac21d-....jidPTTidF0nXv9Q3NvQH1zVhDwTSADubOek3bmMOVfs",
 "expiresAt":"2026-09-28T21:01:23.840Z",
 "toolsUrl":"/api/tool-gateway/tools","callUrl":"/api/tool-gateway/tools/call"}
```

The response names `toolsUrl` and `callUrl`. The token is then rejected on both:

| how the `pcgt_` token is presented | result |
| --- | --- |
| `Authorization: Bearer pcgt_...` | 401 `Agent token did not verify; obtain fresh credentials and retry` |
| `Authorization: Token pcgt_...` | 401 `Tool gateway session token is required` |
| `x-paperclip-gateway-session` header | 401 `Tool gateway session token is required` |
| `x-paperclip-tool-gateway-session` header | 401 `Tool gateway session token is required` |
| `x-tool-gateway-session` header | 401 `Tool gateway session token is required` |
| `x-paperclip-session` header | 401 `Tool gateway session token is required` |
| `x-gateway-session` header | 401 `Tool gateway session token is required` |
| `?sessionId=...` query | 401 `Tool gateway session token is required` |
| `?sessionId=...&token=pcgt_...` query | 401 `Tool gateway session token is required` |
| agent key only, no session | 401 `Tool gateway session token is required` |

`GET /api/tool-gateway/tools` declares only `BoardSessionAuth | BoardApiKeyAuth | AgentBearerAuth`.
There is no security scheme in the document that accepts a `pcgt_` token, and no
`GatewaySessionAuth` scheme exists. The response's own `toolsUrl` is therefore unreachable
by the credential the response itself issued.

**Diagnosis:** the gateway session mint and the gateway session verifier disagree. The
verifier treats a `pcgt_` token as an agent token and rejects it, while treating the agent
token as a missing session token. The two branches each reject the credential the other
branch wants. No presentation order works because the verifier has no branch that accepts
both.

## 5. An agent cannot even self-diagnose its own tool binding

| route | declared actor | agent result |
| --- | --- | --- |
| `GET /api/companies/{companyId}/tools/runtime-health` | board | 403 |
| `GET /api/companies/{companyId}/tools/gateways` | (admin) | 403 |
| `GET /api/companies/{companyId}/tools/profiles/effective/agents/{agentId}` | board | 403 |

`profiles/effective/agents/{agentId}` is the route that would report which tools Loom is
bound to. The agent identity gets 403 on it. So the exact diagnostic needed to fix this is
readable by the board but not by the agent that is broken.

## 6. Acceptance criteria status

| # | criterion | status this run |
| --- | --- | --- |
| 1 | `git push` to a branch and to `main`, no manual wiring | **PASS** — already demonstrated on run `dc6dff44`, three commits (`2aaefc..ff150d3`, `f150d3..a3feb74`) read back over the API. Not re-run this heartbeat. |
| 2 | a Notion tool on `tools/list`, can create a page | **FAIL** — `tools/list` has 2 tools, none Notion. No Notion route in the 704-path spec. Gateway session token rejected. |
| 3 | a Supabase tool on `tools/list`, can read `mirror_health` | **FAIL** — same as above. |
| 4 | non-comment issue writes on an issue with a stale `checkoutRunId` | **PASS — newly fixed.** `AXV-14.checkoutRunId` is now empty. `POST /api/issues/d171db68-.../work-products` returns `400 Validation error` on a malformed body, and `POST .../interactions` returns `400 Validation error` on a malformed body. Both are payload validation, not `409 Issue run ownership conflict`. The route now reaches validation, so ownership no longer blocks it. |

## 7. What the board has to change

Two changes, both in the tool gateway token verifier:

1. Accept a `pcgt_` gateway session token on `/api/tool-gateway/tools` and
   `/api/tool-gateway/tools/call`, and add a security scheme to the OpenAPI document that
   declares it. Without this the `toolsUrl` the platform itself returns is dead.
2. Bind the tool surface for connections `64ec3dca…` (Notion), `a37146be…` (Supabase) and
   `4c59b2fa…` (PostHog) to agent identities `1dc764c3-1c49-4bca-98de-571538e391a5` (Lens)
   and `2b4555f5-1c0b-4ce7-8835-1ed2c311d7c6` (Loom), so `tools/list` carries service tools
   rather than only the two connection-management tools.

Recommended third, so an agent can self-diagnose in future:
`GET /api/companies/{companyId}/tools/profiles/effective/agents/{agentId}` should permit the
agent whose own id is in the path.

No credential change is needed. No connection needs to be requested. No repository needs to
be bootstrapped. GitHub is healthy.
