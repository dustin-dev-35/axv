# AXV publication state and absence ledger

Recorded 2026-09-28 by Loom, run `ecf544e8`, on the board's instruction to
"publish now and record each absence" (interaction `58e918d1`, answered
2026-09-28, owner = `board-fixes-now`, publish = `publish-and-record`).

This file is the honest answer to "what can a reader actually reach today?"

## The one-line answer

**Nothing.** No reader can reach any AXV content by any route. The corpus is
complete in GitHub and invisible to the public.

## What exists

| layer | state | where |
| --- | --- | --- |
| memos | 6 primary memos + addenda, committed | `dustin-dev-35/axv` `corpus/`, `main` |
| posts | 6 posts, committed, 1,689 to 4,530 words each | `dustin-dev-35/axv` `posts/`, `main` |
| white paper | 10 sections, revision 4b, with changelog | `dustin-dev-35/axv` `whitepaper/`, `main` |
| experiment ledger | 61 records in `leaderboard.jsonl`, failures included | `dustin-dev-35/axv` `experiments/`, `main` |
| site build | **works** — `node site/build.mjs` emits 8 HTML files | `site/_site`, gitignored |
| section ids | 7 per post, 8 on the corrected one, `roads-not-taken` present on all 6 | in the built HTML |

The build is not the problem. Verified this run:

```
ok   posts/a-second-plurality-voter-is-worth-zero/   (7 section ids: tldr, what-advanced,
      how-it-works, roads-not-taken, evidence-strength, what-axv-did, links)
ok   posts/completed-pairs-hide-capped-failures/      (7 section ids: ...)
ok   posts/hand-written-rules-beat-generated-ones/     (7 section ids: ...)
ok   posts/low-effective-depth-is-residual-arithmetic/(7 section ids: ...)
ok   posts/overlapping-eval-windows-.../              (8 section ids: tldr, correction, ...)
ok   posts/thinking-5x-asymmetry-is-your-baseline/    (7 section ids: ...)
ok   whitepaper/
ok   index.html
```

## What does not exist

### 1. No domain. `axv.sh` does not resolve.

| probe | result |
| --- | --- |
| `DNS axv.sh` | **NXDOMAIN** |
| `DNS arxiv.org` (control) | 151.101.131.42 |
| `DNS github.com` (control) | 140.82.112.4 |
| `HTTPS https://axv.sh/` | could not resolve host |

The build script itself says so out loud:

```
WARN canonical URL is the placeholder https://axv.sh.
Set AXV_SITE_URL, drop a CNAME in site/, or build on the platform that supplies URL.
```

`axv.sh` was written into the build as a placeholder and never registered. The
`canonical` link in every built page therefore points at a host that does not
exist, which is worse than no canonical at all.

### 2. No Netlify site is linked to the repository

| probe | result |
| --- | --- |
| `https://dustin-dev-35-axv.netlify.app` | **HTTP 404** |
| `https://dustin-dev-35.netlify.app` | **HTTP 404** |
| `https://axv.netlify.app` | HTTP 200, `<title>Jay Doe</title>` — **not AXV** |

Note the third row. `axv.netlify.app` serves a stranger's placeholder page. It
must not be treated as ours and must not be pointed at. AXV has no Netlify site.

`netlify.toml` claims "The push of this repository is the publication; Netlify
builds from the repo and there is no manual upload path." That sentence is false
as written, because no Netlify site is attached to receive the push. **A pushed
commit with no site attached is not a publication.** It is history.

### 3. No Notion page for any post

Notion is the canonical record for readers. There is no Notion tool on the agent
tool surface, so not one of the 6 posts or the white paper has a Notion page.
Tracked on AXV-19.

### 4. `mirror_health` cannot be queried

Supabase has no tool on the agent tool surface, so the pre-publish mirror gate in
the site-publish procedure has never been run, for any post. Tracked on AXV-19.

### 5. No PostHog events, and no read-depth data

The markup carries the right `section_id` on every section of every post, so
instrumentation is structurally correct. The build reports
`analytics: no POSTHOG_KEY`, so no event fires. `us.i.posthog.com` is referenced
in the repo but no key is present. Even if a key were present, the question the
company exists to answer — does anyone reach `roads-not-taken` — cannot be
answered about a site no reader can reach.

## Why this matters more than the connector defect

The connector tool surface gap (AXV-19) costs AXV its *records*. This gap costs
AXV its *readers*, and it is not caused by the connector gap. Fixing the gateway
would let Loom write Notion pages, and those pages would sit in a workspace
nobody is reading, on a domain that does not resolve, behind a site that is not
deployed.

The two must be fixed together. A gateway fix alone does not publish anything.

## What is needed, in order

1. **Link a Netlify site to `dustin-dev-35/axv`.** Until a site exists, every
   push is a no-op for readers. This is the single blocking step.
2. **Register the domain, or drop it.** If `axv.sh` is not being registered, set
   `AXV_SITE_URL` to the real Netlify hostname and remove `axv.sh` from the
   build, so the `canonical` link stops pointing at a dead host. A CNAME in
   `site/` works too, and the build already looks for one.
3. **Then** fix the gateway (AXV-19) so the Notion mirror, the `mirror_health`
   gate, and the PostHog events can be written.
4. **Then** set `POSTHOG_KEY` and confirm `roads-not-taken` read depth is being
   recorded against real traffic.

Steps 1 and 2 cost nothing and are not blocked by the connector defect. They can
start now.

## Correction this record implies

Loom's own procedure says "The push is the act of publication" and "Never publish
an unpushed commit." Both are half-truths as applied. A push is *necessary* for
publication and not *sufficient*. The word "publish" has been used in six commit
messages and in the corpus README for commits that no reader can reach. From this
record forward, "published" means: pushed, deployed, and reachable at a URL that
resolves.
