# SBCT-03 — Minimal Django and MCP OAuth Example

**Document ID:** SBCT-03
**Status:** DRAFT — pending ratification
**Revision:** 0.5.0
**Date:** 2026-09-19
**Owner:** Ira Abbott
**Depends on:** [SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md).

## §0 Authority Policy [Normative]

This phase MUST implement the owner's Django identity and minimal MCP OAuth example boundary.
`INV-SBCT-3`, `INV-SBCT-6`, `INV-SBCT-8` and `INV-SBCT-12` are as defined
in SBCT-00 §9; used without modification. Django owns authentication mechanics;
the host project owns production identity. No production auth is granted by
installing this adapter.

SBCT-00 is ratified as recorded in its §15 entry dated 2026-09-19. This child
is prepared for detailed review under that authority; it remains DRAFT.
Candidate detail in §8 requires this phase's owner review and ratification.

## §1 Purpose

Supply a genuinely runnable small backend/example, not a trimmed consumer application
settings tree. It demonstrates the shared tooling without production services.

## §2 Evidence

The example demonstrates the public store/query interfaces in a small host.
Consumer-specific auth and database layouts are not portable defaults.

## §3 Canonical Glossary [Normative]

Reference backend and host adapter are as defined in SBCT-00 §3; used without
modification. Django's user, group, permission, session and CSRF facilities are
composed for human identity. MCP OAuth composes the pinned protocol authority
in §13; it is separate from Django session authentication, not built into it.

## §4 Source-of-Truth Map [Normative]

| Surface | Owner |
|---|---|
| Standard human authentication/session mechanics | Django |
| HTTP MCP authorization protocol | Pinned MCP authorization specification |
| Bounded OAuth example composition and administration | This phase |
| Minimal project composition and API access policy | This phase §5–§7 |
| Core queries/store interfaces | SBCT-02 |
| Production authentication and deployment | Consuming project only |

## §5 Allowed Composition [Normative]

The shipped example MUST use Django's standard auth user, `ModelBackend`,
authentication/session middleware, standard login/logout views, CSRF protection,
and ordinary Django permissions. Every authenticated active user in the
single-repository human example MAY read its configured corpus; it MUST not expose
multiple visibility scopes without an explicit host authorization adapter.
Inactive and anonymous users MUST be denied protected API access.

The example MUST use one documented local configuration and explicit user
creation. It MUST ship no shared/default password and no automatic superuser.
An optional administrator can create users through standard Django facilities;
the application MUST not add public registration, account recovery services,
social login, MFA services or custom Django identity backends. The MCP OAuth
flow below is an explicit addition, not a production identity stack.

The proposed local store is SQLite under the parent layout decision. Auth data
and projection tables MAY share that example database only if projection reset
is table-scoped and demonstrated to retain users/sessions. The reusable adapter
MUST support a host-selected database alias; split database policy remains
in consumer configuration.

### Bounded MCP OAuth example

The example MUST include a runnable HTTP MCP resource server and a small OAuth
authorization server composed with standard Django users/login. Use an existing
maintained OAuth library selected and pinned before implementation; do not
implement cryptography or a new token protocol in the semantic core.

The protocol baseline proposed for this example is MCP authorization 2025-11-25
(§13). Supply protected-resource and authorization-server metadata, authorization
code flow with PKCE, resource-bound access tokens and bearer challenges. Reject
invalid, expired or wrong-resource tokens and insufficient scopes. No token
passthrough. Use exact registered redirects and protect authorization consent.
The example uses operator-preregistered clients; dynamic registration and client
metadata fetching are outside its initial scope, with interoperability limits
explicitly documented. HTTPS requirements and permitted local-development
exceptions MUST follow the pinned protocol, not an inferred loopback bypass.

Django admin and management commands MUST provide minimal client create/list/
disable, redirect/scope configuration, and grant revocation operations. Standard
Django facilities own user creation and disabling. These operations MUST require
staff permissions or trusted local operator access, redact credentials, and
never turn a corpus read endpoint into a management endpoint. Document secret
creation/rotation without logging secrets or committing fixture credentials.

A token authorizes only the intersection of its granted read scope and the
active user's current repository permission. User/client disabling and grant
revocation MUST take effect on the next protected request, including cached
query results. Do not use bearer tokens as a browser session or a Django session
as MCP authorization. Corpus queries remain read-only; login, consent, token and
administration writes are restricted identity operations, not governance writes.

This is an example host, separate from the reusable adapter contract. Its limited
feature set is intended to become static; production consumers maintain their
own OAuth/identity implementations against SBCT-02's public authorization-context
and query interfaces. Security maintenance/support is declared under SBCT-06.

## §6 API and Runtime Contract [Normative]

The supplied HTTP surface MUST use thin Django views over SBCT-02. Protected
JSON requests MUST receive a documented non-success JSON response when unauthenticated,
not a successful login-page payload. Login navigation MAY use standard Django
redirect behavior. Django sessions MUST remain server-authoritative, and unsafe
browser/session requests including login/logout, consent and admin operations
MUST use framework-appropriate CSRF protection. MCP bearer and OAuth token
endpoints MUST apply their pinned protocol protections without requiring a
Django browser session or browser CSRF token.

Spec/query endpoints MUST be read-only. Ingestion MUST be an explicit local
management operation, not an anonymous HTTP action or an automatic read side
effect. Static dashboard assets MAY be served on the same origin. The setup
MUST document migrations, user creation, configuration, ingestion, startup and
shutdown without a cloud account or external service credentials. MCP setup MUST also
document client preregistration, consent, token acquisition and revocation. The default bind MUST be loopback;
that bind restriction MUST not replace login checks.

`serve` MUST report a missing optional Django installation with a clear setup
instruction, not install or launch production services implicitly.

## §7 Excluded Dependencies and Threat Model [Normative]

The supplied backend MUST contain no consumer-specific auth, custom user model,
entitlement/billing/tenancy logic, production social login, standalone API-key
service, cloud secret fetch or mandatory distributed queue/cache services.
OAuth token format is selected with the library; this exclusion MUST NOT be
misread as prohibiting the explicitly required MCP OAuth implementation.
Disabled code or an optional production-auth extra still violates this boundary.

Threats include anonymous reads, session confusion, CSRF, source-controlled
credentials, sensitive errors and accidental deletion of identity data during
projection rebuild. Errors MUST not disclose filesystem roots, credentials or
session/token material. Reset commands MUST target projection tables only and
retain users, sessions, OAuth clients, grants and revocation state. Host
production methods MUST be implemented outside the supplied backend and passed
through the adapter interfaces; removing them from distribution MUST not remove
authentication or authorization from an actual production host.

## §8 Deferred Detail

The expanded example scope is owner-directed; its exact implementation contract
remains gated by `GATE-307`. Before code, select the OAuth library/version and
protocol pin, URLs and error shapes, scope vocabulary, redirect policy, token
lifetime/storage/refresh/revocation behavior, client types, command/admin schemas
and supported MCP clients. Refresh support MUST NOT be implied by OAuth support;
if omitted, document reauthorization. Record justified protocol SHOULD omissions
and verify supported clients. Parent decisions are approved; their deferred baseline and implementation
details remain gated.
These are child-phase details, not silently approved concepts-level values.

### Prepared candidate example operations

Propose separate endpoint groups for `GATE-307` review: Django login/logout and
admin; read-only `/api/spec-index/` queries; `/mcp` for OAuth-protected MCP; and
OAuth discovery/authorize/token/revocation endpoints supplied by the selected
library. Their exact paths and protocol version remain subject to compatibility
review; do not implement endpoints merely from these proposed names.

Propose local operator commands `mcp_client create`, `mcp_client list`,
`mcp_client disable` and `mcp_grant revoke`. Create accepts a client name, exact
redirects and an allowlisted read scope; list redacts secrets; disable/revoke
remove access on the next protected request. Standard Django commands/admin
own user creation and disabling. Admin mutations use staff permissions and CSRF;
OAuth token/MCP bearer operations use their protocol protections.

Before `GATE-307`: select and audit the OAuth library and dependency tree,
validate supported MCP clients, specify scope strings and token lifetimes,
refresh/revocation semantics and command errors, and prove projection reset
cannot remove identity state. This preparation does not select a library or
claim interoperability. Installation requirements must be explicitly reconciled
with the portable Python/PyPI environment rather than silently adding OS tools.

## §9 Invariant Application [Normative]

Package contents, installed dependencies and runnable auth behavior MUST all
satisfy §0's parent invariants; a clean dependency list alone is insufficient.

## §10 Reconciliation [Normative]

Production consumers compose their own project settings and authentication.
The shared adapter MUST refer to `AUTH_USER_MODEL` or `get_user_model()` only
where a user relationship is necessary and MUST not require a particular
production user field. Core spec objects MUST not own user identities.
No FastAPI host is needed in the distributed example.

## §11 Non-Goals

1. `NONGOAL-301` — **Production identity starter kit.** The example MUST NOT claim enterprise/scaling readiness or ship consumer production identity integrations; minimal MCP OAuth is included only within §5.
2. `NONGOAL-302` — **Shared anonymous dashboard.** A loopback deployment MUST NOT bypass authentication merely because it is local.

## §12 Acceptance [Normative]

A conforming reference backend MUST meet §5–§7 and §9–§10:

- [ ] `GATE-301` — A fresh installation MUST migrate, create a standard user, ingest and serve a fixture without consumer application/cloud credentials or services.
- [ ] `GATE-302` — Login/read/logout MUST work; anonymous/inactive reads and invalid sessions MUST fail, including after logout.
- [ ] `GATE-303` — Browser/session operations without required CSRF protection MUST fail; valid MCP bearer requests and OAuth token exchanges MUST work without Django browser-session credentials while invalid protocol credentials MUST fail. Protected API responses MUST not become successful HTML login pages.
- [ ] `GATE-304` — Package/source/dependency inspection MUST demonstrate the exclusion list, including disabled code and optional extras.
- [ ] `GATE-305` — Projection rebuild MUST retain authentication data; an invalid ingestion MUST retain the previous selected snapshot.
- [ ] `GATE-306` — A downstream test host MUST replace composition without patching the core or requiring custom fields on its user model.
- [ ] `GATE-307` — Owner MUST approve the expanded example policy, exact §8 contracts, transport mapping and store reconciliation before phase ratification and implementation.
- [ ] `GATE-308` — A supported MCP client MUST discover the example, complete code/PKCE consent and read an authorized fixture; missing/invalid PKCE, wrong redirect, wrong resource, expired/revoked tokens and insufficient scopes MUST fail safely.
- [ ] `GATE-309` — Admin/command client setup and revocation MUST work; unauthorized management, disabled users/clients and cached access after revocation MUST fail. Projection reset MUST retain OAuth identity state and secrets MUST not appear in logs.
- [ ] `GATE-310` — Public-adapter parity MUST pass with an independent identity implementation; the shared core MUST import neither the example OAuth library nor Django auth. Example support/freeze and client limitations MUST be documented.

### Named witness specifications [Normative]

These cases MUST be specified for review now and executed only at their
applicable acceptance stage. They are not claims that tests already exist.

| Witness | Positive case | Negative case |
|---|---|---|
| `W-301-P` / `W-301-N` | Standard Django human login and the bounded OAuth MCP flow serve authorized fixture queries. | A package with disabled production auth extras or a wrong-resource token fails the applicable audit/access check. |
| `W-302-P` / `W-302-N` | An active authorized principal reads the single configured repository with current granted scope. | Disabled users/clients, revoked grants and insufficient scope fail before queries or cached results are returned. |
| `W-303-P` / `W-303-N` | Projection rebuild restores identical declared projections and retains identity records where a host supplies them. | An invalid ingestion preserves the selected snapshot; a reset that removes users, sessions, clients, grants or revocation state fails review. |

## §13 Files Cited

[SBCT-00](SBCT-00-CONCEPTS.md), [SBCT-02](SBCT-02-QUERIES-AND-ADAPTERS.md),
[SBCT-04](SBCT-04-DASHBOARD.md), [SIDX-00](https://github.com/iraabbott/softoboros.com/blob/751ffe62027a3030bc989d22f5c2f759234064dc/docs/todo/spec-index/TODO-SIDX-00-CONCEPTS.md),
and [MCP authorization 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization).
The protocol is a versioned composition authority, not a claim that Django
ships an OAuth server. Library selection and verification remain §8 work.

## §14 Unblocks

Runnable mcp-example and local-dashboard profiles and example packaging in SBCT-06.

## §15 Change Log

### 0.1.0 — 2026-09-18 — drafted

**Author:** Codex (draft author)
**Change kind:** scope
**Touches:** SBCT-03
**Commits:** none
**Summary:** Initially recorded the standard-Django-only requirement; the
0.2.0 owner-directed scope below supersedes its OAuth exclusion.

#### Rationale

Considered and rejected: disabled production auth, copying consumer application settings,
and unauthenticated localhost APIs. Deliberately unchanged: downstream control
of production identity, shared query meanings and human release authority.

### 0.2.0 — 2026-09-18 — owner-directed draft revision

**Author:** Codex
**Change kind:** scope
**Touches:** SBCT-03; parent INV-SBCT-3 and conformance boundaries
**Commits:** none
**Summary:** Incorporates accepted standalone conformance and explicit decision
closure; expands the example to MCP OAuth and separates consumer-specific
adoption from the portable contract. This is not family or phase ratification.

### 0.3.0 — 2026-09-19 — ratification package prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-03
**Commits:** none
**Summary:** Prepares explicit proposed decision dispositions, bounded
compatibility policy and child-owned witness specifications. Existing invariant
meanings are preserved. No decision acceptance or ratification is inferred.

### 0.5.0 — 2026-09-19 — child draft prepared

**Author:** Codex
**Change kind:** clarification
**Touches:** SBCT-03
**Commits:** none
**Summary:** Recognizes parent ratification and prepares concrete candidate
contracts and remaining prerequisites in §8. Child ratification and acceptance
are not claimed; all implementation gates remain unchecked.
