# Vendored source provenance

The directional-change core and pomegranate HMM wrapper in this package were
copied from the local `signalfoundry` source repository so that the educational
research folder can later become a self-contained repository.

- Source repository: `D:\projects\quant-studies\signalfoundry`
- Source commit: `e297846e1bc0cb3f564ef94dcddaa72b01fa201b`
- Vendored on: 2026-11-10

## Directional-change core

Source package:
`features/src/okmich_quant_features/directional_change`

Copied modules:

- `_parser.py`
- `_features.py`
- `_tsfdc_features.py`

The local `core/__init__.py` deliberately exposes only the functions used by
this research journey: `parse_dc_events`, `dc_live_features`, `log_r`,
`normalise_minmax`, and `parse_dual_dc`.

## HMM layer

Source package: `ml/src/okmich_quant_ml/hmm`

Copied modules:

- `util.py`
- `base_pomegranate.py`
- `pomegranate.py`
- `distribution/_lambda.py`
- `distribution/__init__.py`

The local HMM `__init__.py` contains the single-model factory required by the
notebooks. It intentionally omits mixture, factorial, coupled, and IOHMM code
that the directional-change notebooks do not use.

## Update policy

Do not silently replace these files from a moving source checkout. Record a new
source commit here and run the parity and invariant tests before accepting an
upstream refresh.
