# Unified SBC repository migration

**Status:** Owner-approved repository amendment, 2026-09-21.

The owner clarified that SBC and its tools should be one item, then approved
consolidation and pushing the combined prerelease to `SoftOboros/sbc` on `main`.
This supersedes the earlier separate-repository decision. It does not approve
runtime gates, draft phases, new authority digests, production adoption or a release tag.

- Discipline documents retain their existing paths.
- `docs/sbc-tools/` is the sole SBCT authoring home, migrated from the consumer's
  `docs/todo/sbc-tools/`. The old home contains a navigation redirect only.
- `tools/` contains the separately installable Python package, tests and helpers.
  Its history through `4e6b07a2be058e2d90f6fcde0146c32da178cfc3` is retained as
  a merge parent. The former local checkout is retained only as a historical copy.
- New repositories adopt one SBC submodule; installing its tools is optional.
- Production policy, credentials and deployment integrations remain downstream.

Historical evidence, approval hashes, fixture paths and source pins are retained
as observations of their original executions. Relocation does not reapprove or
rebase those inputs. The migration inventory records hashes before relocation.
SBC document links now resolve locally. External SIDX document links point to
the recorded source commit; access may still require source-repository permission.
A publicly accessible SIDX authority distribution remains release work. External
consumer reconciliation artifacts are not copied into this portable repository.

SBCT-00 is amended to 0.4.2; SBCT-01/02 approvals remain in force. SBCT-03 through
SBCT-06 remain drafts. Historical references to separate repositories or the old
authoring home describe prior state and are superseded here for current layout.
