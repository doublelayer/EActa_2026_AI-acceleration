# Environment

`requirements.in` is a provisional package list, not a pinned or tested lockfile. Record the actual Python and package versions used for a generation run.

## Scientific inputs

Figure analysis uses the supplied local inputs: five DASC ASE databases in the workspace root, one directory above this package, and `../figure4/predictions.csv`. The notebooks and current scripts read these paths directly. Do not download scientific data from GitHub or another remote source; stop and report a missing input.

The notebooks analyze saved calculations and supplied model predictions. GPAW is not required: the article-generation run performs no new DFT calculations or model fitting. ASE is required to read the databases, including in the Figure 4 notebook; the prediction CSV is read with pandas.

## Rendering dependencies

The Figure 2 notebook includes a POV-Ray installation cell and can fall back to ASE's renderer when POV-Ray is unavailable. `Figure_0_graphical_abstract_v33.py` requires POV-Ray. Install only the software needed by the selected run, and record unavailable dependencies or rendering fallbacks.
