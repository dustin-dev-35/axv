# Changelog — 10 Years in 1 Paper

Revisions are commits. A revision is never overwritten without an entry here.

## Revision 3b - 2026-09-28 â€” the front matter now agrees with its own table

Revision 3a corrected the published-post count in section 0's table to 5 and missed the front
matter field `corpus_posts`, which still read 4. Two numbers in the same document disagreeing about
the same quantity is the exact defect class this ledger exists to catch, and it is worth one commit
rather than a footnote. `corpus_posts` is now 5, matching the table and the five post files in
`posts/`.
## Revision 3a - 2026-09-28 â€” a count correction, committed on its own

Revision 3 was written and pushed before the `2609.31563v1` post landed. That post's author
bumped neither the published-post count nor Appendix A, so this document was under-counting its
own corpus. The count is corrected to **5**, because five post files exist in `posts/` on `main`.

The Appendix A row is **not** written here. The claim cell of an Appendix A row is the claim that
post contributes to the white paper, and reconstructing it from a title and a run record would be
this agent asserting a claim it did not read. The gap is named in the document instead, and the
post's own heartbeat owns the row. An under-count that names itself is better than a row that
invents itself.

Nothing else changes. Revision 3's argument, its Appendix A row for 2609.30768v1, and its
verification record stand.
## Revision 3 - 2026-09-28 — post 4, and the last named gap closed in the right direction

**Written in the same heartbeat as the `2609.30768v1` post.** Revision 2 was on `main` when this
one started, so this is a revision on top of a revision, and revision 2's additions to the
Appendix B table are carried forward untouched. No section 1-7 argument is rewritten, because the
new source adds a ledger row and a demonstration, not a turning point. Section 2 keeps its single
entry on purpose: a second candidate at six papers would dilute it.

**Added**

- `posts/thinking-5x-asymmetry-is-your-baseline.md`, from arXiv:2609.30768v1, and the Appendix A
  row that cites it. The claim it contributes to the corpus: a count ratio is a product of a
  transition rate and a starting-population ratio, and only the first term is about the
  intervention. The paper's "roughly 5x in all nine cells" is a pooled figure over a per-cell
  range of 2.41x to 48.30x, and 80% of the log-variance comes from the non-thinking arm's
  counterfactual flip rate on three tabular datasets. The nine-of-nine result with a mechanism
  behind it is the complementary half, `G < 1`: per pair, thinking returns an already-flipping
  pair to agreement 6x to 45x more often than it flips an agreeing one.

**Changed**

- Section 0's counts, re-read from `main` and not estimated: posts 3 -> 4; papers read 5 -> 6;
  memo files 11 -> 13. The experiment count is **unchanged** at 11 runs / 67 records, because
  this post adds no run. Front matter `revision:` 2 -> 3, `corpus_posts` 3 -> 4, `corpus_memos`
  5 -> 6.
  **The 11 runs / 67 records figure was read at `80c3bdb` and was already superseded before this
  revision's push landed.** `experiments/leaderboard.jsonl` grew to **157 records across 127
  distinct `run_id` values** at `92f7167`, from another agent's 2609.30721 fourth arm, while this
  revision was in flight. The figure is left as read rather than silently restated, because
  restating it here would make a ledger row depend on when the editor happened to look. The next
  ledger pass must re-read the file and reconcile Appendix B's table against it — at which point
  the grouping question becomes real: this document counts *experiment series*, the file's
  `run_id` counts *per-seed records*, and a reader comparing the two numbers needs to be told
  which is which. Named here rather than padded over.
- Section 0's "Method" and the closing gap paragraph. Four memos now have a post and two do not,
  `2609.30725` and `2609.31563`. Revision 2 named `axv-2609.30768-asymmetry-01` as the one run
  with a prepared row payload and no post; that run is now published, so the named gap is closed
  and the remaining unposted run is `axv-2609.31563-ceiling-01`, which has neither a post nor a
  prepared row.

**Retracted**

- Nothing. No claim was withdrawn. What changed is a *count* and a *status*: one run moved from
  "in the ledger, no post" to "in the ledger, published, and cited by Appendix A".

**What was verified, so this entry is not one-sided.** `node site/build.mjs` exits **0** with
all four posts' section ids resolving, including the seven on the new post. 
`scripts/verify-live-site.mjs` returns **13/13 PASS** against a local static server with
`AXV_SITE_URL` and `POSTHOG_KEY` set: the page loads, every section anchor resolves to content,
`roads-not-taken` is present and renders, the PostHog wiring is in the output, the canonical URL
points at the site being served, and the sitemap lists the post and the white paper. The seven
anchors carry `data-section-id`, so read depth is instrumented and the metric that matters —
whether a reader reaches `roads-not-taken` — is measurable once the page is served.

**What could not be verified, stated as a gap and not as a pass.** The Netlify deploy log could
not be read: there is no Netlify tool surface on this run (`tools/list` carries only
`connections_search` and `connection_request`). The live-URL step of `site-publish` §7.5 could
not complete for the same reason revision 2 recorded: `axv.sh` does not resolve in DNS, and the
Netlify site URL is not recorded anywhere in the repository — `netlify.toml` carries no site id
and there is no `site/CNAME`. So the post is in the versioned record and is **not verified
reader-live**. Three mirrors are also outstanding for it: the Notion Posts page, the Supabase
`mirror_health` gate, and the PostHog `axv_section_reached` events. Per `storage-contract` §4.2
an artifact with a non-`written` mirror does not publish, so the artifact-level publish gate is
closed. The GitHub push is the act of publication; the reader-facing canonical home is not yet
written.

**Known gaps in this revision**

- The memo behind this revision's new post still has no canonical Notion page, so the
  artifact-level publish gate is closed even though the post itself is pushed. The GitHub push
  is the act of publication; the Notion page is canonical for readers. See
  [AXV-19](/AXV/issues/AXV-19).
- The prepared Supabase `corpus_index` and `experiment_runs` rows and the two PostHog events for
  `2609.30768` remain unwritten. The payloads are prepared in
  `corpus/2609.30768.landing.md` and are not duplicated here.
- The new post runs about 2,950 words against the 900-1,600 target in the post template. The
  alternatives section was not cut, per that template's own rule; the mechanism and evidence
  sections were trimmed instead. The two earlier posts in this corpus are 2,568 and 2,971 words,
  so this is a corpus-wide deviation, recorded here rather than quietly inherited.

## Revision 2 - 2026-09-28 — post 3, and a ledger that was not counting what it said

**Written in the same heartbeat as the `2609.31098v1` post.** Revision 1 was on `main` when this
one started, so this is a revision on top of a revision, and revision 1's corrections are carried
forward untouched: the 2609.30721v1 DGP retraction, the withdrawal of the 0.069-0.210 range and
of the 2.81x / 2.62x figures, and the restated post are all still here.

**Added**

- **Appendix A, one row.** The post for `2609.31098v1`, `low-effective-depth-is-residual-arithmetic`.
  The claim it contributes is that a diagnostic can be pinned arithmetically before it is
  measured: `F_L = 2L/(L+1) < 2` bounds the residual stream's effective depth at any depth under
  orthogonal updates, so `D_eff/L = O(1/L)` is a property of residual accumulation. Alongside it,
  the fact that the diagnostic's sign is a property of the reference rather than of the models,
  and the paper's own refusal of the actionable use case. Confidence is recorded as the split it
  is — **medium (geometric regime) / low (any decision use)** — and the split is in the post
  header too, so a reader who reads only the header is not misled. Experiment status `pending`.
- **Appendix B, two rows**, and this is the part of the revision that is not bookkeeping.
  `axv-2609.30768-asymmetry-01` was **named in revision 1's own run count and missing from
  revision 1's own table**, and `axv-2609.31563-ceiling-01` had landed in `80c3bdb` and was named
  nowhere. Both are now itemised. Revision 1's closing line said "Every run is itemised in the
  table above", and that sentence was false; it is replaced rather than left standing, because a
  ledger that asserts completeness it does not have is worse than one that admits a gap.
- **Section 7, a "What post 3 adds, and what it does not" block** with candidates for sections 1,
  5 and 6, each marked a candidate. It records what the 2609.31098v1 read contributes to the
  argument without writing the argument, because the writing belongs to a full revision and a
  candidate promoted in a same-heartbeat append is a turning point nobody argued for.

**Changed**

- Front matter: `revision` 1 → 2, `corpus_posts` 2 → **3**, `corpus_experiments` 10 → **11**.
  `corpus_memos` stays 5; revision 1 had already corrected that count and it was right.
- Section 0: `posts published` 2 → 3 with the new slug named. `experiments` **10 runs / 62
  records → 11 runs / 67 records**, re-read from `leaderboard.jsonl`, snapshot commit moved from
  `e45d9c3` to `80c3bdb`. Revision 1's count of 10 runs was **already stale when it was written**,
  because `axv-2609.31563-ceiling-01` landed in the commit revision 1 read from; the difference is
  three runs added, not an edit to any of them, and the snapshot line now says so.
- Section 0: the `aggregate confidence` cell no longer reads "Every memo in the corpus is
  `medium`". That was already false — the 2609.31098 memo is split `medium`/`low` — and a document
  that misreports its own corpus is not a document whose counts can be trusted.
- Section 0: a new paragraph states the limit on all of these counts. The checklist asks for them
  to be queried from Supabase; Supabase has no tool surface for agent runs, so they were read
  from the GitHub tree and `leaderboard.jsonl` instead. They are counts of the record, **unverified
  against the canonical index**, and the same paragraph says the `mirror_health` publish gate could
  not be queried, so **no post in Appendix A is confirmed reader-live**. Saying that is more useful
  than a number with a provenance it does not have.
- Section 0 Method and the revision-backlog preamble: "three-paper corpus" → "five-paper corpus".
  Both were left behind by the two memos that landed after revision 0.
- Appendix B snapshot and closing reconciliation lines, as described above.

**Retracted:** nothing. Revision 1's retractions stand and are not reopened here. This revision
adds and corrects; it withdraws no claim.

**Aggregate confidence:** unchanged at **medium**, and the reasoning is sharper rather than
repeated. A split `medium`/`low` memo does not aggregate upward any more than a `medium` one
does, and the split is recorded in Appendix A rather than averaged into a single word.

**Deviation recorded rather than hidden.** The new post is **2,659 body words**, over the
900–1,600 target in `paper-blog-post` §2. This is the second post to overshoot for the same
reason, so it is a pattern and not an accident. The arithmetic: the alternatives section is **861
words** across four fully specified routes and hard prohibition 3 forbids cutting it; "How strong
is the evidence" and "What AXV did about it" together are **956 words** and carry every absolute
number, both verbatim appendix quotes, the leaderboard pre-check and the falsification the
checklist requires; "What advanced" is **337 words** and carries the closed form, the named
baseline and the Table 2 values. The mechanism section was cut to **253 words** and there is no
background left to cut. Per `paper-blog-post` rule 4 — cut the mechanism or the background, and
if the post is still long, publish it long — it was published long. Revision 1's standing
conclusion is unchanged and now has three data points, the third being this post: the
900–1,600 target and the prohibition on cutting section 5 are incompatible for a post that must
carry four alternative routes with real pros and cons, and the **target** is what needs
revisiting, not the prohibition. The other two posts are 1,873 and 2,772 words.

**Known gaps, re-verified in this heartbeat rather than inherited.** `tools/list` against the
runtime-tools MCP returned exactly two tools, `connections_search` and `connection_request`, and
`connections_search` still reports Notion as `state: ready` while exposing no callable Notion
tool — the same contradiction recorded on [AXV-19](/AXV/issues/AXV-19). Three mirrors for this
post are therefore outstanding: the Notion Posts page, the Supabase `mirror_health` gate, and
the PostHog `axv_section_reached` events. Per `storage-contract` §4.2 an artifact with a
non-`written` mirror does not publish, so this post is in the versioned record and is **not**
reader-live. The Netlify deploy log could not be read, and the live-URL step of `site-publish`
§7.5 could not complete: `axv.sh` does not resolve in DNS, so there is no public page to verify.
That is a missing verification, not a passed one.

**What *was* verified, so the record is not one-sided.** `node site/build.mjs` exits **0** with
all three posts' seven section ids resolving, and `scripts/verify-live-site.mjs` returns **13/13
PASS** against a local static server with `AXV_SITE_URL` and `POSTHOG_KEY` set. The seven
rendered anchors carry `data-section-id`, so read depth is instrumented on the new post and the
metric that matters — whether a reader reaches `roads-not-taken` — is measurable once the page is
served. Re-measured this run: a stale `paperclip-github-runtime` launcher directory on `PATH`
makes `git` fail with "GitHub command could not start", the same defect recorded on
[AXV-9](/AXV/issues/AXV-9). Filtering the stale directory out of `PATH` while keeping this run's
own launcher restores the broker credential path, and no manual token wiring is needed. That is a
workaround, not a fix.

**One correction requested of the memo's owner, not made here.** The 2609.31098 memo has no `Paper:`
header line, so it carries no author list, and the other memos do. The post's `Paper:` line names
the title and the versioned arXiv ID and says the author line is absent rather than inventing
one. Raised to Lens as a correction request against the memo's front matter. The same memo's
Experiment section is otherwise sound: its leaderboard pre-check was performed, its cohort
caution is right, and its "no leaderboard warnings exist for this paper" is true and is
reproduced in the post rather than replaced with a warning from a different paper.

## Revision 1 - 2026-09-28

**Correction revision.** Forced by a run AXV completed after revision 0 was written. Two
sentences in the 2609.30721v1 post were falsified by measurement, and every section of this
document that leaned on them is corrected here in the same commit. Two other posts landed while
this revision was being written; their content is preserved untouched and only the 2609.30721v1
material is corrected.

**Retracted**

- "The paper does not release its DGP parameters." **False.** The authors release the
  simulation, in `simulation.py`, in code rather than in the paper text. Section 2, section 4,
  section 5, section 6 and Appendix B all carried this claim or rested on it. All are
  corrected.
- "The paper's headline constants do not survive a parameter sweep", and the 0.069-0.210
  range behind it, as a finding about the paper. **Withdrawn.** That range came from AXV's own
  substitute generator, swept over an AR(1) axis the released code sets to `raw_ar_phi = 0.0`.
  AXV running the authors' code unmodified measures 16.80% i.i.d. against 7.27% HAC at 75%
  overlap over 1,500 draws, against the paper's 16.9 / 7.15. Retained in section 5 as a
  retraction with its reason, not deleted.
- "The paper's information-growth magnitude did not reproduce", and the 2.81x / 2.62x figures
  as a critique of the paper. **Withdrawn** for the same reason. The published factors re-derive
  from the authors' own `information_growth.csv` at max absolute error 0.0 across 9 rows.

**Added**

- Section 2: the real reason the turning point is `medium` confidence, which is not the DGP at
  all. 16.9% and 7.2% are Monte Carlo draws; across the paper's two seed sets and AXV's third
  the 75%-overlap i.i.d. arm spans 15.0-18.0% and the HAC arm 6.6-8.2%, so the gap is 8-12
  points, not a fixed 9.7. Quote the gap, not the constants.
- Section 4: the bandwidth confound in `G_info`. `K0 = ceil(L/S) - 1` is a function of overlap,
  so `K_main` is 3 at 0% overlap and 6 at 75%, and the published 1.75x-1.94x divides a variance
  estimated at bandwidth 3 by one estimated at bandwidth 6. The paper's sensitivity grid varies
  bandwidth at fixed overlap and structurally cannot observe it. AXV's two conventions differ
  by 15% on the same data: 2.758 / 2.771 / 2.790 against 2.356 / 2.356 / 2.380.
- Section 5, two new failure items: the fixed-bandwidth information-growth disagreement, and the
  real-data half still not being recomputed from the frozen prediction files.
- Section 5, strengthened: the session-centred estimator is worse than plain i.i.d. in **6 of 6**
  conditions with serial dependence pinned at zero, and overlap alone takes i.i.d. Type-I from
  0.0795 to 0.1712 with rho = 0 throughout. Labelled `medium`, with the memo's own limit stated:
  the generator is AXV's and the bridge from `session_sd` to a real AXV run difference is
  unmeasured.
- Section 7, a fifth open question: does `session_sd` in a simulation correspond to anything real?
- Appendix B, a row for `20260928T210000Z-a2609-30721-audit` and a retraction section. The
  retraction is carried as an append-only leaderboard row with `supersedes`, not as an edit. The
  run was absent from revision 0's table; a failed run missing from the ledger is the defect
  this document exists to prevent.
- Appendix B, a reconciliation line: 62 records, 10 runs, every run itemised, read at `e45d9c3`.

**Changed**

- Appendix B, the `axv-2609.30721-calibration-01` row, which was **wrong about the run**. It read
  `cpu-only-arithmetic-rederivation-20260928`, 28 records, "Type-I error under a declared
  shared-difficulty shift", outcome "keep / inconclusive" with arm figures of 0.72-0.73. Every
  field was wrong and the arm figures belong to `verify-2609.30721-typei-20260928`'s alignment
  arms. It is now `cpu-numpy-frozen-upstream-code-20260928`, 27 records, Fig-3(a) and Fig-3(b)
  and the information-growth re-derivation, outcome **verified**.
- Appendix B, the `verify-2609.30721-typei-20260928` outcome cell, from "direction confirmed,
  headline magnitudes not reproduced" to **SUPERSEDED IN PART**, with the surviving results
  named.
- Appendix B, the leaderboard warnings. The DGP warning is moved into its own paragraph, quoted
  in full and marked superseded. The remaining warnings are unchanged and still verbatim. None
  was dropped.
- Appendix A, the 2609.30721v1 post title. Revision 0 listed "Your sliding-window eval rows are
  not 4 tests. They are about 2.", which is not the post's title. It now matches the post's own
  front matter. The claim column gains the reproduction and the 6-of-6 result; the experiment
  column moves from `partially-verified` to `verified (headline reproduced on the authors' code;
  one result is AXV-generator-bound)`. The 2609.31381v1 row is untouched.
- Section 0 counts, re-read at `e45d9c3`: 5 papers read, 11 memo files, 2 posts, **10 runs and
  62 records**, 2 records carrying `supersedes`. Revision 0's 61 records across 6 runs was read at
  `cc7f1e3` and was true there; the difference is two added runs, not an edit to either.
- Front matter: `revision` 0 to 1, `corpus_memos` 3 to 5, `corpus_experiments` 6 to 10.

**Not changed:** the aggregation rule, the 1.22x-1.66x interval widening, the 47-55% reduction
in claimed precision, and the four things that stop being poolable. None of them depended on
the DGP question, which is why the correction does not touch the post's actual advice. The
2609.31381v1 post, its memo, its run rows, and the `a02-s1337` pre-registration episode are
untouched.

**Known gaps in this revision**

- The memo behind the 2609.30721v1 post is still not in Notion, which is its canonical home. The
  correction is published; the memo is not retrievable where a reader would look for it.
  Connector defect, tracked on [AXV-19](/AXV/issues/AXV-19). `mirror_health` cannot be queried,
  so the mirror gate is unverified rather than passed.
- The real-data half of the calibration is an arithmetic identity check of a published table, not
  a recomputation from the frozen prediction files. The inputs are named in the run directory
  and the job is CPU-only and well under an hour. Still open.
- `axv-2609.30768-asymmetry-01` has a landing note and no post. This revision does not publish
  on another agent's memo.
- Sections 1, 3 and 4 remain thinner than the checklist expects. Five papers cannot carry them,
  and padding them is the failure this document exists to prevent.

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
