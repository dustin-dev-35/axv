# Pending mirror writes

A mirror write is derived from a canonical GitHub artifact, is not a secret, and
cannot be executed in the run that derived it. It lives here so the next run
executes a reviewed file instead of retyping a row from memory.

`storage-contract` §1.2 made GitHub the single canonical home for prose on
2026-08-28, so the only mirror a reading memo still has is its Supabase
`corpus_index` row. That is what this directory holds.

| file | canonical artifact | blocked on | issue |
| --- | --- | --- | --- |
| _(none)_ | | | |

**This directory is empty of pending writes as of 2026-09-29.** The one file it
held, `2609.31098-corpus_index.sql`, was executed and deleted in the same commit
that recorded the evidence it landed, per rule 6. Its row is in `corpus_index`
with `confidence = low`, `experiment_status = unverified`,
`experiment_delta = 0.003750`, and `mirror_health` carries one `written` row for
`2609.31098v1`.

An empty table here is not a claim that no mirror is outstanding. It is a claim
that no mirror is outstanding **that has been derived**. The five rows named
below are still unwritten, and they are unwritten because nobody derived them,
not because anything is blocking a derivation.

## This directory is not the whole backlog, and it is not meant to look like it is

`corpus/` holds **six primary reading memos** at this head - `2609.30721`,
`2609.30725`, `2609.30768`, `2609.31098`, `2609.31381`, `2609.31563` - plus ten
addenda, landing notes, a reconciliation note and a batch-metrics file. **One** of
the six is in `corpus_index`. `corpus_index` is a per-memo table with a
`(arxiv_id, version)` primary key, so all six are separate rows and five of them are
unwritten: `2609.30721`, `2609.30725`, `2609.30768`, `2609.31381`, `2609.31563`.

That number is stated here rather than left to be discovered because this file is the
only ledger of pending mirror writes, and a ledger that implies it is complete is
worse than no ledger. Rule 6 below is the reason it is not six files already.

The five remaining rows are **not** derived here on purpose. A row is derived from
one canonical blob by one generator, and the reason `2609.31098` was derivable is
that its Experiment section and Confidence line are settled. Now that it has
landed, nothing blocks the other five: the token problem is gone and the schema is
applied. They are unwritten because deriving them was out of scope for
[AXV-63](/AXV/issues/AXV-63), which was scoped to the one memo whose mirrors were
outstanding. The five are named so the gap is visible from here rather than
discovered by the sweep, and `fill-placeholders.ps1` is the generator to reuse
when someone does pick them up.

## Why a row is staged here rather than written on the spot

Three separate heartbeats staged the same insert in a run scratch directory and
each one lost it, because run scratch is removed when the run ends. `storage-contract`
§2 is explicit that an unwritten mirror is an absence and that absences are worse
than late writes, and §1.2 makes GitHub the record - so a pending mirror write is
itself a record, and it belongs in GitHub.

## Rules for anything in this directory

1. **Derived, never retyped.** Every value is read out of the canonical blob by
   the script that fills the placeholders, and any value that is not verbatim
   canonical text says so in a comment on the row it feeds.
2. **No credential material.** No token, no project key, no `service_role`. The
   script that generates a file here scans for them and refuses to write.
3. **Idempotent.** `on conflict ... do update`, so a re-run is a repair rather than
   a duplicate.
4. **Sections are separate transactions.** A table that turns out not to exist must
   not be able to roll back the row that matters. `storage-contract` §4.1 warns that
   an empty table and a missing table look identical from an agent's seat.
5. **Verify `github_path` resolves before the insert, not after.** A row pointing at
   a commit that does not exist is the corrupt index the reconciliation sweep exists
   to find, and it is cheaper to check than to sweep.
6. **Delete the file when the write lands**, in the same commit as the evidence that
   it landed. A pending-write directory that only grows stops being a ledger and
   starts being a backlog nobody reconciles.

## Notion

There is no Notion entry here, and there will not be one. The board retired Notion
as the record on 2026-08-28 - "Accept GitHub as the only place, and change the rule"
(whitepaper revision 4c, `3b6c6e1`) - and `corpus_index.notion_page_id` is left `null`
rather than guessed. Writing a Notion page now would recreate the second copy the
decision removed.

## The live schema diverges from the skill's `schema.sql`, and one table is a fork

Recorded 2026-09-29, when the schema was applied to project `qfujdoktqipblsxbrxgy`
for the first time. The next agent to touch Supabase will hit this, so it is here
rather than in a comment.

`storage-contract/scripts/schema.sql` could **not** be applied verbatim. It fails at
`create index experiment_runs_cohort_idx`:

```
ERROR: 42703: column "comparability_key" does not exist
```

The cause is that `public.experiment_runs` already existed, created by hand by the
AXV-43 experiment batch on 2026-09-28, and it is **not** the table in the skill's
DDL. It is a richer, differently-named fork. It has `cohort` and `comparability`
where the DDL has `comparability_key`; it has `provisional`, `provisional_reason`,
`spread`, `caveat`, `harness_branch`, `template_id`, `image`, `pod_data_center`
and more, none of which the DDL declares. It is missing exactly two of the DDL's
columns: `comparability_key` and `claim_under_test`. Its 5 rows are intact and
untouched.

`create table if not exists` was therefore a no-op for that table, and the three
indexes and the `v_leaderboard_cohorts` view that reference the missing column
cannot be created against it. What was applied: every other table
(`triage_ledger`, `exclusion_list`, `corpus_index`, `mirror_health`), the
`touch_updated_at` function, both triggers, and the three views that do not touch
`experiment_runs` - including `v_corpus_counts`, which is what §4.1 tells you to
read. What was **not** created: `experiment_runs_cohort_idx`,
`experiment_runs_arxiv_idx`, `experiment_runs_kept_idx`, `v_leaderboard_cohorts`.

Two consequences worth knowing before someone trusts a number:

- `experiment_runs.metric_value` is `double precision` in the live table and
  `numeric` in the DDL. Values already stored are not affected.
- `v_leaderboard_cohorts` does not exist, so "is there a baseline for this config"
  is answered from `experiments/leaderboard.jsonl` and not from a SQL view, until
  the fork and the DDL are reconciled.

**This is a decision for the schema owner, not something to fix silently.** The two
routes are to migrate the fork onto the DDL's column names, or to amend the DDL to
describe the fork. Migrating the fork would rewrite a table five other runs have
written to, so it is not an agent's call to make on the way to writing a memo row.
