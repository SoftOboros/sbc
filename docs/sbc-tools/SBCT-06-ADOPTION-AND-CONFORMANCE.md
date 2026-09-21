# SBCT-06 — Adoption, Distribution and Conformance

**Document ID:** SBCT-06
**Status:** DRAFT — pending ratification
**Revision:** 0.6.0
**Date:** 2026-09-19
**Owner:** Ira Abbott
**Depends on:** [SBCT-00](SBCT-00-CONCEPTS.md) and the other phases required by the selected profile.

## §0 Authority Policy [Normative]

This phase MUST own release evidence and adoption sequencing, not upstream
ratification or production access. `INV-SBCT-1`, `INV-SBCT-3`, `INV-SBCT-4`,
`INV-SBCT-8` and `INV-SBCT-12` are as defined in SBCT-00 §9; used without modification.

SBCT-00 is ratified as recorded in its §15 entry dated 2026-09-19. This child
is prepared for detailed review under that authority; it remains DRAFT.
Candidate detail in §8 requires this phase's owner review and ratification.

## §1 Purpose

Make the reusable distribution independently usable and verifiable in a clean
repository. Consumer adoption is a separate claim owned by that consumer.

## §2 Evidence

Document publication alone proves neither portability nor runtime acceptance.
Selected-profile evidence must be reproducible without an originating host.

## §3 Canonical Glossary [Normative]

Profile membership is as defined in SBCT-00 §5; used without modification.
Ratification, execution and amendment status are as defined in SBC and
ADDENDUM-D; used without modification. A release manifest MUST report distinct
facts for approved specification, implemented code and verified evidence.

## §4 Source-of-Truth Map [Normative]

| Surface | Owner |
|---|---|
| Source compatibility and selected authority revisions | Owner-approved release manifest |
| Profile obligations | SBCT-00 and selected phase §12 gates |
| Production integration and deployment | Consumer repository and operator |
| Package visibility and release authorization | Repository/package owner |

## §5 Extraction and Adoption Order [Normative]

Record the source commit, local patches, supported SBC/SIDX revisions and
license/provenance before extraction. Import the reviewed source into an isolated
tooling checkout. Unrelated parent edits MUST not enter the release by accident.
Move shared logic once; leave compatibility wrappers only where required and
record their intended retirement. Wrappers MUST call the package rather than
preserve an independent semantic implementation.

The core dependency manifest MUST include transitive Python packages and confirm
the approved Python/PyPI-only boundary; a native wheel is not pure Python.
Prebuilt example/dashboard assets MUST support end-user operation without a
Node installation. Build-time tooling is documented separately.

First prove the selected profile in an unrelated fixture repository using only
its declared dependencies. An independent host fixture MUST consume the same
core version and demonstrate adapter parity. No named consumer's adoption or
production deployment may gate standalone conformance. Optional example/UI and
Interlock profiles add their own evidence; a core-only release need not ship them.

Reusable packages and the bounded example MUST have separate maintenance scopes.
The example's feature set is intended to become static after acceptance; it is
not an enterprise/scaling framework or a production auth integration library.
Its release MUST state support status and security-fix policy. Feature freeze
MUST NOT imply indefinite security support or permission to ignore known defects.
Production variants evolve independently against versioned public interfaces.

## §6 Release and Authority Manifest [Normative]

Each distribution MUST declare package versions, source commit/tree, supported
Python/Django/UI dependency ranges, profile/capability support, projection/API
versions, pinned governing documents and their provenance, and exact evidence
references for claimed gates. Unsupported combinations MUST be rejected or
explicitly excluded, not inferred from successful installation.

The tooling family and required SIDX authority references MUST be accessible
to the intended consumer. Relocation MUST retain stable IDs and historical
provenance with one authoritative owner per document. Do not publish a tool
whose claimed contract requires an inaccessible private source without marking
that distribution limitation. Public release is a separate owner action.

An installed SBC/SIDX compatibility update MUST be an explicit reviewed change.
Updating a Git submodule branch head or Python dependency range MUST not silently
change the governing semantics of a running host.

## §7 Integration and Recovery [Normative]

Rebuild/recovery MUST preserve durable authentication and governance data.
Consumer-specific migration, deployment, identity and historical-provider plans
MUST live in consumer documentation and MUST NOT be portable release conditions.
An adopting consumer owns proof that its adapters preserve the public contract.
Local fixture success alone MUST NOT satisfy that consumer's production gates.

## §8 Deferred Detail

Ira Abbott selected BSD-3-Clause on 2026-09-19 for the first-party tooling and
portable documentation. Retain the [LICENSE](LICENSE) notice and each dependency's
own notices/license. This settles the first-party license choice, not redistribution
of unrelated third-party code or any release/deployment authorization.


The owner selected the shared `SoftOboros/sbc` repository on 2026-09-21.
SIDX authority location and publication tooling remain release decisions. Package/support version ranges
MUST be selected against the reviewed extraction, not guessed in this draft.

### Prepared candidate release record and draft sequence

Propose a release manifest with package/version, source tree and patch provenance,
SBC/SIDX authority pins, licenses, supported profiles/capabilities, Python and
adapter versions, API/schema versions, pure-Python transitive dependency audit,
example support/freeze policy, and evidence references by gate. Each gate records
passed, failed, unavailable or not-run; each owner action has its own dated record.

Prepare SBCT-01's baseline/configuration first and SBCT-02's public interfaces
next. SBCT-03/04 can then finalize the example/UI; SBCT-05 can finalize optional
Interlock independently of core release. Release planning may proceed now, but
selected-profile runtime gates cannot pass until the required child work exists.

Before `GATE-607`: choose repository/package names and SIDX authority home,
licenses/access and supported versions, example maintenance responsibility and
publication procedure. The unified public prerelease repository is owner-approved; release tagging and
consumer deployment remain distinct actions with their own authorization.

## §9 Invariant Application [Normative]

Every conformance report MUST name its artifact/version/profile and list passed,
failed, unavailable and not-run gates separately. Missing proof MUST remain
unproven. No agent may classify an unchecked release as complete to close work.

## §10 Reconciliation [Normative]

The existing SBC submodule workflow is a dependency setup mechanism, not a tool
release process. This family composes it. Consumers MAY choose different
production methods while satisfying the same core contract; the distributed
reference backend stays within SBCT-03's Django and MCP OAuth example boundary.

## §11 Non-Goals

1. `NONGOAL-601` — **Automatic publication or rollout.** Drafting or ratifying this phase MUST NOT make private repositories public or deploy code.
2. `NONGOAL-602` — **Conformance by installation.** An installable artifact MUST NOT claim capabilities whose acceptance evidence is missing.

## §12 Acceptance [Normative]

A conforming SBCT release MUST satisfy §5–§7 and §9–§10 plus all gates required
by its SBCT-00 profile:

- [ ] `GATE-601` — Source and authority pins, local patch provenance, license and compatibility manifest MUST be complete and reviewable.
- [ ] `GATE-602` — A clean unrelated repository MUST install and run the selected profile without consumer application credentials, services or source checkout.
- [ ] `GATE-603` — An independent host fixture MUST use the same core package version and pass semantic/transport compatibility fixtures through public adapters; no named consumer adoption is required.
- [ ] `GATE-604` — Rebuild/recovery witnesses MUST retain identity data and historical evidence, with no unexplained behavior or schema downgrade.
- [ ] `GATE-605` — Every distributed backend MUST pass SBCT-03's auth/dependency exclusion audit, including optional extras and example configurations.
- [ ] `GATE-606` — The conformance report MUST separate local proof, production-environment proof and unexecuted gates; owner release/deployment decisions MUST remain explicit.
- [ ] `GATE-607` — Owner MUST select distribution details and record phase ratification before implementation/release work governed by this phase.

### Named witness specifications [Normative]

These cases MUST be specified for review now and executed only at their
applicable acceptance stage. They are not claims that tests already exist.

| Witness | Positive case | Negative case |
|---|---|---|
| `W-601-P` / `W-601-N` | A complete owner-approved authority/source manifest and compatible vectors support a bounded profile claim. | An unpinned authority, invented enum or unsupported full-SIDX claim is rejected during release review. |
| `W-602-P` / `W-602-N` | A review fixture records owner approval, implementation state, verification evidence, publication authorization and deployment authorization as separate facts; absent events remain absent. | A fixture with only an agent assertion of ratification/publication/deployment is rejected as authority. Installation or a passing local test never supplies the missing approval or event evidence. |

## §13 Files Cited

[SBCT-00](SBCT-00-CONCEPTS.md), [README](README.md), [ERRATA](ERRATA.md).

## §14 Unblocks

Release review for the selected profile, with separately authorized publication
and consumer deployment. No such event has occurred for these drafts.

## §15 Change Log

### 0.1.0 — 2026-09-18 — drafted

**Author:** Codex (draft author)
**Change kind:** scope
**Touches:** SBCT-06
**Commits:** none
**Summary:** Specifies evidence-led extraction, consumer adoption and release claims.

#### Rationale

Considered and rejected: treating successful packaging as conformance, retaining
two semantic implementations, and conflating private publication with public
release or production deployment. Deliberately unchanged: production access,
existing authority ownership and forward-only consumer migration requirements.

### 0.2.0 — 2026-09-18 — owner-directed draft revision

**Author:** Codex
**Change kind:** scope
**Touches:** SBCT-06; parent INV-SBCT-3 and conformance boundaries
**Commits:** none
**Summary:** Incorporates accepted standalone conformance and explicit decision
closure; expands the example to MCP OAuth and separates consumer-specific
adoption from the portable contract. This is not family or phase ratification.

### 0.3.0 — 2026-09-19 — ratification package prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-06
**Commits:** none
**Summary:** Prepares explicit proposed decision dispositions, bounded
compatibility policy and child-owned witness specifications. Existing invariant
meanings are preserved. No decision acceptance or ratification is inferred.

### 0.4.0 — 2026-09-19 — owner decision approvals recorded

**Author:** Codex (recorder)
**Decision authority:** Ira Abbott, explicit approval on 2026-09-19
**Change kind:** clarification
**Touches:** PCDN-SBCT-00-001, PCDN-SBCT-00-002, PCDN-SBCT-00-003, PCDN-SBCT-00-004
**Commits:** none
**Summary:** Records approved semantic reuse, pure-Python/PyPI core portability,
submodule-based initial Interlock direction and separate tooling repository.
Deferred child gates remain required. Overall concepts ratification, child
ratification, implementation and publication are not inferred.

### 0.5.0 — 2026-09-19 — child draft prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-06
**Commits:** none
**Summary:** Recognizes parent ratification and prepares concrete candidate
contracts and remaining prerequisites in §8. Child ratification and acceptance
are not claimed; all implementation gates remain unchecked.

### 0.6.0 — 2026-09-19 — license decision recorded

**Author:** Codex (recorder)
**Decision authority:** Ira Abbott
**Change kind:** clarification
**Touches:** SBCT-06
**Commits:** none
**Summary:** Records BSD-3-Clause for first-party tooling and documentation;
dependency notices remain intact. No phase ratification or release is inferred.


### Repository amendment — 2026-09-21

The owner-approved SBCT-00 0.4.2 consolidation resolves repository location.
This phase remains DRAFT; see [the migration record](REPOSITORY-CONSOLIDATION.md).
