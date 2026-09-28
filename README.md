# AXV

AXV is a research company that reads arXiv papers in ML and AI, compresses each
advancement with its alternative routes and pros/cons, publishes a blog post per
paper, and folds the corpus into a decade-long white paper.

The thing AXV is actually after is not the summary of a paper. It is the **roads not
taken**: for a claimed advance, the credible alternative ways to have reached the same
or better result, each with real pros and real cons, and an honest account of why the
authors plausibly did not take it. Most ML papers report one route and call it a
contribution. AXV names the others.

## This repository

This is the single version-controlled home for everything AXV produces. It exists so
that the white paper can cite a memo and a run by commit, and so those citations stay
checkable.

| Path | What lives here |
| --- | --- |
| `corpus/<arxiv-id>.md` | one reading memo per paper |
| `posts/<slug>.md` | blog post markdown source |
| `whitepaper/10-years.md` | the decade white paper |
| `whitepaper/CHANGELOG.md` | what changed in each revision |
| `experiments/leaderboard.jsonl` | the shared append-only run ledger |
| `experiments/runs/<run-id>/` | `run.json`, `train.py`, `diff.patch`, `train.log`, `metrics.json` |
| `site/` | the Netlify-served blog and white paper |

## The separate harness repository

The experiment harness is **not** here. It lives in `dustin-dev-35/autoresearch`, a
fork of `karpathy/autoresearch`. Harness changes — `train.py`, harness behaviour — go
there, one branch per experiment series, named `experiment/<arxiv-id>-<series>`.

A memo does not go in the harness fork. A post does not go in the harness fork.
`leaderboard.jsonl` does not go in the harness fork. Keeping the two histories
separate is the point: the harness has a code history, this repository has a
research history, and mixing them corrupts both.

## Rules that are not negotiable

1. **GitHub is the record.** A Runpod network volume is ephemeral. A run that exists
   only on a pod volume did not happen. Push before you terminate the pod.
2. **`experiments/leaderboard.jsonl` is append-only.** Never rewrite it. A correction
   is a new record carrying `supersedes`.
3. **No secrets.** No token, no API key, no `RUNPOD_API_KEY`, in any commit here.
4. **No bulk artifacts.** No dataset, no checkpoint, no multi-megabyte training log.
   Point at the volume path and record it.
5. **A superseded memo is a new commit, never an edit.** The history of what AXV
   believed, and when, is part of the product.
6. **Do not work around a missing artifact by writing it to the wrong repository.**
   Report the gap instead.

## Storage contract

Routing, schemas, and the canonical-and-mirror rule are defined in the
`storage-contract` skill. This README is orientation, not the contract.
