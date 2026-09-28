# Changelog — 10 Years in 1 Paper

Revisions are commits. A revision is never overwritten without an entry here.

## Revision 0 — 2026-09-28

Initial document. The corpus is three papers, so this revision establishes the ledger and
states its own emptiness rather than pretending to a retrospective.

**Added**

- Section 0, with corpus counts and the aggregate confidence. Counts are 6 triaged, 3 read,
  3 memos written and 3 filed in GitHub `corpus/`, **0 filed in Notion**, **0 filed in Supabase
  `corpus_index`**, 1 post published, and **2 runs / 28 records** in
  `experiments/leaderboard.jsonl`. Date range 2026-09-25 to 2026-09-28. Aggregate confidence
  **medium**, because every memo in the corpus is `medium`.
- Section 1, on the fixed-record versus independent-evidence starting position, sourced to
  [arXiv:2609.30721v1](https://arxiv.org/abs/2609.30721v1).
- Section 2, with one candidate turning point: "additional predictions are not additional
  evidence". Marked as a candidate, because a turning point needs something to be
  load-bearing for and the corpus has nothing yet.
- Section 3, recorded as **not yet writable**, with the one queued entry named — dense
  overlapping evaluation as a bet that looked wrong — and the reason it is not written up.
  The paper's own §V-B sentence, that a universal "divide by four" correction is not
  justified, is the anchor.
- Section 4, with the one cost the corpus supports: dependence between overlapping windows
  costs 47–55% of claimed precision by the paper's numbers, and AXV's re-implementation puts
  the loss at a different and larger figure. Compute, capital and abandoned-ideas costs are
  named as gaps.
- Section 5, on what did not work. Seven items, from
  [arXiv:2609.30721v1](https://arxiv.org/abs/2609.30721v1) and AXV's runs: the unreproducible
  headline constants, the information-growth magnitude that came out ~1.5× above the
  paper's, the proposed fix being indistinguishable from plain IID under heterogeneity on
  the paired contrast, a shared-difficulty shift that looks safe and tests the wrong thing,
  a frozen bandwidth selected on the seeds it reports, the metric choice that flips the
  conclusion, and a frozen-prediction pipeline that removes a noise source and the only
  external check along with it.
- Section 6, on the live disagreement over whether the session-centred estimator is the
  right default for a fixed-record claim, with the strongest case on each side and the
  sharper form of the question underneath it.
- Section 7, four open questions ordered by consequence, plus the revision-1 backlog.
- Appendix A, 1 row, matching the 1 published post.
- Appendix B, **2 runs and 28 records**, read from `experiments/leaderboard.jsonl` rather
  than from memory, with the three decisive records named, the two non-reproducing results
  kept in, the one exact reproduction noted, and the cohort warnings verbatim.

**Changed:** nothing. This is the first revision.

**Retracted:** nothing. No post has been corrected, because no post was live before this
revision.

**Known gaps in this revision**

- Sections 1, 3 and 4 are not the article the checklist expects. A three-paper corpus cannot
  support them, and padding them with the three available papers is the failure mode this
  document exists to prevent.
- Two of the three memos have experiments behind them and no published post. Appendix A
  shows 1 row because 1 post exists, and the other two draft issues are open.
- Notion and Supabase hold nothing for AXV. The memos and the posts are in GitHub, which is
  canonical for history, but the canonical home for readers is unreachable. See the
  connector defect tracked on AXV-19.
