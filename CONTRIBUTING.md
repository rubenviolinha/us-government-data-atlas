# Contributing

## Before submitting data changes

Every new dataset or refresh should include:

1. A reproducible fetch or transformation script under `scripts/`.
2. A raw snapshot or a documented reason a raw snapshot cannot be redistributed.
3. A normalized release under `data/normalized/`.
4. An entry in `metadata/sources.json` with publisher, URL, format, license, and scope notes.
5. A retrieval manifest with timestamp and record counts.
6. Validation updates when the schema or invariants change.

Do not commit API keys, tokens, cookies, private feeds, or unlicensed USPS data. Put access requirements in `metadata/access_requirements.json` instead.

## Local checks

```bash
python3 scripts/build_catalog.py
python3 -m compileall -q api scripts
python3 -m unittest tests/test_api.py
python3 scripts/validate_data.py
python3 scripts/validate_capitals.py
```

Source-specific licensing controls the right to redistribute data; the repository's code license does not override those terms.
