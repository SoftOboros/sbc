# SBCT-01 — Explicit Console Host Binding Proposal

**Document ID:** SBCT-01-CONSOLE-HOST
**Status:** APPROVED — Ira Abbott, 2026-09-21; SBCT-01 0.8.0 amendment
**Revision:** 0.1.1
**Date:** 2026-09-21
**Owner:** Ira Abbott
**Parent:** [SBCT-01](SBCT-01-REPOSITORY-CORE.md), ratified base with approved amendment 0.8.0

## Purpose

The shared engine and explicit in-process host loader can scan, commit, check
and validate a fixture without application services. The default console cannot
yet construct that host: repository registrations, approval pins and family
routing are deliberately not inferred from repository content or environment.
This proposal supplies a data-only binding for a standalone console.

The existing implementation is recorded in
[host-loader evidence](evidence/sbct-01-host-loader-execution.json).
Its tests use synthetic approvals; they do not approve a release baseline.

## Owner decision

Ira Abbott approved this extension explicitly: "explicit --host PATH, with no
implicit discovery or approval inference. APPROVED". The version-1 JSON binding
below amends SBCT-01 §§5–6. Repository TOML remains unchanged. The
[schema](contracts/console-host.schema.json) and
[synthetic example](contracts/console-host.example.json) are part of this proposal.
The example's placeholder hashes are not approvals or usable baseline pins.

This decision authorizes implementing the binding parser and its witnesses.
It does not approve any particular host registration, source baseline, runtime
gate, backend, dashboard, release, or publication destination.

## Invocation

```text
sbc-tools scan --config PATH --host PATH [--format text|json]
sbc-tools check --config PATH --host PATH [--format text|json]
```

Both paths are explicit. `--host` is required for repository operations in the
default console; help and version need neither path. Repeated options, unknown
flags and missing required options follow the existing invocation error contract.
Trusted embedding applications can continue supplying the in-process loader;
combining that loader with `--host` is a conflicting invocation, not an override.

No current-directory search, user-profile default, environment variable, network
fetch, credential lookup, repository hook or content-selected Python import is
introduced. The JSON file is data, not an executable plugin.

## Binding and trust boundary

One binding file selects one registered root repository. The invoking host/operator
supplies it as trusted local input after obtaining the relevant owner approvals.
Passing `--host` selects those inputs; it does not ratify the documents they name.
Neither the binding parser nor the existing loader decides whether a person had
authority to approve a pin. Noninteractive production hosts retain their own
approval and access-control process around the same core.

| Binding field | Meaning |
|---|---|
| `schema_version` | Integer 1; unknown fields/versions reject. |
| `repository_id` | Root identity, present in `source_repositories`. |
| `source_repositories` | Explicit repository-ID to local-directory mapping for root and included children. |
| `authority_repositories` | Explicit repository-ID to local-directory mapping for separately pinned authority inputs. |
| `config_path` | Portable repository-relative path under the registered root. |
| `config_sha256` | Expected digest of the exact configuration bytes, including whitespace. |
| `tracked_branch` | Exact branch matching the configuration's explicit branch ref. |
| `profile_path`, `profile_sha256` | Committed profile evidence path and expected digest. |
| `patch_path` | Committed reviewed support-patch path. |
| `approved_authority_sha256` | Host-supplied expected authority-manifest digest; not an approval mechanism. |
| `approved_support_sha256` | Exact resulting digests for the three supported patched files. |
| `document_families` | Explicit document-path to family mapping covering the selected Markdown corpus exactly. |
| `archive_families` | Unique archive/member/family records; every inspected Markdown member needs a mapping. |
| `evidence_paths` | Explicit additional committed evidence inventory. |

Repository-directory values can be absolute or relative to the binding file's
parent directory; they are local filesystem paths, not URLs. All corpus/config/
profile/patch/member paths retain the existing portable relative-path grammar.
Duplicate JSON keys, duplicate archive/member pairs, conflicting repository IDs,
missing repositories and nonfinite JSON values reject. No path expands variables
or a home-directory shorthand.

The requested `--config` path must identify the registered root's `config_path`
before the configuration is read. Its bytes must match `config_sha256`; the
loader then passes those exact bytes to the existing configuration validator and
committed verifier. The hash is checked, never filled in from whatever file is
present. Committed configuration equality remains mandatory during execution.

The parser reads the binding once and copies its mappings. It must reject a
symlink/reparse binding file or configuration path; registered repository roots
remain explicit host choices. Local directory ownership is a host obligation,
not a claim of hostile-process isolation. Changes after loading do not mutate
the in-memory registration. A later invocation reads and validates anew.

## Family routing and identity

The binding carries routing data only; it does not infer a family from a vendor
directory, document prefix or production application. Existing exact-corpus
coverage checks still apply. Changing a routing assignment can change generated
payloads and their snapshot identity; it does not authorize a semantic rule fork.

Binding-file bytes, machine-specific absolute paths and comments about operator
approval are not added to semantic payloads or corpus identity. Existing committed
configuration/profile/authority/evidence bytes and generated payload hashes
continue to determine identity. Hosts needing an approval record in the corpus
can register its committed path through `evidence_paths`; the tool does not invent
or sign that record.

## Error and compatibility behavior

The existing envelope schema and exit meanings remain unchanged. Binding syntax,
schema, registration or configuration-hash mismatch maps to
`invalid_configuration` / exit 2. An invalid authority manifest maps to
`invalid_authority` / exit 2 at that validation boundary. Missing evidence maps to
exit 3; filesystem access failure maps to `io_failure` / exit 3. Other incomplete
execution failures retain exit 4. No raw exception, credential or machine path
is included in a safe error message.

This is a CLI extension requiring explicit amendment, not a silently accepted
extra TOML key. It does not expand implemented source modes: unsupported
working-tree execution must continue to reject rather than relabel a committed
operation. Existing flat-output migration and atomic-publication constraints
remain unchanged.

## Acceptance witnesses

1. Install the pure-Python distribution and its audited Git provider in an
   unrelated temporary repository. Run the console using only explicit binding
   and config paths, without Django, application services or credentials.
2. Scan, commit output, then check equality; compare payloads with the same
   in-process registration. Confirm identical semantic identities across two
   different absolute checkout paths with identical committed inputs.
3. Reject missing/duplicate flags, duplicate keys, extra schema fields, unknown
   versions, invalid path grammar, wrong config digest and incomplete routing.
4. Reject a mismatched config path before reading it; reject linked binding/config
   files. Confirm missing repositories, interrupted opens and construction failures
   close previously opened readers and preserve the existing selected output.
5. Confirm no auto-discovery, environment override, remote fetch or plugin import.
   Changing a supplied digest to match arbitrary bytes must not be reported as an
   owner approval. Verify safe JSON errors and failure precedence over findings.

## Amendment and implementation boundary

The owner decision is recorded in SBCT-01's change history and its CLI/host-input
boundary. That owner references this schema without duplicating semantic
definitions. The parser converts the data to `HostRegistration`; it does not
introduce a second verifier or scanner.

The approval is recorded in SBCT-01 0.8.0. The console has no implicit loader,
and all existing runtime gates retain their current status.
