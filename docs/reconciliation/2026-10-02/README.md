# SBC discipline source reconciliation

October 2, 2026. Informative transport record; no new ratification, release,
portable-tooling acceptance, or deployed consumer pin.

The owner requested GitHub alignment and then instructed us to proceed. This
candidate imports already-ratified source from monorepo commit
`2808f9bd1c9a85f6ea049a1cd7675ab7d79778e2` onto standalone SBC base
`401c61f7df1403143627268594ba987c7f34ce8a`. The monorepo integration containing
that dashboard history and current webslinger is
`5ec9424afc7162ed6e9933e9040a59e4730868a2`.

## Source alignment

Eight source files are byte-identical to their original Git blobs. All existing
Document IDs are preserved. The superseded predecessor receives its previously
recorded lifecycle and historical-definition metadata. ERRATA-015 remains
outstanding; its accepted rules do not establish implementation acceptance or
resolve individual exceptions.

| Source | Imported revision or role |
|---|---|
| SBC-00 concepts | 0.17.0 |
| Addendum A | 0.4.0 |
| Addendum B | 0.4.0 |
| Addendum C | 0.15.0 |
| Addendum D | 0.8.0 |
| SBC-ERRATA | Living log; ERRATA-015 remains outstanding |
| Superseded predecessor | Historical source and lifecycle metadata |
| ERRATA template | Ratified template |

The [manifest](source-manifest.json) records source blobs, before/after SHA-256
digests, all four ratification packet checks, the source-evidence adoption
receipt, and 27 relative link occurrences. Original receipts and packets remain
at their original monorepo paths and commits; none is edited or reissued here.

The initial September 5 receipt names the accepted patch digest and manifest
commit. The other three receipts also name accepted manifest digests. All
recorded accepted digest checks passed. This establishes packet integrity,
not new approval or runtime proof.

## Evidence navigation

Use the [pinned navigation map](navigation.md) to open original source files,
ratification packets, and source-relative evidence links from this standalone
checkout. The four active ERRATA evidence targets exist at the recorded
monorepo revision. Access may require permission; the complete private evidence
set has not been redistributed into the standalone repository.

Two links require context rather than an invented replacement:

- The Addendum A link appears inside an adoption injection template and is
  relative to the adopting operational-context file.
- The superseded predecessor retains an example referring to the
  disco-analyzer submodule ERRATA. Its target at that historical nested
  repository boundary remains unverified.

These retained references do not create new current work items by themselves.
The source bytes stay exact; no link cleanup is folded into ratified text.

## Ownership and adoption sequence

`tools/`, `docs/sbc-tools/`, hosted verification receipts, approved authority
digests, packaging, and workflows remain unchanged from the standalone base.
README, CLAUDE and AGENTS receive informative navigation and inventory corrections.
Their earlier inventory remains in Git history.

Before consumer adoption:

1. Review the reconciliation and its external evidence navigation.
2. Publish a reviewed child commit through the repository's existing workflow,
   then select that exact commit for the parent gitlink. No pin advances here.
3. Reconcile any SBCT authority-profile upgrade explicitly. Existing approved
   digests and fixtures are not silently rebound to these imported documents.
4. Prove parent checkout and AWS access, scanner traversal, and immutable Git
   history and retained-source reads across the gitlink boundary.
5. Continue the dashboard cache/cursor matrix and signed-in acceptance.

The original parent checkout, staged gitlink, and installed SBC checkout remain
unchanged. The dashboard integration retains its existing in-tree authority
until cross-repository adoption is proved.

## Validation

The [validation receipt](validation.json) records exact source equality, preserved
Document IDs and checklist state, packet integrity, unchanged tooling, and
conflict checks. No executable behavior changes in this slice. Checkboxes in
the transported files are exactly those in the source; none is newly checked
by this reconciliation.
