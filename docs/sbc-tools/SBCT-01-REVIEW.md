# SBCT-01 pre-ratification review

**Document ID:** SBCT-REVIEW-01
**Status:** SBCT-01 RATIFIED by Ira Abbott, 2026-09-19.
**Prepared:** 2026-09-19
**Owner:** Ira Abbott

## Decision now recorded

BSD-3-Clause is the owner's selected license for first-party tooling and
portable documentation. [LICENSE](LICENSE) retains the copyright notice and
conditions. Third-party dependency licenses are not replaced by this choice.

## Concrete approval target

Review SBCT-01 revision 0.7.0 §5/§6 and §8 as one phase contract: complete
configuration keys, CLI exit/error behavior, manifest/envelope schemas,
content-derived snapshot identity, exact candidate source/pure-wheel pins,
and the following evidence. The authority baseline is a base commit plus a
separately hashed operational metadata correction, not a floating branch.
No phase approval is inferred from authorizing this preparation.

| Item | Prepared evidence | Limit |
|---|---|---|
| Authority reconciliation | All 12 installed SBC files compared with exact upstream blobs; 11-file source patch plus separate stale operational metadata correction; both apply to a disposable copy | Live submodule remains unchanged; applying/publishing requires subsequent repository work |
| Source integrity | All 17 fetched source/authority/license files verified against Git blob hashes | Does not claim latest branch state |
| First-party licensing | BSD-3-Clause selected by owner, notice supplied | Retain dependency and third-party terms |
| Pure Python provider | [Provider audit](SBCT-01-PROVIDER-AUDIT.md) with exact wheel hashes and limited Git reads | Installation/history/platform matrix remains unproven |
| Golden parser reference | [Five cases](evidence/sbct-01-golden-vectors.json), original pinned scanner, full rendered payloads and SHA-256s; two identical runs per case | No portable engine exists yet; GATE-105 is not passed |
| Contracts | [Authority schema](contracts/authority-manifest.schema.json), [CLI schema](contracts/cli-envelope.schema.json) and paired examples | Structural validation supplements, not replaces, path/identity/permission semantics |

Source-origin and patch artifacts are held in the originating consumer's review
record, outside this portable family. No consumer-specific reuse procedure is
required by this package. SBCT-01 §8 identifies the exact base-source blobs.

## Golden reference interpretation

The stable case produces document, term, invariant, non-goal and gate objects
without diagnostics. Changing the gate checkbox changes its declared state while
preserving its object ID. A malformed gate remains positional and yields an
invalid dependency target. Duplicate invariant definitions remain ambiguous.
Empty input produces three empty projection manifests. Every output was validated
by the pinned producer and repeated byte-for-byte; expected bytes are retained
verbatim as JSON strings, not edited to force desired outcomes.

To replay, materialize each case's `inputs` beneath a disposable root, import the
exact scanner and location-helper blobs listed in SBCT-01 §8, then call `scan`,
`build_projection_bundle_with_expectations`, `build_location_index`,
`bind_location_expectations` and `_validate_projection_bundle`. Render object/
diagnostic payloads with the producer's `_render` and locations with `render`;
compare each string and hash against `outputs` and `output_sha256`. This is a
reference-producer probe, not the future portable runtime's implementation.

## Owner ratification recorded

Ira Abbott explicitly ratified SBCT-01 on 2026-09-19. SBCT-01 §15 records the
approved baseline, interfaces and dependency selection. GATE-106 is complete.
Runtime gates GATE-101 through GATE-105 remain unchecked. Actual extraction must
preserve approved content/patch provenance; publication and deployment remain
separate owner actions.

## Limited closure review and validation

A read-only subagent closure review found no material blocker after resolving
candidate/reference identity and manifest-role cardinality. Its final wording
cleanup is incorporated. Thirteen schema positive/negative checks passed;
all five retained golden output sets passed hash verification. See
[schema validation evidence](evidence/sbct-01-schema-validation.json).
These are pre-ratification document/reference checks, not runtime gate completion.
