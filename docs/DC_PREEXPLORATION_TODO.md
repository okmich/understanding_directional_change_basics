# Directional Change Pre-Exploration Plan

**Status:** Mandatory intuition conduit in progress — single-threshold milestone completed
**Last updated:** 2026-08-20
**Formal research status:** Not started; the programme in Part II remains parked

# Part I — Mandatory DC intuition conduit

This is the true pre-exploration. It is not optional background reading and it is not alpha research. Every later
directional-change hypothesis must pass through this hands-on conduit before strategy design, feature concatenation,
backtesting, or production componentization begins.

The purpose is to make directional change mechanically, causally, visually, and economically intelligible. A model
output is not accepted merely because it is statistically separable. We must be able to explain what market movement
produced it, when it became knowable, what it does and does not say, and how it appears on actual bars.

The formal programme in Part II is intentionally retained below. It begins only after the mandatory conduit's exit
criteria are satisfied.

## Why this conduit is mandatory

Without this stage, it is easy to make serious conceptual errors:

- treating a retrospectively identified extreme as information available at that extreme;
- confusing the direction of a completed leg with the live DC mode after its confirming reversal;
- interpreting `fast_R` as bullish, `slow_R` as bearish, or either state as a trading signal;
- assuming a state painted across bars was independently recomputed on every bar;
- treating HMM labels as fixed thresholds on R while ignoring transition history;
- evaluating a following extreme or overshoot as though it were known at the current DCC;
- adding thresholds and features before understanding what one threshold represents.

The conduit prevents those errors before they can contaminate a hypothesis or backtest.

## Current laboratory and artefacts

- **Raw data:** `D:\data_dump\market_data\raw\FXPIG-Server\5`
- **Sampling:** five-minute bars
- **Primary executable notebook:** `research/directional_change/single_threshold_dc.ipynb`
- **Emission-family exploration notebook:**
  `research/directional_change/single_threshold_dc_explore_hmm_dist.ipynb`
- **Reusable charts:** `research/directional_change/dc_plotting.py`
- **Feature implementation:**
  `D:\projects\quant-studies\signalfoundry\features\src\okmich_quant_features\directional_change`
- **HMM implementation:** `D:\projects\quant-studies\signalfoundry\ml\src\okmich_quant_ml\hmm`

## Completed single-threshold learning sequence

1. Calculate completed DC events for one symbol and threshold.
2. Plot close prices with extreme-to-extreme legs and opposite DCC confirmations.
3. Inspect TMV, T, and R event by event and reconstruct representative cases by hand.
4. Audit their overall and direction-conditioned distributions.
5. Examine consecutive-bar events to understand when a threshold may be too small for the bar resolution.
6. Fit a two-state HMM using only `log(R)` and causal filtered probabilities.
7. Map the event-time filtered state back to the original bar series without pretending it updates on every bar.
8. Audit state coherence in `log(R)` space, TMV–T space, posterior space, and event time.
9. Compare competing emission families on a common raw-R predictive-density scale.
10. Audit next-event behaviour to distinguish descriptive classification from persistent event tempo.
11. Build a recent-event casebook separating information known at the current DCC from hindsight outcomes.
12. Reproduce the mechanism on a second instrument and adjust the threshold only as an exploratory market-scale
    representation choice, not as a return optimization.

## Locked-in DC mechanics

For threshold $\theta$, a completed extreme-to-extreme leg has:

$$
\mathrm{TMV}_n =
\frac{|P_{\mathrm{EXT},n}-P_{\mathrm{EXT},n-1}|}
{P_{\mathrm{EXT},n-1}\theta}
$$

$$
T_n = t_{\mathrm{EXT},n}-t_{\mathrm{EXT},n-1}
$$

$$
R_n = \frac{\mathrm{TMV}_n\theta}{T_n}
$$

R is normalized extreme-to-extreme directional displacement per bar. It is unsigned. It does not encode bullish or
bearish direction and it is not identical to realized volatility, candle size, path efficiency, or choppiness.

### Opposite DCC semantics

An opposite DCC performs two jobs simultaneously:

1. It retrospectively confirms the final extreme and end of the preceding directional leg.
2. It contemporaneously switches the live DC mode into the DCC direction.

The canonical sequences are:

```text
completed up leg -> peak -> downward reversal of theta -> downward DCC -> live mode down
completed down leg -> trough -> upward reversal of theta -> upward DCC -> live mode up
```

Therefore:

| Completed-leg direction | Confirmation type | Live mode after confirmation |
|---|---|---|
| Up | Downward DCC | Down |
| Down | Upward DCC | Up |

The DCC does not guarantee a subsequent overshoot. It is a confirmed state-machine switch, not a forecast that the new
direction will continue.

### Naive position interpretation

For a naive DC-mode-following position, the opposite DCC acts like a structural trailing exit:

```text
live mode up -> hold long -> price falls theta from running peak -> downward DCC -> exit long
live mode down -> hold short -> price rises theta from running trough -> upward DCC -> exit short
```

Theta is measured from the running extreme, not the entry price. The executable giveback may exceed theta because of
bar discretization, gaps, spread, slippage, and execution after the confirmation bar. Exiting and reversing are separate
decisions.

## Causal information contract learned in the conduit

The ending extreme is not known when it occurs. At the later DCC confirmation:

- the final extreme becomes identifiable;
- the completed leg's TMV, T, and R become knowable;
- the filtered HMM probability can be updated;
- the live DC mode switches;
- subsequent decisions may use the information.

The information is too late to trade the leg that produced it or to exit at its final extreme. It may be actionable for
decisions after the DCC if forward relevance survives validation.

For close-based five-minute detection, the conservative execution convention is:

```text
DCC condition known after the confirmation bar closes -> earliest action at the next realistically executable price
```

Every event-derived value must retain an event identifier and information timestamp. Completed-event values must remain
distinct from live, incomplete-event values.

## Locked-in HMM interpretation

The two-state HMM observes only `log(R)`. The semantic labels are assigned after fitting:

- `slow_R`: lower normalized velocity of the completed-event process;
- `fast_R`: higher normalized velocity of the completed-event process.

The filtered label is model-dependent, not a universal threshold on current R. It combines:

- the current R emission likelihood;
- previous filtered state probabilities;
- fitted transition probabilities;
- fitted emission parameters.

Two events with nearly identical R can therefore receive different labels when they arrive with different histories.
Use the filtered probability, not only the hard label; `fast_R` at probability 0.505 is materially different from
`fast_R` at probability 0.95.

### Event-clock versus bar-clock meaning

The HMM updates when a completed event becomes known at its DCC. Mapping the state back to bars carries the latest
completed-event state forward until the next DCC.

The shaded bar region means:

> The most recently confirmed completed event had this filtered velocity state.

It does not mean:

> Every shaded bar was independently classified as slow or fast.

Current bars may look visually fast while still shaded `slow_R` because the new leg is incomplete. A visual mismatch may
also arise because the eye reacts to candle size or oscillation whereas R measures extreme-to-extreme displacement per
bar.

## Audit 6 — causal next-event relevance

Audit 6 aligns information known for event $n$ at its DCC with outcomes belonging strictly to event $n+1$. It asks
whether the filtered velocity environment has forward relevance after confirmation.

Its strongest economic finding is direction-neutral tempo persistence:

- after `fast_R`, the next event tends to complete in fewer bars;
- the next DCC tends to arrive sooner;
- next-event R tends to be higher;
- next-event TMV is much less differentiated than T;
- slow activity is highly persistent, while fast activity occurs in clusters.

This does not establish directional return predictability, a profitable entry, or guaranteed overshoot continuation.

### Exploratory Audit 6 results

| Symbol | Theta | OOS current slow | OOS current fast | Slow -> next fast | Fast -> next fast | Next median T after slow | Next median T after fast |
|---|---:|---:|---:|---:|---:|---:|---:|
| `US500.r` | 0.300% | 649 | 80 | 4.47% | 63.75% | 29.0 | 16.5 |
| `EURUSD.r` | 0.112% | 1,018 | 193 | 6.39% | 66.32% | 34.0 | 12.0 |

At EURUSD 0.112%, the next-event median TMV was nearly identical after slow and fast states, while median T fell from 34
to 12 bars. This makes the economic interpretation especially clear: the state primarily distinguishes the time taken
to cover broadly comparable structural distances.

HMM-informed probability forecasts improved over a simple logistic current-`log(R)` benchmark on both exploratory
symbols. This is evidence consistent with useful state history, but it does not yet isolate Markov memory from the HMM's
nonlinear transformation of current R. A flexible R-only or emission-only benchmark is still required.

## Audit 7 — recent-event economic casebook

Audit 7 is the qualitative causal-reading exercise. It selects recent examples of:

- `slow_R -> slow_R`;
- `slow_R -> fast_R`;
- `fast_R -> fast_R`;
- `fast_R -> slow_R`.

The transition arrow refers to the previous completed-event state and current completed-event state. It does not refer
to the current state and an unknown future state.

At the current DCC, the completed leg, confirmed extreme, TMV, T, R, filtered probability, and new live DC mode are
known. The next extreme, post-confirmation excursion, next DCC, and next state are hindsight-only outcomes.

The required verbal reading is:

> The prior [up/down] leg completed with [slow/fast] normalized velocity; the opposite DCC has now put the process into
> [down/up] live mode.

Audit 7 demonstrated that:

- slow does not mean small or motionless;
- fast does not guarantee a large following overshoot;
- a large TMV event can remain slow when it takes many bars;
- a moderate current R can remain fast when prior fast-state probability is strong;
- the completed-event velocity state and current live direction have separate responsibilities.

Audit 7 establishes semantic intuition. It is not a performance test and its selected cases are not statistically
representative.

## Exploratory threshold lessons

| Symbol | Theta | Completed events | Median T | Train fast share | OOS fast share | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| `US500.r` | 0.300% | 3,649 | approximately 27–28 | approximately 20% | approximately 11% | Useful single-threshold structural scale |
| `EURUSD.r` | 0.300% | 1,238 | 124 | 12.74% | 3.23% | Multi-session scale; too sparse for stable fast-state OOS inference |
| `EURUSD.r` | 0.112% | 6,060 | 22 | 29.75% | 15.92% | More useful intraday/event-time intuition scale |

Threshold is a representation parameter:

> the minimum price excursion considered structurally meaningful.

It changes the event clock and must be understood in market/risk terms. It must not be selected by optimizing returns.

## Mandatory conduit exit criteria

### Completed at the single-threshold level

- [x] Explain every event landmark and the opposite-DCC mode switch.
- [x] Reconstruct representative TMV, T, and R values from raw bars.
- [x] Separate completed-leg direction from live DC mode.
- [x] Identify the information timestamp and distinguish known information from hindsight.
- [x] Interpret `slow_R`, `fast_R`, and their filtered probabilities without assigning direction.
- [x] Explain why identical R values can receive different HMM labels.
- [x] Interpret event-clock labels mapped into bar time.
- [x] Read and explain Audit 6 and Audit 7 economically.
- [x] Reproduce the single-threshold mechanism on two instruments for intuition.

### Still required before the formal programme begins

- [ ] Introduce exactly two thresholds and understand their nesting visually.
- [ ] Distinguish small-scale mode reversals from large-scale structural reversals.
- [ ] Inspect directional agreement and disagreement across the two scales.
- [ ] Inspect all four slow/fast cross-threshold combinations without assuming their meaning.
- [ ] Determine whether small-scale fast activity propagates into the large-scale event process.
- [ ] Repeat the causal and economic casebook at two thresholds.
- [ ] Add a third threshold only after the two-threshold structure is explainable by inspection.
- [ ] Stop at the smallest hierarchy that provides interpretable incremental information.

No multivariate HMM, feature concatenation, trading rule, or alpha backtest is permitted merely to bypass an unfinished
item in this conduit.

## Research-integrity status and evidence reset

The current results are exploratory intuition evidence only:

- US500 and EURUSD were both inspected before a formal pilot was selected and frozen.
- The current chronological 80/20 splits were used diagnostically, not protected as untouched final tests.
- EURUSD theta was changed from 0.300% to 0.112% after inspecting the first result.
- Emission families and audit designs were inspected on the same available history.
- No return, strategy, cost, or trade-performance hypothesis has been tested.

Consequences:

1. Neither symbol currently qualifies as an untouched external-validation result.
2. The current OOS tables cannot close a formal predictive or trading claim.
3. After the intuition conduit, a pilot, partitions, representation parameters, baselines, and execution contract must
   be frozen prospectively.
4. Final validation must use genuinely untouched time periods or a newly declared walk-forward design.

This reset preserves what has been learned without pretending the learning process produced confirmatory evidence.

## Next mandatory conduit step

Introduce two thresholds slowly. Do not fit a multivariate model first.

For each threshold, retain separate causal fields for:

- live DC mode;
- latest completed-event direction;
- information timestamp;
- TMV, T, and R;
- filtered slow/fast probability;
- event age in bar time.

Then inspect:

```text
large up + small up       -> directional alignment
large up + small down     -> small-scale pullback inside larger up structure
large down + small up     -> small-scale rebound inside larger down structure
large down + small down   -> directional alignment

large slow + small slow   -> quiet across both scales
large slow + small fast   -> local activity burst not yet propagated
large fast + small slow   -> large-scale active phase with small-scale cooling
large fast + small fast   -> synchronized activity expansion
```

These are inspection hypotheses, not accepted economic definitions. Their meaning must be earned through nested-event
plots, causal timestamps, recent-bar casebooks, and next-event audits.

## Current chronological intuition roadmap

This table supersedes earlier informal status lists. "Implemented, pending run" means the notebook and its completion
gate exist, but no empirical conclusion is accepted until the notebook has been executed and interpreted. Model phases
20-24 were implemented in one sprint so that selection, validation, economic, and cross-market criteria were frozen
before model outputs were inspected. Their inferential execution remains ordered: 20 -> 21 -> 22 -> 23 -> 24.

| Phase | Purpose | Status |
|---|---|---|
| 0. Pre-exploration contract | Establish causality, information timestamps, event IDs and the intuition-first sequence | Done |
| 1. Single-threshold mechanics | DCC, live mode, completed legs, TMV, T, R, overshoots and timing | Done |
| 2. Single-threshold HMM | Event-time states, causal filtering, bar mapping and TMV-T interpretation | Done |
| 3. Initial cross-symbol reproduction | Reproduce single-threshold interpretation on EURUSD and US500 | Done at introductory level |
| 4. Two-threshold mechanics | Independent clocks, agreement, counter-moves, propagation, rejection and nesting | Done |
| 5. Two-threshold causal relationships | Initiating-event characteristics, future outcomes, resolution bars and diagnostic probabilities | Done |
| 6. Two-threshold robustness | Repeat across USDJPY and several threshold pairs | Done at foundational level |
| 7. Three-threshold mechanics | Small -> medium -> large propagation ladder and eight configurations | Done |
| 8. Three-threshold linkage | Pin one seed and link exact event-ID hand-offs through two stages | Done |
| 9. Three-threshold causal live development | Stateful pre-resolution progress, survival conditioning and fragmentation | Done |
| 10. Three-threshold interpretation/robustness | Consolidate linkage and live-development conclusions | Done |
| 11. Four-threshold mechanics | Sixteen configurations, agreement breadth, coherent depth and fragmentation | Done |
| 12. Four-threshold linkage | Link small -> medium -> large -> macro lineages | Done |
| 13. Four-threshold causal live development | Follow three stages causally and measure live progress | Done |
| 14. Five-threshold mechanics and grid design | Compare linear and constant-ratio five-clock hierarchies | Done |
| 15. Five-threshold interpretation | Read the 32 configurations and decide what the grid comparison teaches | Done |
| 16. Five-threshold linkage | Link four adjacent contests into one small-origin lineage | Done |
| 17. Five-threshold causal live development | Track attained depth, progress, survival and fragmentation through four stages | Done |
| 18. Five-threshold robustness | Check structural conclusions across symbols, periods and grid choices | Done |
| 19. Multiscale representation design | Define the causal feature/state representation for arbitrary N thresholds | Done |
| 20. Interpretable regime baseline | Classify coherence, shallow/deep counter-moves and fragmentation directly | Run complete; interpretation pending |
| 21. Probabilistic regime models | Compare clustering, mixtures and causal-filtered HMMs with the direct baseline | Run complete; interpretation pending |
| 22. Causal and out-of-sample validation | Validate timing, stability, persistence, confidence and incremental usefulness | Run complete; interpretation pending |
| 23. Economic interpretation | Define state meaning without creating a trading strategy | Run complete; interpretation pending |
| 24. Cross-market robustness | Test frozen markets, periods, frequencies and threshold ladders | Run complete; interpretation pending |
| 25. Code modularization | Extract stable repeated mechanics while retaining scale-specific teaching logic | Done at the notebook-safe boundary |
| 26. Reusable validation/tests | Add timing, ID, nesting, prefix-causality and same-bar invariants | Done at foundational level |
| 27. Educational repository extraction | Curate the examples into understanding_directional_change_basics | Pending |
| 28. Textbook construction | Turn chronological notebooks into chapters, exercises and interpretation gates | Pending |
| 29. Final reproducibility pass | Execute in a clean environment and specify release dependencies | Pending |

### Phase 20-24 evidence boundary

- GBPUSD is the exploratory pilot for model-family and state-count selection.
- The split is chronological 60% train, 20% validation and 20% test; scaling and semantic mapping fit on train only.
- The test is opened only after validation selection, but it is not pristine because this history was already explored.
- Cross-market cases use a frozen procedure and are robustness evidence, not untouched external confirmation.
- Future movement, volatility and DCC activity are diagnostic outcomes only. No position direction, entry, exit, cost,
  PnL, or trading claim is introduced in phases 20-24.

# Part II — Formal research programme

Part II is the original formal programme. It is preserved as the downstream standard and remains inactive until Part I
is complete.

## Objective

Define the smallest defensible research programme needed to decide whether a directional-change representation can
support a causal, executable, and conditionally robust trading idea.

## Governing research strategy

> **One symbol is the laboratory for understanding the mechanism. Other symbols are the test of whether we found a
> mechanism or merely learned that symbol.**

The work proceeds in one direction only:

1. **Perfect the intuition on one pilot symbol.** Understand the event geometry, causal observability, and economic
   meaning of DC before hunting for alpha.
2. **Form one falsifiable hypothesis.** Test continuation, reversal, exhaustion, or regime information one at a time;
   do not combine mechanisms until one survives alone.
3. **Confirm value on the pilot.** Use separated discovery, calibration, validation, and untouched-test periods. A
   promising discovery result is not confirmation.
4. **Componentize only after confirmation.** Freeze the valuable behaviour first, then separate the event engine,
   features, decision rule, execution policy, evaluation, and visualization.
5. **Run the frozen component on other symbols.** Cross-symbol work is external validation, not another opportunity to
   redesign the story.

This sequence is deliberately narrow. New features, regimes, classifiers, and parameter families remain out of scope
until the current phase's exit criteria are met.

### Journey guardrails

- Use exactly one pilot symbol until the pilot final test is complete.
- Select the pilot for data quality and deployment relevance, never because it produced the best exploratory result.
- Fix all pilot partitions before inspecting strategy performance.
- Do not inspect outcome statistics on other symbols during pilot research.
- Do not open the pilot's final test while the mechanism, parameters, conditional hypothesis, or execution model can
  still change.
- Add a feature only when the current mechanism requires information not already represented by a simpler baseline.
- Test one mechanism at a time and keep a written falsification condition.
- Do not productionize speculative abstractions. Maintain clear conceptual boundaries, but componentize only after the
  pilot demonstrates value.
- On external symbols, allow only predeclared market-scale normalization and instrument-specific costs. Any additional
  per-symbol tuning is a new research experiment, not evidence of generalization.

## Starting references

- [Directional-change usage guide](../../docs/directional_change/how_to_use_dc.md)
- [Directional-change system overview](../../docs/directional_change/OVERVIEW.md)
- [Feasibility gate](./DC_FEASIBILITY_GATE.md)

These references describe available concepts and infrastructure. Their prior empirical conclusions are not assumed.

## Candidate mechanism

State the economic or behavioural mechanism before selecting features, parameters, or evaluation periods.

- **Market behaviour:** TBD
- **Why directional change represents it:** TBD
- **Expected position direction:** TBD
- **Expected holding horizon:** TBD
- **Conditions where it should work:** TBD
- **Conditions where it should fail:** TBD

## Scope

- **Pilot symbol:** TBD — chosen once, before outcome inspection
- **External-validation symbols:** embargoed until the pilot specification is frozen
- **Venue and data source:** TBD
- **Sampling frequency:** TBD
- **History available:** TBD
- **Intended deployment horizon:** TBD
- **Operational constraints:** TBD

## Assumptions to challenge

- [ ] Directional-change events add information beyond conventional return, volatility, and trend features.
- [ ] The event threshold can be specified without optimizing on final-period returns.
- [ ] Events are observable with the available bar resolution and timestamp semantics.
- [ ] The expected holding period is long enough to clear realistic trading costs.
- [ ] Any apparent edge recurs across non-contiguous periods and instruments.
- [ ] A proposed regime condition is causal and useful for entry gating or position sizing.

## Research questions

1. What precise prediction is made at each directional-change event?
2. What is the simplest non-DC baseline that expresses the same proposed mechanism?
3. Which parameters define the representation, and which define the trading decision?
4. How will parameter selection be isolated from final evaluation?
5. Under which causal and recurring conditions should the prediction be strongest?
6. What observation would falsify the mechanism?

## Feature and parameter inventory

Document only features required by the candidate mechanism.

| Feature or state | Definition | Parameters | Available at | Causal? | Intended use |
|---|---|---|---|---|---|
| TBD | TBD | TBD | TBD | TBD | TBD |

### Parameter classification

For every parameter, classify it before testing:

- **Market/data constraint:** resolution, tick size, spread, or sample sufficiency.
- **Representation parameter:** changes the directional-change event stream.
- **Decision parameter:** changes entry, exit, gating, or sizing.
- **Risk parameter:** changes exposure or loss limits without changing the alpha thesis.

## Data and provenance audit

- [ ] Identify raw data paths, field definitions, timezone, and session calendar.
- [ ] Verify ordering, duplicates, gaps, stale bars, and invalid prices.
- [ ] Record bid/ask availability and the cost proxy when quotes are unavailable.
- [ ] Confirm whether highs and lows are causally usable by the event parser.
- [ ] Trace every derived feature to information available at the decision timestamp.
- [ ] Define instrument and period inclusion rules before looking at performance.

## Experimental partitions

- **Pilot intuition/discovery:** TBD
- **Pilot parameter calibration:** TBD
- **Pilot model/gate validation:** TBD
- **Pilot final untouched test:** TBD
- **Frozen cross-instrument confirmation:** TBD

All pilot boundaries must be fixed before strategy-performance inspection. The pilot final test must remain untouched
until the mechanism, parameters, cost model, and conditional hypotheses are frozen. External-symbol outcome data remains
embargoed until the pilot final decision and component interface are frozen.

## Baselines and nulls

- [ ] Naive directional-change rule
- [ ] Conventional price-based baseline expressing the same mechanism
- [ ] Equal-exposure or equal-turnover baseline
- [ ] Circular-shift timing null
- [ ] Rate-matched random gate for any entry filter
- [ ] Buy-and-hold or always-flat sanity references where meaningful

## Work phases

### Phase 0 — choose the laboratory and protect the evidence

- [ ] Select one pilot symbol from data quality and deployment criteria.
- [ ] Audit its data and freeze all pilot partitions.
- [ ] Embargo other-symbol outcome analysis.
- [ ] Freeze timestamp, signal, fill, return, and cost conventions.

**Exit only when:** the pilot choice is justified without performance, the data audit passes, partitions are recorded,
and the final pilot period has not been inspected.

### Phase 1 — perfect the DC intuition

- [ ] Verify the event parser on deterministic synthetic paths.
- [ ] Test prefix consistency for every purportedly causal output.
- [ ] Explain extrema, confirmation points, DC legs, overshoots, TMV, duration, and event state bar by bar.
- [ ] Inspect threshold sensitivity as event geometry, not as a return optimization.
- [ ] Produce price charts that make event formation and causal availability visually unambiguous.

**Exit only when:** we can explain what is known at every bar, synthetic cases behave exactly as expected, and real event
charts make structural sense without reference to PnL.

### Phase 2 — specify one falsifiable mechanism

- [ ] Choose exactly one candidate: continuation, reversal, exhaustion, or regime information.
- [ ] State the causal prediction, expected holding horizon, recurring conditions, and failure conditions.
- [ ] Define the simplest non-DC baseline expressing the same economic idea.
- [ ] Translate the mechanism into the smallest possible position stream.
- [ ] Predeclare baselines, nulls, conditional tests, and KEEP/REVISE/KILL criteria.

**Exit only when:** one mechanism can be stated without reference to observed performance and an outcome capable of
falsifying it is written down.

### Phase 3 — discover and calibrate on the pilot

- [ ] Use only the pilot discovery and calibration partitions.
- [ ] Compare the minimal stream with predeclared baselines and timing nulls.
- [ ] Apply explicit execution latency and realistic costs.
- [ ] Inspect actual trades and gross/net equity curves.
- [ ] Evaluate intrinsic conditions with `TemporalPerformanceAnalyzer`.
- [ ] Evaluate any regime substrate with `RegimePerformanceAnalyzer`.
- [ ] Separate timing skill from structural beta with the timing-significance tools.
- [ ] Add complexity only to address a documented failure of the minimal mechanism.

**Exit only when:** the idea is alive under at least one recurring, actionable, causally identifiable condition; it beats
the matched baseline and timing null; and performance is not carried by a few contiguous windows or exceptional trades.

### Phase 4 — confirm on pilot validation

- [ ] Freeze a provisional specification before entering validation.
- [ ] Run walk-forward or expanding-window evaluation on the validation partition.
- [ ] Perturb thresholds, costs, latency, and holding rules.
- [ ] Quantify uncertainty with a dependence-aware bootstrap or equivalent method.
- [ ] Retest every diagnostic condition as a causal gate or sizer.
- [ ] Record all failures and specification changes; return to Phase 3 after any material change.

**Exit only when:** the provisional specification survives realistic costs, plausible perturbations, and non-contiguous
validation periods without relying on an acausal condition. Any material redesign resets this phase.

### Phase 5 — open the pilot final test once

- [ ] Freeze code, parameters, execution assumptions, conditions, and decision criteria.
- [ ] Run the untouched pilot test exactly once.
- [ ] Produce conditional dashboards and trade-level visualizations before assigning a verdict.
- [ ] Record the complete outcome without post-test repair.
- [ ] Assign KEEP, REVISE, or KILL using the frozen criteria.

**Exit only when:** the untouched result supports KEEP. REVISE returns the work to Phase 2 or 3 with a newly protected
test period; KILL ends this mechanism. Neither outcome permits editing the frozen result.

### Phase 6 — componentize the confirmed behaviour

- [ ] Separate the causal event engine, feature extraction, decision rule, execution/sizing policy, evaluators, and
  visualization.
- [ ] Add deterministic event, causality, alignment, cost, and interface tests.
- [ ] Make symbol-specific market scale and costs explicit inputs rather than hidden constants.
- [ ] Reproduce the frozen pilot result through the componentized path.

**Exit only when:** the componentized implementation reproduces the frozen pilot behaviour and results, with no research
logic hidden in notebook state or symbol-specific branches.

### Phase 7 — frozen cross-symbol validation

- [ ] Predeclare the external-symbol set and permitted normalization inputs.
- [ ] Run the frozen component without symbol-by-symbol redesign.
- [ ] Report conditional gross/net results, trade views, and failure modes for every symbol.
- [ ] Separate universal behaviour, lawful scale/cost adaptation, and outright non-transfer.

**Exit only when:** the same mechanism recurs on external symbols under predeclared adaptations. If each symbol requires a
different rule or explanation, conclude that the pilot taught us the symbol rather than a transferable mechanism.

## Execution contract

- **Signal timestamp:** TBD
- **Earliest actionable timestamp:** TBD
- **Fill rule:** TBD
- **Return convention:** TBD
- **Spread and commission:** TBD
- **Slippage:** TBD
- **Position sizing:** TBD
- **Maximum exposure:** TBD
- **Exit and stop semantics:** TBD

## Conditional-analysis contract

An aggregate result cannot close the research question.

- **KEEP:** an edge survives realistic costs and untouched evaluation under at least one actionable, recurring, causal
  condition.
- **REVISE:** a plausible mechanism remains, but the specification or causal condition is not sufficiently identified.
- **KILL:** the idea fails under every tested condition, or apparent performance is isolated to non-recurring windows
  without a defensible reason to repeat.

## Required artefacts

- [ ] Reproducible notebook or report
- [ ] Data and causality audit
- [ ] Baseline and null comparison
- [ ] Conditional performance dashboards
- [ ] Trade-level price chart with entries and exits
- [ ] Gross and net equity/PnL curves
- [ ] Cost, latency, and parameter sensitivity analysis
- [ ] Walk-forward and cross-instrument results
- [ ] Final decision record

## Work queue

| Priority | Task | Purpose | Dependency | Status |
|---|---|---|---|---|
| 1 | Choose the pilot and freeze its partitions | Establish the laboratory without selection bias | None | Not started |
| 2 | Freeze the execution contract | Prevent timestamp and cost ambiguity | Pilot choice | Not started |
| 3 | Master and visualize DC event geometry | Build causal intuition before alpha hunting | Items 1–2 | Part I single-threshold milestone complete; hierarchy pending |
| 4 | Specify one falsifiable mechanism | Prevent a convoluted multi-hypothesis search | Event intuition | Parked until Part I exit |
| 5 | Design baselines, nulls, and phase criteria | Protect validation and the final test | Mechanism | Parked until Part I exit |
| 6 | Implement the smallest pilot test | Fail fast before adding complexity | Items 1–5 | Parked until Part I exit |

## Decision log

| Date | Decision | Evidence | Consequence | Revisit condition |
|---|---|---|---|---|
| 2026-08-20 | Make hands-on DC intuition a mandatory conduit before the original formal programme | Single-threshold work exposed essential distinctions between completed legs, opposite DCCs, live modes, event clocks, and bar clocks | Part I now gates every item in Part II | Revisit only if a smaller process demonstrably achieves the same causal and economic understanding |
| 2026-08-20 | Treat live DC mode and completed-event velocity as separate state variables | R is unsigned; the opposite DCC confirms the old leg and switches the live mode | Never interpret `slow_R` or `fast_R` as bullish or bearish | Revisit only if direction is explicitly added as a separate causal observation |
| 2026-08-20 | Retain filtered probability rather than relying only on the hard HMM label | Nearly identical R observations received different labels because of prior state probability; boundary labels can be close to 0.5 | All later use and plots must expose posterior confidence | Revisit if the HMM is replaced by a non-probabilistic representation |
| 2026-08-20 | Treat Audit 6 as evidence of event-tempo persistence, not directional alpha | On US500 0.300% and EURUSD 0.112%, fast states were followed by shorter-T, earlier-confirming next events | Velocity state is a candidate direction-neutral substrate only | Revisit after a flexible R-only benchmark and protected validation |
| 2026-08-20 | Reset all current symbol and OOS results to exploratory status | Symbols, thresholds, emission families, and audits were inspected before a pilot and partitions were frozen | No current result may be cited as untouched confirmation or external validation | Revisit only with a prospectively frozen experiment |
| 2026-08-20 | Introduce two thresholds before any multivariate HMM or alpha test | Single-threshold semantics are now explainable; cross-scale nesting and propagation remain unknown | Next work is visual, causal two-threshold intuition | Revisit after the two-threshold exit criteria are completed |

## Open questions

- Which two thresholds best express small and large structure without using return outcomes for selection?
- How should small events be nested into large events while preserving each threshold's information timestamp?
- Does small-scale fast activity causally propagate into the large-scale event process?
- Does HMM history beat a flexible nonlinear current-R-only or emission-only benchmark?
- How should event-state age be represented when a completed-event label is carried across many bars?
- Can useful live, incomplete-event velocity be defined without leaking the eventual extreme?
- Which symbol will be the formal pilot, and which future periods will remain genuinely protected?
- What exact close/high/low, signal, fill, spread, slippage, and session conventions will govern the formal experiment?
