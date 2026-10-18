# Canonical terminology and notation

## Function and authority

This file controls scientific names, notation, and evidential labels in manuscript prose, captions, figures, tables, notebooks, and code-generated reports. Use the canonical term repeatedly instead of introducing synonyms for variety. Preserve original wording only in publication titles, direct quotations, software names, and literal database fields.

Operational rules for data, code, figures, manuscripts, and citations live in their function-specific knowledge bases.

## Catalyst and structure

| Meaning | Required term | Avoid or restrict |
|---|---|---|
| First mention of the catalyst class | **molecular dual-atom site catalyst (DASC)**; use **DASCs** after a plural noun | DAC; M-DASC; 0D-DASC; dual atom site catalyst; dual-atom-site catalyst |
| Later mention | **DASC**, **DASCs**, **dual-atom site catalyst**, or **molecular catalyst**, as grammar and context require | spelling out zero-dimensional |
| Catalyst collection | **molecular catalyst dataset** | library; catalyst universe; compound pool |
| Molecule without adsorbate | **clean catalyst** | bare catalyst; empty catalyst; pristine catalyst |
| Fundamental joined observation | **catalyst and adsorption center combination** | catalyst alone when adsorption center identity matters |
| Persistent database identifier | **catalyst name** | catalyst ID unless the field is literally named `id` |
| Reader-facing catalyst identity | **human readable structural description** | opaque `KMC_*` names in the abstract, Results, or Conclusions |
| Metal positions | **metal 1** and **metal 2** | first and second metal; primary and secondary metal |
| Whole paired-metal region in one DASC | **dual-atom site** | calling either metal atom a separate site |
| Metal atom carrying the adsorbate | **metal-atom adsorption center**, then **adsorption center** | metal site; adsorption site; adsorption metal |
| Stored position identifier | **adsorption center label**; literal field name `ads_site` in code | equating the database field name with the chemical site |
| Metal paired with the adsorbing center | **other metal** | spectator; promoter unless demonstrated |
| Chemically operating structure | **active site** or **working active site** | adsorption site when the complete structure under operating conditions is meant |
| Ligand variables | **bridge**, **diamine**, **dialdehyde** | linker; base; amine; acid; para group |
| Physical bridge atoms | **bridge atoms** | bridge when individual atoms are meant |
| Molecular charge field | **total charge** | applied calculation charge unless verified from GPAW input or output |
| Magnetic initialization | **initial magnetic configuration** | magnetism as an interchangeable label |

Define DASC at first mention in the Abstract and use the plural DASCs only for multiple catalysts. Prefer **molecular catalyst** when repeated acronyms would slow reading.

Define the site and its centers once near molecular Figure 2:

> Each molecular dual-atom site catalyst has one dual-atom site containing two metal-atom adsorption centers. An intermediate may bind at either center.

The Abstract and Conclusions discuss the molecular catalyst structures as wholes. Introduce the two-center distinction where needed to explain Figure 1, the database matching, and center-resolved analysis. Do not call a metal atom a site.

Read the active component set and its evidential source from `PROMPT.txt`. At first mention of the component codes, cite the registered source. The chemical symbol **S** is upright when it denotes sulfur or an S bridge; italic **S** is reserved for the entropy quantity.

## Adsorbates and orientations

| Context | Required form |
|---|---|
| Mechanistic prose and equations | **\*O**, **\*OH**, **\*OOH** |
| Database subsets and matching prose | **O**, **OH**, **OOH** |
| Initialized orientations in prose, figures, and tables | **OOH-x**, **OOH-z** |
| Literal database or filename labels | `OOHx`, `OOHz` |
| Configuration retained after comparison | **lower energy OOH orientation** |

Define the asterisk once as an adsorbed intermediate. Do not call the selected orientation the most stable orientation unless thermodynamic stability beyond the two tested structures has been established.

## Energy and electrochemistry

| Meaning | Required term and notation | Unit |
|---|---|---|
| Electronic adsorption quantity before thermochemical corrections | **adsorption energy**, `ΔE_X` | eV |
| Corrected adsorption quantity | **adsorption free energy**, `ΔG_X` | eV |
| Relation across the verified joined dataset | **global adsorption free energy scaling relation** | none |
| Relation within one adsorbing-metal element group | **adsorption center family scaling relation** | none |
| Fit parameters | **scaling coefficients `α` and `β`** | slope dimensionless; intercept eV |
| Four electron CHE potential | **limiting potential**, `U_L` | V |
| `1.23 V − U_L` | **calculated ORR overpotential**, `η_ORR` | V |
| Mean deficit of ORR steps below equilibrium | **electrochemical step symmetry index for oxygen reduction**, `ESSI_ORR` | V |
| Largest intermediate to intermediate free energy span at a stated potential | **free energy span descriptor**, `G_max(U)` | eV |
| Thermodynamically limiting CHE step | **potential determining step** | none |
| Plot of state free energies | **free energy diagram** | none |

Use **O–OH scaling relation** and **OOH–OH scaling relation**. Use **deviation from the global scaling relation** for a residual or family shift. Reserve **distinct scaling branch** and **breaking the scaling relation** for statistically supported cases with structural evidence.

Do not use adsorption energy and adsorption free energy interchangeably. Treat `ESSI_ORR` and `G_max(U)` as complementary thermodynamic activity descriptors, not alternative definitions of overpotential or explicitly calculated kinetic barriers. State the potential when reporting `G_max(U)`. Do not call a potential determining step a rate determining step without kinetic evidence.

## Data and analysis

Use precise nouns by data type and operation; do not rotate synonyms for variety. A **DFT calculation** is a computation for a specified optimized molecular structure and adsorption center, including its calculated energy. An **ML prediction** is an output of the fitted statistical model for a specified molecular structure and adsorption center. Use **database**, **dataset**, **DFT calculation**, **ML prediction**, **result**, or **data point** in manuscript prose. Do not use *record*, *account*, or *sooner* as generic substitutes. In code or technical documentation, use a literal schema term only when required by the software; explain it as a database entry in reader-facing prose.

Repeat the title phrase **accelerating catalyst discovery with artificial intelligence** in the Abstract, Introduction, and Conclusions. Do not replace *accelerating* with *sooner*, *earlier*, *shortening the path*, or figurative alternatives in those thesis statements. Use **guide** and its forms when describing how ML predictions inform candidate selection or how instructions direct an LLM.

For this article, use the author's exact data-article component mapping wherever these codes are used: **B1**, the 1,2-phenylenediamine fragment; **B2**, the 1,8-naphthalenediamine fragment; **A2**, the fixed dialdehyde 2-hydroxyisophthalaldehyde. Cite DOI `10.1016/j.dib.2026.112806` in prose. Follow AUTHOR_FEEDBACK_V47 for the explicitly requested molecular Figure 2 synthesis and data-source citations. Keep figure-number labels plain text and omit unnecessary references from other captions.

Write elemental sulfur as upright Roman `S`, never italic, in prose and figure labels. Italicize scientific variables only where chemically and mathematically appropriate; element symbols remain upright.

| Meaning | Required term |
|---|---|
| Join on both required identifiers | **exact catalyst and adsorption center match** |
| O, OH, and selected OOH for one composite key | **complete catalyst-center pathway** |
| Supplied adsorbate files | **raw adsorption databases** |
| Combined analysis table | **joined center resolved dataset** |
| Source data cross check | **raw database verification** |
| Removed catalyst and adsorption center combination | **excluded pathway**, followed by the reason |

Report unique catalyst counts separately from catalyst and adsorption center combination counts.

## Electronic structure and computational electrochemistry

| First use | Later use |
|---|---|
| **density functional theory (DFT)** | **DFT** |
| **computational hydrogen electrode (CHE)** | **CHE** |
| **projector augmented wave (PAW) method** | **PAW method** |
| **revised Perdew–Burke–Ernzerhof (RPBE) functional** | **RPBE** |

Preferred open compounds include **DFT calculated**, **DFT derived**, **adsorption center resolved**, **CHE derived**, and **spin polarized**. Keep these unhyphenated in ordinary manuscript prose.

## Machine learning and regression

Name every regression model according to the implemented source code and the active scientific fact sheet. Do not substitute the planned final estimator for a different model used in an existing figure.

Define **artificial intelligence (AI)**, **machine learning (ML)**, **density functional theory (DFT)**, and **large language model (LLM)** once in the Abstract, then use AI, ML, DFT, and LLM throughout author-written prose. Do not redefine them in the Introduction or Methods. The unabbreviated article title, official institutional names, keywords, and verbatim reference titles are not redefinitions.

| Meaning | Required term | Avoid or restrict |
|---|---|---|
| Broad field | **machine learning (ML)** at first use; **ML** thereafter | AI in technical Methods and Results |
| Broad title framing | **artificial intelligence (AI)** | use only when the broad framing is intended |
| Final 1176-structure screen | **adsorbate specific ridge regression** | second-order polynomial regression; generic linear regression when the supplied ridge model is meant |
| Electronic structure result | **DFT calculated value** | observed value; true value |
| Statistical model output | **model predicted value** | calculated value; ML calculated value |
| Fit data | **training set** | learning set |
| Data unused for fitting | **validation set** or **test set**, according to role | control set |
| Predictions made without fitting the corresponding target values | **out of fold predictions** | cross validated data |
| Parent molecule grouping | **grouped cross validation by catalyst** | random site split |
| Represented descriptor region | **applicability domain** | universal domain |
| Choosing structures for more work | **candidate prioritization** | claiming experimentally established catalyst discovery without synthesis or experiment |
| New structures selected by the wider ML screen | **prioritized novel candidates** or **ML-prioritized structures** | discovered catalysts before novelty and performance are independently established |
| Final communication demonstration | **one final prompt generated the complete article** | the LLM discovered the catalysts; autonomous scientific discovery; effortless generation |

Use **structure–adsorption–activity relationship**, **catalyst specific descriptors**, **adsorption center specific descriptors**, **prediction error**, and **residual**. Machine learning is a surrogate for the stated DFT protocol within its applicability domain; do not say it replaces DFT.

## Evidential status

| Available evidence | Permitted wording |
|---|---|
| DFT and CHE | **calculated thermodynamic activity**, **calculated ORR overpotential**, **DFT prioritized catalyst and adsorption center combination** |
| Model tested on unseen data | **model predicted adsorption free energy** or **model predicted ORR overpotential** |
| Experimental electrochemistry | **experimental ORR activity**, followed by the measured quantity |
| Static structure | **candidate active site model** |
| Validation under relevant conditions | **working active site**, with the evidence stated |

Prefer **lowest calculated ORR overpotential in the present dataset** to **best catalyst**. Qualify activity, stability, prediction, cooperation, scaling deviation, and validation with the evidence that supports each word. Do not use synergy or mechanism without the required mechanistic evidence.

## Typography and language

- In **dual-atom site catalyst**, place the hyphen only between **dual** and **atom**.
- Avoid hyphens in ordinary modifier and noun phrases. Retain only approved scientific terms, chemical and database identifiers, personal names, and source titles when their spelling requires them.
- Use open forms **adsorption energy**, **adsorption free energy**, **model validation**, **adsorption center resolved**, and **lower energy**.
- Use **linear regression with second-order polynomial features** only for an analysis whose source explicitly documents that feature expansion. The final 1176-structure screen uses adsorbate specific ridge regression.
- Use en dashes only for scientific relations such as **O–OH**, **OOH–OH**, **DFT–ML**, and **structure–adsorption–activity**.
- Use upright Greek symbols, including Δ, η, α, and β, in text and native equations, as explicitly requested by the author. Italicize Latin quantity and variable symbols; keep chemical formulas, units, numbers, functions, and descriptive indices upright. Use structural equation subscripts and superscripts. See the DOCX knowledge base for implementation.
- Use `R²`, the multiplication sign `×`, and a true minus sign where supported.
- Use `quantity / unit` in axes and table headings.
- Use typographic subscripts in formulas such as H₂ and H₂O.
- Use standard capitalization for Cr, Mn, Fe, Co, Ni, Cu, N, O, and S.
- Use American English in author-written text. Preserve source spelling in titles and quotations.
- Use **Figure 1**, **Table 1**, and **Section 2.3** for numbered manuscript elements.

## Prohibited substitutions

- Do not use “library,” “framework,” “scaffold,” or “envelope” in author-written prose. Name the dataset, software, molecular structure, organic ligands, procedure, curve, or other concrete subject. Preserve verbatim source titles.
- Apply the same concrete-language test to **workflow**, **pipeline**, **approach**, **strategy**, and **concept**. Retain one of these words only when it names a defined technical object and the sentence states what that object contains or does. Otherwise name the data, calculation, model, comparison, or writing action directly.
- Avoid words with an unintended second meaning when a direct scientific term is available. In this manuscript, replace **manually** with **without LLM assistance**, and replace figurative uses of **manufacture** with **draft**, **write**, or **compose**. Preserve literal manufacturing and manual operations when they are scientifically accurate.
- Call the central proposition about scientific storytelling the **thesis**. Do not rotate among **argument**, **claim**, **statement**, and **thesis** merely for stylistic variation. Continue to use **claim** for an individual evidence-bearing scientific claim when that is the precise meaning.
- Describe GPAW and ASE as software. Read calculation-cohort versions, optimization facts, numerical settings, and orientation status from `PROMPT.txt`.
- Call each completed analysis by its registered model identity. Do not add evaluative adjectives such as “simpler.” Distinguish a current descriptive model from a separately planned screening model.
- Read the article's main demonstration and division of human and AI responsibility from `PROMPT.txt`; do not restate or alter that hierarchy for stylistic variety.
- Use the conventional order for every displayed equation: introduce the quantity or relation in words, display the equation, and then define every symbol and term that has not already been defined. Cite established methods such as the computational hydrogen electrode without retelling their elementary theory.
- Define each abbreviation once in the main text; reuse it thereafter. Use first-person plural for our actions, choices, and experiences.
- Apply the active citation-format decision from `PROMPT.txt`; keep citation placement grammatically attached to the supported sentence.

- Do not abbreviate the catalyst class as DAC.
- Do not replace diamine with base or amine.
- Do not replace dialdehyde with acid or para substituent.
- Do not call either metal-atom adsorption center a separate adsorption site; the molecular DASC has one dual-atom site.
- Do not treat catalyst identity alone as the observation when site identity matters.
- Do not use calculated and predicted interchangeably.
- Do not describe the two adsorption centers of one molecular catalyst as statistically independent.
- Do not infer an applied GPAW charge from the custom `total_charge` metadata alone.
- Do not call the model universal or claim DFT accuracy without an external reference standard.


## Selected run policy

PROMPT.txt supplies current facts and the execution contract. GitHub input downloads and relevant web research are authorized. Preserve supplied notebooks and use working copies for execution. The root `Electrochimica_Acta_research_article_refernce.docx` is reserved for comparison after generation and excluded from drafting inputs. Any historical offline examples in a reusable profile yield to this selected run policy.
