# Understanding Directional Change from First Principles

An intuition-first, causality-safe journey from one Directional Change threshold to arbitrary-N multiscale market regimes.

This repository is designed to answer a deceptively difficult question:

> What does a Directional Change event mean, what was knowable when it occurred, and how does that meaning evolve across several thresholds?

The project combines three layers:

1. concise [notes](notes/README.md);
2. chronological notebook laboratories using real market paths;
3. a reusable Python implementation with explicit event identities and information timestamps.

It begins with one threshold and hand-readable events. Only after the mechanics are established does it introduce filtered HMM states, cross-threshold propagation, exact multiscale lineage, causal live development, arbitrary-N representations, and probabilistic regimes.

This is a research and education repository. It is not a trading strategy or investment recommendation.

## Why this project is different

Directional Change is easy to implement superficially and easy to misread. I went through the proverbial arc of learning many times until I decided to document it myself. Common errors include:

- treating a peak or trough as known before its reversal confirmation;
- confusing the completed prior leg with the newly confirmed live mode;
- mapping an event state onto bars as if it were recomputed every bar;
- linking multiscale stages by nearby timestamps instead of exact event IDs;
- using terminal propagation depth as a live feature;
- treating a model's state name as market truth;
- interpreting structural recurrence as evidence of trading profitability.

The repository makes those distinctions executable. Every important value carries, or can be traced to, an event identity and the first timestamp on which it became knowable.

## The central intuition

At every DCC, ask three questions:

1. **What ended?** The newly confirmed extreme completes the prior directional leg.
2. **What is live now?** The DCC switches the confirmed mode in the opposite direction.
3. **What remains unknown?** The next extreme, DCC, outcome, and terminal scale depth.

A downward DCC therefore confirms the prior peak and switches the live mode down. An upward DCC confirms the prior trough and switches the live mode up.

With several thresholds, each threshold maintains an independent event clock on the same price path. Small-scale opposition is observable immediately; whether it reaches medium, large, macro, or outer scales remains unknown until the corresponding confirmations occur.

## Start here

If you are learning Directional Change, do not begin with the regime models.

1. Read the [front matter](notes/README.md#front-matter).
2. Read [Chapter 0 — The pre-exploration contract](notes/00_pre_exploration_contract.md).
3. Read Chapters [1](notes/01_directional_change_mechanics.md) and [2](notes/02_tmv_t_r_overshoot.md).
4. Run [`1_threshold_dc_explore.ipynb`](1_threshold_dc_explore.ipynb).
5. Reconstruct several events by hand.
6. Answer the chapter exercises before expanding that chapter's integrated completion-gate guidance.

Then continue in the sequence below. Running a notebook is necessary but not sufficient: advance only after you can explain its completion gate in your own words and apply it to an unseen chart segment.

## Learning path

| Stage | Concepts | Notes | Notebook labs |
|---|---|---|---|
| Pre-exploration | Information time, event identity, causal versus hindsight | [Chapter 0](notes/00_pre_exploration_contract.md) | Research contract and tests |
| One threshold | DCC mechanics, TMV, T, R, overshoot, filtered event states | [Chapters 1–5](notes/README.md#part-i--one-threshold) | [`1_threshold_dc_explore.ipynb`](1_threshold_dc_explore.ipynb), [`1_threshold_dc.ipynb`](1_threshold_dc.ipynb), [`1_threshold_dc_explore_hmm_dist.ipynb`](1_threshold_dc_explore_hmm_dist.ipynb) |
| Two thresholds | Independent clocks, counter-moves, propagation, rejection, survival | [Chapters 6–10](notes/README.md#part-ii--two-thresholds) | [`2_threshold_dc.ipynb`](2_threshold_dc.ipynb), [`2_threshold_dc_event_characteristics.ipynb`](2_threshold_dc_event_characteristics.ipynb), [`2_threshold_dc_robustness.ipynb`](2_threshold_dc_robustness.ipynb) |
| Three thresholds | Eight configurations, exact two-stage lineage, live hand-off | [Chapters 11–14](notes/README.md#part-iii--three-thresholds) | [`3_threshold_dc.ipynb`](3_threshold_dc.ipynb), [`3_threshold_dc_linkage.ipynb`](3_threshold_dc_linkage.ipynb), [`3_threshold_dc_live_development.ipynb`](3_threshold_dc_live_development.ipynb), [`3_threshold_dc_robustness.ipynb`](3_threshold_dc_robustness.ipynb) |
| Four thresholds | Sixteen configurations, coherent depth, fragmentation, three-stage lineage | [Chapters 15–17](notes/README.md#part-iv--four-thresholds) | [`4_threshold_dc.ipynb`](4_threshold_dc.ipynb), [`4_threshold_dc_linkage.ipynb`](4_threshold_dc_linkage.ipynb), [`4_threshold_dc_live_development.ipynb`](4_threshold_dc_live_development.ipynb) |
| Five thresholds | Grid design, 32 configurations, four-stage lineage, robustness | [Chapters 18–22](notes/README.md#part-v--five-thresholds) | [`5_threshold_dc.ipynb`](5_threshold_dc.ipynb), [`5_threshold_dc_linkage.ipynb`](5_threshold_dc_linkage.ipynb), [`5_threshold_dc_live_development.ipynb`](5_threshold_dc_live_development.ipynb), [`5_threshold_dc_robustness.ipynb`](5_threshold_dc_robustness.ipynb) |
| Arbitrary N | Canonical scale, edge, hierarchy, and lineage representations | [Chapter 23](notes/23_arbitrary_n_representation.md) | [`multiscale_representation_design.ipynb`](multiscale_representation_design.ipynb) |
| Regime models | Direct baseline, clustering, filtered HMMs, OOS validation, interpretation | [Chapters 24–28](notes/README.md#part-vii--probabilistic-regimes) | [`20_interpretable_regime_baseline.ipynb`](20_interpretable_regime_baseline.ipynb), [`21_probabilistic_regime_models.ipynb`](21_probabilistic_regime_models.ipynb), [`22_causal_oos_validation.ipynb`](22_causal_oos_validation.ipynb), [`23_economic_interpretation.ipynb`](23_economic_interpretation.ipynb), [`24_cross_market_robustness.ipynb`](24_cross_market_robustness.ipynb) |
| Research engineering | Reusable library, invariant tests, reproducibility | [Chapters 29–30](notes/README.md#part-viii--research-engineering) | `dc_basics/`, `tests/` |

## Installation

The saved notebook outputs were produced with Python 3.12.9, and that is the version the notebooks are validated against. Other recent versions (3.11+) may work but have not completed the final reproducibility pass.

```bash
git clone https://github.com/okmich/understanding_directional_change_basics.git
cd understanding_directional_change_basics
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Linux or macOS
source .venv/bin/activate
```

Install the research dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The HMM dependency is installed from a Git repository, so Git and network access are required during installation.

Start Jupyter:

```bash
jupyter lab
```

## Data contract

Market data is not included. Use data that you are licensed to access.

No notebook contains a machine path. Every notebook calls `dc_basics.resolve_data_root()`, which looks in this order for the data directory:

Accepted Parquet schema:

- a unique, ordered `DatetimeIndex`, or a `time` column convertible to one;
- a `close` column;
- finite, strictly positive close prices;
- native five-minute observations for the supplied resampling workflow.

**Timestamp convention.** MetaTrader-style exports, including the files used for the saved outputs, stamp each bar with its *open* time: the close of the bar stamped 10:05 is first known at 10:10. `load_close(..., bar_timestamp="open")` is the default. Pass `bar_timestamp="close"` for data stamped at bar close.

`dc_basics.load_close` can causally take the last close inside 15-, 30-, or other multiple-of-five-minute intervals. The sampled bar keeps the input's convention: with `"open"` it is labelled by its interval's open and holds the close at the interval's end. The loader rejects duplicate timestamps, missing close columns, and non-positive or non-finite prices.

The existing saved notebook outputs document the original experiments, but a reproducible local run requires compatible input data. A portable sample dataset remains part of the release work.

## Minimal API example

```python
from dc_basics import load_close, parse_dc_events, prepare_event_ledger, resolve_data_root

theta = 0.002  # 0.20%
close = load_close(resolve_data_root(), "EURUSD")

events = parse_dc_events(close, theta=theta)
ledger = prepare_event_ledger(
    source=events,
    prefix="S-E",
    scale="small",
    theta=theta,
)

print(ledger[[
    "event_id",
    "completed_leg_direction",
    "dcc_direction",
    "new_live_mode",
    "ext_end_idx",
    "dcc_idx",
    "information_time",
    "tmv",
    "t",
    "r",
]].tail())
```

The essential timing rule is:

```text
information_time == dcc_idx
```

The ending extreme may occur earlier, but its completed TMV, T, and R are not available until the DCC confirms it.

The essential direction rule is that each row describes the leg that *ended*. The parser's `direction` column is that completed leg, kept as `completed_leg_direction`. A row whose completed leg is `up` was closed by a *downward* DCC (`dcc_direction == "down"`), which switches the live mode down (`new_live_mode == "down"`).

## Causality contract

All contributions and derivative studies should preserve these rules:

1. A completed event's extreme, TMV, T, and R become available only at its DCC.
2. Live features use information through the current bar only.
3. A stage's resolution bar is excluded from its pre-resolution live panel.
4. Propagated/rejected and terminal-depth labels are hindsight until their resolution times.
5. The initiating small event remains the immutable lineage ID through every exact hand-off.
6. With close-only bars, a lower-scale DCC and an opposing upper-scale DCC on the same bar cannot be ordered. That stage is marked `ambiguous_same_bar`. A seed and its upper-scale confirmation on the same bar are different: that is a zero-length propagation, not an ambiguity.
7. Filtered probabilities, not smoothed probabilities, are used for causal state paths.
8. Scaling, semantic mapping, and model selection are training-only.
9. Bar-time and event-time results are identified separately.
10. Structural recurrence, state confidence, and persistence are not trading-profit claims.

## Running tests

Install the test runner with the development requirements, then run the suite from the repository root. `pytest.ini` puts the repository root on the import path, so plain `pytest` works:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

`tests/test_vendor_parity.py` always checks the vendored modules against SHA-256 hashes recorded at vendoring time. It also compares them with the pinned signalfoundry commit when a checkout is available: a sibling `../signalfoundry` directory, or the path in `SIGNALFOUNDRY_ROOT`.

The tests cover:
- core formulas and information times;
- hierarchy identities, same-bar ambiguity and the nesting-parity near-invariant;
- one lineage semantics across 3-, 4- and 5-scale ladders;
- live-panel resolution-bar exclusion and exact joins;
- arbitrary-N construction and regime-model diagnostics;
- optional HMM behaviour;
- vendored-source parity.

`tests/test_prefix_invariance.py` rebuilds ledgers, attempts, lineages and the arbitrary-N state from a price prefix and compares each with the full-sample build. See [Chapter 29](notes/29_reusable_library.md#invariants-as-executable-knowledge) for what remains.


## Credits and acknowledgements

Directional Change is an established research framework. Foundational credit belongs to Dominique M. Guillaume, Michel M. Dacorogna, Rakhal R. Davé, Ulrich A. Müller, Richard B. Olsen, and Olivier V. Pictet.

This project is especially indebted to Jun Chen and Edward P. K. Tsang, authors of *Detecting Regime Change in Computational Finance: Data Science, Machine Learning and Algorithmic Trading*. Their work motivates the progression from Directional Change indicators to regime characterization and causal market monitoring.

See the notes' [credits and acknowledgements](notes/README.md#credits-and-acknowledgements) and [core bibliography](notes/README.md#core-bibliography) for full attribution requirements and primary references.

## Current limitations

- Market data and a portable sample dataset are not included.
- Some notebooks contain large saved outputs.
- The test suite is foundational rather than release-complete.
- A clean-machine execution and dependency-locking pass remains pending.
