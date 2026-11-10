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

## Parity test

`tests/test_vendor_parity.py` enforces that the vendored files are unchanged:

- it always compares each file's SHA-256 (LF-normalised, trailing newlines
  stripped) with the hash recorded at vendoring time;
- when a signalfoundry checkout is available (sibling `../signalfoundry`, or
  `SIGNALFOUNDRY_ROOT`), it also compares each file with
  `git show <source commit>:<path>`, so a moving working tree cannot mask drift.

## Local behaviour lives outside vendored files

Never patch a vendored file in place. Put local fixes or extensions in a
separate module under `dc_basics/` and leave the vendored copy byte-identical.

## Known upstream issues (not patched here)

- `_features.dc_live_features`' docstring refers to an `idc_parse()` function that
  does not exist and to "Chapter 5" of Chen & Tsang's book, not this textbook's
  Chapter 5. Fix upstream, then re-vendor.
- `hmm/pomegranate.py` builds LogNormal emissions from random starting values in log
  space instead of the k-means initialisation used for Normal/Student-t emissions, and
  ignores `covariance_type` / `min_cov` for them. The HMM notebooks work around this
  without editing the vendored file; see the notebook that compares emission families.

## Update policy

Do not silently replace these files from a moving source checkout. Record a new
source commit here, update the hashes in `tests/test_vendor_parity.py`, and run the
parity and invariant tests before accepting an upstream refresh.
