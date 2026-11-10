# Chapter 2 — TMV, T, R, and overshoot

## Purpose

Describe the completed leg's size, duration, and normalized velocity without confusing those values with the new live mode.

## Definitions

Let $P_s$ and $P_e$ be the completed leg's start and end extremes, and let $i_s$ and $i_e$ be their bar positions. With threshold $\theta$:

$$
\mathrm{TMV}_{up}=\frac{P_e-P_s}{P_s\theta}, \qquad
\mathrm{TMV}_{down}=\frac{P_s-P_e}{P_s\theta}.
$$

$$
T=i_e-i_s, \qquad R=\frac{\mathrm{TMV}\,\theta}{T}.
$$

TMV is a move in threshold units. $T$ is an extreme-to-extreme bar count. $R$ is the completed absolute return per bar. Because $R$ is algebraically determined by TMV and $T$, it is not a third independent geometric dimension.

The overshoot is the continuation beyond the threshold-sized directional-change portion before the next opposite DCC confirms the final extreme. On sampled bars, threshold crossing may leap past the exact theoretical boundary.

Concretely, let $P_d$ be the close at the DCC that opened the leg's mode (the previous event's confirmation). The leg splits into a directional-change portion $\mathrm{DC}=|P_d-P_s|/(P_s\theta)\ge 1$ and an overshoot $\mathrm{OS}=|P_e-P_d|/(P_d\theta)\ge 0$. The two compound exactly:

$$
(1\pm\mathrm{DC}\,\theta)(1\pm\mathrm{OS}\,\theta)=1\pm\mathrm{TMV}\,\theta,
$$

with $+$ for up legs and $-$ for down legs, so $\mathrm{TMV}\approx\mathrm{DC}+\mathrm{OS}$. The first event in a sample has no observed opening DCC and therefore no overshoot.

## Information time

The endpoint extreme, TMV, T, R, and completed overshoot are known at the later DCC, not at the endpoint bar. The event row must therefore use the DCC as `information_time`.

## Lab

Continue in [1_threshold_dc_explore.ipynb](../../1_threshold_dc_explore.ipynb).

Inspect:

- distributions and tail quantiles of TMV, T, and R;
- mean versus median by direction;
- the overshoot table: DC portion, overshoot, their bar counts, and the share of legs with zero overshoot;
- the count of $T=1,2,3,\ldots$ events;
- raw bars around a consecutive-extreme event.

These distributions are usually right-skewed. The mean can be dominated by a small tail, so interpret it beside the median and quantiles. Consecutive events are path-dependent, not IID rows suitable for naive significance tests.

## Mandatory exercises

1. Recompute TMV, T, and R for three events directly from the ledger.
2. Explain what $T=1$ means and what it does not mean.
3. Explain why frequent very short events may indicate a threshold that is small relative to sampling noise.
4. Compare upward and downward medians and tails without claiming symmetry from similar means.
5. Point to the bar where each event's statistics first became knowable.
6. For one event, find its opening DCC in the previous row, compute DC and OS by hand, and check that they compound to TMV.

## Completion-gate guidance

<details>
<summary>Open after writing your own response</summary>

These are reasoning outlines, not substitutes for notebook evidence. A complete answer must cite the relevant chart, case, count, or table from your run.

- Recalculate TMV from the two extremes, $T$ from their positions, and $R=\mathrm{TMV}\theta/T$.
- $T=1$ means consecutive extreme positions, not necessarily an extreme and DCC on adjacent bars.
- Frequent short events suggest the threshold may be small relative to bar-scale movement or noise.
- Use median and tails beside means because the indicators are right-skewed and path-dependent.
- The overshoot runs from the opening DCC (the previous row's confirmation) to the ending extreme; $(1\pm\mathrm{DC}\,\theta)(1\pm\mathrm{OS}\,\theta)=1\pm\mathrm{TMV}\,\theta$, and the completed overshoot is known only at the leg's own confirming DCC.

</details>

## Locked in

> TMV says how far, T says how long, and R says normalized return per bar—but all three describe the completed prior leg and become known at its confirming DCC.

## Do not conclude

A large R does not by itself define a future fast market. It is a completed-event observation.

