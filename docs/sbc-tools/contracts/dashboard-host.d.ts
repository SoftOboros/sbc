/** Proposed SBCT-04 host declarations; no implementation or approval implied. */
export type Capability = "C11" | "C12";
export type PublicationSelector =
  | { readonly kind: "current" }
  | { readonly kind: "publication"; readonly publication_id: string };

export interface DashboardScope {
  readonly repositoryId: string;
  readonly selector: PublicationSelector;
}

export interface FilterState {
  readonly search?: string;
  readonly family?: readonly string[];
  readonly attention_class?: readonly string[];
  readonly native_state?: readonly {
    readonly attribute: string; readonly value: string;
  }[];
  readonly tag?: readonly { readonly key: string; readonly value: string }[];
  readonly location_kind?: readonly string[];
}

export type QueryRequest = {
  readonly version: 1;
  readonly repository_id: string;
  readonly selector: PublicationSelector;
} & (
  | { readonly capability: "C11"; readonly filters?: FilterState;
      readonly limit?: number; readonly cursor?: string | null }
  | { readonly capability: "C12"; readonly requested_id: string }
);

export type TransportResult =
  | { readonly kind: "response"; readonly body: unknown }
  | { readonly kind: "failure";
      readonly reason: "authentication" | "authorization" | "transport" | "cancelled" };

export interface QueryTransport {
  query(request: QueryRequest, signal: AbortSignal): Promise<TransportResult>;
}

export interface SessionSnapshot {
  readonly revision: string;
  readonly admission: "allowed" | "unavailable";
  readonly access: "authenticated" | "anonymous" | "expired" | "denied";
}

export interface SessionHost {
  current(): SessionSnapshot;
  subscribe(onChange: (state: SessionSnapshot) => void): () => void;
  requestSignIn(): void;
}

export interface FilterNavigation {
  read(): FilterState;
  replace(filters: FilterState): void;
  subscribe(onChange: (filters: FilterState) => void): () => void;
}

export interface PublicationContext {
  readonly repositoryId: string;
  readonly snapshotId: string;
  readonly publicationId: string;
  readonly projectionCommit: string;
}

/** Populated only after the owning C12 validator accepts the record. */
export interface ValidatedLocation {
  readonly kind: "repository" | "archive" | "memalpha" | "pointer";
  readonly target: Readonly<Record<string, string>>;
  readonly baseline: string | null;
  readonly integrity: Readonly<Record<string, string>> | null;
}

export type LocationAction =
  | { readonly kind: "link"; readonly url: string; readonly label: string }
  | { readonly kind: "unavailable"; readonly reason: string };

export interface LocationNavigation {
  resolve(location: ValidatedLocation, context: PublicationContext): LocationAction;
  open(action: Extract<LocationAction, { kind: "link" }>): void;
}

export interface Labels {
  text(sourceMessage: string, parameters?: Readonly<Record<string, string | number>>): string;
}

export interface DashboardHost {
  readonly scope: DashboardScope;
  readonly transport: QueryTransport;
  readonly session: SessionHost;
  readonly filters: FilterNavigation;
  readonly locations: LocationNavigation;
  readonly labels: Labels;
}
