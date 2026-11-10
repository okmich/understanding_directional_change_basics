# Completion-gate solution guide

Open this guide only after writing your own response. These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

## Chapter 0 — Pre-exploration contract

- An extreme has an occurrence time; its completed-event statistics have the later DCC information time.
- Post-confirmation calculation does not authorize backdating.
- Future outcomes may group rows diagnostically but may not enter causal features.
- Event IDs preserve identity across same timestamps, thresholds, hand-offs, and repeated joins.

## Chapter 1 — Directional-change mechanics

- A downward DCC is the first sampled close at least $\theta$ below the running peak; it confirms the peak and switches mode down.
- An upward DCC is the symmetric rise from the running trough.
- The ending extreme is retrospective; the new mode is causal at the DCC close.
- Same-bar multi-threshold order is unknowable from close-only data.

## Chapter 2 — TMV, T, R, and overshoot

- Recalculate TMV from the two extremes, $T$ from their positions, and $R=\mathrm{TMV}\theta/T$.
- $T=1$ means consecutive extreme positions, not necessarily an extreme and DCC on adjacent bars.
- Frequent short events suggest the threshold may be small relative to bar-scale movement or noise.
- Use median and tails beside means because the indicators are right-skewed and path-dependent.
- The overshoot runs from the opening DCC (the previous row's confirmation) to the ending extreme; $(1\pm\mathrm{DC}\,\theta)(1\pm\mathrm{OS}\,\theta)=1\pm\mathrm{TMV}\,\theta$, and the completed overshoot is known only at the leg's own confirming DCC.

## Chapter 3 — Event-time state models

- The event HMM updates once per completed event; a bar HMM would model a different sequence.
- Equal current R can produce different filtered posteriors because the previous posterior and transition matrix differ.
- Forward-filled bar states repeat the latest event result; they do not add evidence.
- Bar occupancy weights event duration and therefore differs from event occupancy; read both columns of the occupancy table.
- `slow_R` is the state with the lower filtered-probability-weighted training mean of raw R, not necessarily the lower log-R emission mean.

## Chapter 4 — HMM economic meaning

- State labels are semantic summaries learned from training, not thresholds on individual R values.
- A visually fast current segment may still display the previous completed event's state.
- At a DCC, the completed leg and filtered state are known; the next extreme, event, and state are not.
- Any claim about the next event must come from chronological OOS evidence and incremental metrics, not the state chart.
- Audit 6's target is the HMM's own next label, computed from the current filtered probability, so `p_fast_r` helps there by construction; only the model-free Audit 6b targets (next log R, next R above the training median) test whether history adds information.

## Chapter 5 — Distribution choice and reproduction

- Real-support families can use log-R; positive-support families can model raw R.
- Density comparison across transforms requires the Jacobian so likelihoods share the raw-R scale. pomegranate's LogNormal is a density over log R too, so it needs the same correction; afterwards Normal(log R) and LogNormal(R) tie exactly.
- A lead smaller than the fold-to-fold or seed-to-seed spread is not a ranking.
- Prefer stable OOS predictive density and non-collapsed interpretable states over balanced occupancy.
- A near-zero sequence-order premium means transitions add little beyond marginal mixture partitioning.
- Transfer concerns meanings and qualitative relationships, not identical percentages.

## Chapter 6 — Two independent clocks

- Every threshold independently tracks its extreme and confirmations.
- Small/large disagreement is a current counter-scale state, not a large-scale reversal.
- Configuration occupancy is duration-weighted bar share.
- A small DCC ignored by the large scale has not reversed far enough from the large running extreme.
- "Small confirms first" is a near-invariant. Each threshold is relative to its own running extreme, so the large clock can rarely confirm first; `find_upper_led_reversals` lists those bars.

## Chapter 7 — Agreement, propagation, and rejection

- Propagation occurs when the upper DCC confirms target before the lower clock reverses; rejection is the opposite race result.
- The resolving DCC is the outcome-information time and is excluded from live rows.
- Odd nesting applies to correctly bounded, completed, clean intervals; initialization and same-bar ambiguity must remain explicit.
- Odd parity is a near-invariant: an interval in which the upper clock confirmed first holds an even lower count and is flagged `parity_violation`, not asserted away.
- A same-bar propagation (seed and joining upper DCC on one bar) is a zero-bar *resolved* propagation. `ambiguous_same_bar` is different: opposing lower and upper DCCs resolving an *active* attempt on one bar. A rejection can never take zero bars.
- Propagation rates are conditional on the declared attempt cohort.

## Chapter 8 — The initiating small DCC

- The seed reveals the completed prior leg and begins the new opposing mode simultaneously.
- Completed prior-leg TMV/T/R do not measure the new counter-leg.
- Large live context is unfinished and must not be mislabeled completed R.
- Heavy outcome overlap and nearest opposite-outcome pairs reject a deterministic initiation rule.
- This lab (USDJPY 25/50) changes both market and pair relative to Chapters 6–7 (EURUSD 20/40); a numerical difference between them cannot be attributed to either alone.

## Chapter 9 — Counter-leg development and survival

- Checkpoint-zero live TMV includes the move needed to confirm the seed; post-DCC excursion begins at zero.
- Current excursion can retrace; maximum excursion preserves earlier reach.
- Later checkpoints contain unresolved survivors, not the original cohort.
- Later separation describes when paths diverge and is not automatically an initiation-time forecast.

## Chapter 10 — Two-threshold robustness

- Absolute thresholds change the size of every clock; ratios change the relative propagation hurdle.
- Structural semantics should recur while event counts, durations, and rates change.
- With nesting parity, each large interval holds one propagation and $(n+1)/2$ attempts, so the all-resolved rate is about $2/(N_S/N_L+1)$. The rate follows the event-count ratio, which follows the threshold ratio, so the 20/30 vs 20/40 comparison moves it far more than 15/30 vs 25/50.
- Fixed-cohort comparison: the same 20-bar survivors measured at their seed show how much of the 20-bar separation is information rather than a change of cohort.
- Same-bar (propagation only), ambiguous, unresolved, and parity-exception counts are reported before any rate.
- Weak sample size, direction concentration, and period concentration must be reported.
- Reproduction is neither threshold optimization nor profitability evidence.

## Chapter 11 — Three-scale configurations

- `up/up/up` and `down/down/down` are broad agreement.
- `down/up/up` and `up/down/down` are small-only opposition.
- `down/down/up` and `up/up/down` show propagation through medium.
- `down/up/down` and `up/down/up` are fragmented.
- The 2.0 and 1.5 adjacent ratios imply different edge behavior.

## Chapter 12 — Exact event-ID linkage

- A Stage-1 propagating medium DCC is the only valid Stage-2 hand-off.
- Timestamp proximity is insufficient because multiple candidate events may occur nearby.
- Terminal depths 0/1/2 are final outcomes; attained depth changes causally at exact hand-offs.
- $P(D\ge2)=P(D\ge1)P(D\ge2\mid D\ge1)$ is the chain rule for one cohort, not independence. It holds by arithmetic, so it is not a test; the checks that can fail are the genealogical ones (every depth-1+ lineage has an exact medium hand-off and a propagated first edge).
- With three-scale broad-agreement roots, the linked and unconditional medium-to-large rates coincide: a medium DCC against large is almost always preceded by a small DCC that left three-scale agreement and propagated through it, so nearly every medium-to-large attempt is linked. They differ under narrower roots (four-scale agreement), lineage filters such as strict-clean, or deeper hand-offs.
- The all-resolved ladder is unbiased. Strict-clean removes same-bar stages, which are always propagations, so its reach rates are lower by construction.

## Chapter 13 — Two-stage live development

- The small seed remains lineage identity; the medium event only advances the stage.
- Later small DCCs inside Stage 2 are nested activity.
- Stage-1 propagation can be known while Stage-2 and terminal depth remain unknown.
- Every row's feature time is current; its stage and terminal outcome-information times are later.
- The active lower and upper clocks cannot fire inside a stage panel, because either DCC is the resolution bar. Nested activity therefore comes only from clocks below the lower clock, and Stage 1 has none.
- Whether live progress adds information is judged against the completed seed and hand-off legs on the same survivor cohort (Live Audit 2b). A positive out-of-sample gain is diagnostic, not a forecast.

## Chapter 14 — Three-scale robustness

- Common dates prevent period composition from masquerading as symbol effects.
- Predeclared cases prevent result-driven threshold selection.
- Exact probabilities are case-specific; identity and timing semantics are structural.
- Live-progress evidence must be checked across direction, period, symbol, and ladder and compared with initiation geometry.
- Compare 20-bar survivors with the same lineages at initiation. Comparing them with the full initiation cohort mixes information gain with survivor selection; Audit 6 reports the two separately.

## Chapter 15 — Four-scale configurations

- Direction counts lose scale order; boundary count restores it.
- `down/down/up/up` is one coherent boundary; `down/up/down/down` has two and is fragmented.
- Coherent depth is undefined when multiple boundaries exist.
- `coherent_frontier` means at most one boundary, so it includes broad agreement; "exactly one boundary" is `direction_boundaries == 1`.
- Linear absolute spacing creates unequal adjacent ratios and edge behavior.

## Chapter 16 — Three-stage linkage

- Broad agreement on the prior bar gives the seed a definite origin.
- Medium and large IDs are exact hand-offs; the small ID remains root.
- Terminal depths 0–3 identify the stage of final rejection or macro attainment.
- A deep lineage may contain retracements; confirmation genealogy does not require monotonic price.
- Linked stage rates differ from unconditional edge rates here because a root needs four-scale agreement; at three scales they coincide.
- Report reach rates on the all-resolved cohort. The strict-clean cohort drops same-bar stages (always propagations) and is biased low; it is for live-interval work.

## Chapter 17 — Four-scale live development

- Stage-local features identify the active contest; hierarchy-wide features identify surrounding coherence or fragmentation.
- Agreement breadth and boundary count are not substitutes, but they can only differ from Stage 3 on. In Stages 1–2 they are deterministic functions of each other, so their AUCs coincide.
- Later checkpoints are survival-selected, and later AUC cannot be backdated to initiation.
- Deep attained depth remains distinct from unknown terminal depth.

## Chapter 18 — Five clocks and grid design

- Five is a pedagogical scale count, not a standard calibration.
- Linear ratios are 2.0, 1.5, 1.33, and 1.25; the geometric ladder holds 1.5.
- Shared small thresholds produce the same small clock; different higher thresholds produce different causal hierarchies.
- Grid choice must follow a predeclared structural objective, not ex-post outcomes. Here the rule is a constant adjacent ratio, so every hand-off asks the same relative question; adequacy does not separate the grids (both show 32 configurations and the same outer-event count).
- Adjacent propagation rates are close to $2/(N_{lower}/N_{upper}+1)$: equal ratios give similar rates, shrinking linear ratios give rising rates, and neither is economic evidence.

## Chapter 19 — Thirty-two configurations

- Five binary modes produce $2^5=32$ vectors.
- The vector is lossless; breadth, boundary count, and coherent depth are summaries.
- One boundary is coherent, two or more are fragmented, and all-equal is broad agreement. The code's `coherent_frontier` flag is "at most one boundary", so it also includes broad agreement.
- Unequal occupancy is expected and is not a defect by itself.

## Chapter 20 — Four-stage linkage

- Exact hand-offs form `small -> medium -> large -> macro -> outer` under one seed.
- Depth zero is a real rejected small attempt; depth four confirms outer reach, not continuation.
- Attained depth updates at each upper DCC; terminal depth waits for final resolution.
- Strict-clean live cohorts exclude same-bar stages but report them separately. Every excluded same-bar stage is a propagation, so the strict-clean ladder is biased low; the all-resolved ladder is the unbiased description.
- Ambiguous, unresolved, and unlinked lineages have no terminal depth; `max_attained_depth` records how far they got before ending.
- Stage-anatomy counts exclude the resolving DCC, so a propagated stage's upper-scale count measures activity before the propagation.

## Chapter 21 — Five-scale live development

- Pre-resolution target progress remains below one by construction.
- The lower mode is target and the upper mode is origin during each adjacent contest.
- Sub-lower DCC counts and firing rates, breadth, and boundary count describe different aspects of the path. The active lower and upper clocks' own counts are zero by construction and carry no information.
- Outcome separation appearing later must be interpreted with survivor selection and direction checks (Live Audit 2b splits by target mode).
- Live TMV/T/R describe the unfinished path; `seed_leg_*` and `stage_start_leg_*` are completed legs known at the seed and hand-off times. Live Audit 2c tests what the live path adds beyond them.

## Chapter 22 — Five-scale robustness

- Compare cases only after checking outer-event and lineage sample adequacy. The lineage accounting must reconcile: strict-clean + resolved-with-same-bar + ambiguous + unresolved + unlinked = eligible roots.
- The strict-clean ladder is biased down because only propagations can be same-bar; describe depth with the all-resolved ladder.
- Cross-symbol, absolute-scale, and grid-geometry comparisons change different axes.
- The primary ladder remains primary regardless of attractive ex-post rates.
- Robust conclusions are qualitative structural recurrences; exact occupancies and depths are case-specific.

## Chapter 23 — Arbitrary-N representation

- $N$ thresholds create $N$ scale nodes and $N-1$ adjacent edges.
- The scale state separates live and completed clocks and timestamps.
- The full ordered vector must remain because summaries cannot reconstruct fragmented shape.
- Bar time weights duration; union-event time weights event-bearing observations.
- Diagnostic resolutions must never be backward-joined to causal lineage rows.
- The notebook's explicit builders must match `dc_multiscale_research.build_multiscale_state` on every shared column; two drifting implementations would make later phases study a different object.

## Chapter 24 — Interpretable regime baseline

The final response must use the notebook output. Its logic should establish:

- structural class and direction are separate;
- shallow/deep are current scale fractions, not future outcomes;
- fragmented states have no single depth;
- preprocessing must retain fragmented observations or report and reject total class loss;
- bar and event clocks yield different occupancy;
- the taxonomy is a transparent comparator, not truth;
- discrete hierarchy geometry is not a valid continuous-density input, and neither is a zero-inflated point mass such as mode age 0 on the scale that just fired.

Do not mark G20 passed until you state what later models must add beyond the direct taxonomy.

## Chapter 25 — Probabilistic regime models

The final response must compare fitted output, but should establish:

- only HMM candidates carry filtered transition history;
- scaling and semantic mapping are training-only;
- raw state IDs remain the fitted objects;
- unsupported or surplus state semantics remain `unmatched`;
- variance-floor hits qualify confidence and likelihood, and the per-feature likelihood table shows whether a gain comes from floored features;
- restart agreement is read for every family before any partition is named;
- clock choice changes transition meaning;
- confidence, persistence, and baseline overlap are descriptive, not selection criteria alone.

## Chapter 26 — Causal and OOS validation

The final response must reconstruct the notebook's validation-only selection. It should verify:

- test results did not choose the family or state count;
- prefix invariance, occupancy floor, and immutable mapping pass;
- every eligible candidate clears the predeclared restart-ARI threshold;
- persistence is interpreted with confidence and switching;
- raw states drive partition metrics;
- bias-corrected, permutation-audited separation is compared with direction-neutral and direction-aware baselines;
- the block-bootstrap verdict, not a hand-picked positive difference, decides whether the model adds information beyond the stronger baseline;
- the test remains exploratory because the history was previously inspected.

## Chapter 27 — Economic interpretation

There is no generic empirical answer. Pass G23 only when every raw state has a state card covering hierarchy, ages, progress, activity, confidence, persistence, restart stability, variance-floor warnings, transitions, later diagnostic behavior, and added distinction beyond both direct baselines. No state card may specify a position or expected return.

## Chapter 28 — Cross-market robustness

There is no acceptable answer that drops inconvenient cases. A passing response must:

- account for all 45 declared structural cases;
- preserve common dates, fixed ladders, and frozen adequacy rules;
- select model specification only on GBP validation;
- refit but not reselect externally;
- apply identical eligibility rules externally and retain failures;
- compare permutation-audited separation with both direct baselines, and state "no information beyond baseline" for every market whose bootstrap verdict says so;
- report instability across shared calendar thirds, and inadequate cases;
- reject symbol-specific reinterpretation as non-transfer;
- avoid calling explored markets untouched confirmation.

## Chapter 29 — Reusable library

- Modules should centralize semantics that must not drift across notebooks.
- Synthetic invariant tests protect construction without depending on empirical outcomes.
- Provenance records both copied software lineage and prior conceptual work.
- A thin notebook still keeps the research question, configuration, evidence, and interpretation visible.

## Chapter 30 — Reproducibility and release

- A clean run must require only declared dependencies, data instructions, configuration, and commands.
- Saved outputs do not replace re-execution.
- Technical success must be followed by causal, statistical, economic, pedagogical, and attribution review.
- Previously explored samples and unresolved gates must appear in limitations.

## Final self-test

Close every notebook and explain this sequence from memory:

```text
DCC confirmation
-> completed leg versus live mode
-> independent threshold clocks
-> adjacent disagreement
-> exact linked hand-off
-> causal live development
-> attained versus terminal depth
-> arbitrary-N hierarchy
-> direct structural baseline
-> filtered probabilistic state
-> validation-only selection
-> economic interpretation without a trading claim
```

If any arrow requires future information to explain the current state, revisit the preceding chapter.

