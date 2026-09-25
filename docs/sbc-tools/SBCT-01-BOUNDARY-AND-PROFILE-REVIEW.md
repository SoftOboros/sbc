# SBCT-01 path-boundary and golden-profile reconciliation

**Date:** 2026-09-25
**Status:** Informative acceptance evidence; no gate closure.
**Runtime:** `0.1.0.dev34`, revision `9d666f43efe6ffab4c478a97ba199077e611d7de`.
**Source baseline:** `751ffe62027a3030bc989d22f5c2f759234064dc` as approved by SBCT-01.

## Result

The command-level injected path-boundary matrix and pinned golden comparisons
pass without runtime changes. Evidence is recorded in
[the execution record](evidence/sbct-01-boundary-profile-execution.json). These
results support a bounded acceptance review; they do not establish every supported
platform or a new authority/profile selection.

The provider suite ran 164 tests: 163 passed and one native directory-symlink test
was skipped because creation failed with errno 22. The 111 core tests also passed.
The skipped case is not counted as a successful link witness, and no elevation
or native junction support was inferred.

## Command path-boundary matrix

| Witness | Executed scope | Result |
|---|---|---|
| Injected symlink/reparse rejection | Committed, single-source observation and mounted observation; scan/check; source, registry, authority and output paths; nested source or child mount as the fifth path role | All 60 combinations return configuration failure without guarded content opens, link resolution or descendant metadata reads. |
| Escaping configured scope | Three modes, scan/check, explicit `../outside` source scope and an external sentinel file | All six combinations reject without guarded reads or file mutations. |
| No mutation on rejection | Exact fixture file inventories before/after, including Git metadata, host binding, authored inputs and any output | Equal across the injected and escaping-path cases. |
| Native directory symlink | Actual filesystem link targeting an external fixture directory | Creation unavailable; skipped, not proven. |

Injected metadata reaches the actual explicit-host CLI path and error handling.
It is useful deterministic evidence but does not substitute for Windows junction
or native symlink execution. Previous empty-existing/missing-root command tests
remain in the passing provider suite. Concurrent hostile path replacement remains
outside the bounded observation guarantee.

## Exact profile and golden reconciliation

The authority-manifest role profile is `sidx-schema3-location1` under SBCT-01 §6.
New projection ingestion uses the exact `c6-v3` triple: object/diagnostic schema 3
and location schema 1. This is separate from the `sbct-query-v1` query profile and
its proposed retained-profile paths under SBCT-02. Passing producer fixtures does
not establish query, Django-store or transport parity.

The checked source objects are:

| Role | Git blob |
|---|---|
| Scanner | `551c0ab7d70f82ad9e6fdfd99ef57a1ff78aeabb` |
| Locations | `31217a012c99785cd0bda3cae3a3d9feb3cf33d5` |
| Suspicion helper | `d4da35b954285f757e03add62c5087765a754b88` |
| Ingest validation | `d77b462102367d143a4d1d204df3df7dd586d193` |

All source blobs are checked by their regeneration tools. The ingest blob was
read directly from the local Git object store; no dirty working source replaced
the pinned input. Public retrieval of these objects was not tested here.

- Five committed reference-source cases regenerate exactly: empty, stable IDs,
  checked-state change, malformed gate and duplicate invariant.
- Nine full object/location/diagnostic comparisons pass, adding cross-family,
  historical cross-family, archive and declared archive/lifecycle cases. Pure
  builds reject file, process and network access after reference preparation.
- Five emitted-wire fixtures and the recorded per-document fixtures reproduce
  exactly; neither authored fixtures nor generated runtime modules were rewritten.
- Parser/location closure and all 46 extracted validator/helper functions
  reproduce exactly from the pinned source.

## Difference disposition

No new semantic producer difference was found in these bounded cases. Existing
portable boundaries remain explicit:

1. Host-supplied source roots, repository ownership and family routing replace
   consumer directory conventions under SBCT-01 configuration. The shared parser
   consumes selected bytes without gaining filesystem or identity authority.
2. Mechanical extraction removes runtime IO/ORM composition, qualifies validator
   helpers and supplies corpus roots. Reproduction confirms those declared
   transformations; it does not approve an alternate semantic algorithm.
3. Historical `projection-vectors.json` serialization remains immutable rejection
   evidence. Exact pinned emitter bytes in `projection-wire-vectors.json` are the
   accepted wire fixtures. Runtime validation is not relaxed to ingest malformed
   historical serialization.
4. Version-2 observation metadata and null committed identities are the approved
   SBCT-01 observation wrapper. They do not change inherited projection payloads
   or reinterpret a dirty observation as clean committed evidence.

## Gate recommendation and next work

`GATE-103`, `GATE-104` and `GATE-105` now have an explicit bounded witness mapping
across this record and the [installed review](SBCT-01-MOUNTED-ACCEPTANCE-REVIEW.md).
Keep their formal dispositions open for owner review. `GATE-102` retains the native
link/junction execution gap; `GATE-101` retains Python/platform matrix and final
distribution-recipe reconciliation. Source accessibility for public adopters is
also distinct from local blob availability.

Next prepare a consolidated gate decision packet with these exact scope limits
and the outstanding platform/native-link witnesses. Do not infer an exemption,
release/tag, query-engine acceptance or downstream production approval.
