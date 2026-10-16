# Data integrity and analysis

## Function

This file contains reusable procedures for adsorption databases, computational-hydrogen-electrode analysis, scaling relations, and regression validation. Article-specific filenames, counts, coefficients, candidates, software versions, and pending results belong in `PROMPT.txt`.

## Scientific auditor contract

Receive the resolved scientific inputs, their manifest, current author decisions, analysis definitions, and the claims or artifacts to check. Audit within the requested scope. Use a reader appropriate to the source format; a supplied CSV prediction table can be checked without loading atomic-structure software. Prefer existing verified outputs with matching input and code hashes before repeating an analysis.

Resolve numerical authority before checking prose. When the author designates an annotated source, extract the human numerical insertions, deletions, and subsequent clarifications into the article packet. Keep their author and date or other provenance. During isolated generation, use the consolidated decisions in the declared packet. Compare them with active data and distinguish a superseded instruction, a different population, and an actual discrepancy. Record disagreements with both sources and affected claims; ask the responsible role or human for a consequential unresolved decision rather than silently changing either source.

Maintain a compact numerical ledger. For each scientific value or count, record its quantity, unit, population or denominator, analysis stage, source identity and location, precision, and evidential status: supplied, author-confirmed, verified-derived, or pending. Link derived values to their inputs and operation. Keep scientific values separate from identifiers, DOI strings, years, and version labels.

Audit counts through the full selection sequence: input rows, unique parent structures, supplied adsorption centers, complete intermediate combinations, retained combinations after each filter, model structures and data points, and prediction populations. Count dataset overlap by identity. A parent count, a model-point count, and a plotted-point count can differ legitimately; each must keep its definition and source.

Verify quantity definitions before arithmetic. Establish whether each column contains total energy, adsorption potential energy, corrected free energy, a fitted value, or a prediction. Resolve the correction source and apply each contribution once. For supplied model outputs, parameter replay checks arithmetic reproduction; it does not establish predictive accuracy. Report only validation and uncertainty supported by the supplied procedure and data.

Hand the Author and reviewers the verified tables and numerical ledger, with a concise discrepancy report. Check every affected numerical claim in the latest manuscript, captions, equations, and result summaries against those definitions. Preserve full computational precision and apply rounding only for presentation. Recheck changed inputs or calculations and their downstream uses; reuse valid checks for unaffected artifacts.

The Programmer repairs code when authorized; the Scientific reviewer evaluates inference; the Expert checks literature claims. Send each issue to the responsible role and verify its correction before closure. Keep audit details outside the article. Record actual checks and pending dependencies, with human scientific approval tracked separately.

## Observation unit and identity

Define the scientific observation before joining data. When one molecular catalyst contains more than one possible adsorption center, use a composite key that preserves both parent-catalyst identity and adsorption-center identity. Never join adsorbates by row order, parent name alone, metal element alone, or partial string matching.

Validate the cardinality of every source and join. Report parent-catalyst counts separately from catalyst-center or pathway counts.

## General matching sequence

1. Read each source row with its stable parent identifier, adsorption-center identifier, total energy, structure, and relevant metadata.
2. Identify supplied adsorption-center combinations and any declared expected coverage. Record missing combinations; preserve complete supplied combinations without fabricating an absent center.
3. Detect duplicate composite keys before joining.
4. Join single-orientation adsorbates on the complete composite key with one-to-one validation.
5. Compare alternative initialized orientations only within the same composite key.
6. Select the available alternative with the lowest stated energy while retaining the selected orientation and energy difference.
7. Join all required intermediates and the clean structure with explicit cardinality validation.
8. Mark a pathway complete only when every required component belongs to the same composite key.
9. Reconstruct adsorption quantities from raw energies where possible and compare them with stored assembled values.
10. Fail loudly on discrepancies instead of silently choosing a source.

## Filtering

Apply scientific filters only after exact matching and quantity reconstruction. Store, for every excluded pathway:

- the composite key;
- the filter condition;
- the value that triggered exclusion;
- the stage at which exclusion occurred.

Treat project-specific cutoffs as author-defined working rules, not universal physical laws. Read their active values from the article fact sheet or input manifest.

## Computational hydrogen electrode analysis

### General method versus study-specific parameters

The reusable knowledge concerns how electronic energies are converted to free energies, how reaction corrections are assembled, and how consistency is checked. Correction values, temperature, reference states, species coverage, solvation assumptions, and the particular literature source adopted for those values are study-specific inputs. Obtain them from the final prompt or the plotting notebooks explicitly designated by that prompt. This guide supplies no numerical correction defaults.

In a compatible convention, adsorption free energy is the electronic adsorption energy plus the reaction zero point energy correction, minus temperature times the reaction entropy change, plus any separately adopted solvation correction. Determine which terms are already combined in the supplied constants. Distinguish species-level contributions from reaction-level differences; assemble them with the declared stoichiometry and reference states. Other declared corrections must likewise retain their definition and provenance.

Resolve one correction specification for the run before using it in analysis or prose. For prompt-supplied values, preserve the specified units, precision, and scope. For notebook-supplied values, identify the designated notebook, effective cell or function, parameter names, units, and energy convention; account for later assignments and cell dependencies rather than extracting the first matching number or an old displayed output. Record the file hash and cell identifiers or indices in the execution provenance. Do not silently choose between conflicting notebook definitions or conflicting prompt and notebook values. Apply an explicit author override when present; otherwise report the scientific discrepancy for resolution.

Use the resolved specification consistently in DFT analysis, conversion of ML predictions, figures, and Methods. A plotting notebook may be the authoritative parameter source without turning those values into universal scientific rules. A historical article-specific correction note is provenance, not a default for future studies or replacement inputs.

Never infer correction status from a legacy column name such as G_OH. Establish the target definition from source provenance and author confirmation. Keep potential energies, individual corrections, and resulting free energies in separate columns. Validate potential energies against the raw database before corrections, and check that each correction is applied exactly once. Gas ZPEs must not be added on top of combined reaction corrections that already include them.

For the four-electron associative oxygen reduction pathway, evaluate the four reduction steps from consistently referenced adsorption free energies. The limiting potential is the minimum step potential, and the thermodynamic oxygen reduction overpotential is the equilibrium potential minus that limiting potential.

The step associated with the limiting potential is the **potential determining step**. Do not call it a rate determining step without kinetic barriers.

Keep these quantities distinct:

- electronic adsorption energy;
- adsorption free energy after stated corrections;
- step reduction potential;
- limiting potential;
- calculated thermodynamic overpotential;
- kinetic activation barrier;
- experimentally measured activity.

Use the article's native equations and reference convention when producing numerical results.

## Scaling relations

- Fit the specified adsorbate quantities against the chosen descriptor only after identity checks and filters pass.
- Report global and family fits only when the family definition is scientifically meaningful.
- Store slope, intercept, sample size, residuals, and validation statistics in machine-readable output.
- Interpret a family difference only when sample size, uncertainty, and residual behavior support it.
- Round display values according to the figure or manuscript specification; retain full precision in analysis tables.
- Scaling relations are empirical correlations, not mechanisms by themselves.

## Regression and validation

- Name the implemented estimator and feature construction exactly as the code defines them.
- Distinguish fitted values, out-of-fold predictions, validation predictions, test predictions, and predictions for an unsampled dataset.
- Keep every observation from one parent catalyst in the same training or validation group.
- Use grouped out-of-fold predictions for performance estimates when the scientific claim concerns unseen parent catalysts.
- For transfer claims, check which chemically structured holdouts were actually supplied. Identify any additional validation needed to support the retained claim; perform new validation only when the task authorizes and specifies it.
- Report documented sample counts and preprocessing. Evaluate error metrics, residuals, uncertainty, and applicability domain when the declared method and inputs support them. Their absence is a status to report, not permission to invent a validation procedure or refit a supplied model.
- Do not call an all-training-set visualization independent validation.
- Do not present model predictions as density functional theory calculations or experiments.

## Candidate prioritization

For screening a larger molecular library, report:

- total structures evaluated;
- structures inside and outside the training library;
- exclusions at every selection stage;
- the ranking rule and follow-up threshold;
- predicted quantities and uncertainty;
- applicability-domain status;
- structure-family enrichment with sample sizes;
- targeted calculation or experimental validation when available.

Before targeted validation, use **prioritized novel candidates** or **machine-learning-prioritized structures**. Use **discovered catalyst** only after novelty and performance have been independently established.

## Minimum audit outputs

- input file identity and hash or persistent identifier;
- schema and row count for every source;
- duplicate-key report;
- join-stage counts and cardinality checks;
- orientation selection per composite key;
- exclusion table with reasons;
- final identity-preserving analysis table;
- parent grouping and model-split assignments;
- fitted, validation, and screening outputs labeled by evidential status;
- comparison with the article-specific verified snapshot.

Use the charge evidence explicitly supplied in the article packet before making charge claims. Stored charge metadata do not by themselves prove the charge applied in an electronic-structure calculation. A project-specific charge audit is an article input, not an implicit dependency of this reusable guide.



## Selected run policy

PROMPT.txt supplies current facts and the execution contract. Use the registered local project data files; relevant web research remains authorized when needed. Preserve supplied notebooks and use working copies for execution. The root `Electrochimica_Acta_research_article_refernce.docx` is reserved for comparison after generation and excluded from drafting inputs. Any historical offline examples in a reusable profile yield to this selected run policy.
