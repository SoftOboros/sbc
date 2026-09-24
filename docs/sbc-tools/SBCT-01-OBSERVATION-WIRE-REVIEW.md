# SBCT-01 observation wire approval review

**Status:** APPROVED — Ira Abbott, 2026-09-23.
**Date:** 2026-09-23
**Target:** SBCT-01-OBSERVATIONS 0.1.2, proposed SBCT-01 amendment.

## Recommendation

Approve the three proposed decisions below as the exact first-version observation
wire extension. First-version boundaries and immediate-parent observed-HEAD
recursion are already accepted; this review does not reopen them. No additional
runtime acceptance gate is declared complete. Existing GATE-106 specification
approval remains historical; this packet is an explicit amendment decision.

| Decision | Proposed contract | Consequence |
|---|---|---|
| Dirty-state scope | Each participant reports its own checkout/index state against its observed HEAD. Registered child mounts are boundaries. A child's HEAD mismatch makes its immediate parent dirty; dirtiness inside a child stays on its own row. | Dirty content and pin mismatch stay independent. Both can describe known work in progress without preventing a complete observation. |
| Observation identity | Hash the canonical complete observation-set object excluding `selection_sha256`; incomplete sets have a null digest. This includes repository identities, relations, observed HEADs and local states. | Observation context has a separate identity from content-derived projection snapshots. No timestamp or machine-specific absolute path enters either hash. |
| Versioned framing and failure | Version-2 CLI envelope carries observation-set version 1. Existing version-1 commands and committed dependencies stay unchanged. Required unavailable participants prevent aggregate selection/publication. Descendants not inspected because an ancestor is unavailable are `blocked_by_ancestor`. | New metadata cannot be mistaken for committed dependency evidence or a partial successful projection. Committed IDs remain null. |

## Exact artifacts

- [Contract revision 0.1.2](SBCT-01-SUBMODULE-OBSERVATIONS.md).
- [Observation-set schema](contracts/observation-set.schema.json) and
  [synthetic example with computed selection digest](contracts/observation-set.example.json).
- [CLI version-2 schema](contracts/cli-observation-envelope.schema.json) and
  [example](contracts/cli-observation-envelope.example.json).
- [Review evidence and artifact hashes](evidence/sbct-01-observation-wire-gate-review.json).

## Limited review findings

1. Resolved: unavailable ancestors previously left descendant status ambiguous.
   `blocked_by_ancestor` avoids claiming an unobserved checkout is missing.
2. Resolved: dirty-state scope now treats repository boundaries explicitly;
   generated-output changes can make a checkout dirty without changing corpus content.
3. Resolved: the selection example now has a computed digest, independently checked
   by the developer contract checker. Other example IDs remain synthetic.
4. Retained limitation: schema validation alone cannot establish graph ownership,
   correct Git evidence, temporal stability or authorization. Limited semantic
   checks add ordering, identity, parent coverage and false-match rejection;
   runtime witnesses remain required.

## Evidence and scope of approval

The developer checker passes 3 structural positive and 18 negative cases,
plus 1 complete-set semantic positive and 8 negative cases. These checks do not
exercise real nested Git traversal, unavailable ancestry, concurrent changes,
publication failure or the full acceptance matrix. No runtime code was changed.

Owner approval would authorize the wire amendment and its implementation under
SBCT-01. It would not ratify SBCT-05 Interlock, update gitlinks, clear work-in-progress
conditions, close runtime gates, or authorize a release tag. Indexing helpers for
surfacing and reconciling these observations remain future implementation work.

## Owner decision

The owner accepted the recommendation with "proceed as recomended". All three
wire decisions are approved and incorporated by SBCT-01 0.9.0. Runtime gates
and release approval remain separate. The review evidence records the preapproval
artifact hashes; it is retained unchanged.
