# Vendored source provenance

The directional-change core and pomegranate HMM wrapper in this package were copied from the [signalfoundry](https://github.com/okmich/signalfoundry) repository so that this educational repository is self-contained.

- Source repository: <https://github.com/okmich/signalfoundry>
- Vendored on: 2026-11-10

## Directional-change core

Source package:
[`features/src/okmich_quant_features/directional_change`](https://github.com/okmich/signalfoundry/tree/e297846e1bc0cb3f564ef94dcddaa72b01fa201b/features/src/okmich_quant_features/directional_change)

Copied modules:

- `_parser.py`
- `_features.py`
- `_tsfdc_features.py`

The local `core/__init__.py` deliberately exposes only the functions used bynthis research journey: `parse_dc_events`, `dc_live_features`, `log_r`, `normalise_minmax`, and `parse_dual_dc`.

## HMM layer

Source package: [`ml/src/okmich_quant_ml/hmm`](https://github.com/okmich/signalfoundry/tree/e297846e1bc0cb3f564ef94dcddaa72b01fa201b/ml/src/okmich_quant_ml/hmm)

Copied modules:

- `util.py`
- `base_pomegranate.py`
- `pomegranate.py`
- `distribution/_lambda.py`
- `distribution/__init__.py`

The local HMM `__init__.py` contains the single-model factory required by the notebooks. It intentionally omits mixture, factorial, coupled, and IOHMM code that the directional-change notebooks do not use.
