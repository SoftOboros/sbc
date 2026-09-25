# SBCT-01 incomplete participant evidence review

**Status:** APPROVED — Ira Abbott, 2026-09-25: "Approve the bounded amendment."
**Date:** 2026-09-25
**Target:** SBCT-01-OBSERVATIONS 0.1.2 and observation-set version 1.

## Problem and recommendation

When a child checkout is missing or its history is unavailable, its parent's
HEAD and recorded gitlink can still be observed. Aggregate capture correctly
returns no corpus. The current schema and validator nevertheless require every
`available` participant to have clean/dirty state and a corpus hash, including
inside an incomplete observation. That cannot describe this known-HEAD parent
without inventing evidence or discarding its observed relation.

Approve this bounded amendment: in an incomplete observation only, an available
participant may report `checkout_state: "unknown"` and `corpus_sha256: null`.
Known checkout state and a captured corpus hash may still be retained separately
when actually obtained. `available` describes readable required Git context;
it does not by itself certify checkout state or captured content.

Complete observations still require every participant to be available, every
checkout state to be clean or dirty, every corpus hash to be present, all relations
to have match/mismatch evidence, and all aggregate stability checks to pass.
Unavailable participants retain null HEAD/corpus and unknown checkout state.
Incomplete observations retain null selection digest, exit 3, null selection and
null result; publication remains prohibited. No new enum or automatic approval
is introduced. This is a prerelease semantic amendment, not runtime acceptance.

## Alternatives considered

- Mark the parent unavailable too: rejected because its required Git context may
  be readable, and that would falsely block evidence already read from its children.
- Invent a clean/dirty state or empty corpus hash: rejected because neither is
  evidence of the parent's actual state or selected content.
- Return a null observation for all missing-child failures: rejected because it
  loses the explicitly required unavailable/blocked participant diagnostics.

## Review witness

For a known parent HEAD with a missing child, retain the parent's available row,
HEAD and recorded gitlink, with unknown checkout state and null corpus. Mark the
child missing and any uninspected descendants blocked. The same object must reject
if `complete` is changed to true. Previously valid complete captures and version-1
single-repository CLI results remain unchanged.

The owner explicitly approved this bounded amendment on 2026-09-25. It is
incorporated in SBCT-01 0.9.1 and SBCT-01-OBSERVATIONS 0.1.3. Runtime acceptance
and release remain separate decisions.
