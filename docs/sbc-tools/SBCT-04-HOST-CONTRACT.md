# SBCT-04 — Dashboard Host Contract

**Document ID:** SBCT-HOST-04
**Status:** DRAFT — proposed for GATE-406 review
**Revision:** 0.1.0
**Date:** 2026-09-20
**Owner:** Ira Abbott

## Authority and approval boundary

This candidate completes the host-interface direction in
[SBCT-04](SBCT-04-DASHBOARD.md). It depends on the proposed
[SBCT-02 contract package](SBCT-02-CONTRACT-PACKAGE.md); no approval of either
package is inferred. SIDX-06C §§5–9 own inherited dashboard behavior.
Its local-only admission rule is retained by existing consumers.

The portable component boundary is proposed separately: a trusted host supplies
admission and authenticated transport. This does not authorize removal of an
existing consumer's local gate or deployment of its dashboard. Before GATE-406,
pin the exact SIDX-06C authority and extracted client/component source bundle,
record the clause-level adaptation, and freeze presentation dependency versions.

## Public interfaces

The proposed exports are described in [dashboard-host.d.ts](contracts/dashboard-host.d.ts).
These are declarations for review, not runtime implementation.

| Interface | Owns | Excludes |
|---|---|---|
| QueryTransport | Send typed read requests with AbortSignal; return unknown wire data | Semantic filtering, implicit refresh, provider or identity overrides |
| SessionHost | Current admission/access state, opaque revision, change subscription, sign-in notification | Tokens or Django/OAuth objects in component props |
| FilterNavigation | Read/replace allowlisted filter URL state | Cursor, payload, object text or history persistence |
| LocationNavigation | Resolve validated typed locators into allowed navigation actions | Automatically treating repository content as executable URLs |
| Labels | Translate source messages with named scalar parameters | Raw HTML, semantic enum coercion, mandatory host locale context |
| DashboardScope | Repository and explicit/current publication selection | Caller-asserted server authorization |

The package validates unknown transport results once using shared versioned
validators before exposing typed data to components. Capability-specific
nested validation follows the owning SIDX contracts, not TypeScript casts.
An unfamiliar valid enum-like string displays neutrally as an unknown value;
malformed structure is a protocol error. HTTP success carrying a login page
is a protocol/authentication failure, never an empty queue.

The reference transport is same-origin Django session authentication. Production
hosts inject their own authenticated transport. A browser does not call MCP,
manage OAuth secrets, import a production token store, or refresh tokens inside
the reusable components. Hosts may perform their normal authenticated retry,
but cancellation and the captured session revision still govern delivery.

## Request and display lifecycle

At mount, subscribe to session changes before starting queries. No request is
sent unless admission is allowed and access is authenticated. Read-only UI
scope does not confer permission; the server authorizes each request.

Each request captures a monotonically increasing request generation, session
revision, repository/selection and normalized filter key. A result may install
only if all still match and its validated response context matches the request.
Abort is best effort: generation checks remain mandatory after abort.

| Event | State transition |
|---|---|
| Mount, login completion | First page; no restored cursor |
| Filter change | Cancel obsolete work; clear cursor and selection; request first page |
| Explicit refresh | Retain filters, clear cursor/selection; old rows remain labeled with their old context until replacement |
| Load more | One request at a time; append only under identical validated context and filter key |
| Cursor mismatch/invalidity | Retain labeled rows, discard continuation and offer refresh from first page |
| Repository/publication change | Cancel all work; clear rows, inspectors and cursors before querying the new scope |
| Logout, revoked access, admission loss or session revision change | Clear protected state immediately; cancel and reject old responses; query again only under an admitted authenticated context |
| Unmount | Unsubscribe, cancel and drop all retained response references |
| Transport/protocol failure | Show a distinct error; no fabricated empty result; explicit retry |

The response context compared for pagination includes repository, content
snapshot, publication, selection generation, evidence identity and capability
profile. The client does not decode a cursor to obtain context. Scope/session
revision is checked independently because authorization context is host-owned.
If C12 returns another publication than the selected C11 row's publication,
do not install the inspector result; offer refresh. C12 requests use the row's
explicit publication selection.

Preserve SIDX-06C's 250 ms search debounce and no-polling behavior. The server
computes membership, counts, facets, confidence and staleness. The client
does not sum partial pages into totals or infer healthy evidence from zero rows.
No corpus or responses go to localStorage, IndexedDB, service-worker caches,
build artifacts or URLs.

## Navigation and presentation

Only search, family, attention_class, native_state, tag and location_kind
filter state may enter a shareable URL, using inherited URLSearchParams
serialization. The host owns the route, locale and back/forward integration.
Repository scope is selected by trusted host state, not inferred from arbitrary
filter URL parameters.

Location navigation accepts the validated C12 record and publication context.
Repository/archive paths remain typed locators, not file URLs. An absent
resolver returns unavailable. memalpha records remain inspectable without a
resolver. The host resolves only configured origins/schemes; the package
rejects javascript, data and arbitrary file navigation. Opening requires an
explicit user action. No repository-supplied HTML is rendered.

Keep the inherited vertical order, inspectors, grouping and native-state
labels. Show zero, empty, partial, uncomputable, stale and unavailable distinctly.
Controls must work by keyboard, announce pending/error states and preserve
focus when inspectors open/close. Test both narrow and wide viewports.
The host may supply styling and labels without changing semantic values.

## Packaging and reuse

The component/client build is shared by the minimal Django example and an
independent shell fixture. Public components cannot import application aliases,
Next.js routing, application auth/localization providers or a consumer header.
Extraction must retain one implementation of validators and presentation
models; downstream wrappers supply their host integrations.

The first release includes prebuilt dashboard assets and their manifest in the
Python distribution. Runtime setup requires no Node installation, CDN, build
service or external font fetch. Developer build tooling and lockfiles remain
separate from end-user requirements. A built-asset manifest pins package
version, query-contract version and file SHA-256 values.

Interlock is optional and deferred from the first release. Missing or
incompatible extension support cannot disable repository inspection.
The initial dashboard exposes no ratify, clear, waive, amend or ingest controls.
Ingestion remains an explicit operator command in the example.

## Required witnesses before implementation acceptance

| Case | Expected evidence | Gate |
|---|---|---|
| Independent hosts | Identical artifact and shared fixtures work in the Django example and isolated host shell | GATE-401 |
| Semantic distinctions | Reference C11/C12 cases retain metrics, safe errors and unknown values | GATE-402 |
| Out-of-order responses | An older filter/scope response cannot replace a newer view | GATE-403 |
| Session change during pagination | Protected rows clear; delayed page cannot reinstall them | GATE-403 |
| Inspector context change | A late or differently published C12 response is discarded | GATE-403 |
| Unsafe/missing resolver | No navigation for unsafe targets; unavailable resolver stays explicit | GATE-403 |
| No browser corpus | Source and runtime storage checks; build contains no corpus payload | GATE-404 |
| Keyboard and responsive layout | Focus, labels and error states verified in both hosts | GATE-404 |
| No Interlock | Core dashboard functions with no extension registered | GATE-405 |

These cases are specified, not executed. GATE-406 remains open for exact source
and dependency pins, SIDX reconciliation and owner approval. SBCT-03's runnable
auth/OAuth example still requires its own contract review and ratification.
