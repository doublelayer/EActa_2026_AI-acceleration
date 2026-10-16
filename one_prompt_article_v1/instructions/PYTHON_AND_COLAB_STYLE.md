# Python and Google Colab style

## Scope

Apply these rules to Python scripts, Jupyter notebooks, Colab notebooks, and code-generated tables or figures in this project.

## Preserve author formatting

The author deliberately uses multiple spaces to align related assignments, arguments, comments, and table-like code. Preserve this spacing. Do not run an autoformatter, collapse repeated spaces, reorder aligned declarations, or rewrite a cell merely to match a generic style guide.

Keep the user-designated filename exactly. Do not create a renamed copy unless a new name is explicitly requested.

Treat an author- or student-supplied notebook as a protected source. For a narrowly scoped request (for example, changing a data host or removing a call to an older plotting script), make only the necessary cell-level edits. Preserve notebook filename, cell order, cell count, cell IDs, markdown, comment banners, deliberate spacing, and the separation between installation, setup, acquisition, analysis, plotting, and export. Never collapse an existing multi-cell notebook into one large cell or rebuild its analysis from scratch unless the author explicitly requests that restructuring. Before release, compare the notebook against its supplied source and report exactly which cells changed. A previous-script dependency should be removed by placing the required function in its proper existing analysis cell, not by replacing the notebook with an unrelated generated script.

Keep each analysis notebook and its databases in the locations declared by the article manifest. For this project's ordinary revisions, notebooks stay in their designated figure output folders and ASE inputs in `databases/`; resolve paths relative to the notebook. During an isolated regeneration run, use the run's declared output directory. When downloads are authorized in Colab, use `/content/` directly and do not write implicitly to Google Drive. An offline execution must use supplied local files and skip network acquisition cells.

## Notebook organization

- Make each current notebook self-contained. Explain its inputs, observation unit, calculations, filters, and outputs without referring to another notebook as assumed background.
- Use short Markdown sections that explain the scientific purpose of the following code.
- Use visible code-cell banners in the established pattern and preserve their alignment.
- Put package installation in the first executable cell.
- Put imports and runtime configuration in the next executable cell.
- Separate data acquisition, validation, transformation, analysis, interactive display, and summary into readable cells.
- Display intermediate audits at the point where they establish correctness.
- End with a concise analysis summary derived from the actual in-memory data.

## Colab behavior

- Install Python packages with `!pip install` in the first executable cell.
- Install system packages with `!apt-get` only when they are actually required.
- When downloads are authorized, download databases directly to `/content/` with their exact filenames. Do not create an extra database subdirectory. Offline runs use the supplied files.
- Replace stale runtime copies before downloading so the displayed results correspond to the declared links.
- Verify that each downloaded database has the SQLite header before opening it with ASE.
- Configure Plotly explicitly for Colab and enable the custom widget manager when `ipywidgets` is used.
- Use `%matplotlib inline` for static display.
- Display plots explicitly with `plt.show()` or `figure.show(renderer=...)`.
- By default, keep data and figures in memory and do not save analysis files. Add an export cell only when the author requests one.
- Never write to Google Drive implicitly.
- When a notebook is tied to a published release, resolve that release by its immutable tag and select assets by exact filename. Check the declared local path first; reuse a database only when its file signature and expected SHA-256 both match. If the file is absent or invalid, download the exact asset to a temporary sibling, validate it, and atomically replace the invalid or missing target only after validation succeeds. Report the release tag, asset identifier, whether it was reused or downloaded, byte size, row count where applicable, and SHA-256 hash. Support a token through an environment variable when a release is private; never embed credentials. A release webpage is not a file URL.
- When figure export is requested, use collision-safe versions in the declared output folder. Never overwrite a prior image or interactive export. Export PNG with an opaque white background. Follow the active article figure brief for design and [`../figures/FIGURE_PRODUCTION_CORE.md`](../figures/FIGURE_PRODUCTION_CORE.md) for production; historical figure specifications are not implicit inputs to a fresh-generation run.

## Dependencies and imports

- A maintained figure generator must contain every figure-specific transformation and drawing function it calls. It may read declared scientific data and artwork inputs and use installed libraries or renderers; it must not import, execute, or copy code from an earlier figure version at runtime. Preserve historical versioned sources, but point current navigation to the standalone generator.
- A second run must create a new version or stop before writing; it must never silently overwrite a released figure. Check every companion format, including interactive HTML, for collisions. Interactive HTML should bundle Plotly JavaScript when offline reproduction is required.
- Declare every nonstandard dependency in the installation cell.
- Import only packages used by the notebook.
- Use `pathlib.Path` for local paths.
- Keep database filenames, Google Drive file identifiers, physical constants, and plot-style maps in a clearly labeled configuration cell.
- Fail with an informative error when a download, database signature, required column, unique-key condition, or validation check fails.

## Data-frame and numerical conventions

- Use explicit, descriptive internal column names that distinguish total energies, adsorption energies, adsorption free energies, limiting potentials, and overpotentials.
- Validate join cardinality with `validate='one_to_one'` where one record per catalyst and adsorption site combination is required.
- Never rely on data-frame row order for scientific identity.
- Preserve both the catalyst name and adsorption site label in every analysis table.
- Use `.round(2)` or explicit `'{:.2f}'` formatting for displayed floating-point values. Preserve trailing zeros in tables and hover text.
- Keep full internal precision for calculation and fitting; round only presentation values.
- Sort chemical categories by the project order, not alphabetically.

## Interactive output

- Use Plotly for point-level hover inspection.
- Hover text must identify the catalyst, adsorption site, other metal, structural components, plotted adsorption quantities, selected OOH orientation, limiting potential, overpotential, and potential determining step when those fields exist.
- Free energy diagram selectors must appear in one aligned vertical column.
- Build selections from separate structural components registered for the active dataset. Omit a selector for any component that is fixed across the active data.
- Restrict selector options to valid combinations remaining after exact matching and filtering.
- Show a clear in-notebook message when no complete pathway matches a selection.

## Execution and verification

- The agent should run code and validation itself whenever the environment permits. Do not shift routine execution to the author.
- For a notebook edit, validate JSON, inspect all changed cells, execute the relevant analysis if dependencies are available, and confirm that plots are explicitly displayed.
- When local execution is blocked by an environment defect, identify the defect precisely, preserve a Colab-compatible notebook, and provide a user command only if the user must run it in their environment.
- Do not modify unrelated files while testing.


## Selected run policy

PROMPT.txt supplies current facts and the execution contract. GitHub input downloads and relevant web research are authorized. Preserve supplied notebooks and use working copies for execution. The root `Electrochimica_Acta_research_article_refernce.docx` is reserved for comparison after generation and excluded from drafting inputs. Any historical offline examples in a reusable profile yield to this selected run policy.
