# Link the site to Netlify

AXV has version-controlled content and no readers. This file is written down so
nobody has to reconstruct it from a thread.

The repository is ready. `main` builds green and passes the acceptance checks. What
is missing is a Netlify site that builds it.

## Corrections

Measured 2026-09-29 by Loom, run `ff1a5bd8`, against `main` at `4e3f112`. The
previous revision of this file said the work was nearly finished. It was not, and
two of its statements were false. They are retracted here rather than edited away,
because an operator who read the old text would otherwise act on it.

| retracted claim | measured reality |
| --- | --- |
| "The site already exists. Do not create another one." | **False.** `https://axv-ml.netlify.app` returns HTTP 404 with Netlify's own site-not-found body (`Build and deploy your own site for free: ... site-not-found-text`). The site does not exist. |
| "A Netlify personal access token exists as the company secret `netlify_token`." | **False.** `GET /api/agents/me/secrets` returns `{"secrets":[]}` for this agent. No secret is stored, or none is bound. |
| "Everything above is done. One step is left." | **False as a consequence of the two rows above.** There is no site to link a repository to, so the site itself is work, not a prerequisite. |
| "One step is left, and it cannot be done through the Netlify API." | **Unverified, and now moot.** It could not be checked without a token, and the site it referred to does not exist. Treat it as an open question, not as a finding. |

Probes behind the table, all 2026-09-29:

| probe | result |
| --- | --- |
| `GET /api/agents/me/secrets` | `{"secrets":[]}` |
| `https://axv-ml.netlify.app` | HTTP 404, site-not-found |
| `https://dustin-dev-35-axv.netlify.app` | HTTP 404 |
| `https://axv.netlify.app` | HTTP 200, a stranger's placeholder. Not ours. Do not point at it. |
| `axv.sh` | does not resolve |

**What this run did establish**, from a fresh clone of the pushed tree, so that the
moment a token exists the only remaining step is the Netlify call itself:

- `node site/build.mjs` on `main` at `4e3f112` builds 8 pages and exits 0. Seven
  section ids per post, eight on the corrected one, `roads-not-taken` on all six.
- `node scripts/verify-live-site.mjs <base> <slug>` exits 0, 13 of 13 checks, for
  **all six** post slugs — **but only when `POSTHOG_KEY` is set in the build
  environment.** Without it, exactly one check fails on every post:
  `section analytics present`. See the next section; this is a new finding and it
  changes what has to be asked of the board.

## What the repository already declares

These are in `netlify.toml` at the repository root. Netlify reads them. Do not
retype them into the Netlify screen unless the screen insists on non-empty fields,
in which case use the values below verbatim.

| setting | value | source |
| --- | --- | --- |
| build command | `node site/build.mjs` | `netlify.toml` |
| publish directory | `site/_site` | `netlify.toml` |
| Node version | `24` | `netlify.toml` |
| deploy previews | off, ignored | `netlify.toml` |
| `POSTHOG_KEY` | unset, **and required for the acceptance check** | build env |

Deploy previews are off on purpose. A preview of a half-written post is a way to
put an unpublished claim on the public internet.

## `POSTHOG_KEY` is not optional, whatever `netlify.toml` implies

`netlify.toml` calls the key unset and optional. The acceptance check disagrees,
and the acceptance check is the thing that has to pass.

`scripts/verify-live-site.mjs` includes `section analytics present` in its 13
checks, and the build emits the `axv_section_reached` wiring **only** when
`POSTHOG_KEY` is non-empty. Measured on `main` at `4e3f112`, all six slugs:

| build | result per post |
| --- | --- |
| `POSTHOG_KEY` unset | 12 of 13. Only `section analytics present` fails. |
| `POSTHOG_KEY` set | 13 of 13, exit 0. |

So a Netlify site linked to this repository, with no `POSTHOG_KEY`, produces a
**red** verification on a perfectly good site. The site would be live and the
publication would look failed.

This is worth stating plainly because the check is deliberate: the alternatives
section is the point of the company, and "did any reader reach `roads-not-taken`"
is unanswerable without the events. The check is right and the key is required.
A PostHog project key is a publishable project key, not a secret, so it can live
in the Netlify build environment or be handed over as a bound Paperclip secret.
Either is fine; leaving it unset is not, if the acceptance check is to pass.

## No Netlify site exists

The site name `axv` is not available. It is held by an unclaimed Netlify site that
serves a stranger's placeholder page, and a request to claim it is refused. Any
name must therefore be one that is free. `axv-ml` is free **because nothing holds
it**, not because a site was created there.

| field | value |
| --- | --- |
| site name | a free name; `axv` is taken, `axv-ml` does not exist |
| build command | `node site/build.mjs`, read from `netlify.toml` |
| publish directory | `site/_site`, read from `netlify.toml` |
| repository link | **not established** |

## What an agent run needs from the board

Two things, and the second was not in the original ask.

1. **`netlify_token`.** A Netlify personal access token, stored as a Paperclip
   secret and **bound to the agent `Loom`**
   (`2b4555f5-1c0b-4ce7-8835-1ed2c311d7c6`). A company secret that is not bound to
   an agent is invisible to that agent, and this fails silently. After binding,
   `GET /api/agents/me/secrets` lists the key.
2. **`POSTHOG_KEY`.** A PostHog project key for the AXV project, either as a
   Paperclip secret bound to `Loom` or typed into the site's build environment.
   Without it the acceptance check cannot pass, for the reason above.

The token never appears in a comment, a chat message, an issue body, a Notion page,
or a commit. It belongs in Paperclip secrets.

With the token bound, an agent run can create the site, set the build command and
publish directory, create a build hook, and read deploy status. Whether it can also
**link the repository** is not established: an earlier revision of this file claimed
it could not, and that claim was made without a token to test it, so it is recorded
as an open question above rather than as a constraint. If linking turns out to need
a browser consent, that is one Netlify screen and it is not an agent's to click.

## The steps, once unblocked

1. Create the site, or find the existing one, and connect `dustin-dev-35/axv` on
   branch `main`. Do not retype the build settings; `netlify.toml` supplies them.
2. Set `POSTHOG_KEY` in the site's build environment.
3. Trigger the first deploy and **read the deploy log**. A green commit is not a
   green deploy.
4. From a **fresh clone of the pushed tree**, run the verification command below
   and require exit 0 for all six slugs, not only the default one.
5. Record the live URL on the tracking issue and in `whitepaper/CHANGELOG.md`.

`site/_site` is the output. `axv.sh` is not used and does not resolve; the build
warns and fails its exit code if the canonical URL is still the placeholder, so a
green build already proves the canonical URL is real.

## Verify, from a fresh copy of the pushed code

Not from a working tree. A working tree proves the file you edited, not the
published site.

```bash
git clone https://github.com/dustin-dev-35/axv
cd axv
AXV_SITE_URL=https://<the-site-address> node site/build.mjs
for slug in a-second-plurality-voter-is-worth-zero \
            completed-pairs-hide-capped-failures \
            hand-written-rules-beat-generated-ones \
            low-effective-depth-is-residual-arithmetic \
            overlapping-eval-windows-are-not-independent-tests \
            thinking-5x-asymmetry-is-your-baseline; do
  node scripts/verify-live-site.mjs https://<the-site-address> "$slug" || echo "FAILED $slug"
done
```

The build has to run with `AXV_SITE_URL` set to the address being verified, or the
canonical-origin check fails against a locally built tree. That is the check
working, not the check being wrong.

The checker exits 0 only when all of these hold, and prints a table:

- the post page, the white paper page, and the front page all load
- all seven section ids resolve to real content, not to an empty target
- `roads-not-taken` is present and resolves
- the section analytics snippet is shipped
- the canonical URL points at the site being served
- the sitemap lists the post and the white paper

A green deploy with a canonical URL on a hostname that does not resolve is the
failure this exists to catch, because nothing else reports it.

## Not attempted: Cloudflare DNS

There is no Cloudflare token in the environment, so DNS cannot be done from an
agent run. The Netlify hostname is the canonical URL until someone changes that.

