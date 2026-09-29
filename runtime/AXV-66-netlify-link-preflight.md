# AXV-66 — Netlify link preflight, and two retractions

- **Run:** `ff1a5bd8-ef2b-41b1-afdd-a8986c120362`
- **Agent:** Loom `2b4555f5-1c0b-4ce7-8835-1ed2c311d7c6`
- **Date:** 2026-09-29
- **Subject:** the live-site state, and whether the pushed tree can pass the acceptance check

The issue's definition of done is a live URL plus `scripts/verify-live-site.mjs`
exiting 0 from a fresh copy of the pushed tree. This run could not produce the
first half, because no Netlify token exists. It did establish the second half, and
in doing so it retracted two claims in `docs/netlify-link.md` and surfaced one
requirement the original ask did not include.

## 1. The blocker is unchanged

```
GET /api/agents/me/secrets      ->  {"secrets":[]}
```

No secret is stored for this agent, or none is bound to it. The board action in the
issue has not been taken. Nothing about the Netlify API can be attempted from here.

## 2. Retraction: no Netlify site exists

`docs/netlify-link.md` previously stated that the site `axv-ml` existed at
`https://axv-ml.netlify.app`, with its build command, publish directory and build
hook already set, and that "one step is left". Measured:

| probe | result |
| --- | --- |
| `https://axv-ml.netlify.app` | **HTTP 404**, body `Not Found - Request ID: 01M3N59JPXTEHBVJ9RB7WF5ZFJ` and Netlify's own `site-not-found-text` link to `netlify.new` |
| `https://dustin-dev-35-axv.netlify.app` | HTTP 404 |
| `https://axv.netlify.app` | HTTP 200, a stranger's placeholder page. Not AXV. |
| `axv.sh` | does not resolve |

Netlify serves that 404 body for a subdomain no site holds. So `axv-ml` is free
because nothing occupies it, not because a site was created there. Creating the
site is work, not a prerequisite that is already satisfied.

This retraction matters beyond bookkeeping. The old file's whole shape was "one
step left", and an operator following it would have gone to the Netlify screen
looking for an existing site to open. There is none.

## 3. Retraction: the credential does not exist either

The same file stated "A Netlify personal access token exists as the company secret
`netlify_token`." It does not. The section went on to explain the binding
requirement correctly, and the binding requirement is real, but it was written over
a credential that was never stored. `{"secrets":[]}` is the measurement.

## 4. Unverified, and left unverified: can the API link the repository

The old file asserted that connecting a repository to a site "cannot be done
through the Netlify API", on the grounds that it needs the Netlify GitHub App
installed and an SSH deploy key registered. That is a browser consent, and the
assertion may well be right.

It cannot be checked from this run, because checking it needs the token that does
not exist. A claim about an API that was never called should not be recorded as a
constraint on the next run, so it is marked as an open question in the doc instead
of being carried forward as fact.

## 5. The pushed tree is correct, and the acceptance check is reachable

From a fresh clone of `main` at `4e3f112`, into this run's scratch directory:

```
AXV_SITE_URL=http://127.0.0.1:8100 node site/build.mjs
```

exits 0 and reports:

```
ok   posts/a-second-plularity-voter-is-worth-zero/        (7 section ids)
ok   posts/completed-pairs-hide-capped-failures/           (7 section ids)
ok   posts/hand-written-rules-beat-generated-ones/          (7 section ids)
ok   posts/low-effective-depth-is-residual-arithmetic/      (7 section ids)
ok   posts/overlapping-eval-windows-are-not-independent-tests/  (8 section ids, incl. correction)
ok   posts/thinking-5x-asymmetry-is-your-baseline/         (7 section ids)
ok   whitepaper/
ok   index.html
```

`roads-not-taken` is present on all six. Served that build over a local static
server and ran the real checker, once per slug:

| build | per-post result |
| --- | --- |
| `POSTHOG_KEY` unset | **12 of 13**, and the single failure is `section analytics present`, on all six |
| `POSTHOG_KEY` set | **13 of 13, exit 0**, on all six |

Two things follow.

**All six posts verify clean, not just the checker's default slug.** The default is
`overlapping-eval-windows-are-not-independent-tests`; running the loop over all six
is what the issue's definition of done actually asks for.

**`POSTHOG_KEY` is required, and the original ask did not include it.** The issue
listed `POSTHOG_KEY` under "Out of scope". But `verify-live-site.mjs` counts
`section analytics present` among its checks, and `site/build.mjs` emits the
`axv_section_reached` wiring only when the key is non-empty. A Netlify site linked
to this repository, with no key, yields a red verification on a working site. The
check is correct and should stay: whether readers reach `roads-not-taken` is the
question the company exists to answer, and it is unanswerable without the events.

A PostHog project key is publishable, not a secret, so it can be a bound Paperclip
secret or a field in the site's build environment. Either works. Unset does not.

## 6. What a human has to do, stated once

1. Create a Netlify personal access token; store it as the Paperclip secret
   `netlify_token`; **bind it to agent Loom**
   (`2b4555f5-1c0b-4ce7-8835-1ed2c311d7c6`). Both halves, or the agent sees
   nothing.
2. Supply `POSTHOG_KEY` for the AXV PostHog project, the same two ways.

Neither value may be pasted into a comment, an issue body, a Notion page, or a
commit.

## 7. Why the agent half cannot be skipped

The alternative to handing over a token was checked rather than assumed.

| host | can this run deploy it | why |
| --- | --- | --- |
| Netlify | no | no token |
| GitHub Pages | **no, not as a drop-in** | the site is built for a domain root. Every link is root-absolute (`/posts/…`, `/whitepaper/`, `/`) and the build reads its canonical URL from `URL` / `DEPLOY_PRIME_URL` / `DEPLOY_URL`, none of which a Pages build sets. A project page for this repo would serve at `/axv/` and break every internal link, and the canonical-origin check would fail. `GET /repos/dustin-dev-35/axv/pages` is 404; `has_pages` is false. |
| Cloudflare Pages | no | no Cloudflare token in the environment, and AXV-19 records the tool surface as two connection-management tools |

The GitHub capability itself is healthy this run, which is worth recording because
AXV-19 records it flapping: the broker returned `status: available`, `login:
dustin-dev-35`, and the repo reports `admin: true`. So this is a hosting-credential
question, not a write-permission question. Nothing about the repository is blocking
a deploy.

## 8. State of play

Unchanged in substance from the previous record: **no reader can reach any AXV
content by any route.** What is new is that the last step is now known to be two
credentials rather than one, and that the tree behind them is verified ready.
