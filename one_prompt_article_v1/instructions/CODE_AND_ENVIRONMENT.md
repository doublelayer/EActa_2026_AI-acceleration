# Local code and execution conventions

## Paths and supplied sources

The directory containing PROMPT.txt, inputs/, and instructions/ is the task root. Resolve supplied relative paths against that root. The entire package must remain usable after relocation; do not embed a user's Windows/WSL home path or a predecessor project path.

Read each entry point and its declared inputs before execution. Keep the supplied notebooks at the package root and preserve their deliberate multiple-space alignment. Keep the TOC script in tools/ and its supplied publication-page image in source_data/. Execute notebook working copies from the package root so their declared relative paths resolve. If a script assumes a different working directory or absolute path, make the smallest necessary adaptation in `inputs/run_.../work/`, record it, and preserve the scientific operations. Retain supported configuration options when possible. Do not invoke old manuscript generators.

Write generated figures and derived plot tables directly in `inputs/`. Write manuscript drafts, logs, temporary files, caches, and release materials in `inputs/run_.../`. Configure rendering caches there when needed. Do not use `/tmp` or a remote drive for project artifacts. Never overwrite a prior run or immutable supplied source files.

## Authorized online access

Inspect notebook input and installation cells before execution. Follow PROMPT.txt for the workspace-relative scientific input paths and their provenance. Relevant web research and bibliography verification are authorized. Preserve the supplied scientific operations in working copies, adapting data paths to the locations specified in the prompt.

Use installed software first. Run the supplied installation cells in Colab when applicable. Record missing local dependencies and the actual execution environment; scientific calculation software versions and present analysis versions serve different purposes.

Interactive HTML must be self-contained when requested: embed the plotting JavaScript rather than use a CDN, and avoid external fonts or math-rendering resources. Static plots use installed local renderers. Preserve offline usability of delivered figures and reports.

## Scientific operations

Keep input identifiers, energy definitions, correction parameters, and selection rules explicit. Preserve full numerical precision in calculations and round presentation only. Validate schemas, composite keys, duplicates, and join cardinality. Use the declared chemical category order rather than alphabetic sorting.

Read correction values from the article brief or designated notebook code, as selected by the author. Do not infer a correction from a column name or add it twice. Preserve the distinction between potential energies, free energies, step potentials, limiting potential, and overpotential.

Execute only supplied/authorized model operations. Fitted-parameter replay is not independent validation. Do not refit a supplied model, change features, or generate new DFT calculations merely to fill a missing result.

## Notebooks and dependencies

Keep notebooks self-contained with clear input/configuration, validation, analysis, interactive, and final static-output sections. Preserve existing useful analyses when a final publication plot is added. Display plots explicitly. Validate notebook JSON after adaptation.

The package's dependency list is a provisional baseline. The actual supplied imports and external tools determine the final environment. Historical calculation software versions describe how the original scientific data were obtained, not necessarily the versions required to read those data today. Record the actual analysis environment separately.

Environment and end-to-end checks occur when the author initiates that stage. During instruction preparation, do not import analysis packages, execute notebooks, inspect scientific datasets, or render replacement figures merely to claim readiness.


## Selected run policy

PROMPT.txt supplies current facts and the execution contract. Local scientific inputs are used without GitHub downloads; relevant web research remains authorized. Preserve supplied notebooks and use working copies for execution. The root `Electrochimica_Acta_research_article_refernce.docx` is reserved for comparison after generation and excluded from drafting inputs. Any historical offline examples in a reusable profile yield to this selected run policy.
