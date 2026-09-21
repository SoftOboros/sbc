# Spec Before Code (SBC)

<p align="center">
  <a href="assets/sbc-spec-before-code.png">
    <img src="assets/sbc-spec-before-code.png" alt="Spec Before Code: specifications and conformance gates guiding an AI agent's code generation" width="900">
  </a>
</p>

A portable, standards-body-style planning discipline for multi-phase software initiatives,
designed to survive agent context resets, weak model executors, and cross-team vocabulary
drift.

## Prerelease status and release direction

This repository is public and developed on `main`. Guiding documents and
incomplete work are shared there as prerelease material; each document's own
status identifies its approval state. Release tags will identify release
milestones.

The first release goal for the supporting tools is a working, limited indexing
and dashboard set that can be used in an independent repository. The shared
core and public interfaces should support maximum reuse by downstream hosts,
while internal production policy, identity integrations, and deployment
configuration remain in those hosts. Supporting tooling lives in `tools/`, with its governing documents in
[`docs/sbc-tools/`](docs/sbc-tools/README.md). One submodule supplies the discipline
and optional tooling.

The guiding documents are available now. Their publication does not claim that
the indexing or dashboard implementation is complete.

## Supporting tools

The [Python package](tools/README.md) implements offline committed-source indexing,
validation, immutable publication and an explicit-host CLI. Queries and the
dashboard remain incomplete. See the [consolidation record](docs/sbc-tools/REPOSITORY-CONSOLIDATION.md).

Add this repository once with `git submodule add https://github.com/SoftOboros/sbc.git path/to/sbc`.
Tool installation is optional: `python -m pip install ./path/to/sbc/tools`.
Git-provider dependencies require the separately audited pure-Python wheels
described in the package README. Repository operations require explicit
`--config PATH --host PATH`; adoption never supplies approval pins implicitly.

## What it is

SBC enforces a simple invariant: a ratified behavioural specification precedes every
executable artifact derived from it.  The discipline borrows RFC 2119 keyword semantics,
frozen enumeration registration policy, and authority-boundary declarations from established
standards bodies — because those bodies solved the same problem of independent implementors
needing to converge without shared context.

In agentic workflows, every context window is an independent implementor.  SBC is the
spec that loads before the code.

## Normative artifact

[`docs/SBC-00-CONCEPTS.md`](docs/SBC-00-CONCEPTS.md) — the authoritative definition of the
discipline, its invariants (`SBC-INV-1` … `SBC-INV-14`), and its frozen enums.

## Repository structure

```
sbc/
├── CLAUDE.md                  # operational context — the injected form, instantiated
├── AGENTS.md                  # semantic state variable — current phase and ratification status
├── LICENSE                    # BSD 3-clause
├── README.md                  # this file
├── docs/
│   ├── SBC-00-CONCEPTS.md     # normative authority
│   ├── SBC-00-ADDENDUM-A.md   # operational context injection template
│   ├── SBC-00-ADDENDUM-B.md   # ErrataStatus enum; ERRATA boundary rules; ERRATA.md template
│   ├── SBC-ERRATA.md          # errata log for the sbc family itself
│   └── SPEC-BEFORE-CODE-CONCEPTS.md  # SUPERSEDED predecessor / input (ERRATA-003); kept as memory
└── templates/
    └── ERRATA.md              # bare ERRATA.md template (extracted from ADDENDUM-B §3)
```

## How to adopt

1. Copy [`docs/SBC-00-ADDENDUM-A.md`](docs/SBC-00-ADDENDUM-A.md) §1 injection block into
   your project's `CLAUDE.md`.  Fill in the `<PLACEHOLDER>` values for your project.
2. Copy [`templates/ERRATA.md`](templates/ERRATA.md) to
   `<your-initiative-docs-root>/<family>/ERRATA.md`.
3. When your first initiative family produces a `-00-CONCEPTS` gate, it SHOULD open by citing
   `SBC-00-CONCEPTS.md` for its form and reserving its own content for domain vocabulary.

## Strange loop

This repository's own `CLAUDE.md` is an instance of the injection template it distributes.
`CLAUDE.md` (operational authority) and `docs/SBC-00-CONCEPTS.md` (normative authority) point
at each other per `SBC-00-CONCEPTS.md §0`.  The errata log (`docs/SBC-ERRATA.md`) was
created because `SBC-INV-10` requires one, and its entries record defects caught during the
authoring of the documents that mandate it — including `ERRATA-003`, which used the discipline's
own supersession trail (errata + §15 + SUPERSEDED marker) to retire the predecessor concepts doc
this one was synthesised from, rather than silently deleting it.

The recursion is intentional and load-bearing.

## License

BSD 3-Clause.  See [`LICENSE`](LICENSE).
