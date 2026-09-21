> Current repository layout: [owner-approved consolidation](REPOSITORY-CONSOLIDATION.md).
> SBC and its tools share one repository; SBCT-00 is now 0.4.2. Earlier progress entries are historical.

# SBC Supporting Tools — First Release Work Order

**Document ID:** SBCT-RELEASE-01
**Status:** DRAFT execution sequence — no new ratification or acceptance
**Date:** 2026-09-20
**Owner:** Ira Abbott

## Owner direction

The owner directed public prerelease development on main until a release tag.
The first release target is working, limited indexing and a reusable dashboard.
Guiding documents can be shared before implementation is complete. The public
surface must support substantial internal reuse without shipping internal
production policy. BSD-3-Clause remains the first-party license.

The discipline repository and the separate supporting-tool repository retain
their approved boundary. Publication of incomplete work does not promote draft
specifications or satisfy runtime gates.

## Minimum release path

| Order | Deliverable | Prerequisite | Exit evidence |
|---|---|---|---|
| 1 | Separate tooling checkout with portable docs and exact authority/source inventory | Record authoring-home migration; preserve discipline submodule | Repository layout and accessible pins; no dangling consumer-only references |
| 2 | Offline pure-Python indexing, validation and CLI | Ratified SBCT-01 and approved baseline reconciliation | GATE-101 through GATE-105, including clean unrelated fixture and deterministic output |
| 3 | Shared C11/C12 engine, immutable file view and publication selection | Owner approval of completed SBCT-02 contract package, GATE-206 | GATE-201 through GATE-205; scoped cursor and provider cases executed |
| 4 | Minimal Django store/session example and bounded MCP OAuth | SBCT-03 exact library/protocol/endpoint contract and ratification | GATE-301 through GATE-310 |
| 5 | Reusable read-only dashboard plus prebuilt assets | SBCT-04 source/dependency pins, host contract approval and ratification | GATE-401 through GATE-406 in two independent hosts |
| 6 | Public first-release candidate and tag | SBCT-06 review/ratification; all selected-profile gates and owner release authorization | Reproducible distribution, notices, support declaration and clean-machine walkthrough |

SBCT-05 Interlock is deferred from the minimum first release. Its extension
boundary remains available; no cross-repository governance writes are added.
The dashboard target includes the reference-host profile and its explicitly
required MCP OAuth example; a core-only milestone is useful but does not
complete this first-release goal.

## Next concrete work

1. Implement [SBCT-02's approved package](SBCT-02-CONTRACT-PACKAGE.md);
   GATE-206 was explicitly approved 2026-09-20.
2. Complete SBCT-03's OAuth dependency audit and exact example contract.
3. Review the proposed [dashboard host contract](SBCT-04-HOST-CONTRACT.md),
   select exact extraction pins and presentation dependency versions.
4. Prepare the separate tooling repository and authority-reference layout,
   then implement each approved phase with the shared reference fixtures.

## Public versus downstream contents

Ship configurable corpus roots and identities, shared validators/queries,
synthetic fixtures, standard Django human auth, bounded MCP OAuth, reusable
UI/client interfaces, and public protocol/authority references.

Keep production identity, entitlement/tenancy, cloud settings, operational
secrets, private corpus data, internal policy documents and deployment machinery
in downstream hosts. Do not copy them into the public package as disabled code.
Do not remove the shared authentication or semantic validation boundary to
accomplish that separation. A downstream host must compose the same core
through published interfaces, not maintain a forked semantic engine.

## Progress record

The query package has bounded pinned-producer and structural evidence; it is
not yet a complete portable query implementation. The dashboard host declarations and runtime
witnesses are proposed. No release tag or runtime acceptance is recorded here.

GATE-206 was approved 2026-09-20. A separate local tooling checkout now contains
the first cursor-codec implementation with 13 focused standard-library tests.
This does not complete the semantic engine, stores, CLI, example or dashboard,
nor the full GATE-204 cursor/access-context witness.
