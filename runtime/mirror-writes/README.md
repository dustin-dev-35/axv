# Pending mirror writes

A mirror write is derived from a canonical GitHub artifact, is not a secret, and
cannot be executed in the run that derived it. It lives here so the next run
executes a reviewed file instead of retyping a row from memory.

`storage-contract` §1.2 made GitHub the single canonical home for prose on
2026-08-28, so the only mirror a reading memo still has is its Supabase
`corpus_index` row. That is what this directory holds.

| file | canonical artifact | blocked on | issue |
| --- | --- | --- | --- |
| `2609.31098-corpus_index.sql` | `corpus/2609.31098.md` @ `b8f56eae` | the Supabase OAuth **access** token is not bound to Lens | [AXV-63](/AXV/issues/AXV-63) |

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
