# SBCT-01 — Repository Core, Configuration and CLI

**Document ID:** SBCT-01
**Status:** RATIFIED — Ira Abbott, 2026-09-19
**Revision:** 0.9.1
**Date:** 2026-09-25
**Owner:** Ira Abbott
**Depends on:** [SBCT-00](SBCT-00-CONCEPTS.md), especially §8 baseline/layout decisions.

## §0 Authority Policy [Normative]

This phase MUST own repository configuration and provenance without owning
SBC parsing semantics. `INV-SBCT-2`, `INV-SBCT-4`, `INV-SBCT-5` and
`INV-SBCT-9` are as defined in SBCT-00 §9; used without modification.
Extraction MUST wait for the selected source and authority baseline.

SBCT-00 is ratified as recorded in its §15 entry dated 2026-09-19. This child
was explicitly ratified by Ira Abbott on 2026-09-19 as recorded in §15.
Its approved contracts and baseline govern subsequent implementation; runtime
acceptance and publication remain separate gates.

## §1 Purpose

Make the existing scanner, location validator and Git-history helpers usable
from an ordinary repository without application installation or service access.

## §2 Evidence

Scanner roots, module imports and history lookup must be configurable.
Submodules require source traversal to remain distinct from Git ownership.

## §3 Canonical Glossary [Normative]

Shared core and repository scope are as defined in SBCT-00 §3; used without
modification. Git commit, tree, worktree and gitlink are composed Git concepts.
Configuration MUST describe their use, not reinterpret their identity.

## §4 Source-of-Truth Map [Normative]

| Surface | Owner |
|---|---|
| Object grammar, identifier normalization, source-derived diagnostics | Pinned SBC/SIDX contracts |
| File/path configuration and CLI behavior | This phase §5–§7 |
| Repository revision and submodule pins | Git plus explicit host selection |
| Query and evidence consumption | SBCT-02 |

## §5 Configuration Contract [Normative]

The v1 draft schema below is the complete proposed configuration key set.
Owner approval is recorded at `GATE-106` and §15. No environment variable,
repository hook or application settings file may silently supplement these keys.
The owner-approved [console host binding](SBCT-01-CONSOLE-HOST-PROPOSAL.md)
is supplied only through explicit `--host PATH`; it registers host inputs without
adding TOML keys, implicit discovery or approval inference.
The supported interpreter floor proposed for v1 is Python 3.11, permitting
standard-library TOML parsing; the final supported-version matrix is a release gate.

| Key | Required type and v1 constraint |
|---|---|
| `schema_version` | Integer exactly `1`; booleans are not integers |
| `repository_id` | Nonempty host-registered string; no identity derived from path/URL |
| `repository_root` | Existing directory, resolved relative to the config file's directory |
| `source_roots` | Nonempty array of existing, nonoverlapping repository-relative directories |
| `exclude` | Array of repository-relative literal directory/file paths; no glob or regex execution |
| `registry_paths` | Array of existing repository-relative regular files; empty permitted if profile needs none |
| `output_root` | Repository-relative directory outside every source root and registry path |
| `tracked_ref` | `HEAD`, a full `refs/heads/…` or `refs/tags/…` name, or an exact supported commit OID; no revision expressions |
| `mode` | `committed` or `working-tree`; explicit choice, never inferred from checkout state |
| `capabilities` | Nonempty unique subset of `scan`, `check`; names are CLI capabilities, not SIDX capability claims |
| `authority_manifest` | Existing repository-relative JSON file identifying exact SBC/SIDX/source pins, integrity and profile |
| `submodules` | Array of tables with exactly `path` and `repository_id`; empty permitted; explicitly allowlisted source mounts |

All keys are required; unknown keys, duplicate entries, unsafe paths, unsupported
modes/versions fail configuration validation with exit 2. OID syntax alone is not proof
that an object exists or is a commit. After structural configuration validation,
the provider resolves each reference once and pins the resulting commit. A
malformed/disallowed reference or available object of the wrong type is exit 2;
a syntactically valid reference with missing objects/history is exit 3. This
rule applies to root refs, child pins and authority evidence alike. Tags must
resolve unambiguously to a commit; an unavailable tag target is exit 3.
Repository identity uses the registered mapping; its cross-repository canonical
schema remains SBCT-05's contract. The authority manifest is a validated release
input under SBCT-06, not a user override for parser grammar.

For `submodules`, each path is a root-relative mount path. Resolve nested entries
through their explicitly registered ancestor mounts, longest enclosing mount
first; validate the remaining parent-relative path as a gitlink in that immediate
parent repository's pinned tree. For example, `vendor/a/vendor/b` belongs to A's
tree at `vendor/b` after root mount `vendor/a` has been validated and pinned.
It is not required to be a gitlink in the root tree. Missing ancestor registration,
duplicate mounts and conflicting identity mappings are configuration errors
(exit 2); missing required parent/child evidence is unavailable (exit 3).

Traverse only allowlisted mounts explicitly included by source roots, never
arbitrary discovered children. Missing/uninitialized/dirty/mismatched children
follow §7. Nested mounts require explicit entries; no implicit recursion or fetch
is authorized. Process parents before children with deterministic path ordering,
and reject cycles in the configured ownership mapping.

Paths MUST be resolved relative to the declared repository root. Output roots
MUST be distinct from authoritative input roots. A scan MUST reject traversal
outside scope, escaping symlinks and conflicting output destinations. It MUST
not import Python plugins, run commands, fetch a ref or read ambient credentials
because a document/configuration value requests it. Empty input is valid only
when configured roots exist; a missing root MUST not masquerade as an empty corpus.

Configuration MAY select authoritative roots and capabilities; it MUST NOT
replace frozen grammars, ignore a changed invariant, or auto-accept diagnostics.
Consumer-specific root lists and branch names belong in consumer configuration only.

The installation contract is the approved PCDN-002 boundary in SBCT-00 §8.
Core and transitive runtime dependencies MUST run from Python/PyPI without
third-party native extensions, a compiler, a Git executable, OS packages or
administrator permission. Standard-library modules shipped with Python are
part of the baseline. Git evidence providers MUST preserve exact Git semantics
within that boundary or report unavailable evidence.

## §6 CLI Contract [Normative]

The executable name proposed for v1 is `sbc-tools`; package publication names
remain SBCT-06 detail. Every command requires `--config PATH`. `--format text|json`
defaults to text; `--help` and `--version` require no repository/configuration.
Default-console repository operations also require `--host PATH`, following the
[approved binding contract](SBCT-01-CONSOLE-HOST-PROPOSAL.md) and its
[version-1 schema](contracts/console-host.schema.json). An explicitly injected
in-process host remains supported; supplying both mechanisms is an invocation
error. Selecting a binding does not approve its authority pins.
Unknown flags and conflicting invocations fail with exit 2.

| Command | Contract |
|---|---|
| `scan --config PATH --host PATH` | Derive, validate and atomically publish a bundle under configured output_root; never edit authored sources |
| `check --config PATH --host PATH` | Regenerate in memory/temporary storage and compare with the selected committed projection payloads; no persistent writes or baseline changes |

`inspect` is reserved for SBCT-02's query contract and is not part of this phase's
v1 executable surface. Neither scan nor check can change source mode by inference.
Working-tree check reports comparison as an observation, never committed acceptance.
Missing committed reference projections are unavailable (exit 3), not an empty
reference that automatically passes. The payload schema and identity are inherited
from the selected SIDX profile; wrappers cannot silently change its byte rules.

| Exit | Meaning | Publication behavior |
|---|---|---|
| 0 | Complete successful operation; check has no drift or source findings | Scan publishes validated bundle |
| 1 | Complete result with source findings or check drift | Scan may publish a structurally valid diagnostic-bearing bundle; check never writes |
| 2 | Invocation, configuration or authority-manifest validation failure | No publication |
| 3 | Required evidence/reference unavailable or I/O failure | No publication; prior bundle remains usable |
| 4 | Internal failure or structurally invalid candidate bundle | No publication; safe error, no stack/secret disclosure in JSON |

Validate invocation/configuration first. Once execution begins, incomplete failure
(3/4) takes precedence over findings (1); report both findings and completeness.
Domain confidence remains a payload field and is not encoded as an exit status.
On JSON requests, stdout contains one UTF-8 JSON object terminated by a newline;
progress is stderr-only. Proposed envelope keys are `schema_version` (1),
`command`, `mode`, `status` (`ok`, `findings`, `error`), `exit_code`, `selection`,
`findings`, `error`, and `result`. Inapplicable values are null, findings is an
array, and `error` is null or an object with `code` and safe `message`. Canonical
domain diagnostic codes are inherited, not replaced by this CLI error vocabulary.
Proposed CLI error codes: `invalid_invocation`, `invalid_configuration`,
`invalid_authority`, `evidence_unavailable`, `io_failure`, `internal_failure`.
A config-less invocation error has null mode/selection. Detailed selection/result shapes are specified by the contract schemas below;
an invalid or missing command is null in an invocation-error envelope.

### Manifest, selection and projection identity

The proposed v1 shapes are [authority-manifest.schema.json](contracts/authority-manifest.schema.json)
and [cli-envelope.schema.json](contracts/cli-envelope.schema.json). Examples in
that directory are validation fixtures, not execution/approval records. An
authority manifest records base commit/blob/SHA-256 identities plus separately
identified reviewed patches. It MUST contain each required authority and producer
role exactly once; conflicting duplicate path/role entries fail. A digest is
integrity evidence, not proof of owner approval or access authorization.

Canonical manifest paths MUST be nonempty POSIX repository-relative paths with
no absolute prefix, drive/URI colon, backslash, empty segment, dot/dot-dot segment
or control character. Resolving any path outside its owning root fails even if
its spelling passes JSON Schema. Files and dependency rows MUST be uniquely
keyed and sorted by owning repository ID then path; unknown semantic profile
roles, unavailable pins and unreviewed patches follow the existing error rules.
JSON Schema structural acceptance alone does not satisfy those semantic checks.

Registration policy for this phase's versioned profile, role, mode, command and
CLI error/exit enumerations is Standards Action; extensions require an explicit
owner-approved contract revision, never an arbitrary manifest value.

The `sidx-schema3-location1` role inventory is closed for v1. Each listed role
appears exactly once, carrying one file. The filename-like role labels are
logical identifiers and are not permission to substitute a file based only on
its basename. Paths/blobs must match the owner-approved baseline manifest.

| Manifest group | Required roles, each exactly once |
|---|---|
| `authority_inputs` | `SBC-00-CONCEPTS.md`, `SBC-00-ADDENDUM-A.md`, `SBC-00-ADDENDUM-B.md`, `SBC-00-ADDENDUM-C.md`, `SBC-00-ADDENDUM-D.md`, `TODO-SIDX-00-CONCEPTS.md`, `TODO-SIDX-06A-CORPUS-AND-LOCATION-PROJECTION.md`, `SBC-ERRATA.md`, `SPEC-BEFORE-CODE-CONCEPTS.md` |
| `producer_inputs` | `scan.py`, `locations.py`, `suspect.py` |
| `support_inputs` | `AGENTS.md`, `CLAUDE.md`, `README.md`, `LICENSE` |

Support inputs preserve operational/license provenance; they do not override
normative authority. The superseded predecessor and errata retain their declared
historical/disposition roles, not new ratification. `reviewed_patches` contains
exactly one `proposed-operational-metadata-correction` record; its `applies_to`
is exactly the set `AGENTS.md`, `CLAUDE.md`, `README.md`. It may change only those
support roles, using the pinned base inputs. New normative/code patches require
an explicitly revised approved profile; a generic patch slot cannot authorize
them. Absence of the correction cannot satisfy this profile. Patch order is trivial
with one;
verify patch hash and resulting per-file identities before use.


Inherited object/diagnostic payloads remain schema 3 and locations remain schema 1.
Their bytes MUST follow the selected producer's existing render functions. The
new CLI envelope stays outside those payloads; no `index_commit`, object identity
or location field is removed or rewritten to accommodate this wrapper.

For wrapper identity, canonical JSON uses sorted keys, compact separators,
UTF-8 with unescaped Unicode, no nonfinite numbers, and a single trailing LF.
`corpus_sha256` hashes the canonical sorted list of authoritative input records
`{repository_id, path, sha256}`. Include configuration, authority manifest,
registries and selected source/evidence bytes; exclude output payloads, Git
administrative files and run timestamps. Missing relevant inputs fail rather
than disappear from the inventory.

`snapshot_id` hashes canonical JSON containing exactly `authority_manifest_sha256`,
`corpus_sha256`, and the sorted `files` array of `{path, sha256}` for inherited
payload files. Source/projection commit IDs and runtime observations are NOT
part of this content identity. `source_commit` describes the command's selected
source commit; `projection_commit` identifies the Git commit from which comparison
or served payloads were actually read (null before publication or in observation
mode). These are provenance, not interchangeable values.

`result.files` and `snapshot_id` ALWAYS describe the regenerated candidate,
including when `check` reports drift. `projection_commit` identifies only the
committed comparison reference and MUST NOT be represented as the commit of
candidate bytes. For a complete reference, compare the full union of candidate
and reference payload paths: missing, extra or different files cause exit 1.
An absent/unreadable reference manifest or an internally incomplete/corrupt
reference is unavailable (exit 3), not ordinary drift. Working-tree comparisons
remain observations. No identity of a drifted candidate is proof it was committed.


Thus a payload can be generated from source commit C, committed in C2, and checked
at C2 without embedding a prediction of C2's hash. If authoritative bytes are
unchanged, the content identity remains the same; the command's provenance reports
C2. A later SIDX service binds `index_commit` to the actual ingested projection
commit at its transport boundary. Working-tree mode uses null committed source/
projection identities and is explicitly an observation. This model MUST NOT be
used to relabel a dirty bundle as committed evidence.

`check` compares inherited payload files read from the selected commit against
regenerated payloads. It does not compare timestamped run envelopes. Reference-bundle unavailability as defined above is exit 3; byte differences are exit 1. `scan` writes a validated
candidate set to a new directory and atomically switches the selected bundle
pointer only after all files validate; readers pin the old or new complete set.
A failed write/switch leaves the old selection usable. Filesystems lacking a
supported atomic publication method fail safely instead of falling back to
partial overwrite. Cross-platform acceptance of that mechanism remains a runtime
witness.

Core commands MUST run offline with only their declared package dependencies.
JSON output MUST have a versioned envelope; progress messages MUST not corrupt
it. Repeated scans of identical declared inputs MUST emit identical projection
bytes regardless of directory enumeration order or host timezone. Timestamped
run observations MUST be outside content-derived projection identity.

An explicit emission command MUST validate the complete candidate bundle before
making it current. A partial write/failure MUST leave the prior usable bundle
available and MUST NOT report success. No command may silently rewrite source
specifications, acknowledgments or accepted diagnostic baselines.

## §7 Git and Submodule Provenance [Normative]

The owner-approved [submodule observation contract](SBCT-01-SUBMODULE-OBSERVATIONS.md)
revision 0.1.3 extends working-tree mode with observation-set version 1 and CLI
version 2. Its identity, ownership, failure and dirty-state rules are normative
for that extension. Existing single-repository and committed version-1 behavior
remains unchanged.


A committed scan MUST identify each source's owning repository and exact commit.
For included submodules, the parent commit, mount path and recorded child commit
MUST be retained together. History MUST be read from that child repository.
An uninitialized, dirty or mismatched child MUST prevent a clean committed
claim; explicit working-tree mode MAY inspect it but MUST label its observation
and keep it out of committed-history evidence.

Missing history MUST produce the appropriate unavailable/partial confidence,
not parent-history substitution or reconstruction by replaying today's parser
over old Markdown. Including a dependency's documents and resolving its
identifiers are distinct capabilities. Cross-repository resolution MUST follow
SBCT-05 and MUST not be enabled merely by discovering a submodule.

## §8 Baseline and Remaining Approval Inputs

### Proposed coherent source candidate

Propose immutable source commit `751ffe62027a3030bc989d22f5c2f759234064dc` as the
reconciliation/extraction candidate. The following exact objects were inspected;
this is neither an approved extraction nor a claim about the newest branch head.

| Role | Candidate revision / Git blob |
|---|---|
| SBC concepts | 0.15.0 / `397824d5d057c368d0fe970d430e7ffb49706f77` |
| SBC addenda | A 0.4.0; B 0.2.0; C 0.12.0; D 0.7.0, all from the same source commit |
| SIDX concepts | 0.3.0 / `27f2c598abbc6149577ba14afcace114bcf3e1b2` |
| SIDX corpus/location phase | 0.10.0 / `2a01a52959f9546dc8a9ab79fb4d76523751dae6` |
| Scanner | `551c0ab7d70f82ad9e6fdfd99ef57a1ff78aeabb` |
| Location helpers | `31217a012c99785cd0bda3cae3a3d9feb3cf33d5` |
| Suspicion helpers | `d4da35b954285f757e03add62c5087765a754b88` |

The installed SBC snapshot is still concepts 0.11.0. The candidate's stable-term,
gate and non-goal grammar addresses that mismatch; the whole addendum set must
be reconciled, not just the concepts header. Candidate producer code already
contains stable-gate parsing. Local edits and old positional projection behavior
are not silently carried into this candidate. Preserve them as separate reviewed
patches and retain immutable historical evidence.

The candidate location and suspicion helpers still invoke Git subprocesses;
extract their semantics through the pure-Python provider boundary before claiming
portability. The candidate SIDX-06A header explicitly retains execution-evidence
gates, so ratified source does not prove producer conformance. Consumer-specific
origin inventory and patch reconciliation are maintained outside this family.

### Proposed Git provider and bounded evidence

Propose Dulwich `1.2.15`, universal `py3-none-any` wheel only, with urllib3
`2.8.0` and (Python <3.12) typing_extensions `4.16.0`, no extras. The
[provider audit](SBCT-01-PROVIDER-AUDIT.md) records exact artifact hashes and
bounded inspection results. Native platform wheels do not satisfy this contract.
Use artifact hashes to select the approved pure wheel: an ordinary unqualified
`pip install dulwich` is not the specified installation path.

The audit found no native binary members in these wheels. A Python 3.14.6
isolated read-only probe read repository commits/trees and a staged gitlink with
process/network calls rejected. This proves only those operations in that
environment; it does not prove Windows/non-Windows installation acceptance,
all supported Python versions, dirty detection, pack/history variants or full
submodule fixtures. Do not mark `GATE-101` or `GATE-104` passed from this audit.

### Review-ready example

This is a parseable example shape, not a runnable fixture or an approved manifest.

```toml
schema_version = 1
repository_id = "example-repository"
repository_root = "."
source_roots = ["docs/specs"]
exclude = []
registry_paths = []
output_root = ".sbc/index"
tracked_ref = "HEAD"
mode = "committed"
capabilities = ["scan", "check"]
authority_manifest = "docs/specs/authority.json"
submodules = []
```

### Prepared `GATE-106` review package

The [phase review packet](SBCT-01-REVIEW.md) records the authority reconciliation,
license decision, exact schema/examples and golden reference evidence. BSD-3-Clause
was selected by Ira Abbott for first-party tooling and documentation on 2026-09-19;
[LICENSE](LICENSE) carries the notice. Dependency and third-party notices retain
their own licenses; this decision does not relicense them.

The complete proposed source set is the pinned candidate above plus the separately
hashed operational metadata correction; normative source bytes are unchanged by
that correction. The review artifact preserves local Document IDs and distinguishes
base blobs from proposed patched bytes. Applying/publishing the dependency update
and assigning its new Git commit remain subsequent repository work, not a hidden
prerequisite for recording this content-exact pre-ratification decision.

Five [golden reference cases](evidence/sbct-01-golden-vectors.json) were generated
by the exact pinned producer, validated with its bundle validator, and repeated
byte-for-byte. They cover empty input, stable IDs, gate checked-state changes,
malformed gate fallback and ambiguous duplicate invariants. They are current
synthetic fixtures, not recreated historical acceptance evidence.

The owner approved the content-exact baseline, §5/§6 contracts, pure-wheel
dependency selection and this phase through explicit ratification recorded in §15. No new
unresolved schema value is delegated to an implementer. Runtime matrix, history,
submodule and publication-atomicity tests remain implementation acceptance; the
reference vectors alone do not pass `GATE-101` through `GATE-105`.

## §9 Invariant Application [Normative]

The implementation MUST satisfy the four parent invariants cited in §0 through
the witnesses below. Those definitions MUST NOT be duplicated here.

## §10 Reconciliation [Normative]

Existing scan/location/suspicion helpers MUST be extracted or wrapped, not
reimplemented independently. The existing committed projection schema MUST
remain compatible unless its owner amends it. This phase owns a runtime
configuration envelope, not a new authored SBC object kind.

## §11 Non-Goals

1. `NONGOAL-101` — **Implicit dependency installation.** Scanning MUST NOT clone, update submodules, install packages, or execute repository hooks automatically.
2. `NONGOAL-102` — **Remote evidence acquisition.** Credentialed acquisition MUST remain a host operation outside the offline scanner.

## §12 Acceptance [Normative]

A conforming SBCT repository core MUST pass §5–§7 and §9–§10, with these witnesses:

- [ ] `GATE-101` — A fresh unrelated fixture repository MUST scan/check offline in an environment without Django, consumer applications or credentials; the import/dependency audit MUST confirm that boundary.
- [ ] `GATE-102` — Empty-existing roots MUST succeed; missing roots, bad configuration, escaping paths and symlinks MUST fail without out-of-scope reads or source mutations.
- [ ] `GATE-103` — Repeated emission MUST match byte-for-byte; a source change MUST cause nonwriting `check` to fail; interrupted emission MUST preserve the previous bundle.
- [ ] `GATE-104` — A parent/child Git fixture MUST use the pinned child history; missing, dirty and different child revisions MUST not be reported as a clean parent snapshot.
- [ ] `GATE-105` — Golden vectors from the selected original scanner MUST match portable output; every intentional difference MUST have an owning specification change.
- [x] `GATE-106` — Owner MUST approve the exact schema, CLI/error contract and baseline, then record ratification before supporting code is derived.

### Named witness specifications [Normative]

These cases MUST be specified for review now and executed only at their
applicable acceptance stage. They are not claims that tests already exist.

| Witness | Positive case | Negative case |
|---|---|---|
| `W-101-P` / `W-101-N` | An ordinary-user Python environment installs only pure-Python PyPI dependencies, then scans an offline fixture without native build tools or a Git executable. | Import/dependency audit rejects native extension wheels, transitive compiled dependencies, elevated installation, external executables or runtime service requirements. |
| `W-102-P` / `W-102-N` | Committed results retain repository, revision and evidence; a dirty report is labeled as an observation. | A dirty or mismatched-child observation is rejected as a clean committed snapshot. |
| `W-103-P` / `W-103-N` | A parent/child fixture resolves history in the child at the parent gitlink pin. | Missing child history is unavailable; resolution never fabricates a parent-owned path or substitutes the child head. |

## §13 Files Cited

[SBCT-00](SBCT-00-CONCEPTS.md), [SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md),
[SBCT-05](SBCT-05-INTERLOCK.md), [SIDX-06A](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-06A-CORPUS-AND-LOCATION-PROJECTION.md),
and [provider audit](SBCT-01-PROVIDER-AUDIT.md).

## §14 Unblocks

SBCT-02 semantic extraction and repository fixtures for all other phases.

## §15 Change Log

### 0.1.0 — 2026-09-18 — drafted

**Author:** Codex (draft author)
**Change kind:** scope
**Touches:** SBCT-01
**Commits:** none
**Summary:** Defines the offline repository core and explicit Git ownership boundary.

#### Rationale

Considered and rejected: copying the monorepo scan roots, silently fetching
missing children, and using parent Git history for submodule files. Deliberately
unchanged: SBC grammar, committed diagnostic meaning and historical evidence.

### 0.2.0 — 2026-09-18 — owner-directed draft revision

**Author:** Codex
**Change kind:** scope
**Touches:** SBCT-01; parent INV-SBCT-3 and conformance boundaries
**Commits:** none
**Summary:** Incorporates accepted standalone conformance and explicit decision
closure; expands the example to MCP OAuth and separates consumer-specific
adoption from the portable contract. This is not family or phase ratification.

### 0.3.0 — 2026-09-19 — ratification package prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-01
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
**Touches:** SBCT-01
**Commits:** none
**Summary:** Recognizes parent ratification and prepares concrete candidate
contracts and remaining prerequisites in §8. Child ratification and acceptance
are not claimed; all implementation gates remain unchecked.

### 0.6.0 — 2026-09-19 — configuration and baseline review draft

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-01
**Commits:** none
**Summary:** Supplies a complete proposed TOML key set, deterministic CLI/error
contract, exact source candidate and bounded pure-wheel provider evidence.
Remaining authority, license and profile-schema decisions are explicit at
GATE-106. No phase ratification, extraction or supporting implementation occurs.

### 0.7.0 — 2026-09-19 — pre-ratification evidence and license decision

**Author:** Codex (recorder)
**Decision authority:** Ira Abbott selected BSD-3-Clause for first-party code/docs
**Change kind:** clarification
**Touches:** SBCT-01
**Commits:** none
**Summary:** Completes proposed manifest/envelope shapes and non-self-referential
projection identity; records exact reconciliation artifacts and five reproducible
reference cases. The license decision is accepted; phase ratification and runtime
acceptance are not inferred.

### 0.7.1 — 2026-09-19 — RATIFIED

**Ratifier:** Ira Abbott
**Authority:** Explicit owner instruction: "SBCT-01 is RATIFIED"
**Recorded by:** Codex
**Change kind:** clarification
**Touches:** SBCT-01
**Commits:** none
**Decision:** Ratifies revision 0.7.0's configuration/CLI, manifest and identity
contracts, content-exact source baseline with its separately identified operational
metadata correction, pure-wheel provider selection and first-party BSD-3-Clause
license. Revision 0.7.1 records the act without changing those contracts.
**Review evidence:** Limited closure review found no material blocker; 13 schema
checks and five repeatable golden reference cases are recorded in SBCT-01-REVIEW.
GATE-106 is complete as an owner specification approval; GATE-101 through GATE-105
remain unchecked runtime/implementation acceptance gates.
**Unblocks:** Governed SBCT-01 implementation planning and SBCT-02 interface and
semantic-extraction review. Actual extraction must retain approved source/patch
provenance. Child phase ratification, live submodule changes, publication and
production deployment are not implied by this act.

### 0.8.0 - 2026-09-21 - approved console host amendment

**Decision authority:** Ira Abbott, explicit instruction: "explicit --host PATH, with no implicit discovery or approval inference. APPROVED".
**Change kind:** extension
**Touches:** SBCT-01 configuration host boundary and CLI options.
**Decision:** Approves the explicit data-only console binding, version-1 schema, exact configuration matching and no implicit discovery or approval inference. Repository TOML remains unchanged. The in-process host remains available; conflicting mechanisms reject.
**Unblocks:** Console binding implementation and validation witnesses. No particular host registration, baseline, runtime gate or release is approved by this amendment.


### 0.9.0 — 2026-09-23 — Approved submodule observation wire extension

**Authority:** Ira Abbott, "proceed as recomended" accepting the wire review packet.
**Decision:** Incorporates SBCT-01-OBSERVATIONS 0.1.2: local dirty-state scope,
separate observation-context digest, version-2 envelope, explicit unavailable and
blocked descendants, and no partial aggregate publication. The previously accepted
immediate-parent observed-HEAD recursion and known-work-in-progress interpretation
remain in force. Implementation is unblocked; runtime gates and release remain open.

### 0.9.1 — 2026-09-25 — Incomplete participant evidence

**Authority:** Ira Abbott, "Approve the bounded amendment."
**Decision:** Incorporates SBCT-01-OBSERVATIONS 0.1.3 and the
[incomplete evidence review](SBCT-01-INCOMPLETE-OBSERVATION-REVIEW.md).
An available participant in an incomplete observation may retain known Git HEAD
context without invented checkout state or corpus evidence. Complete observations
still require clean/dirty state and a corpus hash for every participant. Incomplete
results remain exit 3 with null selection/result and no publication. The review
records the rationale and rejected alternatives. No runtime gate or release is approved.
