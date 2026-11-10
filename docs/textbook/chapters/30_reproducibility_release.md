# Chapter 30 — Reproducibility and release discipline

## Purpose

Make the learning journey executable outside the author's current machine and honest about what has and has not been independently confirmed.

## Release contract

A release must specify:

- supported Python version and pinned dependencies;
- installation and environment commands;
- input data schema, timezone, frequency, price column, and cleaning rules;
- public sample data or a documented acquisition path;
- parameter files for symbols, periods, thresholds, grids, splits, and seeds;
- notebook execution order and expected artifacts;
- deterministic seeds and known nondeterministic components;
- test command and expected scope;
- intellectual provenance, software provenance, and license;
- limitations, explored datasets, and unresolved interpretation gates.

Machine-specific paths such as private data drives must be parameters, not instructions embedded in public labs.

## Where this repository stands

| Release item | Current answer |
|---|---|
| Python | 3.12.9 produced the saved outputs; other 3.11+ versions are unvalidated |
| Dependencies | `requirements.txt`; the pomegranate fork is pinned to commit `6f88cc7`. No full lock file yet |
| Tests | `pip install -r requirements-dev.txt`, then `pytest -q` from the repository root (`pytest.ini` sets the import path) |
| Data location | `dc_basics.resolve_data_root()`: the `DC_DATA_ROOT` environment variable, or a git-ignored `.dc_data_root` file. No notebook contains a machine path |
| Timestamp convention | Native bars are stamped at bar open; `load_close(..., bar_timestamp="open")` keeps that convention when downsampling |
| Software provenance | `dc_basics/VENDORED_FROM.md`; `tests/test_vendor_parity.py` checks recorded hashes and the pinned source commit |
| Known nondeterminism | HMM fits depend on thread count and BLAS reduction order. HMM notebooks fix torch and BLAS to one thread before fitting, and compare restarts rather than trusting one fit |
| Not yet done | Sample dataset, license, full dependency lock, clean-machine execution |

## Clean-environment pass

From a fresh environment:

1. install only declared dependencies;
2. run the unit and invariant tests;
3. execute notebooks in textbook order;
4. verify figures, tables, and gate prompts appear;
5. compare key counts and hashes within documented tolerances;
6. confirm that no notebook imports a private source repository;
7. scan for secrets, absolute paths, hidden state, and stale outputs.

Execution success is not enough. A reviewer must also check information timing, price-path casebooks, declared exclusions, and whether prose matches current output.

## Final review layers

- **Technical:** code, formulas, links, and dependencies.
- **Causal:** timestamps, IDs, filtering, splits, and label timing.
- **Statistical:** sample adequacy, stability, conditioning, and OOS claims.
- **Economic:** state descriptions match actual paths without invented trading meaning.
- **Pedagogical:** each chapter prepares the lab and each gate tests understanding.
- **Attribution:** foundational and derivative work is credited accurately.

## Mandatory exercises

1. Execute the repository in a clean environment using only public instructions.
2. Record every manual intervention required; each is a release defect or documented exception.
3. Verify every chapter link and notebook path.
4. Audit one result end to end from raw data through figure and interpretation.
5. Produce a limitations statement separating explored robustness from untouched confirmation.

## Locked in

> Reproducibility means another careful reader can rebuild the evidence and its causal interpretation—not merely open saved notebook outputs.

## Do not conclude

A reproducible experiment can still be wrong, overfit, or economically useless. Reproducibility makes those problems inspectable.

