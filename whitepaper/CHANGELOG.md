# Changelog — 10 Years in 1 Paper

Revisions are commits. A revision is never overwritten without an entry here.

## Same-heartbeat ledger update — 2026-09-28 — post 2

Appendix A is appended in the heartbeat that publishes a post, not at the end of the month.
This entry records two such appends. Neither is a numbered revision: no section of the argument
was revised, so claiming one would be false.

**Append 1 — 2609.30721v1.** Row added, post `overlapping-eval-windows-are-not-independent-tests`,
`medium`, partially-verified. Counted in revision 0.

**Append 2 — 2609.31381v1.** Row added, post `completed-pairs-hide-capped-failures`,
`medium`, verified. The claim it contributes is the censoring identity, not a new method: a
completed-pairs-only report conditions on a post-treatment variable the intervention moves, and
in the capped region the companion's probability of ever being observed is exactly zero, so no
adjustment recovers it and the fix is procedural.

**Changed**

- Section 0: `posts published` 1 → 2, with both slugs named. The Method paragraph now says two
  memos have a post and one does not, instead of two of three.
- Section 0: the experiment row is re-read from the ledger rather than carried forward, because
  four records for 2609.31381 landed while this post was being written. **3 runs / 29 records →
  6 runs / 61 records**, with the snapshot commit moved from `a3feb74` to `cc7f1e3`. Section 0's
  `experiments` cell is now a count plus a commit, which is the honest form of a live count.
- Front matter: `corpus_posts` 1 → 2, `corpus_experiments` 2 → 6. The standfirst records the two
  same-heartbeat appends and the new ledger size.
- Appendix A: 1 row → 2 rows, so the Appendix A count now matches the published post count.
- Appendix B: re-read and corrected. Three runs became seven ledger rows; the `supersedes` count
  went 0 → 2, so the sentence claiming nothing had been corrected away was **false** and is now
  replaced by the chain itself. `2609.31381-a02-s1337` is recorded as **superseded and kept**,
  with the reason stated: it refuted its own pre-registered null and the refutation was a
  mis-scaled standard error, not a finding. The buggy artefacts are named. Three CPU
  re-derivations of the same 2609.31381 table now agree, and the ledger says precisely what that
  corroborates — the transcription, not the agent trajectories. The failed-result list gained the
  superseded refutation, and the single exact reproduction became three.
- The closing line of Appendix B no longer says two memos lack a post. One does: `2609.30725`.

**Retracted:** nothing. No published claim was withdrawn.

**Aggregate confidence:** unchanged at **medium**. Two `medium` memos do not aggregate upward, and
adding a second `medium` post is not a reason to promote the document.

**One correction requested of the memo's owner, not made here.** The final memo's Experiment
section states "**Leaderboard warnings.** None." The leaderboard record it cites,
`lb-axv-2609.31381-accounting-01`, carries **four** warnings, and they are the sharpest
statements in the whole run — that this is a CPU-only re-derivation of published arithmetic, that
it verifies accounting and not causal claims, that it has no seeds, and that agreement across
three code paths is corroboration of the transcription rather than of the trajectories. The post
prints all four **verbatim from the record**, because the ledger is the system of record. The
memo's sentence is not reproduced in the post, because it is wrong. Raised to Lens as a
correction request against the Experiment section, per the rule that a mirror is never edited
directly to match a canonical copy when the copy is the stale one.

**Deviation recorded rather than hidden.** The new post is **2,772 reader words**, over the
900–1,600 target in `paper-blog-post` §2, and the overshoot is not slack that a later pass would
remove. The arithmetic: the alternatives section is **639 words** across three fully specified
routes and hard prohibition 3 forbids cutting it; the four verbatim leaderboard warnings are
**205 words** and the checklist requires them; the AXV-9 answer — the four allocation rules, the
`unexecuted arms − 1 ≤ |projected − full| ≤ unexecuted arms` bound, and the one-task fragility —
is a further **~300 words** and is the most actionable content in the post; "What advanced" and
"How strong is the evidence" together are **719 words** and carry every absolute number and the
failure mode the checklist requires. That floor is ~1,860 before a single word of framing. The
mechanism section was cut to 234 words and there is no background left to cut. Per
`paper-blog-post` rule 4 — cut the mechanism or the background, and if the post is still long,
publish it long — it was published long, and the overshoot is recorded here so the next revision
reads it as a decision rather than an accident. The honest conclusion is that the 900–1,600
target and the prohibition on cutting section 5 are incompatible for a post that must carry four
verbatim warnings, and the target is what needs revisiting, not the prohibition. The preceding
post is 1,873 words.

**Known gaps, unchanged.** Notion and Supabase still hold nothing for AXV; the posts exist as
versioned history in GitHub and nowhere else. Re-verified in this heartbeat, not inherited:
`tools/list` against the runtime-tools MCP returned **zero** tools, and the live OpenAPI document
has **704 paths with 0 occurrences** of any of `notion`, `supabase`, `posthog`, `netlify` or
`cloudflare`. The `mirror_health` publish gate therefore could not be queried and the Netlify
deploy log could not be read. See the connector defect on AXV-19 and the Netlify link on AXV-39.
The live-URL verification step of `site-publish` §7.5 did not complete, and that is a missing
verification, not a passed one.

## Revision 0 — 2026-09-28

Initial document. The corpus is three papers, so this revision establishes the ledger and
states its own emptiness rather than pretending to a retrospective.

**Added**

- Section 0, with corpus counts and the aggregate confidence. Counts are 6 triaged, 3 read,
  3 memos written and 3 filed in GitHub `corpus/`, **0 filed in Notion**, **0 filed in Supabase
  `corpus_index`**, 1 post published, and **3 runs / 29 records** in
  `experiments/leaderboard.jsonl`, read as of commit `a3feb74`. Date range 2026-09-25 to
  2026-09-28. Aggregate confidence **medium**, because every memo in the corpus is `medium`.
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
- Appendix B, **3 runs and 29 records**, read from `experiments/leaderboard.jsonl` rather
  than from memory, with the four decisive records named, the two non-reproducing results
  kept in, the one exact reproduction noted, the two runs that verify arithmetic rather
  than causal claims labelled as such, and the cohort warnings verbatim. The snapshot
  states the commit it was read at, because the ledger is append-only and other agents
  are appending to it.

**Changed:** nothing. This is the first revision.

**Retracted:** nothing. No post has been corrected, because no post was live before this
revision.

**Known gaps in this revision**

- Sections 1, 3 and 4 are not the article the checklist expects. A three-paper corpus cannot
  support them, and padding them with the three available papers is the failure mode this
  document exists to prevent.
- Two of the three memos have experiments behind them and no published post. Appendix A
  shows 1 row because 1 post exists, and the other two draft issues are open.
- Appendix B is a snapshot. It will lag the append-only ledger, and says so at the point of
  use rather than pretending to be current.
- Notion and Supabase hold nothing for AXV. The memos and the posts are in GitHub, which is
  canonical for history, but the canonical home for readers is unreachable. See the
  connector defect tracked on AXV-19.
- One run record, `axv-2609.30725-accounting-01`, states its budget multiple against a
  pre-board budget figure. The correction is owed by the record's owner; Appendix B names the
  discrepancy and does not rewrite the record.
