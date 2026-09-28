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

## The site already exists. Do not create another one.

| field | value |
| --- | --- |
| site name | `axv-ml` |
| address | `https://axv-ml.netlify.app` |
| build command | `node site/build.mjs`, already set |
| publish directory | `site/_site`, already set |
| build hook on `main` | created |

The name `axv` is not available. It is held by an unclaimed Netlify site that
serves a placeholder page, and a request to claim it is refused.

Everything above is done. **One step is left, and it cannot be done through the
Netlify API:** connect the repository to the existing `axv-ml` site.

## The one remaining step

In the Netlify screen, open the `axv-ml` site, go to site settings, and connect the
GitHub repository `dustin-dev-35/axv` on branch `main`.

That single action does two things at once, which is why the API cannot substitute
for it: it installs the Netlify GitHub App on the account, and it registers
Netlify's SSH deploy key with the repository.

Without it the build fails in a specific and unhelpful-looking way:

```text
Failed during stage 'preparing repo': Unable to access repository.
Cloning into '/opt/build/repo'...
Host key verification failed.
fatal: Could not read from remote repository.
: exit status 128
```

That is Netlify falling back to an SSH clone of a repository whose deploy key was
never registered. The Netlify API accepts a repository in six different shapes and
returns HTTP 200 with the repository still unlinked every time, and it exposes no
endpoint for the deploy key it would need. The step is a browser consent, not a
setting.

After it, a push to `main` builds on its own. A green commit is still not a green
deploy, so watch the log, then run the verification command below.

The site address is the canonical one. The build reads it from the host, so nothing
else needs setting. `axv.sh` is not used.

Optional, and not needed for the site to work: set `POSTHOG_KEY` in the build
environment. The build is green without it and simply ships no analytics snippet,
so read depth is unmeasurable until it is set.

Optional, and a separate action after the site exists: add a custom domain and
point Cloudflare at the Netlify target. There is no Cloudflare token in the
environment, so DNS cannot be done from an agent run.

## The credential, for later runs

A Netlify personal access token exists as the company secret `netlify_token`. It is
what lets an agent run create and configure the site without a browser. It is
stored as a secret, and it never appears in a comment, a chat message, an issue
body, a Notion page, or a commit.

Two things must both be true for an agent to see it, and the second is the one that
fails silently:

1. The token is stored as a secret.
2. The secret is **bound to the agent `Loom`**. A company secret that is not bound
   to an agent is invisible to that agent. After binding, the agent lists its own
   secrets and sees the key.

With the token bound, an agent can create a site, set the build command and
publish directory, create a build hook, and read deploy status. It still cannot
connect the repository, for the reason above.

## Verify, from a fresh copy of the pushed code

Not from a working tree. A working tree proves the file you edited, not the
published site.

```bash
git clone https://github.com/dustin-dev-35/axv
cd axv
node site/build.mjs
node scripts/verify-live-site.mjs https://axv-ml.netlify.app
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
