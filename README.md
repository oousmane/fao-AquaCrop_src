# AquaCrop 7.3 — Python source

A partial copy of the FAO AquaCrop repository, [un-fao/fao-AquaCrop](https://github.com/un-fao/fao-AquaCrop),
containing **only the Python source code** of the model — upstream's
`python_source_code/AquaCrop73_src/`. The Windows GUI and the released binary
archives are not included.

The git history of that directory is preserved, so this copy can still be
compared with upstream commit by commit.

## Why this copy exists

A standalone executable is built from these sources, so that AquaCrop can run on
machines without a Python installation and be driven from `aquacropr`. Producing
that executable required a few changes on top of upstream, which is what this
repository holds.

**This is a test setup, not a release.** Nothing here is endorsed by FAO, and the
results have not been validated beyond the single test case described below.

## What was changed

- **Runtime directory lookup.** The model resolves `LIST/`, `PARAM/`, `SIMUL/`,
  `OUTP/`, `DATA/` and `OBS/` from the current directory when it holds a `LIST/`,
  and falls back to the executable's own directory, then to `testcase/`. Upstream
  resolved them relative to the process working directory, which only worked when
  the model was launched from one specific place.
- **Packaging.** `aquacrop.spec` (PyInstaller) and a `[tool.pycrucible]` section
  in `pyproject.toml`, which declares the project metadata and its single
  third-party dependency, numpy.
- **Fortran-to-Python porting fixes.** Several calls did not match their
  definition and raised `TypeError` as soon as the affected branch was reached:
  a missing `VirtualTimeCC` argument in `DetermineCCxAdjusted_Days`, Fortran
  output parameters still passed to `DetermineDate` and `DetermineDayNr`, and two
  module-level functions sharing the name `GetSetofThreeMonths`, where the rain
  variant shadowed the ETo one.

## Layout

```
src/aquacrop.py      entry point
src/modules/         the model
testcase/            Ottawa.PRM reference project
  LIST/ PARAM/ SIMUL/ DATA/ OBS/   inputs
  OUTP/                            outputs, written here
  OUTP_REF/                        reference outputs, for comparison
aquacrop.spec        PyInstaller build recipe
pyproject.toml       project metadata and pycrucible configuration
```

## Running

From the sources, with numpy installed and Python 3.13 or later:

```bash
python3 src/aquacrop.py
```

With no `LIST/` in the current directory, this falls back to `testcase/` and runs
the bundled Ottawa project.

To build the executable:

```bash
pip install pyinstaller
pyinstaller --clean --noconfirm aquacrop.spec
```

PyInstaller does not cross-compile, so run it on the operating system you are
targeting. Then copy `dist/aquacrop` into a directory holding `LIST/`, `PARAM/`,
`SIMUL/`, `DATA/`, `OBS/` and an empty `OUTP/`, and run it from there.

## Known deviation from the reference output

On the bundled Ottawa project, 70 of the 98 columns of `OttawaPRMday.OUT` are
byte-identical to `testcase/OUTP_REF/`. The rest differ in the last digit, except
the profile water content `WC(3.05)`, which is **14.5 mm low from the very first
simulated day** and stays within 14.4–14.6 mm for all 892 days.

A constant offset present on day one is an initial-condition problem rather than
a drift in the water balance. It has not been diagnosed yet.

## Copyright

© FAO. All rights reserved — see [LICENSE](LICENSE) and [src/COPYRIGHT](src/COPYRIGHT).
FAO authorises non-commercial reproduction free of charge upon request; enquiries
go to copyright@fao.org.
