# Mismatches and reference findings for correction

Prepared 18 October 2026 for review of article-generation run `inputs/run_20261018T130444564598Z/`.

This report consolidates the run's manifest, bibliography, scientific, path, and document findings. It also identifies a few directly visible inconsistencies in the package's maintenance helpers and audit summaries. Those additional observations are labeled below. No new literature search, scientific calculation, or database integrity check was performed for this report. Current hashes were checked only for the eight registered non-database files that had mismatches.

**A closed run issue means that the generated article or its execution was corrected. It does not mean that the original package files were corrected.** The original prompt, bibliography, notebooks, instructions, and input manifest were preserved during generation. Many source-package corrections therefore remain for you to make.

The requested root-level location of this report is an explicit exception to the generation prompt's usual `inputs/` output rule. The historical run's frozen manifests have not been rewritten to include this later report.

## 1. Review priorities

| Priority | Finding | Generated article/run | Original package or external action still needed |
|---|---|---|---|
| High | Eight input-manifest hashes and byte sizes differ from the files actually supplied | Actual identities frozen and used; no registered source changed during generation | Review the intended source versions, then regenerate the package manifest after all intended edits |
| High | Supplied DFT ranking, low-decile composition, and scaling checks disagree with executed local data | Article uses independently checked current results | Correct the numerical check paragraph in `PROMPT.txt`, or investigate the source of the older snapshot |
| High | Root graphical-abstract script has obsolete database/artwork paths and root output/cache defaults | Repaired execution copy used | Port reviewed path/configuration fixes into the maintained source |
| High | Dataset reference [17] lacks formal metadata; public availability of local analysis/prediction resources is unverified | Minimal author-confirmed DOI retained; availability claim narrowed | Complete dataset metadata and verify/deposit the intended resources |
| Medium | Reference [8] was incomplete; reference [9] was generic; reference [35] lacked an access date | Three entries corrected in the generated bibliography | Synchronize `article/BIBLIOGRAPHY.json` and the duplicated bibliography in `PROMPT.txt` |
| Medium | Minto reference [11] edition/year/publisher remains unverified | Supplied entry retained with external qualification | Verify the edition actually used from its title/copyright page or authoritative catalogue |
| Medium | Instructions contain obsolete cohort counts, historical feedback references, and source-location statements | Current prompt took precedence | Update the specific instructions and preparation/status files listed below |
| Medium | Notebook defaults do not consistently implement the declared `inputs/` output policy | Working copies adapted | Consolidate output/cache configuration in maintained notebooks |
| Low | Initial DOCX used the wrong graphical-abstract file and reaction-electron typography | Both defects fixed and independently rechecked | Preserve the final generator fixes; no final manuscript defect remains on these points |
| Review boundary | Most references were supported by approved summaries, not freshly checked full papers | Explicitly disclosed | Treat the checks as source/citation correspondence, not complete independent verification of all 35 references |

## 2. Input-manifest mismatches: eight files

Sources: [supplied manifest](article/input_manifest.json), [frozen current identities](inputs/run_20261018T130444564598Z/frozen_input_manifest.json), and [source-preservation check](inputs/run_20261018T130444564598Z/reports/source_preservation_check.json).

The frozen manifest contains 45 selected inputs and records eight hash mismatches. For all eight, the current file hash still matches the hash recorded at intake for the generation run. Thus these differences predated the run; they are not evidence that generation modified the original sources. A hash difference alone does not establish which version is scientifically correct, nor whether the difference is in code, prose, or notebook outputs.

The exact expected and observed hashes and byte sizes are in Appendix A. All eight still need package-manifest reconciliation after you select the intended source versions.

**Recommended correction sequence:** review and edit the actual sources first; inspect the manifest generator's inclusion policy; then regenerate `article/input_manifest.json` once. Keep the run's `frozen_input_manifest.json` unchanged as historical evidence. Do not replace its observed identities with the old manifest hashes or edit scientific data to make a checksum match.

### Maintenance-helper observations from this summary review

These are direct code observations, additional to the generation run's original issue log:

1. [`tools/verify_package.py`](tools/verify_package.py) checks every manifest hash with assertions. The stale hashes therefore prevent it from passing. Even after those are refreshed, its root-file allowlist permits only `PROMPT.txt`, `AGENTS.md`, the excluded reference DOCX, and `.ipynb` files. It does **not** permit the registered root graphical-abstract `.py` or supplied root `.png` files. It also does not permit this newly requested report. Reconcile the root-layout check with the intended package contents; no verifier was run or changed for this summary.
2. [`tools/prepare_manifest.py`](tools/prepare_manifest.py) recursively registers files outside its excluded directories. As currently written, it would include this root `mismatches_summary.md` as a future generation input unless you exclude it. This retrospective audit should not silently become evidence or prose input for a fresh isolated article run.
3. The manifest helper hardcodes `generation_executed: false`, and the verifier's success message says generation has not yet executed. Decide whether these are intentionally **fresh-package** declarations or should report actual run state; they cannot be used as evidence of execution status without that distinction.

## 3. Bibliographic entries: actual differences and unresolved metadata

Comparing `article/BIBLIOGRAPHY.json` with the final `manuscript.json` shows **exactly three changed bibliography-entry texts**: HESS, Coursera, and the project repository. The other 32 entry texts were retained. That does not establish that all retained metadata were independently verified.

Reference numbers below are those in the final generated article. The complete 35-entry number/key inventory is in Appendix B.

### BIB-01 — HESS writing article, final reference [8]

- **Key:** `10.5194/hess-20-2965-2016`.
- **Original:** `Hydrol. Earth Syst. Sci. 20 (2016), starting at p. 2965.` Authors, title, and end page were missing.
- **Run finding:** the publisher landing page supplied the missing metadata. The title is **Improving together: better science writing through peer learning**, by Stiller-Reeve et al., pages **2965–2973**.
- **Corrected final entry:**

  > M. A. Stiller-Reeve, C. Heuzé, W. T. Ball, R. H. White, G. Messori, K. van der Wiel, I. Medhaug, A. H. Eckes, A. O’Callaghan, M. J. Newland, S. R. Williams, M. Kasoar, H. E. Wittmeier, V. Kumer, Improving together: better science writing through peer learning, Hydrol. Earth Syst. Sci. 20 (2016) 2965–2973. https://doi.org/10.5194/hess-20-2965-2016.

- **Evidence recorded by the run:** [publisher page](https://hess.copernicus.org/articles/20/2965/2016/), accessed 18 October 2026. The recorded corrigendum concerns reviewer identities, not a different article identity.
- **Status:** corrected in run outputs; original `article/BIBLIOGRAPHY.json` and `PROMPT.txt` still contain the incomplete entry. Update both and revise the associated note saying the metadata are missing. This was incomplete metadata, not a demonstrated incorrect DOI.

### BIB-02 — Coursera course, final reference [9]

- **Key:** `COURSERA`.
- **Original:** `Coursera, Scientific writing course. https://www.coursera.org/learn/sciwrite (author-supplied course reference; date not supplied).`
- **Corrected final entry:** `K. Sainani, Writing in the Sciences, Stanford Online, Coursera. https://www.coursera.org/learn/sciwrite/ (accessed 18 October 2026).`
- **Evidence recorded by the run:** [official course page](https://www.coursera.org/learn/sciwrite/), accessed 18 October 2026. No course publication year was invented.
- **Status:** corrected in run outputs; update both original bibliography copies. The problem was a generic/incomplete citation, not the wrong course URL.

### BIB-03 — Minto book, final reference [11]

- **Key:** `MINTO2010`.
- **Retained entry:** `B. Minto, The Minto Pyramid Principle: Logic in Writing and Thinking, Prentice Hall, 2010.`
- **Unresolved point:** the run's visit to [Barbara Minto's official site](https://www.barbaraminto.com/) described a **1996** textbook edition and a longer subtitle. That check did not establish the supplied **2010 / Prentice Hall** edition metadata.
- **Interpretation:** this is an unresolved edition/year/publisher question. The run did **not** prove that the supplied entry is wrong and did not silently substitute another edition.
- **Action:** identify the exact edition used and verify author, full title/subtitle, publication year, publisher, and preferably ISBN from that edition's title/copyright page or an authoritative catalogue. Then update both original bibliography copies and the article if necessary.
- **Status:** still pending; the generated article retains the author-supplied entry.

### BIB-04 — Current Zenodo dataset, final reference [17]

- **Key:** `10.5281/zenodo.23408498`.
- **Retained entry:** `[dataset] Zenodo record 23408498 (2026). https://doi.org/10.5281/zenodo.23408498.`
- **Unresolved point:** formal dataset title, creators, and version were not supplied and could not be retrieved during the run. The record page/API was inaccessible through the tools used; no usable metadata were obtained.
- **Interpretation:** the DOI is explicitly author-confirmed in `PROMPT.txt`. Inaccessibility and incomplete metadata are **not proof that the DOI is invalid or incorrect**. No replacement DOI is proposed here.
- **Action:** complete the reference with the deposited record's exact creators, title, repository, version, year, and identifier. Verify that the intended released resources correspond to that record.
- **Status:** still pending; update the original bibliography copies once authoritative metadata are available.

The parent dataset **[16], `10.5281/zenodo.18601379`**, is a separate source. It was not identified as interchangeable with the current dataset, and its DOI was not reported as a mismatch.

### BIB-05 — Project repository and availability claim, final reference [35]

- **Key:** `PROJECT_REPOSITORY`.
- **Original entry:** `Project analysis and data repository, EActa_2026_AI-acceleration. https://github.com/doublelayer/EActa_2026_AI-acceleration.`
- **Corrected final entry:** `Project analysis and data repository, EActa_2026_AI-acceleration. https://github.com/doublelayer/EActa_2026_AI-acceleration (accessed 18 October 2026).`
- **Evidence recorded by the run:** the [repository landing page](https://github.com/doublelayer/EActa_2026_AI-acceleration) was viewed on 18 October 2026. Its visible listing established related molecular calculation databases; it did not establish public availability of all locally supplied notebooks and the prediction table. No scientific data were downloaded and no commit was resolved.
- **Initial article defect:** Data availability implied that the analysis notebooks and prediction resource were identified through the public repository beyond what that check established.
- **Final article wording:** “The project repository provides related molecular calculation data [35]. The analysis notebooks and prediction table used here were supplied locally.”
- **Action:** synchronize the web entry in the original bibliography copies. Verify or complete public deposition of notebooks/predictions before claiming they are publicly available, then give exact links to those resources. An access date must describe an actual visit, not be refreshed automatically without access.
- **Status:** article claim and access date corrected; public deposit completeness remains pending.

### What was and was not verified for the other references

The run established citation-key correspondence, first-use numbering, reuse of the same number, active links, and a 35-entry cited-reference list with no unused entries. It did **not** perform fresh full-text inspection or exhaustive metadata/DOI validation for all 35 sources. The supplied literature summaries and metadata were the declared evidence for most sources. Some author lists remain in supplied `et al.` form. The final report's citation “pass” is limited to that scope.

## 4. Literature-attribution cautions already present in the prompt

The following are important distinctions that could look like “incorrect reference” comments. They were already stated in the approved prompt or were interpretation/terminology safeguards. They are **not newly proven wrong DOI links** and do not mean all these references need replacement.

| Final reference | Distinction preserved in the generated article | Source-package review action |
|---|---|---|
| [3] Chen et al., `10.1021/acsenergylett.8b02322` | *We Editors Are Authors, Too* is the multi-author 2019 editorial; do not attribute it as a single-author 2018 Kamat paper | Keep the correct author/year/title association when editing |
| [2] Ding and Du, `10.1007/s11192-023-04640-6` | Supplied PLOS chemistry median is 154 days; mean is 173.36 days. “Six-month median” is not the supplied result. Post-submission intervals do not measure manuscript-writing time | Retain the population/time-interval distinction; no measured writing-time savings were established |
| [13] Kobak et al., `10.1126/sciadv.adt3813` | Vocabulary evidence is consistent with increased assisted writing; it does not identify fabricated articles or quantify misconduct | Do not attach unsupported fraud/accuracy claims to this citation |
| [14] Ifargan et al., `10.1056/aioa2400555` | NEJM AI methodological precedent, distinct from this run's performance; guidance and traceable outputs do not transfer their metrics to this study | Retain the current journal article identity and bounded comparison |
| [24] Žoglo et al., `10.26434/chemrxiv.15001712/v1` | ChemRxiv preprint; related +4 O-bridged Co–Co calculation uses different empirical corrections from this study's +2 set | Preserve preprint status, charge/correction limits, and avoid common-protocol ranking |
| [25] Sun et al., `10.1021/jacs.4c12705` | Molecular Co₂/bidentate OOH interpretation; catalyst-specific 2.73 eV separation is not a fitted population intercept | Do not equate that individual separation with the global scaling intercept |
| [26] Li et al., `10.1021/acscatal.6c00046` | Single-metal Fe–N₄ macrocycles, not Sun's Co dual-atom catalyst | Use for coordination/ligand context, not direct proof of bimetallic cooperation |
| [27] Zhang et al., `10.1002/adma.202403549` | OER study using XGBoost/SISSO, not this ORR ridge model; supplied principal fit is 0.96/2.98 eV | Preserve reaction/model differences. OER and SISSO were expanded in review; source title retained verbatim |
| [29], [30], [31], [32] Jia/Chen/Benarbia studies | Distinct catalyst classes, ORR/OER/HER tasks, supervised/unsupervised methods, and research/review types. Chen [30] is a research article; Jia [32] is the review | Keep experimental confirmation and model metrics with their original studies |
| [22], [23] thermochemistry/solvation | Sources support adopted conventions; rounded constants are this study's transferred parameters, not newly computed vibrational/solvent results for every molecule | Do not add gas ZPE again or infer unsupported solvent mechanisms |

SISSO's expansion was narrowly checked against the method authors' [primary preprint abstract](https://arxiv.org/abs/1710.03319) during review; no new bibliography entry or research result was introduced. OER and HER expansions were also added. These were explanation corrections, not replacements of the Zhang or Benarbia sources.

## 5. Scientific result mismatches with the prompt

**Issue SCI-01; corrected in the article, still present in the original prompt.**

Affected location: the “Author-supplied DFT result checks” paragraph under **Section structure and supplied result checks** in [`PROMPT.txt`](PROMPT.txt).

| Quantity | Supplied prompt check | Executed current local result |
|---|---|---|
| Lowest DFT pathway | Cr–Mn, S–S, B1, at Mn; 0.29 V | Same; A2, `metal2`; 0.2945470235353691 V |
| Second-lowest pathway | Mn–Mn, S–S, B1, at Mn; 0.34 V | **Mn–Ni**, A2/B1, S–S, Mn `metal1`; **0.3000782108708899 V** |
| Third-lowest pathway | Fe–Cu, S–S, B2, at Fe; 0.36 V | **Mn–Mn**, A2/B1, S–S, Mn `metal1`; **0.3386373966832929 V** |
| Fe–Cu example | Included as third example in the supplied check list | Fourth in the current ranking; A2/B2, S–S, Fe `metal1`; 0.35604357762049355 V; retained in article as an additional example |
| DFT low-decile metal counts | Co 5, Mn 4, Fe 3 | **Co 6, Mn 4, Fe 2** |
| DFT low-decile bridge counts | S–S 7, N–N 4, O–O 1 | **S–S 6, N–N 5, O–O 1** |
| OOH–OH slope/intercept | 0.69 / 3.05 eV | **0.6951945339269502 / 3.0399070276870654 eV**, displayed **0.70 / 3.04 eV** |
| O–OH slope/intercept | 1.66 / 1.17 eV | **1.6579040313086317 / 1.1755173231154934 eV**, displayed **1.66 / 1.18 eV** |

Slopes are dimensionless; intercepts are in eV. The last decimal in exported floating-point fit values can differ at machine precision; full-precision calculation tables are the reproducible authority, not rounded prose values.

The first four pathways were reconstructed separately from original local source energies, exact parent/`ads_site` matches, and the lower available OOH orientation. All passed the declared electronic filters; agreement with the executed table was within 1e−12 V. The missing Mn–Ni pathway is complete and cannot be omitted under the stated selection. The origin of the older supplied snapshot was **not established**; no claim is made that a particular earlier manuscript or code revision caused it.

Review evidence:

- [Scientific discrepancy report](inputs/run_20261018T130444564598Z/reports/scientific_discrepancies.md)
- [Independent top-four reconstruction](inputs/run_20261018T130444564598Z/reports/independent_top_four_check.json)
- [Source energies and identifiers](inputs/run_20261018T130444564598Z/tables/top_four_raw_energy_sources.csv)
- [Ranked DFT results](inputs/run_20261018T130444564598Z/tables/DFT_ranked.csv)
- [Numerical ledger](inputs/run_20261018T130444564598Z/reports/numerical_ledger.json)

### Energy-field naming mismatch, not an established cause of the result changes

The prompt names `post_opt_rpbe_d4_E`. The original Figure 3 reader, zero-based cell **7**, assigns `row.energy` into an internal column with that name. All **20 source rows inspected for the top four** stored the energy in ASE `row.energy`, without a separate key-value `post_opt_rpbe_d4_E` field. The working copy preferred an explicitly stored field if present and otherwise used ASE energy; the targeted check showed no numerical effect for these pathways.

**Action:** document storage field versus analysis-column name accurately. Do not attribute the ranking change to this fallback, and do not rewrite the scientific databases merely to change a label.

### Counts that agreed and should not be “fixed” to match each other

The execution reproduced 118 retained DFT combinations; the ML input's 1,288 names, 28-name DFT overlap and 1,260 outside-DFT names; 2,216 complete ML center combinations before filters; 2,197 retained combinations across 1,278 names; and the 220-combination low-decile pool with the supplied ML family counts.

The 88 DFT parents, 79 parents with retained complete pathways, 1,348 total clean structures, 1,288 prediction-table names, 1,278 retained prediction names, and 2,197 retained center combinations are **different populations**, not contradictory versions of one count.

The review also narrowed broad “sulfur-containing bridges” wording in the Abstract/Conclusions to supported **S–S** enrichment: N–S is modestly enriched, while O–S is depleted. That wording was corrected; it was not a change to the prediction data.

## 6. Stale instructions, statuses, and missing cross-references

| Location | Mismatch or ambiguity | How the run handled it / suggested source correction |
|---|---|---|
| `instructions/TERMINOLOGY.md`, regression table and typography bullet | Two references to a **1176-structure** screen, superseded by current cohorts | Replace with the current clearly defined population, or remove hardcoded cohort counts from this reusable guide. Do not substitute 1,260 for every distinct population |
| `instructions/TERMINOLOGY.md`, component-notation paragraph | Refers to unavailable historical **AUTHOR_FEEDBACK_V47** | Replace with the current prompt/source reference; do not require a predecessor manuscript for an isolated run |
| `instructions/TERMINOLOGY.md`, paragraph after the two-center definition | Says to explain the molecular two-center distinction for **Figure 1**, although Figure 1 is the writing cycle and Figure 2 is molecular | Align the figure cross-reference with current Figure 2 |
| `instructions/TERMINOLOGY.md`, asterisk wording | Says to define `*` as an adsorbed intermediate, while current prompt includes the clean catalyst `*` | Use the current definition: catalyst/clean catalyst, with `*O`, `*OH`, `*OOH` denoting adsorbed intermediates |
| `instructions/CODE_AND_ENVIRONMENT.md`, paths paragraph | Says the TOC script is in **tools/**; current designated script is the root `Figure_0_graphical_abstract_v33.py` | Correct the source-location statement without creating a second competing script |
| `article/PREPARATION_REPORT.md`, historical acquisition paragraph | Describes GitHub commit resolution, downloads, SQLite validation and checksums | Clearly mark as superseded historical preparation, or remove from the active instructions; current run forbids those scientific-data operations |
| `article/PREPARATION_REPORT.md`, earlier preparation paragraphs | Says inputs are empty and two scientific decisions remain open | Separate dated historical state from current state; current local-input/new-evidence policy and conceptual SI treatment already resolved those execution choices |
| `article/READ_ME.md`, final sentence; `article/INPUT_CHECKLIST.txt`; manifest execution flag | Independent generation is described as pending/not yet run | Either explicitly define these as fresh-template state or link to actual dated run state; do not silently claim the root manifest was updated by generation |
| `PROMPT.txt`, DFT-check paragraph | Says “downloaded and corrected data” despite the selected local-only policy | Change to “supplied local data” or equivalent while correcting the result checks |
| `article/SCIENTIFIC_PROVENANCE.md` | Says the corrected reference supplies settings, then says that comparison reference is excluded | State that current settings are consolidated in the prompt and that no excluded reference document is needed at runtime |
| `PROMPT.txt` and `article/READ_ME.md`, empty-input premise | `inputs/` already contained prior artifacts at intake | Define a fresh-run directory and preservation/version policy, or deliberately prepare an empty package before distribution. Earlier artifacts were preserved and excluded, not deleted |

These mismatches did not authorize reading the excluded comparison DOCX. It remained excluded throughout drafting and review.

## 7. Source code and output-path mismatches

Notebook cell indices below are **zero-based**, matching the execution provenance. The original sources still contain these defaults; repairs were made in run working copies.

| Source | Original mismatch | Working-copy resolution / correction to review |
|---|---|---|
| `Figure_0_graphical_abstract_v33.py`, `complete_structure()` | Reads `databases/3d_B1B2_ch2_{kind}_rpbe_d4.db` beneath the parent project, inconsistent with declared DASC files | Map OH to `../DASC_OH_Adsorption_RPBE_D4.db` and OOHz to `../DASC_OOHz_Adsorption_RPBE_D4.db` |
| Same script, publication-page loading | Expects page image beside the script | Use `source_data/reference_EActa_open_article_2020_page1.png` |
| Same script, `HERE`, `BASE`, Matplotlib and temporary-directory defaults | Direct execution at package root writes figure files/cache/temporary render material there | Separate source root from output/cache roots and write generated material under `inputs/` |
| Figure 1 notebook, cell 4 | Defaults to `/content` or `figure1_outputs/` | Current run writes `inputs/` |
| Figure 2 notebook, cell 8 | Rendering temporary directory defaults to the working directory | Current run redirects temporary files under its `inputs/run_.../cache/` |
| Figure 2 notebook, cell 10 | Defaults to `/content` or `figure2_outputs/` | Current run writes `inputs/` |
| Figure 3 notebook, cells 18 and 23 | Defaults to `/content` or `figure3_outputs/` | Current run writes `inputs/`, preserving supplementary analyses |
| Figure 3 notebook, cell 2 | `notebook_connected` renderer is a connected-display default inconsistent with self-contained/offline delivery | Working copy uses a local renderer; retain embedded JavaScript for exported interactive HTML |
| Figure 4 notebook, cell 2 | Plot base, cohort audit and fit-statistics files are placed beside the root notebook | Current run routes all derived outputs to `inputs/` |
| Installation cells | Some notebook cells contain Colab `pip` / `apt-get` setup, while installed software was already available locally | Keep a clear environment-specific setup guard; the run used installed software instead of unnecessary installation |

The declared prediction path `../figure4/predictions.csv` was used directly. It was not reported as a missing or wrong prediction file, and no replacement CSV was downloaded.

Current fresh asset names differ from some root source/version names because older `inputs/` artifacts already existed and were preserved:

| Figure | Fresh run PNG |
|---|---|
| Graphical abstract | `inputs/Figure_0_graphical_abstract_v33.png` |
| 1 | `inputs/Figure_1_writing_cycle_v12.png` |
| 2 | `inputs/Figure_2_modular_design_space_v34.png` |
| 3 | `inputs/Figure_3_scaling_relations_v29.png` |
| 4 | `inputs/Figure_4_predicted_scaling_volcano_v26.png` |

These intentional output-version increments are not stale input-manifest hashes. The exact final associations are in the [Artist asset manifest](inputs/run_20261018T130444564598Z/reports/figure_asset_manifest.json).

Evidence and maintained-run implementations: [execution provenance](inputs/run_20261018T130444564598Z/reports/execution.json), [science/figure handoff](inputs/run_20261018T130444564598Z/reports/science_and_figure_handoff.md), [working copies](inputs/run_20261018T130444564598Z/work/), and [figure execution script](inputs/run_20261018T130444564598Z/scripts/execute_figures.py). Review the source differences before porting them; do not copy executed notebook outputs back indiscriminately.

## 8. Defects introduced during generation and already repaired

These were errors in intermediate generated artifacts, not proof that the supplied scientific inputs were wrong.

| Issue | Intermediate defect | Final correction and verification |
|---|---|---|
| R3-B01 | DOCX embedded root supplied `Figure_0_graphical_abstract_v33.png` instead of the freshly executed `inputs/` image | Generator now follows the structured source path and restricts image sources to `inputs/`; all five embedded image bytes match the independent Artist manifest |
| R3-B02 | Reaction electron `e` in Eqs 1–4 was italic under the author's convention requiring upright species | Reaction electron made upright; physical elementary charge in Eqs 6–7 remains italic; both distinctions explicitly checked |
| R3-D01 | Repository availability statement overstated what had been verified and web entry lacked actual access date | Corrected in final A3 article and bibliography; local/public resource distinction verified |
| R1-J01/J02 | Audit-only metadata and a production instruction about avoiding individual predicted-catalyst lists reached the manuscript | Removed from reader-facing prose; underlying provenance retained externally |
| R1-S01 | Compressed sulfur-family claim could imply every sulfur bridge was favored | Narrowed to supported S–S finding, consistent with full-population comparison |
| R1-S02 | OER, HER and SISSO appeared without adequate expansion | Defined at first use; no reaction or model reassignment |
| STY-01–04 | Local repetition, participial phrasing, vague emphasis and unnecessary hyphens | Eleven minimal replacements integrated; numerical/citation tokens conserved during the style round |

Graphical-abstract hashes, useful for distinguishing the two same-named files:

- Root supplied image: `d30dd213798b6a2a575344dda5776a9ff04c07dfc98987b5eb4bed3c66c793f9`.
- Fresh generated image now embedded: `2555b92c961aab736aae288c377a0c1bfadc771b58c706ec7e61a87ba9a0678f`.

The first 31 automated checks missed the source-selection defect because they compared the embedded image against the Builder's own selected-file manifest. Independent release inspection caught it. The checks were extended to compare against the separately registered **fresh Artist outputs**, and to test electron species versus charge typography. The final article passed 34 checks plus the independent release audit. This explains why earlier “checks passed” messages were followed by further repairs.

Final reviewed DOCX SHA-256: `e37b87e508931088770cebea955dee81bad1b90abfb25a6931365a1872eddc9c`. Final structured source SHA-256: `9c49bbd092e82ecfc7bb027965f018f7cba36a45b6ef5e9e49aa356a3320aaaa`.

## 9. Execution differences and audit qualifications

- Source-notebook and executed-working-copy hashes are expected to differ because working copies contain declared path/configuration changes and fresh execution outputs. Those differences must not be confused with the eight original-file-versus-input-manifest mismatches in Appendix A.
- The final DOCX container hash is `e37b87e508931088770cebea955dee81bad1b90abfb25a6931365a1872eddc9c`; its independently regenerated container hash is `359e8a315523c0c52196ad3ae827c229a62ebc28e1a554a779273838c570d1f7`. All **23 archive-member contents** matched byte for byte. Different ZIP container timestamps explain why this reproduction check did not require identical whole-file hashes; no document-content mismatch was found. See [reproduction evidence](inputs/run_20261018T130444564598Z/reproduction_check.json).
- The initial Jupyter attempt needed local socket permission; Figure 3 later terminated with signal 143 before its final publication exports. Figures 3/4 were recovered by executing the working-copy cells in order with headless IPython. This was documented recovery, not a scientific-data discrepancy. The observed execution modes are recorded in `reports/execution.json`.
- An initial dependency probe created a Matplotlib cache under `/tmp` before full cache configuration. It was relocated under the run. Do not interpret the final output-location check as proof that no temporary outside-directory creation occurred at any earlier instant.
- Analysis used ASE **3.29.0**, whereas the supplied original DFT protocol specifies ASE **3.23.0** and GPAW **24.6**. Reading saved calculations with a newer analysis package is not a claim that the original DFT was recomputed with that package. Keep original calculation versions separate from current analysis/build versions.
- Cambria and Arial were specified in DOCX styles but were not installed locally; no Word/LibreOffice renderer was available. Structural correctness was checked, while rendered pagination, equation line fit, and realized font appearance remain uninspected. This is a verification limit, not a demonstrated final rendering defect.
- The actual model version behind Codex was not exposed. The run reported the tool identity and did not infer a model from a role name. The author's two-week instruction development and actual run elapsed time are separate; no matched time-saving comparison was performed.
- Whole-run elapsed time was **1,578.93 seconds (26.32 minutes)**; successful figure computation/rendering totaled **36.21 seconds**, excluding setup, the interrupted attempt and editorial work. These are different timing populations, not competing estimates of total generation time.

### Audit-summary consistency observations from this review

These affect the precision of the audit summaries rather than the manuscript's scientific results:

1. The final `release_report.md` groups J01–J05 and J10–J16 as passed. The detailed `reviews/round3_release_audit.md` more precisely marks **J02** as a nonmandatory recommendation, **J14** as not applicable because there are no scientific tables, and the separate-caption portion of **J11** as deferred submission work. Use the detailed table when correcting or reconciling the summary.
2. The top portion of `evidence_map.md` retains preparation-stage statements such as numerical checks “pending” and bibliography numbering delegated to Builder. Later appended sections and the final release audit document their completion. Label those early tables as preparation snapshots if maintaining a single current-status ledger; do not infer that the final numerical audit was omitted.
3. `scripts/compose_manuscript.py` is the original A0 composition helper, not the final reviewed source. Rerunning it would overwrite later author corrections. The final rebuild entry point is `generate_article.py` with current `manuscript.json`; internal composition scripts should be labeled accordingly.

## 10. Missing evidence and intentional author choices

The following are not established reference/manifest errors:

- **Missing SI attachment:** alternative rankings were author-reported, but the SI artifact was not supplied. Section 3.6 therefore discusses reuse conceptually; no missing numerical table was invented. Supply the SI if the final article is to cite or claim its specific comparison.
- **Missing current ridge coefficients/preprocessing tables:** supplied predictions and model settings were available, but matching parameter tables were not. No refitting, parameter replay, validation accuracy or uncertainty estimate was claimed. Provide those inputs only if such verification is intended.
- **Journal drafting exceptions:** numeric affiliation markers, two corresponding authors, the selected equation/Greek typography, Arial captions and chosen figure export profile are explicit author choices. They are not accidental mismatches to be silently corrected. Portal/submission alignment is separate work.
- **Human approval:** internal simulated role review is not final human scientific approval or journal peer review. Subsequent author approval/correction status remains pending.
- **Literal titles and identifiers:** some reference titles use wording or capitalization excluded from ordinary manuscript prose. They were retained as supplied reference titles rather than rewritten stylistically. No additional wrong title is asserted here without a source check.

## 11. Suggested correction order

1. Review the DFT discrepancy evidence and select the intended numerical source; synchronize the prompt's checks with that decision.
2. Complete the Minto edition and current dataset metadata, and verify the public availability of notebooks/predictions.
3. Copy the three verified bibliography-entry updates into both original bibliography copies; preserve actual access dates and source notes.
4. Remove or clearly label obsolete instructions, cohort counts, historical feedback dependencies, and preparation-state claims.
5. Port the reviewed path/cache/output fixes into maintained figure sources while preserving the scientific operations.
6. Align the manifest/verifier helpers with the intended root layout and exclusions, including this retrospective report.
7. Regenerate the package manifest only after those edits are settled; verify the resulting package without database hashing/downloading/copying. Preserve the completed run's frozen input/output manifests as historical records.
8. Rebuild and review any manuscript changed by these decisions; obtain rendered layout and final human scientific approval before submission.

Primary audit trail: [shared issue log](inputs/run_20261018T130444564598Z/role_issue_log.md), [final release audit](inputs/run_20261018T130444564598Z/reviews/round3_release_audit.md), [release report](inputs/run_20261018T130444564598Z/release_report.md), and [evidence ledger](inputs/run_20261018T130444564598Z/evidence_map.md).

## Appendix A. Exact manifest differences

The following table is generated directly from the frozen input identities and current file sizes/hashes. “Manifest” is the original `article/input_manifest.json`; “observed” is the run-intake identity, still matching the current file at summary preparation.

| File | Manifest bytes | Observed/current bytes | Manifest SHA-256 | Observed/current SHA-256 |
|---|---:|---:|---|---|
| [AGENTS.md](AGENTS.md) | 911 | 900 | `805bb724494df7be677e476390f60c6da6ea9e485ad80af044a45b3373b9ee7c` | `5290e12c9965b64f4fdcafde5cfcd8f800c1cfa5b0d4ce9f603c37cc00257e38` |
| [article/INPUTS.md](article/INPUTS.md) | 914 | 926 | `f1b73a11a8111226710651adc06da4b7fd65f2bd9a5ec03c1e21b387d7e62db5` | `9bb4feef4d1fb349416a86a2f44a966295039ce79c5299529965244e59935236` |
| [article/READ_ME.md](article/READ_ME.md) | 1129 | 1226 | `369c3f190ed5339feb571298945eff30c9d10a31a21d83dd3c76ba12b872c897` | `b10db788431e696d0d2ab592ee82bf6ffdcf2535e2c3ac0bb978736f69d1faf4` |
| [environment/README.md](environment/README.md) | 457 | 1130 | `3dd119b9c82c2ba63a71d3c50328460be692519e5ecf87fdbe24cce157d990dc` | `d6c3ee020b0b714eaefc0b08f86d1f50768679ddc69253996742fe65364de789` |
| [Figure_2_modular_design_space_v33.ipynb](Figure_2_modular_design_space_v33.ipynb) | 310624 | 309839 | `64ebeb99bc7d940b324c94e6e6f1e9779e76b42613531bf79c2f612fc3a7cf14` | `e39820dfaab379456f37d490c6714b79fb9c0e7f3b93ec147d43c2644c8368de` |
| [Figure_3_scaling_relations_v28.ipynb](Figure_3_scaling_relations_v28.ipynb) | 1523283 | 1511979 | `d28981ddc49c34b3fa73f8236dd9d540c575ca226e360b98b80ab16849bd6120` | `db7ccf9cbb275f386f951f620792202eefcad03c82913e814d81fb5bc6e17850` |
| [instructions/PYTHON_AND_COLAB_STYLE.md](instructions/PYTHON_AND_COLAB_STYLE.md) | 8907 | 8083 | `cb24d11ed8c4b44afb1531a233917160e0932a20a83cc8c16a5cf0c51efe4f68` | `b86119754874a004b4454461a95ab55480bddc36d3bd74e32ec9776076f7d2a2` |
| [PROMPT.txt](PROMPT.txt) | 61167 | 61164 | `9f2504b9f132122b051ff526d82bab11b57e564ecbc75d8b993c33e814ac0940` | `abd633ae81ea15295f7e684fff9966475ef52fbd8828977409ad823cce73b779` |

## Appendix B. Final reference inventory and verification scope

“Supplied” means that metadata and claim support were retained from the approved packet; no specific bibliographic mismatch was established during the run, and no exhaustive fresh verification is implied. Numbers identify the final generated article, not the ordering of the original JSON file.

| Final number | DOI or stable key | Recorded verification / mismatch status |
|---:|---|---|
| 1 | [10.1016/j.joi.2013.09.001](https://doi.org/10.1016/j.joi.2013.09.001) | Supplied; no specific bibliographic mismatch established |
| 2 | [10.1007/s11192-023-04640-6](https://doi.org/10.1007/s11192-023-04640-6) | Supplied; no specific bibliographic mismatch established |
| 3 | [10.1021/acsenergylett.8b02322](https://doi.org/10.1021/acsenergylett.8b02322) | Supplied; no specific bibliographic mismatch established |
| 4 | [10.1038/nphys724](https://doi.org/10.1038/nphys724) | Supplied; no specific bibliographic mismatch established |
| 5 | [10.1021/acsenergylett.1c02401](https://doi.org/10.1021/acsenergylett.1c02401) | Supplied; no specific bibliographic mismatch established |
| 6 | [10.1038/s41551-018-0202-5](https://doi.org/10.1038/s41551-018-0202-5) | Supplied; no specific bibliographic mismatch established |
| 7 | [10.1038/nmeth.2726](https://doi.org/10.1038/nmeth.2726) | Supplied; no specific bibliographic mismatch established |
| 8 | [10.5194/hess-20-2965-2016](https://doi.org/10.5194/hess-20-2965-2016) | BIB-01: missing metadata completed from publisher page; original package still incomplete |
| 9 | `COURSERA` | BIB-02: title/instructor/provider and actual access date completed |
| 10 | `GLASMAN2010` | Supplied; no specific bibliographic mismatch established |
| 11 | `MINTO2010` | BIB-03: supplied entry retained; edition/year/publisher verification pending |
| 12 | [10.1038/sdata.2016.18](https://doi.org/10.1038/sdata.2016.18) | Supplied; no specific bibliographic mismatch established |
| 13 | [10.1126/sciadv.adt3813](https://doi.org/10.1126/sciadv.adt3813) | Supplied; no specific bibliographic mismatch established |
| 14 | [10.1056/aioa2400555](https://doi.org/10.1056/aioa2400555) | Supplied; no specific bibliographic mismatch established |
| 15 | [10.1016/j.dib.2026.112806](https://doi.org/10.1016/j.dib.2026.112806) | Supplied; no specific bibliographic mismatch established |
| 16 | [10.5281/zenodo.18601379](https://doi.org/10.5281/zenodo.18601379) | Supplied; no specific bibliographic mismatch established |
| 17 | [10.5281/zenodo.23408498](https://doi.org/10.5281/zenodo.23408498) | BIB-04: author-confirmed DOI retained; formal metadata and deposit completeness pending |
| 18 | [10.1063/5.0182685](https://doi.org/10.1063/5.0182685) | Supplied; no specific bibliographic mismatch established |
| 19 | [10.1088/1361-648X/aa680e](https://doi.org/10.1088/1361-648X/aa680e) | Supplied; no specific bibliographic mismatch established |
| 20 | [10.1063/1.5090222](https://doi.org/10.1063/1.5090222) | Supplied; no specific bibliographic mismatch established |
| 21 | [10.1021/jp047349j](https://doi.org/10.1021/jp047349j) | Supplied; no specific bibliographic mismatch established |
| 22 | [10.1016/j.chemphys.2005.05.038](https://doi.org/10.1016/j.chemphys.2005.05.038) | Supplied; no specific bibliographic mismatch established |
| 23 | [10.1039/c1cp21228a](https://doi.org/10.1039/c1cp21228a) | Supplied; no specific bibliographic mismatch established |
| 24 | [10.26434/chemrxiv.15001712/v1](https://doi.org/10.26434/chemrxiv.15001712/v1) | Supplied; no specific bibliographic mismatch established |
| 25 | [10.1021/jacs.4c12705](https://doi.org/10.1021/jacs.4c12705) | Supplied; no specific bibliographic mismatch established |
| 26 | [10.1021/acscatal.6c00046](https://doi.org/10.1021/acscatal.6c00046) | Supplied; no specific bibliographic mismatch established |
| 27 | [10.1002/adma.202403549](https://doi.org/10.1002/adma.202403549) | Supplied; no specific bibliographic mismatch established |
| 28 | [10.1039/D5CS00597C](https://doi.org/10.1039/D5CS00597C) | Supplied; no specific bibliographic mismatch established |
| 29 | [10.1002/adma.74833](https://doi.org/10.1002/adma.74833) | Supplied; no specific bibliographic mismatch established |
| 30 | [10.1021/acscatal.6c02383](https://doi.org/10.1021/acscatal.6c02383) | Supplied; no specific bibliographic mismatch established |
| 31 | [10.1039/d6ra03405e](https://doi.org/10.1039/d6ra03405e) | Supplied; no specific bibliographic mismatch established |
| 32 | [10.1002/adfm.77325](https://doi.org/10.1002/adfm.77325) | Supplied; no specific bibliographic mismatch established |
| 33 | [10.1016/j.coelec.2018.03.025](https://doi.org/10.1016/j.coelec.2018.03.025) | Supplied; no specific bibliographic mismatch established |
| 34 | [10.1021/acscatal.2c03997](https://doi.org/10.1021/acscatal.2c03997) | Supplied; no specific bibliographic mismatch established |
| 35 | `PROJECT_REPOSITORY` | BIB-05: access date and availability wording corrected; local-resource public deposit unverified |
