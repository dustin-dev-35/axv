# Link the site to Netlify

AXV has version-controlled content and no readers. This file is the one remaining
step, written down so nobody has to reconstruct it from a thread.

The repository is ready. `main` builds green and passes the acceptance checks. What
is missing is a Netlify site that builds it.

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
| `POSTHOG_KEY` | unset, optional | build env |

Deploy previews are off on purpose. A preview of a half-written post is a way to
put an unpublished claim on the public internet.

## Path A: link the site in the Netlify screen

1. In Netlify, add a new site and import an existing project from GitHub.
2. Choose the repository `dustin-dev-35/axv`.
3. Accept the build command and publish directory. Netlify reads both from
   `netlify.toml`. If the fields are empty, type `node site/build.mjs` and
   `site/_site`.
4. Save. The first deploy starts on its own. Watch the log. A green commit is not
   a green deploy.
5. The site address is the canonical one. The build reads it from the host, so
   nothing else needs setting. `axv.sh` is not used.

Optional, and not needed for the site to work: set `POSTHOG_KEY` in the build
environment. The build is green without it and simply ships no analytics snippet,
so read depth is unmeasurable until it is set.

Optional, and a separate action after the site exists: add a custom domain and
point Cloudflare at the Netlify target. There is no Cloudflare token in the
environment, so DNS cannot be done from an agent run.

## Path B: give the agent the credential instead

This path is the one an agent can complete end to end, and it is the faster one
if the board does not want to click through the Netlify screen.

Create a **Netlify personal access token**, then store it in **Paperclip secrets**
as the company secret `netlify_token`.

Two things must both be true, and the second is the one that goes wrong:

1. The token is stored as a secret. It never goes in a comment, a chat message,
   an issue body, a Notion page, or a commit.
2. The secret is **bound to the agent `Loom`**. A company secret that is not bound
   to an agent is invisible to that agent. After binding, the agent lists its own
   secrets and sees the key.

With the token bound, the agent creates the site, links the repository, sets the
build command and publish directory from `netlify.toml`, triggers the deploy, and
runs the verification below.

## Verify, from a fresh copy of the pushed code

Not from a working tree. A working tree proves the file you edited, not the
published site.

```bash
git clone https://github.com/dustin-dev-35/axv
cd axv
node site/build.mjs
node scripts/verify-live-site.mjs https://<the-site-address>
```

The checker exits 0 only when all of these hold, and prints a table:

- the post page and the white paper page both load
- all seven section ids resolve to real content, not to an empty target
- `roads-not-taken` is present and resolves
- the section analytics snippet is shipped
- the canonical URL points at the site being served
- the sitemap lists the post and the white paper

A green deploy with a canonical URL on a hostname that does not resolve is the
failure this exists to catch, because nothing else reports it.
