# Chapter 3 — Event-time state models

## Purpose

Use a model to summarize the sequence of completed-event velocities without losing the distinction between event time and bar time.

## Observation process

The HMM receives one observation per completed event: $\log(R_n)$ in the baseline Normal-emission experiment. The log transform compresses the strongly right-skewed positive distribution and matches a real-valued emission family more naturally.

The model therefore advances when a DCC makes a new completed event available. It does not receive a fresh observation on every intervening price bar.

## Causal filtering

At event $n$, the filtered state probability is

$$
p(S_n\mid R_1,\ldots,R_n).
$$

It combines the current emission evidence with the previous filtered belief and transition matrix. Smoothing would condition on later observations and is therefore diagnostic, not deployable here.

State numbers have no economic meaning. The notebook maps them semantically using the training data: `slow_R` is the state with the lower filtered-probability-weighted mean raw R over the training events, and `fast_R` the higher. One helper, `semantic_r_state_order` in `dc_basics/hmm_support.py`, applies this rule in both Chapter 3 and Chapter 5 labs. It need not agree with ordering the states by their log-R emission means when the state variances differ a lot. The labels are relative to the fitted model.

## Mapping to bars

For visualization, carry the latest filtered event state forward from its DCC until the next DCC. This is a piecewise-constant event-state display. A state that covers 80% of bars need not own 80% of events because event intervals have unequal duration.

## Lab

Run the “Single-threshold HMM” section of [1_threshold_dc.ipynb](../../1_threshold_dc.ipynb).

Verify:

- chronological train/test splitting;
- filtered rather than smoothed probabilities;
- state semantics learned without test relabeling;
- source event ID and state information time on the bar mapping;
- the event-weighted versus bar-weighted occupancy table, by sample.

## Mandatory exercises

1. Explain why an event HMM and a bar HMM model different transition processes.
2. Explain why two identical current R values can receive different filtered probabilities.
3. Using the occupancy table, explain why a dominant bar-time state can coexist with less dominant event-time occupancy.
4. State what information is repeated during forward-filling and what is not recomputed.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- The event HMM updates once per completed event; a bar HMM would model a different sequence.
- Equal current R can produce different filtered posteriors because the previous posterior and transition matrix differ.
- Forward-filled bar states repeat the latest event result; they do not add evidence.
- Bar occupancy weights event duration and therefore differs from event occupancy; read both columns of the occupancy table.
- `slow_R` is the state with the lower filtered-probability-weighted training mean of raw R, not necessarily the lower log-R emission mean.

</details>

## Locked in

> The filtered HMM state is a history-conditioned description of the completed event stream; mapping it to bars does not create new observations.

## Do not conclude

`fast_R` is not a directional forecast, a volatility promise, or a trading instruction.

