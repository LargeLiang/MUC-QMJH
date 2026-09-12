# Project instructions

## Current authority

Read CURRENT_RESULTS.json, UNIFICATION.md and REPRODUCIBILITY.md before changing analysis or conclusions.
The current entry is Codes/reproduce.py; current results are selected explicitly by CURRENT_RESULTS.json.
This is observational association research, not an identified causal or mediation study.

## Preservation and migration

Do not overwrite raw data, immutable run directories, historical papers or original figures.
C01-C23 and C00_all_collection.ipynb are legacy; their estimates must not be mixed with current results.
Legacy direct execution requires MUC_ALLOW_LEGACY=1 and may overwrite historical outputs.
New runs need a new output directory. Do not promote a run automatically.
Formal Word/PDF changes and public release require the user's choice of canonical document and scope.

## Statistical interpretation

Prompt criteria are not independent response-quality measurements.
Model identity contrasts do not remove question-specific quality confounding.
Retain denominator, variable scale, sample definition, confidence interval type and multiplicity family when quoting results.
Do not treat run status complete, matrix rank or unit tests as full scientific acceptance.
Known audit limitations remain open unless implemented and verified in a new run.

## Verification and engineering

Use Python 3.13.5 and requirements-analysis.lock.txt for analysis.
Run python -m unittest discover -s tests -v.
Run python Codes/verify_current.py --raw when local data are available.
Use --public-only only to validate public outputs; disclose skipped private files.
Use pathlib, explicit schemas, small testable functions, clear Chinese documentation and non-overwriting outputs.
Do not regenerate historical outputs to make them appear current.
