-- Pending Supabase mirror write for the reading memo arXiv:2609.31098v1.
--
-- WHY THIS FILE EXISTS
--   The memo is canonical in GitHub (storage-contract section 1.2, board decision
--   2026-08-28, whitepaper revision 4c at commit 3b6c6e1). Its only remaining
--   mirror is the Supabase `corpus_index` row. This file is that write, derived
--   from the canonical text and not from memory, so the row is reviewable
--   instead of being retyped by a later run.
--
--   It is committed rather than held in a run scratch directory because three
--   heartbeats have now staged this insert in ephemeral storage and lost it.
--
-- SOURCE OF EVERY VALUE
--   Canonical blob 79297db5e289b07a155a0efdf9709ddf47738cda
--   (dustin-dev-35/axv:corpus/2609.31098.md at commit b8f56eae, 52,927 bytes,
--   sha256 3857e24cc6f7c85289b92d8c8bf37a5a4d487fd00d8bbd5ee35b3a4eccb7346c)
--   No value below is typed from a summary. The five lines that are NOT verbatim
--   memo text are marked DERIVED and say so in a comment on the row they feed.
--
-- HOW TO APPLY
--   1. Apply the schema first if you have not:
--        supabase db execute --file scripts/schema.sql
--      schema.sql is idempotent (storage-contract 4.1). Note that the experiment
--      batch of 2026-09-28 created public.experiment_runs by hand; that does NOT
--      prove corpus_index or mirror_health exist. An absent table and an empty
--      table look identical from an agent's seat, which is exactly why 4.1 says
--      to check explicitly rather than trust an exit code.
--   2. Run step 0 and read the result. If either regclass is null, stop and apply
--      the schema.
--   3. Run section A. It is its own transaction and touches corpus_index only.
--   4. Run section B. It is a SEPARATE transaction, on purpose: if mirror_health
--      is absent, section B fails alone and cannot roll back section A. The
--      earlier staging put both in one transaction, which made the index row
--      hostage to a table that is no longer load-bearing.
--
--   Nothing here contains a credential, a token or a project key. The memo body
--   is not copied into Supabase (storage-contract section 1: Supabase owns the
--   queryable layer, not prose); only the index row and its pointers go in.

-- ===========================================================================
-- Step 0 - preflight. Read this output before running anything else.
-- ===========================================================================
select
  to_regclass('public.corpus_index')  as corpus_index,
  to_regclass('public.mirror_health') as mirror_health,
  to_regclass('public.experiment_runs') as experiment_runs;

-- ===========================================================================
-- Section A - the index row. One table, one transaction.
-- ===========================================================================

begin;

insert into corpus_index (
  arxiv_id,
  version,
  title,
  short_title,

  claim,
  novelty,
  confidence,
  unknowns,

  alternative_routes,
  failure_mode,

  experiment_status,
  experiment_run_id,
  experiment_delta,

  notion_page_id,
  github_path,
  post_slug,
  post_url,
  post_published_at,

  superseded_by_version,

  lens_run_id,
  created_at
) values (
  '2609.31098',
  1,
  $axv$The Residual Stream's Effective Depth$axv$,
  $axv$Residual stream effective depth$axv$,

  -- VERBATIM: the memo's own **Claim.** sentence, markdown link included.
  $axv$Treating the layer-wise residual stream of a decoder-only transformer as a discrete-time process and aggregating its CKA similarity autocorrelation with a Bartlett taper gives a scalar effective depth whose *closed-form* orthogonal-update reference is `F_L = 2L/(L+1) < 2` — so `D_eff/L = O(1/L)` is a structural property of residual accumulation and not evidence of unused depth — and the residual signed gap to that reference is uniformly sub-zero across sixteen decoder-only LMs (+20% to +44%, 15 of 16) and is explained by measured *update correlations* rather than by the persistent initial state `h_0` or by update-size imbalance. ([arXiv:2609.31098](https://arxiv.org/abs/2609.31098))$axv$,
  -- DERIVED: Lens's classification from the memo's "What advanced", which says
  -- the advance is the closed form F_L = 2L/(L+1), not the ratio. This is NOT
  -- the unverified triage_ledger row's novelty field; that row's durability is
  -- unverified (AXV-2) and is a different table.
  'new-mechanism',
  -- DERIVED, and this is a decision, so it is stated rather than defaulted.
  -- The memo is split: `medium` for the geometric claim, `low` for any use as a
  -- selection criterion. The column is single-valued and exists so that
  -- "every claim with confidence = low" is a query. This memo's operative
  -- conclusion is a negative - do not use D_eff to choose a checkpoint - and
  -- filing it as `medium` would index a memo that argues against its own
  -- diagnostic as a medium-confidence claim. The split is preserved verbatim in
  -- the memo's Confidence section and in the post's front matter, so `low` here
  -- loses nothing and misleads nobody.
  'low',
  -- VERBATIM: the memo's explicit numbered unknowns list.
  $axv$(1) ~~trained-checkpoint seed variance of `D_eff` — never measured~~ **now measured at `n=3`, `σ = 0.001375`; what remains unknown is whether that figure holds at 7B+ scale, and the same-cohort between-architecture arm that would test it was not run**; (2) cross-corpus sensitivity of both the absolute value and the model ranking, since S13 changes corpus without reporting the delta; (3) whether the sub-`F_L` sign survives a reference that is not a scalar surrogate, since Table S3 shows the sign is surrogate-dependent; (4) whether the nanoGPT γ-sweep transfers to 7B-class, which the authors explicitly decline to claim; (5) whether the Figure 3 training-dynamics gaps are seed-stable, given 10 of 35 planned checkpoints are missing and were not interpolated; (6) why OLMo-2 and Pythia differ, which the authors attribute to neither training progress nor any single architectural choice; (7) whether the three-way table inconsistency (2, S3, S15) is recomputation drift or transcription error; (8) whether CKA-invisible rotations matter in practice — acknowledged as out of scope, and S8's Remark 7 states the beta-mixing bound "does not directly bound the CKA-based `ρ̂(k)`"; (9) whether the S9 taper-robustness claim survives being given numbers; (10) **new, from AXV's own run — the source of the 3.3% implementation gap**, since the training setup reproduces exactly and the bias correction moves the estimate *away* from the paper, so neither the finite-`n` bias nor a training difference accounts for it and the `D_eff` protocol as specified is evidently underdetermined somewhere between the paper's code and AXV's; (11) **whether the `−3.04%` finite-`n` bias is depth-dependent**, since it was measured at one operating point (`d=384, L=12`) and every Table 2 value spans `d` from 512 to 5120 and `L` from 6 to 64.$axv$,

  -- DERIVED: the memo numbers four items under Alternative routes, but item 4 is
  -- explicitly "Ruled out, and worth recording" - a negative, not a live route.
  -- Counted as three live routes.
  3,
  -- VERBATIM, condensed from the memo's "The single most likely way this claim
  -- is wrong" (Evidence quality). Kept short because the column says so.
  $axv$The 15-of-16 sub-F_L headline is a property of the reference, not of the models. F_L assumes equal-norm orthogonal updates with no persistent initial component - a construction no trained model satisfies - and Table S3 shows the sign flipping for all sixteen rows (-2.9% to -89.1%) the moment the measured update-similarity profile is retained. The authors call F_L a first structural yardstick, not a definitive null; the headline, the abstract and the triage-worthy phrase all rest on it.$axv$,

  -- VERBATIM: the memo's Experiment status line, as corrected at b8f56eae.
  -- Revision 2 wrote `measured`, which is not one of the four values this check
  -- constraint accepts and not one the output contract allows.
  'unverified',
  -- DERIVED: this column is single-valued and the series is six leaderboard
  -- records over five run ids (2609.31098-a03-s1337 appears twice, the second
  -- record supersedes the first). The reference arm is the representative one.
  '2609.31098-a00-s1337',
  -- VERBATIM: the memo's Result 3, trained-minus-random-weight D_eff/L, which
  -- is the decision-relevant effect the series measured. Seed sigma is 0.001375,
  -- i.e. 37% of this number.
  0.003750,

  -- NULL, deliberately, and for a reason rather than out of caution. The board
  -- retired Notion as the record on 2026-08-28 (storage-contract 1.2, whitepaper
  -- 4c at 3b6c6e1): "Notion is not the record and is not a mirror of it." There
  -- is no Notion page to point at, and a guessed page id would make the index
  -- lie about where the record is.
  null,
  'corpus/2609.31098.md',
  'low-effective-depth-is-residual-arithmetic',
  -- NULL: the site has no public address. netlify.toml carries no site id and
  -- there is no site/CNAME, so the post is in the versioned record and is not
  -- reader-live. See runtime/publication-state.md.
  null,
  null,

  null,

  -- The run that produced the canonical file at origin/main.
  '0d5873b9-a59a-495a-b31d-fd32fb2450f0'::uuid,
  -- First commit of the memo, not the row's write time. cc7f1e3.
  '2026-09-28T16:54:41-04:00'::timestamptz
)
on conflict (arxiv_id, version) do update set
  title               = excluded.title,
  short_title         = excluded.short_title,
  claim               = excluded.claim,
  novelty             = excluded.novelty,
  confidence          = excluded.confidence,
  unknowns            = excluded.unknowns,
  alternative_routes  = excluded.alternative_routes,
  failure_mode        = excluded.failure_mode,
  experiment_status   = excluded.experiment_status,
  experiment_run_id   = excluded.experiment_run_id,
  experiment_delta    = excluded.experiment_delta,
  notion_page_id      = excluded.notion_page_id,
  github_path         = excluded.github_path,
  post_slug           = excluded.post_slug,
  post_url            = excluded.post_url,
  post_published_at   = excluded.post_published_at,
  superseded_by_version = excluded.superseded_by_version,
  -- corpus_index.updated_at exists (not null default now()) and the do-update
  -- list omitted it, so a re-run of this upsert would rewrite every field and
  -- still leave updated_at at the first insert time. That defeats the point of
  -- an idempotent upsert: the row could not say when it was last corrected.
  -- Section B in this same file already sets written_at = now(); this makes the
  -- two halves consistent.
  updated_at          = now();

-- Verify inside the same transaction, so a bad row never commits.
select arxiv_id, version, confidence, experiment_status, experiment_delta,
       alternative_routes, github_path, post_slug,
       (notion_page_id is null) as notion_intentionally_null,
       length(claim) as claim_len, length(unknowns) as unknowns_len
from corpus_index
where arxiv_id = '2609.31098' and version = 1;

commit;

-- ===========================================================================
-- Section B - the mirror_health row. SEPARATE transaction, on purpose.
--
-- storage-contract 1.2 retires the mirror_health publish gate as a blocking
-- gate, so this row is not load-bearing. It is still written because the
-- reconciliation sweep reads it, and it is written last and separately so that
-- a missing mirror_health table cannot take the index row down with it.
-- ===========================================================================

begin;

insert into mirror_health (
  artifact_type, artifact_key, canonical, mirror_service, mirror_ref,
  status, error, agent_name, written_at
) values (
  'memo',
  '2609.31098v1',
  'github:dustin-dev-35/axv@corpus/2609.31098.md',
  'supabase:corpus_index',
  'corpus_index:2609.31098/1',
  'written',
  null,
  'lens',
  now()
)
on conflict (artifact_type, artifact_key, mirror_service) do update set
  mirror_ref = excluded.mirror_ref,
  status     = excluded.status,
  error      = excluded.error,
  agent_name = excluded.agent_name,
  written_at = now();

select artifact_type, artifact_key, mirror_service, status, written_at
from mirror_health
where artifact_key = '2609.31098v1';

commit;

-- ===========================================================================
-- Step 3 - post-write verification, after both sections.
-- Expected: one row, confidence = low, experiment_status = unverified,
-- experiment_delta = 0.003750, notion_page_id null, github_path
-- corpus/2609.31098.md.
-- ===========================================================================
select arxiv_id, version, confidence, experiment_status, alternative_routes,
       experiment_run_id, experiment_delta, github_path
from corpus_index
where arxiv_id = '2609.31098'
order by version desc;
