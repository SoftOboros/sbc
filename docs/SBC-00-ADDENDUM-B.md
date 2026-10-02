# SBC-00-ADDENDUM-B — ERRATA.md Schema and Injection Template

**Document ID:** SBC-00-ADDENDUM-B
**Status:** RATIFIED AMENDMENT — exact condition-verification packet accepted 2026-09-13; implementation remains outstanding
**Revision:** 0.4.0
**Date:** 2026-09-13
**Parent:** `docs/SBC-00-CONCEPTS.md`
**Canonical path:** `docs/SBC-00-ADDENDUM-B.md`
**See also:** `docs/SBC-00-ADDENDUM-A.md` (operational context injection)

---

## §0 Purpose

This addendum owns two things deferred from `SBC-00-CONCEPTS.md`:

1. The **`ErrataStatus` frozen enum** — the four-value lifecycle legend for every entry in a
   family's `ERRATA.md`.  Deferred from the concepts doc because it is operational (agents read
   it in `ERRATA.md` on every session) rather than normative (no code path is gated against it
   directly).

2. The **`ERRATA.md` file template** — the verbatim shape a new initiative family copies when
   activating SBC-INV-10.  The template is the artifact; this addendum is the spec for that
   artifact.

The normative rules governing `ERRATA.md` (permanence, location, stealth-revert obligation)
live in `SBC-00-CONCEPTS.md` SBC-INV-7 and SBC-INV-10.  This addendum does not restate them;
it instantiates them into a copyable shape.

---

## §1 Frozen Enum — `ErrataStatus` [Normative]

The lifecycle legend for every entry in a family's `ERRATA.md`.

| Icon | Value | Meaning |
|---|---|---|
| 🟢 | `resolved` | Root-caused and fixed; resolving commit SHA and verification evidence recorded. |
| 🟡 | `diagnosed` | Root cause known; fix prescription clear; no longer needs user input to proceed. |
| 🔴 | `open` | Undiagnosed or unresolved; appears in the Open Questions list. |
| ⚪ | `deviation-pending-ratification` | A deviation from ratified spec (including a structurally-necessary revert) awaiting ratification; appears in the Open Questions list. |

**Lifecycle rules:**

- An entry enters at 🔴 (undiagnosed) or ⚪ (known deviation).
- ⚪ → 🟡 or 🟢 once the deviation is ratified via §15 amendment in the affected phase doc.
- 🔴 → 🟡 once root cause is known.
- 🟡 → 🟢 once the fix lands and verification evidence is recorded.
- **Entries are permanent.**  A 🟢 entry stays in the log; status transitions, the entry is
  never deleted.  The log is institutional memory, not a queue.
- A question leaves the Open Questions list when its entry reaches 🟢 or 🟡.

**Registration policy: Standards Action.**  Adding, removing, or renaming a value requires a
§4 amendment to this addendum and a ratification session.

---

### §1.1 Assessment and disposition of exact members [Normative]

An erratum MAY retain append-only assessments and human dispositions of exact
members. This does not transition `ErrataStatus`. `resolved` continues to require
a landed fix and verification. Acceptance of an unrepaired exception MUST NOT
be represented as repair, a completed gate, or a C6 clearing.

The following closed values have registration policy Standards Action:

| Field | Values | Meaning |
|---|---|---|
| `applicability` | `applicable`, `not_applicable`, `undetermined` | Whether the named rule governed the named act. |
| `obligation` | `required`, `none`, `undetermined` | Present work required by an identified authority. |
| `effect` | `retain_open`, `accept_exception`, `record_non_applicability` | Operational disposition of one exact member, independent of its native state. |
| `action` | `assess`, `supersede`, `withdraw` | Append a decision, explicitly replace named decisions, or withdraw named decisions. |

Missing or unsupported applicability/obligation evidence means `undetermined`.
Non-applicability requires the governing document and revision, adoption boundary,
the act and evidence of their ordering. Ancestry and recorded authority govern;
a calendar-date tie supplies no ordering. Lack of formal ratification alone is
not proof that an operational rule did not exist. Modern checker output alone
does not establish a historical violation.

`record_non_applicability` requires `not_applicable` and positive supporting
evidence; it does not remove an independent current roadmap, errata, gate, or
migration obligation. `accept_exception` requires an applicable understood
obligation or an explicitly bounded evidence limitation; its rationale MUST
state why repair is unavailable or inappropriate. Accepting uncertainty leaves
`applicability: undetermined` visible. Conditions and obligations outside the
exact accepted condition remain actionable. No effect is an exception to the
rules for invalid evidence carriers, missing identities, or ambiguous references.

#### §1.1.1 Authored record grammar

Under the owning erratum's `### Assessments and dispositions` heading, each
record is exactly one fenced `sbc-review-v1` JSON object. Commentary outside the
fence is informative. Duplicate JSON keys, unknown fields, invalid UTF-8,
non-NFC strings, lone surrogates, floats, and duplicate set members are invalid.
The record has exactly these fields:

| Field | Type and constraint |
|---|---|
| `schema` | Literal `sbc-review-v1`. |
| `id` | Local decision identity from parent §4.1; containing erratum must match. |
| `action` | Closed value above. |
| `predecessors` | Sorted array of decision IDs in the same erratum; empty for `assess`, nonempty for `supersede`/`withdraw`. |
| `proposal` | `{commit, path, sha256}` naming an immutable exact proposal blob. |
| `members_sha256` | SHA-256 of the canonical `members` array. |
| `members` | Nonempty array ordered by `member_id`; exact member shape below. |
| `authority` | `{issuer, grant_id, source_uri, source_sha256}`; no field is itself proof of authority. |
| `rationale` | Nonempty human-reviewable text. |

Each member has exactly `{member_id, subject, rule, act, applicability,
applicability_evidence, obligation, obligation_evidence, effect,
accepted_limitation, conditions, exclusions, rationale}`. `member_id` is a
positive integer unique in that decision. `subject` and `rule` use ADDENDUM-C
§7.1. `act` and all evidence-array entries are `{commit, path, sha256, locator}`,
where `locator` is a nonempty source-relative locator string. Evidence arrays
are ordered by `(commit, path, sha256, locator)` and have no duplicate tuples.
All Git commits are full lowercase 40-hex IDs; all SHA-256 values are lowercase
64-hex. Repository paths are normalized relative POSIX paths with no empty,
dot, parent, absolute, backslash, or symlink component. Digests bind raw blob
bytes except where canonical JSON is explicitly named. Canonical JSON uses
SIDX-06E §3.1's existing encoding without a new serializer contract.

`accepted_limitation` is null except for `accept_exception`, where it is
nonempty text specifying the bounded obligation or evidence limitation.
`exclusions` is an ordered array of nonempty strings. `conditions` is an array
of `{subject, evidence, text}` ordered by canonical bytes, naming continuing
work; `evidence` uses the same evidence-reference array. The applicability,
obligation, and effect fields use the enums above. Rationale is nonempty.
`required` needs nonempty obligation evidence. `none` also needs positive
evidence; absence of an obligation citation cannot establish it. Undetermined
evidence MAY be empty but its rationale MUST state the limitation.

The immutable proposal MUST contain the exact canonical `members` array.
Its digest and the decision's `members_sha256` MUST both verify. A human MAY
approve the complete enumerated batch; wildcards, group titles, count-only
approvals, and an instruction covering future matches cannot bind members.

#### §1.1.2 Authority, replay, and conflict

A valid decision additionally requires a receipt independently admitted by the
SIDX-06D §7.6 trusted approval profile, binding the canonical SHA-256 of the
entire record, the proposal/member digests, issuer, grant, and approval source.
Repository author strings, copied conversation text, an agent's assertion,
Git author identity, and diagnostic baselines supply no such trust. Historical
non-applicability is an authorized assessment, not an agent's default classifier.

Identical ID and canonical body replay idempotently. One ID with different
bodies invalidates all versions for effects. Incompatible concurrent effective
decisions on one member require an authorized successor explicitly naming all
predecessors; no timestamp, parser order, or lexical-ID tie-break applies.
`supersede` replaces only the member scope it explicitly binds; other members
of a predecessor persist. `withdraw` binds the exact predecessor members and
ends their effect, without applying its repeated assessment fields anew.
Predecessor cycles, missing predecessors, scope expansion, or invalid receipts
have no operational effect and remain visible for review. Old records MUST NOT
be edited or deleted; all changes append. Partial dispositions leave the
remaining erratum members and conditions actionable.

### §1.2 Recorded verification of continuing conditions [Normative]

This profile permits a human authority to confirm that retained evidence
verifies the whole work named by one exact continuing condition. It records
that confirmation; the dashboard does not execute verification, infer semantic
coverage from prose, or certify deployment. An exception approval or removal
of an obligation MUST NOT be presented as this confirmation.

The only verification profile is `owner-recorded-v1`. Its human verifier MUST
review the full condition, every required acceptance clause and environment,
the exact tested revision, evidence, and before/after subject mapping. A partial
test result, source hash, checked gate, or nonempty verification link alone
does not establish completion. A failed revalidation known to the verifier
MUST be recorded by an authorized withdrawal before continued reliance on the
prior confirmation. This is a recorded-evidence system, not automatic monitoring.
Additional machine-execution profiles require another Standards Action.

#### §1.2.1 Exact authored record

Each owning errata source MAY have one optional companion at its exact
repository-relative path plus `.condition-verification.md`. This is metadata
owned by that same errata source, not another errata log. Its exact level-two
heading `## Condition verification for <canonical-errata-id>` identifies one
uniquely defined erratum in that source; the angle-bracket term is a grammar
metavariable. Each following complete `sbc-condition-verification-v1` JSON fence
is one record for that owner. Other headings end that container; examples and
ordinary code are not records. At most one such heading per owner is permitted
in a companion; duplicate owner containers make their candidates invalid. Companion headings do not define SpecObjects.
Keeping the new confirmation outside the verified source avoids a self-referential
source hash when the condition names work in the original errata document.
The record has exactly:
`{schema, decision_id, decision_sha256, member_id, condition_sha256,
action, predecessors, verification, authority, rationale}`.

The schema value is the fence label. `decision_id` imports §1.1; the owning
erratum MUST match. `decision_sha256` binds the complete canonical parent
decision, `member_id` its exact member, and `condition_sha256` the canonical
entire `{subject, evidence, text}` condition. None of the parent bytes is edited.
`authority` imports §1.1's exact four-field shape; it is admitted only by
SIDX-06D §7.7, not by a disposition receipt. `rationale` is nonempty text.

`action` is `verify` or `withdraw`. `predecessors` is an ascending, unique
array of canonical verification-record SHA-256 values for the same exact
decision/member/condition tuple. It is empty for initial verification and
nonempty for replacement or withdrawal. `withdraw` has `verification: null`.
`verify` has exactly:
`{profile, before, after, tested_commit, scope, checks, source_scope}`.

`profile` is `owner-recorded-v1`; `before` and `after` are complete
ADDENDUM-C §7.1 subjects subject to §7.2. `tested_commit` is a full Git commit
at or after the after snapshot and at or before receipt adoption on the retained
first-parent chain. It names the tested revision independently of the earlier
source-state transition. `scope` MUST equal the whole parent
condition's `text` byte-for-byte. `checks` is a nonempty array of exactly
`{criterion, environment, evidence}`, sorted uniquely by canonical bytes.
Criterion and environment are nonempty strings; evidence is a nonempty §1.1
reference array. The human confirmation covers all required criteria and
environments collectively, with no omitted continuing requirement. Parsing
these strings does not prove coverage.

`source_scope` is a nonempty evidence-reference array naming every repository
source input needed to retain the verification claim, including both the
completed subject's source document and any code, configuration, test, and
dependency source on which the result depends. Every scope reference's commit
equals `tested_commit`; its locator names the relevant source, while
its SHA-256 binds the whole blob. One path has exactly one tuple. The human
verifier attests scope completeness. A material external/environment change
requires withdrawal and a new confirmation; this profile cannot detect an
unrecorded external change. Check evidence may be recorded later than the tested
snapshot but MUST precede or equal the verification receipt's adoption commit.
It MUST explicitly support the tested revision `tested_commit`.
Evidence references import exact bytes and ordering from §1.1; no new serializer
or source-path grammar is introduced.

All §1.1 strict JSON, Unicode, bounds, hash, reference, and duplicate rejection
rules apply. The canonical record digest excludes its fence and surrounding
prose. It never includes its own digest as a field. A copied record has the
same digest and replays idempotently; its retained candidate sites remain
available. Changed bytes make a different record, not an in-place amendment.

#### §1.2.2 Succession and results

Only independently admitted records can affect results. Every predecessor
must exist, be admitted for the same tuple, and first appear before its
successor on the retained first-parent chain. Cycles, missing predecessors,
scope expansion, and changed parent bindings have no effect. A successor
replaces only its explicitly named predecessors. Concurrent terminal records
require an authorized successor naming all of them; parser order, timestamps,
and digest ordering MUST NOT select a winner. A withdrawal is a terminal
record that supplies no satisfaction claim. A subsequent new verification
names that withdrawal as a predecessor. Old records and receipts remain.

The closed derived `condition_result` values are `recorded_satisfied`,
`outstanding`, and `undetermined`. `recorded_satisfied` requires one effective
terminal verification plus ADDENDUM-C §7.2's validity at the selected snapshot.
It means recorded human-confirmed verification with mechanically checked
binding, never fresh execution or an accepted unrepaired exception.
`outstanding` means the condition is effective and independently bound but
has no usable completion confirmation, including an effective withdrawal.
Unavailable required authority/source/history, unsupported transition, ambiguity,
or concurrent independently admitted terminal records yield `undetermined`.
Invalid/unadmitted candidates confer no effect and do not override an otherwise
usable verification. With no usable verification, an invalid candidate bound to
that tuple makes the result undetermined.
A valid successor explicitly resolving those terminal conflicts can restore a
determinate result. A malformed unbound candidate cannot invent a condition
tuple; it remains owning-erratum classification work and cannot invalidate
unrelated tuples. Registration policy for all values/shapes in §1.2 is
Standards Action.

Neither result changes the condition's original authored array, parent approval,
ErrataStatus, native checked state, independent work, or C6. An authorized parent
successor that removes a condition remains an obligation change under §1.1,
with the old verification retained as history rather than transferred to a new
decision or to recurring work.

---

## §2 ERRATA vs. Adjacent Artifacts [Normative]

Two boundaries that MUST be maintained explicitly:

**ERRATA vs. issue tracker.**  The issue tracker is the outward-facing intake surface.
Once an issue is *accepted* (root cause identified or deviation scope agreed), the canonical
record moves into the family's `ERRATA.md`.  Never-accepted reports (duplicates, won't-fix,
out-of-scope) stay in the tracker only.  The log is curated, not a mirror of every report.

**ERRATA vs. phase §15.**  A §15 amendment changes spec text.  An errata entry records the
*evidence* that motivated the amendment, or records a bug that did not require a spec amendment.
Both MAY reference each other; neither replaces the other.

- Resolution edits a normative section of a `-NN-CONCEPTS.md` → §15 entry is canonical;
  errata entry cites the §15.
- Resolution edits code / tests / non-normative docs → errata entry is canonical;
  §15 entry cites the errata id if a spec touch was incidental.

---

## §3 ERRATA.md File Template

Copy everything between the `<!-- ERRATA-TEMPLATE-BEGIN -->` and `<!-- ERRATA-TEMPLATE-END -->`
markers into `<INITIATIVE_DOCS_ROOT>/<FAMILY>/ERRATA.md`.  Replace every `<PLACEHOLDER>`.
Delete the "How to add" footer if you prefer a separate contributing guide.

---

<!-- ERRATA-TEMPLATE-BEGIN -->

# ERRATA — `<FAMILY>`

**Family:** `<FAMILY>`
**Phase docs:** `<INITIATIVE_DOCS_ROOT>/<FAMILY>/`
**Governed by:** `docs/SBC-00-CONCEPTS.md` SBC-INV-7, SBC-INV-10; `docs/SBC-00-ADDENDUM-B.md`

**Status legend**

| Icon | Meaning |
|---|---|
| 🟢 | resolved — fix landed, verification evidence recorded |
| 🟡 | diagnosed — root cause known, fix prescription clear |
| 🔴 | open — undiagnosed or unresolved |
| ⚪ | deviation-pending-ratification — awaiting §15 amendment |

---

## Open Questions

*One line per ⚪ or 🔴 entry; remove when entry reaches 🟢 or 🟡.*

| EOQ id | Errata | Ask |
|---|---|---|
| *(none)* | — | — |

---

## Index

| Id | Title | Status | Phase | First seen |
|---|---|---|---|---|
| *(none)* | — | — | — | — |

---

<!-- ============================================================ -->
<!-- ENTRY TEMPLATE — copy this block for each new entry         -->
<!-- ============================================================ -->

<!--
## ERRATA-001 — <one-line title>

**Status:** 🔴 open
**First seen:** YYYY-MM-DD
**Owning phase:** `<INITIATIVE>-<NN>` (`<phase doc path>`)
**EOQ:** `EOQ-001-ERRATA-001` — <one-line open question>

### Symptom

<What the observer sees.  Pin to artifact path and line where possible.>

### Root cause

<Mechanism.  "Unknown" until diagnosed.>

### Fix

<Proposed location and minimal change sketch.  Resolving commit SHA once landed.>

### Verification

<How to confirm the fix is correct.  Evidence recorded once resolved.>

### Assessments and dispositions

Optional append-only records use ADDENDUM-B §1.1 verbatim. Omit this section
until an exact proposal and authority evidence exist. Accepted unrepaired
members retain their native repair status. Conditions remain outstanding unless
separate recorded verification satisfies ADDENDUM-B §1.2. Optional verification
records use that section's exact companion-file grammar and independent authority;
never edit an approved condition to append later evidence.

### Tracking

<Cross-references: related phase §15 entries, related EOQ ids, related commits.>
-->

<!-- ============================================================ -->

---

## How to add an entry

1. Assign the next monotonically-increasing `ERRATA-NNN` id.
2. If the entry is a deviation from ratified spec, set status ⚪ and file a §15 amendment in
   the affected phase doc in the same commit.  Cite `ERRATA-NNN` in the commit subject.
3. If the entry is a stealth revert (SBC-INV-7), the errata commit MUST land first, before
   the reverting fix commit.
4. Add a row to the Index table and, if status is ⚪ or 🔴, a row to Open Questions with a
   stable `EOQ-NNN-<ERRATA-id>` handle.
5. Entries are permanent.  On resolution: update status to 🟢, record the resolving commit SHA
   and verification evidence in the Fix and Verification fields, remove from Open Questions.
   Do not delete the entry.

<!-- ERRATA-TEMPLATE-END -->

---

## §4 Change Log

| Rev | Date | Author | Status | Summary |
|---|---|---|---|---|
| 0.1.0 | 2026-05-31 | I. Abbott | DRAFT | Initial draft; `ErrataStatus` frozen here (deferred from SBC-00-CONCEPTS); ERRATA vs §15 / tracker boundary; copyable file template |
| 0.2.0 | 2026-07-31 | I. Abbott (ratifier) | **Ratified** | Ratification only — no content change. Closes the gap recorded in ERRATA-004, where this addendum sat DRAFT while `ErrataStatus` and the ERRATA/§15 boundary were in active use across 28 errata logs and 220 entries. Ratified at existing content. **No amendment follows:** the ERRATA↔§15 boundary (SBC-INV-13) and the four-value `ErrataStatus` lifecycle are unaffected by the `SBC-00-CONCEPTS.md` 0.7.0 object-model amendment — an `errata` is one `ObjectKind` among twelve and its lifecycle rules were already the most fully specified surface in the family. Recording that nothing changed here is itself the finding: the object model generalised over the existing errata shape without modifying it. |

### 0.3.0 — 2026-09-05 — ratified ERRATA-015 amendment

**Author:** Ira Abbott (ratifier); OpenAI Codex (drafting and recording)
**Change kind:** semantic
**Touches:** SBC-00-ADDENDUM-B
**Summary:** Define separate historical applicability, current obligation, exact member records, and trusted forward dispositions. The owner ratified this exact coordinated packet in task `01a06eee-bae3-7911-9198-adfae97256f1` on September 5, 2026. Accepted patch SHA-256: `220d77faff10b8132768a2d0a19ec7e099decf605ad72dd7f57a174f40e69de1`. This records specification ratification, not implementation, clearance, or deployment.

#### Rationale

The owner accepted decision-packet version 1 and subsequently ratified this exact
amendment packet on September 5, 2026. This amendment supplies the reserved contract. Treating every old
missing process field as a present violation, equating acceptance with repair,
and hiding diagnostics by client arithmetic were considered and rejected.
The native repair lifecycle, retained historical evidence, C6 clearings, and
C11/C12 response meanings deliberately do not change. This ratification authorizes deriving implementation from the coordinated
amendment after the specification commit boundary.

### 0.4.0 — 2026-09-13 — ratified condition-verification amendment

**Author:** Ira Abbott (ratifier); OpenAI Codex (drafting and recording)
**Change kind:** semantic
**Touches:** SBC-00-ADDENDUM-B
**Summary:** Specify §1.2's part of recorded condition verification under
SBC ERRATA-015. The owner ratified this exact packet and its linked digest
manifest on September 13, 2026 in task `01a06eee-bae3-7911-9198-adfae97256f1`.
Accepted packet commit: `7645b24614f181b64ac254b7028367b9f26b6842`.
Accepted patch SHA-256: `8d61a050dd6ed81ee8ec41cdf3829f020185b4e132d1419dbad12df88fb1cb39`.
Accepted manifest SHA-256: `fbb41f409f5445b8d7b53a09dc35fb657520e3c275adc94d1b6624831a8832fb`.
This ratifies the specification; no concrete verification record, approval pin,
native-state change, implementation, or deployment is asserted.

#### Rationale

Independent condition binding does not admit later verification or establish a
before/after completion transition. The ratified coordinated amendment supplies those
contracts while preserving approved obligation changes as a distinct action.
Automatic interpretation of arbitrary test logs, reuse of exception authority,
editing approved condition evidence, and inference from absence were rejected.
The initial profile records human-confirmed evidence; machine-execution profiles
remain unregistered. Exact-text ratification precedes implementation.
