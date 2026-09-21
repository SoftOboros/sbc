> Current repository layout: [owner-approved consolidation](REPOSITORY-CONSOLIDATION.md).
> SBC and its tools share one repository; SBCT-00 is now 0.4.2. Earlier progress entries are historical.

# AGENTS.md — SBC Supporting Tools

**Document ID:** SBCT-AGENTS
**Status:** SBCT-00 through SBCT-02 RATIFIED; SBCT-03 through SBCT-06 DRAFT.
**Owner:** Ira Abbott

| State | Value |
|---|---|
| Family/prefix | `sbc-tools` / `SBCT` |
| Active gate | SBCT-02 implementation; GATE-206 approved; runtime acceptance remains open |
| Ratified SBCT artifacts | SBCT-00 0.4.1, SBCT-01 0.8.0 (approved console amendment), SBCT-02 0.6.2; GATE-206 approved 2026-09-20 |
| Authored artifacts | SBCT-03 through SBCT-05 drafts 0.5.0; SBCT-06 draft 0.6.0 |
| Execution evidence | Cursor codec and SQLite store: 25 focused tests, including isolated Python; full runtime gates remain open |
| Concepts decisions | Four PCDNs approved 2026-09-19; deferrals retained in SBCT-00 §8 |
| Open errata | None filed |

Read README.md and SBCT-00-CONCEPTS.md before authoring. Load the relevant
phase and its referenced SBC/SIDX contract before implementation. Preserve
single ownership of definitions; cite invariants in code formatting outside
their defining table. Keep ratification, implementation, deployment, and public
publication as separate recorded events. The owner ratified SBCT-00 and authorized preparing the child drafts.
The owner subsequently ratified SBCT-01 explicitly. SBCT-03 through SBCT-06
remain drafts; no implementation acceptance is inferred.

All supplied backends are bounded examples with standard Django human auth
and minimal OAuth for MCP. Production variants and consumer-specific adoption
documents belong in consuming projects. The example is intended to become
feature-frozen; support and security-fix status must remain explicit. Do not introduce production integration code
behind a disabled feature flag in the shared distribution.

Do not edit `docs/spec-before-code` to accommodate tooling requirements. It is
a separate submodule and authority. Record conflicts for the relevant owner.
Preserve unrelated dirty/staged work in the parent repository. These files
will travel with the tooling when its repository is established; this folder
is their sole authoring home until that migration is recorded.

The [ratification packet](RATIFICATION.md) assembles the approved dispositions,
compatibility policy, observed authority inputs and named witness coverage.

First-party license: BSD-3-Clause, owner-selected 2026-09-19.
SBCT-01 pre-ratification evidence is assembled in [SBCT-01-REVIEW.md](SBCT-01-REVIEW.md).

SBCT-02 review items 1–3 were accepted by the owner on 2026-09-19.
Their concrete contract package revision 0.1.1 was approved under GATE-206 on 2026-09-20.

SBCT-02 was explicitly ratified 2026-09-19. Its
[contract package](SBCT-02-CONTRACT-PACKAGE.md) is now approved by the owner.
GATE-206 is checked; implementation is underway in a separate local tooling checkout.

The owner directed public prerelease development on main toward a limited
working indexing/dashboard release on 2026-09-20. See
[FIRST-RELEASE.md](FIRST-RELEASE.md) for the gated sequence.
[SBCT-04-HOST-CONTRACT.md](SBCT-04-HOST-CONTRACT.md) contains proposed dashboard
interfaces and witnesses. This preparation does not ratify SBCT-03/04/06 or
close GATE-406. GATE-206 was subsequently explicitly approved.

Implementation now includes the cursor codec and transactional SQLite
publication store. [Storage execution evidence](evidence/sbct-02-store-execution.json)
records the initial 25 focused tests and synthetic-validator limitation.
[Validation execution evidence](evidence/sbct-02-validation-execution.json)
records extracted SIDX semantics, SQLite integration and 36 focused tests.
Committed-source verification, shared queries, Django parity and reset remain
unimplemented. Subsequent pinned-emitter reproduction established that the
historical golden serialization, not the producer, used incorrect diagnostic
formatting. The original vectors remain historical rejection witnesses; exact
emitter bytes pass validation. The offline committed Git reader now verifies
exact objects and projection subtree bytes, with eight additional provider tests.
Full authority/corpus verification remains pending. See
[Git reader and wire reconciliation evidence](evidence/sbct-02-git-reader-execution.json).
Runtime gates remain open.

Authority input verification now checks the closed role inventory against a
trusted manifest digest and exact committed blobs. Committed corpus inventory
covers configured roots and required inputs. There are 36 core tests and 18
Git/provenance tests. Reviewed-patch application, complete configuration and
child-mount validation, and BundleValidator provenance composition remain open.
See [authority/corpus execution evidence](evidence/sbct-02-provenance-inputs-execution.json).
