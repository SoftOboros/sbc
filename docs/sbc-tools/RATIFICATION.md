# SBCT ratification review packet

**Document ID:** SBCT-RATIFICATION
**Status:** SBCT-00 RATIFIED by Ira Abbott on 2026-09-19; child phases remain DRAFT.
**Prepared:** 2026-09-19
**Owner:** Ira Abbott

This is a review aid, not a second normative authority. [SBCT-00](SBCT-00-CONCEPTS.md)
§8 owns decisions, §10 owns compatibility and witness coverage, and child §12
sections own witness specifications. The owner explicitly approved all four
PCDNs and then explicitly ratified SBCT-00. No implementation witness is inferred.

## Approved decision package

SBCT-00 §8 records the four approved dispositions and clarifications. They select
one portable Python core, optional adapters/UI and a bounded Django/MCP OAuth
example; optional initially read-only Interlock modeled on submodule relations; a separate initially private tooling
repository; and bounded semantic reuse with exact reconciled pins selected
before extraction. Each unresolved detail has a named child gate.

Already accepted directions remain recorded in SBCT-00 §8: standalone
conformance, explicit decision closure, minimal MCP OAuth administration, and
consumer-independent portable docs with separate production maintenance.
Preparation of this package does not request their approval again.

## Ratification review checklist

- Completed: owner dispositions for all four PCDNs, including retained deferrals,
  are recorded in SBCT-00 §8. Python/PyPI portability and Interlock direction
  are clarified there.
- Review the clause-level compatibility policy in §10. It excludes full SIDX
  deployment conformance and does not amend existing consumers' policies.
- Review the 12-invariant mapping and each child-owned positive/negative case.
  Specification completeness is distinct from successful witness execution.
- If accepted, record the owner's dated dispositions and explicit concepts
  ratification in SBCT-00 §15. Child phases remain unratified until separately
  approved; extraction, implementation, release and deployment gates still apply.

## Observed authority inputs

This byte inventory records the local files examined for the approved bounded policy.
It is NOT a coherent approved release baseline, a remote freshness claim, or an
assertion that all local edits are ratified. In particular the installed SBC
snapshot is concepts 0.11.0; reconciliation against the intended newer grammar
remains gated. File digests identify working-copy bytes, separately from Git pins.
Consumers must receive accessible authority references before a release claim.

Installed SBC Git commit: `b20a6e8f2a0761b638f22d48a5b564b671f9f964`.

| Reviewed document | SHA-256 of observed bytes |
|---|---|
| [SBC-00-CONCEPTS](../SBC-00-CONCEPTS.md) | `bff52dc6d076287bccec397ad27ccb645a19cb677b27f6614a1b772fd4eb1fd1` |
| [SBC-00-ADDENDUM-A](../SBC-00-ADDENDUM-A.md) | `1d1278eb256636648acc6cf8b247819434629246f251e6ff8ec9b8b60c50fd0e` |
| [SBC-00-ADDENDUM-B](../SBC-00-ADDENDUM-B.md) | `4f0ce82403333b7abc9377d0acf6c5cb18bf48926cabc81dddbb1ae67d8e584d` |
| [SBC-00-ADDENDUM-C](../SBC-00-ADDENDUM-C.md) | `61b047431600a7d4923fac4d3ddb0de70b7acf7affa2381cbb93b294b350d284` |
| [SBC-00-ADDENDUM-D](../SBC-00-ADDENDUM-D.md) | `4045dbab4f1308322fd3eac24790e04f6eafc2bcefc9b19de500d83032a45c82` |
| [TODO-SIDX-00-CONCEPTS](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-00-CONCEPTS.md) | `803a333ed7a301381be0059c21909eeecf5d1a3bd388209ff5cc18fa429f415e` |
| [TODO-SIDX-06A-CORPUS-AND-LOCATION-PROJECTION](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06A-CORPUS-AND-LOCATION-PROJECTION.md) | `15cb5ea9eedf473cacf0646108ddb1aa2bc2bd2d37fc9743c72f7b602a59e5c4` |
| [TODO-SIDX-06B-SHARED-QUERIES-AND-TRANSPORT-PARITY](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06B-SHARED-QUERIES-AND-TRANSPORT-PARITY.md) | `3a05246abc6d477cc08f12f35867de8f3879ec369cfab704b4e89674b64efb94` |
| [TODO-SIDX-06C-LOCAL-TSX-DASHBOARD](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06C-LOCAL-TSX-DASHBOARD.md) | `ae5a3dfc64386e8d4512dadf2f1c7d8cadd74a7937784945f029cde50aacc95b` |
| [TODO-SIDX-06D-CONFORMANCE-INPUTS-AND-GIT-PROVIDERS](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06D-CONFORMANCE-INPUTS-AND-GIT-PROVIDERS.md) | `9b4c3c3270defec275eb71a7b701cb6dfadc574606b516aef0390866f1abf67b` |
| [TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06E-C6-OBJECT-GRAPH-AND-ACKNOWLEDGMENT.md) | `109ff1f52e93f674e8da122a0d21970c6c7d156480d2cb1b2438d5c8950b0a66` |

## Limits

No implementation, runtime acceptance, publication, deployment or complete
upstream reconciliation is established here. Generated-index diagnostic debt
is reported separately and is not silently waived by this review packet.

## Ratification recorded

The owner explicitly ratified SBCT-00 on 2026-09-19. SBCT-00 §15 records that act
and the five completed specification-review gates. The owner subsequently
ratified SBCT-01 revision 0.7.1 and SBCT-02 revision 0.6.1 on the same date.
SBCT-03 through SBCT-06 remain drafts; see AGENTS.md for their current revisions.
SBCT-02's [contract package](SBCT-02-CONTRACT-PACKAGE.md) revision 0.1.1 was
approved under GATE-206 on 2026-09-20. Its evidence does not close runtime gates.
The observed working-copy inventory above remains historical evidence; exact
phase-specific pins are recorded in the relevant completion packages.
