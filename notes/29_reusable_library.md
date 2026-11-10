# Chapter 29 — A causality-safe reusable library

## Purpose

Turn the notebook journey into reusable research components without hiding the semantics that made the journey understandable.

## Module map

The local `dc_basics/` package is self-contained:

- `core/`: completed-event parsing, live features, and supporting indicators;
- `data.py`: data-directory resolution, loading with an explicit bar-timestamp convention, threshold catalogs, and validation;
- `events.py`: event ledgers, IDs, information times, and explicit `completed_leg_direction` / `dcc_direction` / `new_live_mode` columns;
- `configuration.py` and `hierarchy.py`: mode vectors, adjacent contests, configurations, and nesting;
- `two_scale.py`: two-threshold attempts and live panels;
- `lineage.py`: exact multistage genealogy;
- `live.py`, `live_panel.py`, and `audit.py`: causal pre-resolution geometry and invariants;
- `plotting.py` and `live_plotting.py`: price-path, state, and audit visualizations;
- `hmm/`: vendored HMM factory, distributions, filtering, and utilities (byte-identical to the pinned source);
- `hmm_support.py`: local HMM additions kept outside the vendored files, such as seeded log-space LogNormal initialisation, the raw-R predictive score with its Jacobian, the shared `fast_R`/`slow_R` labelling rule, and thread pinning.

`dc_multiscale_research.py` contains the shared arbitrary-N representation and phase 20–24 research helpers. Its direct taxonomy and model comparison code remain research-scoped rather than being confused with the foundational parser.

`VENDORED_FROM.md` records implementation provenance. A local copy removes a private runtime dependency; it does not remove the obligation to credit conceptual or software sources.

## Notebook boundary

A notebook should declare the question, configure the case, call reusable functions, display evidence, and interpret it. It should not contain an independent parser, another version of linkage logic, or silent timing rules.

Keep notebook-specific assembly visible when it teaches the concept. Extract code when repetition creates semantic drift or makes invariants difficult to test.

## Invariants as executable knowledge

The tests cover:

- core formulas and DCC information time;
- hierarchy identities, same-bar ambiguity, and the nesting-parity near-invariant (including a synthetic path on which the upper clock confirms first);
- one lineage semantics across 3-, 4-, and 5-scale ladders, with exact hand-offs;
- live panels: resolution-bar exclusion, lineage age, exact joins of completed initiation legs, and features that are constant by construction;
- arbitrary-N state construction, feature screening, and regime-model diagnostics;
- optional HMM behaviour, including the LogNormal Jacobian;
- vendored-source parity against recorded hashes and the pinned commit;
- end-to-end prefix invariance (`tests/test_prefix_invariance.py`): ledgers, live features, mode frames, adjacent attempts, exact lineages, and every column of the arbitrary-N state are rebuilt from a price prefix and compared with the full-sample build, at cut points that straddle the train/validation/test boundaries.

Still worth adding: seed immutability as its own test, and an explicit check that no diagnostic resolution is backward-joined into a feature row.

## Mandatory exercises

1. Trace one notebook output from plotting call to event parser.
2. Identify one invariant enforced by a test and the error it prevents.
3. Find duplicated notebook logic that should—or should not—be extracted, and justify the boundary.
4. Explain the difference between software provenance and intellectual attribution.
5. Add a synthetic path test for one failure mode without using empirical market data.

## Completion gate G25–G27 — Research engineering and repository extraction

Before release, the maintainer must verify:

1. Repeated mechanics, linkage, live-panel, audit, and plotting code lives in reusable modules rather than being independently reimplemented in notebooks.
2. The repository contains local implementations of required directional-change functionality and does not depend on private source repositories.
3. Tests cover timestamp causality, event identity, nesting parity, exact hand-offs, same-bar ambiguity, and resolution-bar exclusion.
4. Notebooks remain readable laboratories rather than hidden application layers.
5. Public examples do not depend on unavailable private data paths without an explicit data-acquisition or sample-data alternative.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Modules should centralize semantics that must not drift across notebooks.
- Synthetic invariant tests protect construction without depending on empirical outcomes.
- Provenance records both copied software lineage and prior conceptual work.
- A thin notebook still keeps the research question, configuration, evidence, and interpretation visible.

</details>

## Locked in

> Reusable code is valuable only when it preserves the event identities, information times, and exclusions that give its outputs meaning.

## Do not conclude

Passing unit tests does not validate empirical conclusions. Tests protect construction; notebooks and out-of-sample audits evaluate evidence.

