# Chapter 20 — Four-stage linkage

## Purpose

Follow one small-origin disturbance through small, medium, large, macro, and outer confirmations.

## Exact genealogy

A valid strict root starts from broad agreement on the preceding bar. The initiating small DCC supplies the target direction and immutable lineage ID.

Four exact hand-offs are possible:

```text
small -> medium -> large -> macro -> outer
```

At each arrow, the upper-scale event that resolves the current contest must be the exact event that initiates the next. Nearest-time matching can attach the wrong branch and create false ancestry.

## Depth meanings

- depth 0: real small attempt rejected before medium;
- depth 1: medium attained, next stage rejected;
- depth 2: large attained, next stage rejected;
- depth 3: macro attained, next stage rejected;
- depth 4: outer attained.

Depth four says the target reached the outer clock. It does not say price will continue. Attained depth is causal once each hand-off occurs; terminal depth remains future information until the active contest resolves.

## All-resolved and strict-clean cohorts

The cohort rules are the same as in Chapter 16:

- Ambiguous, unlinked, and unresolved lineages remain counted in the status audit. They have no terminal depth, so no probability ladder includes them; `max_attained_depth` records how far they got.
- The **all-resolved** ladder is the unbiased description of propagation.
- **Strict-clean** lineages also exclude same-bar stages, which have no unresolved pre-resolution life. They are the cohort for live-stage analysis. Every excluded same-bar stage is a propagation, so strict-clean reach rates are biased low and must not be quoted as propagation probabilities.

Conditional reach rates multiply by the chain rule within one cohort, without stage independence.

## Lab

Run [5_threshold_dc_linkage.ipynb](../../../5_threshold_dc_linkage.ipynb).

Audit root eligibility, all hand-offs, depth counts, exclusions, conditional reach for both cohorts, nested activity strictly before each resolution bar, direction/period stability, and the five-depth casebook.

## Mandatory exercises

1. Trace one lineage through all four exact event IDs.
2. Explain why the seed remains immutable.
3. Distinguish attained and terminal depth at each stage.
4. Explain why depth zero is a genuine attempt and depth four is not a continuation forecast.
5. Derive the cumulative reach product.
6. Explain why every strict-clean conditional rate is at or below its all-resolved counterpart.

## Locked in

> Five-scale linkage is one immutable small seed advanced by exact confirmation genealogy through at most four stages.

## Do not conclude

The depth distribution belongs to the declared roots, grid, symbol, period, and exclusions. It is not a universal law.

