# SBCT-01 submodule observation contract

**Document ID:** SBCT-01-OBSERVATIONS
**Revision:** 0.1.3
**Status:** APPROVED — Ira Abbott; incomplete-evidence amendment 2026-09-25, incorporated by SBCT-01 0.9.1.
**Date:** 2026-09-25

## Authority and scope

The owner agreed to the first-version boundaries: explicit registrations, separate
parent-recorded pins/observed HEADs/captured bytes, immediate-parent ownership,
change detection, null committed identities, and failure of the aggregate when a
required participant is unavailable. This records that approval without treating
this newly authored wire format as ratified. SBCT-01 remains 0.8.0; runtime gates
remain open. Interlock governance and cross-repository writes remain deferred.

## Approved wire boundary

Keep the existing version-1 CLI envelope and its committed `dependencies` unchanged.
Use CLI envelope version 2 for multi-repository working-tree commands: retain
the version-1 fields, change `schema_version` to 2, and add required `observation`.
It contains the separately versioned [observation set](contracts/observation-set.schema.json),
or null if configuration/authority failure prevents an observation. Version-2
working-tree selection has null source/projection commit IDs and an empty
`dependencies` array. Recorded gitlinks appear only in `observation.relations`.
Existing single-repository and committed commands continue emitting version 1.
The [draft version-2 envelope schema](contracts/cli-observation-envelope.schema.json)
and [illustrative example](contracts/cli-observation-envelope.example.json) make this
extension concrete. No runtime emits version 2 yet. Version-1 clients must reject unsupported versions.

## Registration and traversal

Reuse explicit host repository IDs, source mappings and mount allowlists. Do not
infer identity from `.gitmodules`, paths or URLs. Do not discover, initialize,
clone, fetch, update, or run hooks. Include only mounts intersecting configured
source scope; every included ancestor must be registered. Reject duplicate IDs,
conflicting ownership, cycles, unsafe paths and unregistered nested repositories.
A registered relation absent from the selected immediate-parent tree is invalid
configuration, not a newly inferred relationship from working `.gitmodules`.

For the root, resolve the explicitly configured reference once as baseline context.
For each child, record the gitlink from that immediate parent's selected context.
Capture the child's observed HEAD separately. For recursion, use the immediate
parent child's observed HEAD as the context for its child relations: observations
follow the checked-out composition, not an implied recursively clean pinned tree.
The outer relation still retains its original recorded pin, exposing divergence.
Staged gitlink edits do not replace recorded pins; they contribute dirty checkout
state. No working-tree change can rewrite an observed baseline relation.

## Observation fields and semantic validation

Participants are sorted by repository ID; each ID occurs once and is NFC text.
The root must occur once. Each other participant has exactly one incoming relation.
Relations are sorted by `(parent_repository_id, path)` and form one rooted acyclic
tree. Paths are immediate-parent-relative, safe POSIX paths, not flattened host paths.
These are semantic checks in addition to JSON Schema; JSON Schema alone is insufficient.

A participant's `observed_head` is contextual metadata, never a claim that captured
bytes equal that commit. `checkout_state` reports whole-checkout clean/dirty status
against that HEAD using local repository files and index state, treating registered
child mounts as boundaries. A child HEAD differing from its local parent gitlink
makes that parent dirty; dirtiness inside the child is reported on the child row
without recursively duplicating it into parent state. Captured corpus hashes
cover only selected source and required inputs; generated output is excluded.
Thus output changes can make a checkout dirty without changing captured corpus.

For an available parent, `parent_commit` is its selected context commit. For a
relation with evidence, `recorded_child_commit` is exactly its gitlink. `pin_state`
is `match` only if that pin equals the child's observed HEAD; otherwise `mismatch`.
Dirty is independent of match/mismatch. Unknown evidence uses null and `unavailable`,
never an all-zero hash or an invented clean state. If child HEAD/history cannot be
read, its availability is `unavailable_history`; absent checkout uses `missing_checkout`.
Unavailable participants have unknown checkout state and no corpus hash. Report all
required participants, including unavailable descendants, without opening an
unavailable ancestor's descendants. Those descendants use `blocked_by_ancestor`,
not an invented missing-checkout diagnosis. Their relation evidence remains
null/unavailable. Required pinned commit objects must also be available; an
observed HEAD alone cannot substitute for missing pinned history.

For an incomplete observation, an `available` participant MAY retain its known
HEAD while using unknown checkout state and a null corpus hash. Availability
describes required Git context, not completed checkout/corpus capture. Known
local evidence MAY be retained when actually acquired. A complete observation
MUST have clean/dirty state and a non-null corpus hash for every participant.
This bounded distinction is approved in the
[incomplete evidence review](SBCT-01-INCOMPLETE-OBSERVATION-REVIEW.md).

## Capture, identity and failure

Capture every participant with explicit owning repository ID and relative path.
Retain stable ordered byte inventories. Observe relevant refs, index/checkout state,
selected gitlinks and content before/after aggregate capture. Any detected change
rejects the aggregate as evidence unavailable (exit 3); no publication occurs.
This is bounded change detection, not a simultaneous filesystem snapshot or lock.

`complete` is true only when every required participant and relation is available
and stable. Dirty content and pin mismatch do not by themselves make it incomplete.
Required unavailable participants yield exit 3, `selection: null`, `result: null`,
and an incomplete observation set. No partial projection, successful empty corpus,
or pointer switch is permitted. Early configuration/authority errors use exit 2;
local IO failures use the existing safe IO error. Availability is evidence context,
not authorization or permission to expose a repository.

For a complete set, `selection_sha256` is SHA-256 of canonical UTF-8 JSON with sorted
keys, compact separators and final LF, of the observation object with that field
removed. Incomplete sets use null. This hash includes HEAD/pin/state context, so it
is distinct from the content-derived projection `snapshot_id`. Canonical source
records retain `(repository_id, relative_path, content_sha256)` and feed the existing
corpus hash. No timestamp or checkout absolute path enters either identity.
Example commit/corpus hashes are synthetic; the example selection digest is
computed and checked against those synthetic fields. It is not runtime evidence.

## Acceptance cases to implement

1. Clean matching child: preserve pin, observed HEAD and owning file identity.
2. Dirty matching child: inspect changed bytes; retain null committed identities.
3. Clean/dirty mismatched child: report mismatch independently of dirty state.
4. Missing checkout, missing child history and unreadable parent context: aggregate
   unavailable, no output publication, explicit unknown states.
5. Nested child with diverged parent HEAD: outer mismatch preserved; inner gitlink
   belongs to the observed immediate parent, not the root or original child pin.
6. Participant/ref/index/content changes during capture: reject without switching.
7. Excluded/unregistered/cyclic mounts and linked paths: no out-of-scope reads.
8. Identical captures with different enumeration order: identical selection digest.
9. Version-1 committed dependency behavior remains unchanged; malformed version-2
   states, false matches and incomplete-but-successful results reject.

## Next review

Nested recursion context is accepted. Review the remaining dirty-state scope,
digest and version-2 framing before implementing the extension. The runtime currently rejects submodule
observations, which remains safe during this contract preparation.


## Structural verification

The offline developer check `tools/tools/check_observation_contract.py` passes
three positive and eighteen negative cases. It verifies closed/versioned fields,
null committed identities, unavailable participant structure, incomplete-result
restrictions, and unsafe-path rejection. Graph ownership, digest correctness,
false-match detection and cross-repository runtime stability remain semantic
acceptance work; this structural check does not claim them.


## Owner disposition — 2026-09-23

The owner accepted the review point: nested relationships use the immediate
parent's observed HEAD while retaining its mismatch against the recorded pin.
The owner identified this as a known work-in-progress condition that will need
support from the indexing helpers later.

Treat the mismatch as visible observation evidence of work in progress, not a
clean pinned composition, an approval, or a reason by itself to block a complete
observation. Existing distinctions remain: dirty content is independent of pin
mismatch; unavailable required evidence prevents aggregate publication.

Future indexing helpers should surface the recorded pin, observed HEAD and
owning relation together so users can inspect and reconcile the work in progress.
This is follow-up work, not a claim that those helpers currently implement it.
It adds no new frozen SBC status, automatic clearance rule or permission to update
a gitlink. Exact wire framing was subsequently approved below; runtime acceptance remains open.


## Gate preparation — revision 0.1.2

The [wire approval packet](SBCT-01-OBSERVATION-WIRE-REVIEW.md) collects the three
remaining proposed decisions. This revision distinguishes descendants blocked by
an unavailable ancestor from checkouts actually observed missing, and makes local
dirty-state scope explicit. The existing accepted recursion/WIP decision is retained.
Approval of this packet would authorize the exact wire extension, not runtime
acceptance, an Interlock governance model, or automatic gitlink reconciliation.


## Wire amendment approval — 2026-09-23

The owner instructed "proceed as recomended" in response to the wire approval
packet's recommendation. This approves revision 0.1.2's dirty-state scope,
observation identity and version-2 framing, including blocked descendants and
aggregate failure on unavailable required evidence. SBCT-01 0.9.0 incorporates
this extension. Implementation is authorized; runtime gates remain open.
Historical draft/review wording above describes preparation before this approval.

### Incomplete evidence amendment — 2026-09-25

Ira Abbott explicitly approved the bounded amendment permitting known Git context
with unknown checkout state/null corpus in incomplete results. Revision 0.1.3
incorporates that decision; complete-result requirements and no-partial-publication
rules remain unchanged. SBCT-01 0.9.1 records the owning amendment.
