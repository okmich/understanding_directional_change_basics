# Chapter 9 — Counter-leg development and survival

## Purpose

Follow the unresolved attempt after its seed using only measurements available on each bar.

## Pin the seed

Once the small DCC initiates opposition, keep its attempt ID fixed until rejection or propagation. Measure the new path rather than repeatedly redefining its beginning.

Useful causal fields include:

- bars elapsed since the seed;
- bars since the now-confirmed starting extreme;
- current and maximum post-DCC excursion;
- live small TMV, T, and R;
- progress toward the large DCC;
- current small and large modes.

At elapsed bar zero, post-DCC excursion is zero, but live small TMV is already near one threshold unit: the move required to confirm the seed occurred before and including the DCC. These are two clocks with different origins.

Current excursion can retrace without changing mode. Maximum excursion preserves earlier path reach. Live TMV can also fall because it uses current price relative to the confirmed extreme.

## Survival conditioning

The cohort still unresolved after 40 bars is not the initiation cohort. Fast resolutions have left it. Outcome rates, feature medians, and AUCs at later checkpoints describe selected survivors. They are not forecasts available at initiation.

## Lab

Run the live-development sections of [2_threshold_dc.ipynb](../2_threshold_dc.ipynb) and [2_threshold_dc_event_characteristics.ipynb](../2_threshold_dc_event_characteristics.ipynb).

Audit fixed checkpoints, survivor counts, trajectories, and recent paths. Confirm that the resolution bar is absent.

The two notebooks run the same live-development audit on different settings: EURUSD at 0.20% / 0.40% and USDJPY at 0.25% / 0.50%. Agreement between them is a first sign that the survival logic is structural. A numerical difference, however, mixes a market change with a threshold change; [2_threshold_dc_robustness.ipynb](../2_threshold_dc_robustness.ipynb) (Chapter 10) separates them.

## Mandatory exercises

1. Explain why live TMV can be positive at checkpoint zero.
2. Contrast current excursion with maximum excursion during a retracement.
3. Explain why progress can become more separating after the path develops without being an initiation-time forecast.
4. Compare the 20-bar survivors with the original cohort and list what has changed mechanically.
5. Identify the exact outcome-information bar for one propagation and one rejection.

## Completion gate G5 — Two-threshold causal relationships and live development

Before robustness or a third threshold, the learner must be able to:

1. Explain that the initiating small DCC simultaneously completes the prior small leg and begins the new counter-scale mode.
2. Identify which prior-leg TMV, T, and R values are causally known at initiation.
3. Explain why those completed features may overlap heavily between later propagated and rejected outcomes.
4. Define propagation as the upper-scale DCC confirming the target direction and rejection as the lower clock reversing before that confirmation.
5. Pin the initiating small event and follow elapsed time, current excursion, maximum excursion, live TMV/T/R, and progress toward the large threshold.
6. Explain why live TMV may start near or above one and why current excursion can fall while maximum excursion retains path information.
7. Identify the resolution bar and exclude it from every pre-resolution live panel.
8. Explain why later checkpoints contain only surviving unresolved attempts.
9. Explain why outcome-conditioned medians or AUCs are diagnostic hindsight even when every input feature is causal.
10. Compare actual paths in a nearest-opposite-outcome casebook and state why visual similarity at initiation does not imply identical outcomes.

**Locked-in statement:** The seed fixes the question, the live panel describes how the contest develops, and the outcome label remains hindsight until resolution.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Checkpoint-zero live TMV includes the move needed to confirm the seed; post-DCC excursion begins at zero.
- Current excursion can retrace; maximum excursion preserves earlier reach.
- Later checkpoints contain unresolved survivors, not the original cohort.
- Later separation describes when paths diverge and is not automatically an initiation-time forecast.

</details>

## Locked in

> The seed fixes the question; causal live features describe how the unresolved contest develops; the outcome remains future information until resolution.

## Do not conclude

Waiting does not cause propagation. Later cohorts differ because resolution has selected who remains.

