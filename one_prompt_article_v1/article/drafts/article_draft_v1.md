Accelerating Catalyst Discovery with Artificial Intelligence Using Molecular Dual-Atom Site Catalysts as a Case Study

Denis Savchenko,¹ Bruno Inácio da Silva Roux Leite,¹ Timmo-Henrik Pukk,¹ Ba Long Nguyen,¹ Vladislav Ivanistsev,²† Nadezda Kongi,¹†

¹ Institute of Chemistry, University of Tartu, Ravila 14a, 50411 Tartu, Estonia
² Department of Chemistry, University of Latvia, Jelgavas iela 1, Riga, LV-1004, Latvia

Corresponding authors: vladislav.ivanistsev@lu.lv; nadezda.kongi@ut.ee

Abstract

Accelerating catalyst discovery with artificial intelligence (AI) depends on evaluating candidate materials and communicating the evidence behind them. Here, we examine guided large language model (LLM) preparation of a complete research article from verified computational and machine learning (ML) inputs, using the oxygen reduction reaction (ORR) on molecular dual-atom site catalysts (DASCs) as a case study. Spin polarized density functional theory (DFT) calculations covered 88 structures and yielded 118 retained pathways resolved by adsorption center. The lowest calculated overpotential was 0.29 V for a Cr–Mn complex with an S–S bridge and adsorption at Mn; this is a thermodynamic descriptor, not a measured rate. Supplied ML predictions extended screening to 1,260 structures outside the DFT cohort and yielded 2,197 retained combinations of catalyst and adsorption center. Of the 220 combinations with the lowest predicted overpotentials, 215 (97.7%) had Fe at the adsorption center, compared with 17.7% of the retained pool. Sulfur-bearing bridges accounted for 53.6% of the pool and 60.5% of this group. No model was refit, and no validation performance or experimental activity is inferred. OpenAI Codex prepared the article from verified values, figures, source summaries, and author guidance; final human scientific approval remains pending. ML screening and guided LLM writing are complementary potential contributions to accelerating catalyst discovery with artificial intelligence; their effect on time or discovery outcomes was not measured.

Keywords: oxygen reduction reaction; dual-atom site catalysts; density functional theory; machine learning; scientific writing

[[FIGURE:0]]

1. Introduction

Accelerating catalyst discovery with artificial intelligence may involve both broader evaluation of candidate materials and clear communication of the evidence behind them. DFT can compare adsorption energetics across structures, while ML can extend screening beyond the structures for which each adsorbate has been calculated. Writing is a further stage: results become available for examination, comparison, and reuse only when methods and interpretations are clearly reported. Studies of chemistry journals describe publication intervals of several months, but those intervals do not measure manuscript-preparation time or the time any researcher could save by using an LLM [1,2].

Editors have emphasized a coherent scientific theme, purposeful figure selection, and interpretation that helps readers understand why results matter [3–6]. We agree that evidence needs explanation and organization. At the same time, scientific value rests on the methods and data that withstand scrutiny; narrative skill should help readers follow those foundations rather than substitute for them. We therefore ask whether guided LLM writing can communicate a data-first scientific argument while leaving the underlying calculations and their limits explicit.

Scientific writing is taught to early-career researchers through research-article instruction, peer learning, and structured writing resources [7–10]. We translated this guidance into explicit requirements for section purpose, paragraph logic, evidence attribution, and calibrated claims. These instructions constrained the LLM to explain scientific reasoning and preserve the distinction between calculated results, model predictions, and interpretation; they did not provide training or fine-tuning on the cited books or full articles.

Reusable, documented data let other researchers examine a study and pursue questions beyond its original analysis [11]. A database preserves structures and calculated values, whereas a paper selects and explains a particular interpretation of them. We used both forms: the molecular structures and energy data remained available for inspection, while the article connects them to oxygen-reduction thermodynamics and candidate screening. This separation makes writing delegation compatible with independent scientific reuse.

Scientific text prepared with LLM assistance has attracted attention because changes in vocabulary may be consistent with increased LLM use, while faithful communication still depends on evidence and context [12]. A recent data-to-paper study linked generated manuscripts to annotated data and analytical outputs and emphasized the value of human guidance as research questions became more complex [13]. Our contribution is narrower: we guided an LLM to prepare a complete electrochemistry research article from verified DFT calculations, supplied ML predictions, figures, and approved scientific and literature summaries. Generation demonstrates that a manuscript can be produced; it does not by itself establish scientific novelty, accuracy beyond the checked evidence, or faster publication.

Figure 1 presents scientific communication as a seven-stage cycle: brainstorm, structure, draft, revise, polish, publish, and share. We used the LLM during author-guided brainstorming, structuring, drafting, revision, and polishing, and for authorized assistance with data checks and figure code. We set the research question and evidence boundaries, examined generated values against the local databases and tables, and revised claims when the audit changed the ranking. Publication and sharing remain subsequent author actions.

[[FIGURE:1]]
Figure 1. Seven-stage scientific-writing cycle: brainstorm, structure, draft, revise, polish, publish, and share. The surrounding notes connect each stage to the relevant research inputs, manuscript tasks, checks, journal submission, archiving, and open sharing. In this study, the LLM assisted authors during guided brainstorming through polishing and supported authorized code and data-analysis tasks; publication and sharing remain subsequent author actions.


We examined how the metal pair, adsorption center, bridge pair, and diamine relate to calculated ORR thermodynamics for molecular DASCs, and whether supplied predictions extend that comparison beyond the DFT cohort. Our DFT calculations established adsorption and ORR thermodynamic evidence for 88 molecular DASC structures through the limiting-potential analysis [14]. Supplied ridge-model predictions extended screening to 1,260 additional structures outside that cohort. We then used an author-guided LLM to prepare a complete electrochemistry article from verified inputs while preserving the distinction between calculations and predictions. This case examines guided writing as a potential contribution to accelerating catalyst discovery with artificial intelligence; faster publication or research was not measured.

2. Computational methods

2.1. Catalyst structures

Molecular DASC structures were obtained from the supplied parent dataset and its extended set [15,16]. Each structure was composed of a pair of metal atoms, two bridging donor atoms, a diamine unit, and a dialdehyde unit. The diamines were designated B1 (1,2-phenylenediamine) and B2 (1,8-naphthalenediamine), and the dialdehyde was designated A2 (2-hydroxyisophthalaldehyde) [15]. Eighty-eight parent structures were included in the current DFT cohort. A total of 1,348 clean catalyst structures were included in the wider database, of which 1,260 were outside the DFT cohort. When intermediate energies were available, each pairing of a parent structure and a metal-atom adsorption center was treated as a separate pathway.

2.2. DFT calculations and adsorption structures

Spin polarized calculations were performed with the projector augmented-wave method in GPAW 24.6, using the revised Perdew–Burke–Ernzerhof functional and the D4 dispersion correction [17–19]. A plane-wave cutoff of 550 eV and a real-space grid spacing of 0.15 Å were used, and periodic images were separated by 6 Å of vacuum. Structures were fully optimized until the maximum force was below 0.05 eV Å⁻¹. A net charge of +2 was used for clean and adsorbate bound calculations. Structures and calculations were managed with the Atomic Simulation Environment (ASE) 3.23.0 [18].

OH, O, and OOH adsorption calculations were matched to clean structures by parent structure name and adsorption center identity. A leading asterisk marks a species bound at the selected adsorption center: *X is intermediate X adsorbed there, and * alone denotes the corresponding clean catalyst. Adsorption energies were reconstructed from the total energy of each structure with an adsorbate, the corresponding clean structure, and the supplied reference offsets specific to each species: 10.605 eV for OH, 7.240 eV for O, and 17.845 eV for OOH. Each offset was added once (Eq 1).

[[EQ:1]]

2.3. Adsorption free energies and ORR thermodynamics

Adsorption free energies were obtained from the adsorption potential energies and the supplied combined thermochemical corrections at 300 K. The net corrections were 0.05 eV for OH, 0.05 eV for O, and 0.10 eV for OOH, incorporating transferred zero-point-energy, entropy, and solvation terms [20,21] (Eqs 2–3). Corrections were added once to both DFT derived and predicted adsorption potential energies. No catalyst specific vibrational or solvent calculations were performed, and no gas-phase zero-point correction was added a second time.

[[EQ:2]]
[[EQ:3]]

The four-electron ORR was evaluated through the associative sequence O₂ to *OOH, *OOH to *O, *O to *OH, and *OH to H₂O. The computational hydrogen electrode (CHE) was used to calculate the potential of each proton-electron transfer from the corrected intermediate free energies [14] (Eqs 4–7); e denotes the positive elementary charge, which converts the free-energy change per transferred electron to a potential. For each pathway, the limiting potential was defined as the smallest of the four step potentials (Eq 8), and the thermodynamic overpotential was defined as the 1.23 V equilibrium potential minus that limiting potential (Eq 9). These values are thermodynamic descriptors under the stated model, not reaction rates or experimentally measured activities.

[[EQ:4]]
[[EQ:5]]
[[EQ:6]]
[[EQ:7]]
[[EQ:8]]
[[EQ:9]]

2.4. Scaling and thermodynamic activity analyses

Adsorption energy scaling relations were fitted across the retained pathways resolved by adsorption center using ordinary least squares. The OOH–OH and O–OH scaling relations were calculated separately. The CHE activity plot was constructed from the fitted scaling relations and compared with the ideal relation; its limiting-potential curve is a thermodynamic construction rather than a fit to measured current or rate. Only complete, exactly matched intermediate sets that satisfied the filters on uncorrected adsorption potential energies were included in the DFT pathway analysis: OH adsorption potential energy at or above 0 eV and O adsorption potential energy at or below 4.92 eV.

2.5. Regression analysis and catalyst family screening

Separate ridge regressions for OH, O, and OOH adsorption potential energies were supplied as the source of the prediction inputs. The models were described by the authors as using descriptors of electron population, charge, spin, metal-pair polarization, and ligand environment, with eight predictors for OH and O and six for OOH. The specified ridge parameters were 0.10 for OH and 1.00 for O and OOH. Training medians, means, standard deviations, and standardized coefficients were not included in the registered inputs used for this independent run; therefore, model parameters were not replayed and no model was refit.

Roles were assigned to 50 training structures and 10 validation structures; predictions were supplied for 1,288 named structures, including 28 that overlapped the DFT parent cohort and 1,260 outside it. Target energy spread was used to inform validation membership, so the validation set is not an untouched external test. Validation metrics were unavailable. A total of 6,648 prediction rows were supplied, with three intermediate specific values for each of 2,216 combinations of parent structure and adsorption center. The OH and O electronic energy filters were applied first to the uncorrected prediction energies; thermochemical corrections were then added once to retained values for free energy and CHE analysis. The 220-member lowest decile group was defined by ascending predicted overpotential among the 2,197 retained combinations, with ties ordered by parent name and adsorption center label.

2.6. LLM manuscript generation

A consolidated instruction package was developed over approximately two weeks before the independent article-generation run. OpenAI Codex was given the registered data, generated figures, author-approved scientific decisions, literature summaries, journal requirement map, and writing instructions. The LLM was directed to produce original prose, distinguish DFT results from supplied predictions, cite the approved sources, and retain unresolved review status. Working copies of the figure notebooks were executed in sequence, and generated values were checked against the registered databases and prediction tables. The article was then reviewed through separate scientific, journal-editorial, and style passes; the document was built from the approved text and figure assets. The two-week instruction-development period was not treated as a manuscript-generation time measurement, and no time-saving comparison was performed.

3. Results and discussion

3.1. Molecular structures and adsorption centers

The molecular design varies the metal pair, bridge pair, and diamine while retaining A2 in the illustrated structure. Figure 2 shows a representative Co₂ complex with O–O bridging, B1, and adsorption at one metal-atom adsorption center. Each molecular DASC has one dual-atom site containing two metal-atom adsorption centers; an intermediate may bind at either center. These structural variations provide distinct metal pair and ligand environments for comparing adsorption energies, while each molecular structure remains one catalyst parent. Thus, each pathway represents a parent structure paired with one adsorption center, not a separate molecular structure.

[[FIGURE:2]]
Figure 2. Molecular structure and adsorption center definition for a representative Co₂–A2–B1 complex with an O–O bridge. The two metal atoms provide the paired adsorption centers within one dual-atom site; the marked center shows where the intermediate binds in the pathway analysis. B1 is 1,2-phenylenediamine, B2 is 1,8-naphthalenediamine, and A2 is 2-hydroxyisophthalaldehyde. Structure notation and parent molecular dataset are from Nguyen et al. [15].

3.2. Adsorption scaling relations and calculated ORR thermodynamics

Exact matching produced 123 complete pathways for parent structure and adsorption center combinations from the adsorbate calculations; 25 additional parent structure and adsorption center pairs lacked at least one required intermediate. The OH and O filters then excluded five complete pathways: four with O adsorption potential energy above 4.92 eV and one with OH adsorption potential energy below 0 eV, leaving 118 retained pathways from 79 parent structures. The DFT lowest decile comprised 12 pathways: five with Co, four with Mn, and three with Fe at the adsorption center, with seven S–S, four N–N, and one O–O bridge pair.

Across the 118 retained pathways, the fitted OOH–OH scaling relation had a slope of 0.70 and an intercept of 3.04 eV; the O–OH fit had a slope of 1.66 and an intercept of 1.18 eV. The slope is dimensionless, and the intercept is expressed in electronvolts. These regressions summarize the sampled pathways and feed the CHE activity construction; their intercepts are not individual catalyst specific adsorption separations. The calculated limiting potential analysis identified the Cr–Mn complex with an S–S bridge, A2/B1 ligands, and adsorption at Mn as the lowest overpotential retained pathway (Uₗ = 0.94 V; η = 0.29 V). The next two were Mn–Ni and Mn–Mn, both with S–S bridges, A2/B1 ligands, and adsorption at Mn, at 0.30 and 0.34 V, respectively. OH removal was the potential determining step for all three. These rankings identify calculated thermodynamic candidates for further study, not experimentally established catalysts.

[[FIGURE:3]]
Figure 3. DFT adsorption scaling and ORR thermodynamic analysis for 118 retained combinations of parent structure and adsorption center. (a) Calculated OH, O, and OOH adsorption free energies and their fitted scaling relations; squares denote OOH and circles denote O. (b) CHE limiting-potential curve derived from the fitted scaling relations, with the ideal scaling relation shown separately as a dotted line. Volcano points are diamonds. Colors identify the element at the adsorption center: Cr, blue gray; Mn, violet; Fe, orange; Co, pink; Ni, green; and Cu, brown. The plotted potentials are calculated thermodynamic descriptors.

3.3. Regression predictions across catalyst families

The supplied predictions produced complete OH/O/OOH triples for 2,216 combinations of parent structure and adsorption center; 2,197 passed the electronic energy filters. Of those retained combinations, 220 formed the lowest decile by predicted overpotential. The group contained 215 combinations with Fe and five with Co at the adsorption center; 141 used B1 and 79 B2. Bridge pair counts were S–S 58, N–S 46, O–O 33, O–S 29, N–N 29, and N–O 25.

Fe at the adsorption center accounted for 388/2,197 (17.7%) of the retained pool and 215/220 (97.7%) of the lowest decile group, a 5.53-fold representation ratio. Any sulfur-bearing bridge (S–S, N–S, or O–S) accounted for 1,178/2,197 (53.6%) of the full pool and 133/220 (60.5%) of the lowest decile. S–S bridges specifically comprised 364/2,197 (16.6%) overall and 58/220 (26.4%) in the group with the lowest predicted overpotentials, while B1 accounted for 52.4% overall and 64.1% of that group. The joint category with Fe at the adsorption center, a sulfur-containing bridge, and B1 accounted for 105/2,197 (4.8%) overall and 83/220 (37.7%) in the lowest decile. These are descriptive proportions among the supplied model predictions; they do not establish that any one feature causes low overpotential or that an individual combination is experimentally active.

The predicted-energy fits differed from the DFT regressions: the O-versus-OH slope/intercept were 1.775/1.093 eV, and the OOH-versus-OH values were 0.650/3.161 eV. Figure 4 shows the supplied predictions and corresponding thermodynamic construction for the retained combinations. The prediction tables are an extension of candidate screening, not an independent measurement or a validation set. The absence of current model coefficients, scalers, and validation metrics limits attribution of these family patterns to a reproducible model mechanism.

[[FIGURE:4]]
Figure 4. Adsorption scaling and ORR thermodynamics from supplied ML predictions for 2,197 retained combinations of parent structure and adsorption center. (a) Predicted OH, O, and OOH adsorption free energies and fitted scaling relations; squares denote OOH and circles denote O. (b) CHE limiting-potential curve derived from the fitted relations, with the ideal scaling relation shown separately as a dotted line. Volcano points are diamonds. Colors identify the element at the adsorption center: Cr, blue gray; Mn, violet; Fe, orange; Co, pink; Ni, green; and Cu, brown. The 220 combinations with the lowest predicted overpotentials define the lowest decile discussed in the text; predictions are not experimental activities.

3.4. Molecular catalyst design in context

Scaling relations provide useful thermodynamic organization, yet breaking a relation alone does not establish improved electrocatalysis [22,23]. The present DFT fits and volcano construction locate pathways within the assumptions of the CHE analysis. They do not establish kinetic barriers, stability under operating conditions, or measured ORR performance.

A study of 60 homonuclear salphen catalytic units examined oxygen evolution through DFT, XGBoost, and SISSO. Its reported OH–OOH fit (slope 0.96, intercept 2.98 eV) differs from our DFT fit (slope 0.70, intercept 3.04 eV), but reaction, sampled structures, and computational corrections also differ [24]. We treat the comparison as context rather than as a controlled benchmark.

Other molecular dual-atom studies illustrate structural and scaling possibilities beyond the present +2 calculation set. A Co₂ study associated a bidentate OOH geometry with an OH–OOH separation of 2.73 eV, below the conventional 3.15 eV comparison; that individual separation is not the global intercept of a fitted scaling relation, and our present calculations did not obtain that bidentate OOH geometry [25]. A related +4 O-bridged Co–Co calculation used different free-energy corrections and cannot be ranked directly against the current +2 set [26].

ML screening is already used with DFT in electrocatalysis. The cited work spans Fe dual-atom and cluster-modified single-atom ORR studies, data-driven OER research, and unsupervised HER candidate grouping [27–30]. These sources document candidate selection informed by ML across catalyst families and reactions, but their model evidence and experimental results do not transfer to our predictions. This study examines a molecular ORR set and a guided article-generation demonstration; it does not establish novelty for ML screening itself.

Related Fe–N coordination studies concern single-metal macrocycles and offer ligand context rather than evidence for bimetallic cooperation in these DASC structures [31].

3.5. Closing the scientific communication gap

Writing is part of scientific work because methods and results can be evaluated only when their sources and limits are clear. In this case, an author-guided LLM produced a complete article from verified calculations, supplied predictions, figures, and approved scientific and literature summaries. This demonstrates feasibility for one bounded case; no time comparison or downstream discovery outcome was measured, and article generation did not independently establish the scientific findings.

Explicit scientific-writing conventions provided a teachable basis for linking claims to evidence. During review, the verified Mn–Ni pathway replaced an initially proposed second-place DFT example, illustrating the need to check the complete ranking against the pathway results. This correction shows that researchers retain responsibility for interpreting calculations and deciding which claims the evidence supports; an LLM can assist with article preparation under that oversight.


3.6. Data and alternative interpretations

The CHE limiting-potential analysis is one thermodynamic interpretation of the adsorption energies. A free-energy-span descriptor could reorganize the same sequence of intermediate energies, and alternative corrections or explicit solvent and kinetic calculations could change the comparison [32]. None of those analyses was performed here. The current results therefore identify candidate pathways within the supplied correction scheme and emphasize which structural families the prediction screen places in its lowest decile; they do not resolve kinetic control, solvation dependence, catalyst stability, or experimental performance. The 88-structure DFT cohort and 1,260 additional predicted structures remain distinct evidence sources, with 28 parent structures represented in both the DFT and prediction inputs.

The DFT databases, molecular structures, derived figure data, and prediction inputs support reanalysis and reuse. The parent molecular structures are available under a separate DOI from the current DFT and extended-structure dataset [16,33]. The prediction CSV and JSON inputs were supplied in the project’s figure4 directory. Sharing these structured files alongside the article allows other researchers to select alternative adsorption centers, compare subsets, or apply additional thermodynamic analyses, consistent with the aims of reusable scientific data [11].

4. Conclusions

A guided large language model prepared a complete scientific article from verified calculations, supplied predictions, figures, and author instructions, while machine learning predictions extended screening beyond the density functional theory cohort. Together, ML-based screening and guided manuscript preparation represent complementary potential contributions to accelerating catalyst discovery with artificial intelligence; neither writing time nor discovery acceleration was measured. Final human scientific approval remains pending.

Density functional theory calculations covered 88 molecular dual-atom site catalysts and yielded 118 retained pathways, each pairing a parent structure with an adsorption center. Supplied machine learning predictions extended screening to 1,260 structures outside the density functional theory cohort. Among the 2,197 retained predicted combinations, sulfur-bearing bridges accounted for 53.6%, compared with 60.5% of the 220 combinations with the lowest predicted overpotentials; 215 of those 220 combinations had Fe at the adsorption center. These family patterns among the model predictions nominate candidates for further calculation rather than experimental recommendations.

Explicit scientific-writing conventions guided the large language model toward a coherent article while methods, data provenance, and the distinction between calculations and predictions remained visible. Density functional theory and machine learning expand the candidate structures available for evaluation, while a guided large language model can assist researchers in communicating the resulting evidence under scientific oversight. The potential for this assistance to give researchers more room to focus on scientific questions and methods remains unmeasured.

CRediT authorship contribution statement

Denis Savchenko: Methodology, Software (regression-model development), Formal analysis, Visualization. Bruno Inácio da Silva Roux Leite: Investigation (DFT calculations), Data curation, Formal analysis. Timmo-Henrik Pukk: Investigation (DFT calculations), Data curation, Formal analysis. Ba Long Nguyen: Investigation (DFT calculations), Software, Data curation, Formal analysis, Visualization. Vladislav Ivanistsev: Conceptualization, Supervision, Funding acquisition. Nadezda Kongi: Conceptualization, Supervision, Funding acquisition.

Declaration of competing interest

The authors declare no competing financial interests or personal relationships that could have influenced the work reported in this article.

Data availability

The project source repository is available at https://github.com/doublelayer/EActa_2026_AI-acceleration [34]. The parent molecular-structure dataset is available at https://doi.org/10.5281/zenodo.18601379 [16], and the author-confirmed DOI for the current DFT and extended-structure dataset is https://doi.org/10.5281/zenodo.23408498 [33]. The prediction CSV and JSON inputs used in this work are supplied with the project’s figure4 analysis files. The source notebooks and the generated figure exports accompany the project files.

Generative AI declaration

OpenAI Codex was used under author guidance to prepare the manuscript and assist with authorized data auditing, figure execution, and document construction. Authors supplied the research question, source data, scientific decisions, and review instructions; the generated text and numerical claims were checked against the registered inputs and revised through scientific, editorial, and style review. OpenAI Codex is not an author. The authors remain responsible for the article’s content, and final human scientific approval is pending.

Funding
This work was supported by the National Research Program BioPhoT through the project Nr. OSI_PIP_BioPhoT-2025/2-0069.

Acknowledgments

This work was supported by the National Research Program BioPhoT through the project Nr. OSI_PIP_BioPhoT-2025/2-0069.

We acknowledge support from the Estonian Ministry of Education and Research (TK210) and the Estonian Research Council (PRG3174, TEM-TA306), COST Action EU-CONCERT (CA24103), the University of Latvia Artificial Intelligence and Computing Center, and the High Performance Computing Center of the University of Tartu.

References

[1] B.-C. Björk, D. Solomon, The publishing delay in scholarly peer-reviewed journals, J. Informetr. 7 (2013) 914–923. https://doi.org/10.1016/j.joi.2013.09.001.

[2] J. Ding, D. Du, A study of the correlation between publication delays and measurement indicators of journal articles in the social network environment: based on online data in PLOS, Scientometrics 128 (2023) 1711–1743. https://doi.org/10.1007/s11192-023-04640-6.

[3] L. X. Chen, P. Christopher, F. De Angelis, S. Jin, Y.-S. Hu, N.-G. Park, D. Das Sarma, Y.-K. Sun, P. V. Kamat, We Editors Are Authors, Too, ACS Energy Lett. 4 (2019) 249–250. https://doi.org/10.1021/acsenergylett.8b02322.

[4] Elements of style, Nat. Phys. 3 (2007) 581. https://doi.org/10.1038/nphys724.

[5] Storytelling in research, Nat. Biomed. Eng. 2 (2018) 53. https://doi.org/10.1038/s41551-018-0202-5.

[6] Should scientists tell stories?, Nat. Methods 10 (2013) 1037. https://doi.org/10.1038/nmeth.2726.

[7] H. Glasman-Deal, Science Research Writing for Non-Native Speakers of English, Imperial College Press, London and Hackensack, NJ, 2010.

[8] M. A. Stiller-Reeve, C. Heuzé, W. T. Ball, R. H. White, G. Messori, K. van der Wiel, I. Medhaug, A. H. Eckes, A. O’Callaghan, M. J. Newland, S. R. Williams, M. Kasoar, H. E. Wittmeier, V. Kumar, Improving together: better science writing through peer learning, Hydrol. Earth Syst. Sci. 20 (2016) 2965–2973. https://doi.org/10.5194/hess-20-2965-2016.

[9] Coursera, Writing in the Sciences (Stanford Online). https://www.coursera.org/learn/sciwrite (accessed 17 October 2026).

[10] B. Minto, The Minto Pyramid Principle: Logic in Writing and Thinking, Prentice Hall, 2010.

[11] M. D. Wilkinson et al., The FAIR guiding principles for scientific data management and stewardship, Sci. Data 3 (2016) 160018. https://doi.org/10.1038/sdata.2016.18.

[12] D. Kobak, R. González-Márquez, E.-A. Horvát, J. Lause, Delving into LLM-assisted writing in biomedical publications through excess vocabulary, Sci. Adv. 11 (2025) eadt3813. https://doi.org/10.1126/sciadv.adt3813.

[13] T. Ifargan, L. Hafner, M. Kern, O. Alcalay, R. Kishony, Autonomous LLM-Driven Research: from Data to Human-Verifiable Research Papers, NEJM AI 2 (2025). https://doi.org/10.1056/aioa2400555.

[14] J. K. Nørskov, J. Rossmeisl, A. Logadottir, L. Lindqvist, J. R. Kitchin, T. Bligaard, H. Jónsson, Origin of the overpotential for oxygen reduction at a fuel-cell cathode, J. Phys. Chem. B 108 (2004) 17886–17892. https://doi.org/10.1021/jp047349j.

[15] B. L. Nguyen, T. K. Madsen, V. Ivanistsev, N. Kongi, Dataset of molecular dual-atom site complexes for catalysis, Data Brief 66 (2026) 112806. https://doi.org/10.1016/j.dib.2026.112806.

[16] [dataset] B. L. Nguyen, T. K. Madsen, V. Ivanistsev, N. Kongi, Dataset of molecular dual-atom site complexes for catalysis, Zenodo, version 1.0, 2026. https://doi.org/10.5281/zenodo.18601379.

[17] J. J. Mortensen et al., GPAW: An open Python package for electronic structure calculations, J. Chem. Phys. 160 (2024) 092503. https://doi.org/10.1063/5.0182685.

[18] A. H. Larsen et al., The Atomic Simulation Environment—A Python Library for Working with Atoms, J. Phys.: Condens. Matter 29 (2017) 273002. https://doi.org/10.1088/1361-648X/aa680e.

[19] E. Caldeweyher, S. Ehlert, A. Hansen, H. Neugebauer, S. Spicher, C. Bannwarth, S. Grimme, A generally applicable atomic-charge dependent London dispersion correction, J. Chem. Phys. 150 (2019) 154122. https://doi.org/10.1063/1.5090222.

[20] J. Rossmeisl, A. Logadottir, J. K. Nørskov, Electrolysis of water on (oxidized) metal surfaces, Chem. Phys. 319 (2005) 178–184. https://doi.org/10.1016/j.chemphys.2005.05.038.

[21] F. Calle-Vallejo, J. I. Martínez, J. Rossmeisl, Density functional studies of functionalized graphitic materials with late transition metals for oxygen reduction reactions, Phys. Chem. Chem. Phys. 13 (2011) 15639–15643. https://doi.org/10.1039/c1cp21228a.

[22] V. Ivanistsev, R. Cepitis, J. Rossmeisl, N. Kongi, Twenty years after: scaling relations in oxygen electrocatalysis and beyond, Chem. Soc. Rev. 54 (2025) 10956–10976. https://doi.org/10.1039/D5CS00597C.

[23] N. Govindarajan, J. M. García-Lastra, E. J. Meijer, F. Calle-Vallejo, Does the breaking of adsorption energy scaling relations guarantee enhanced electrocatalysis?, Curr. Opin. Electrochem. 8 (2018) 110–117. https://doi.org/10.1016/j.coelec.2018.03.025.

[24] Z. Zhang, Z. Zhang, C. Chen, R. Xu, X.-B. Chen, H. Lu, Z. Shi, Y. Han, S. Feng, Design and Synthesis of Electrocatalysts Base on Catalysis-Unit Engineering, Adv. Mater. 36 (2024) 2403549. https://doi.org/10.1002/adma.202403549.

[25] Q. Sun et al., Well-Defined Co₂ Dual-Atom Catalyst Breaks Scaling Relations of Oxygen Reduction Reaction, J. Am. Chem. Soc. 146 (2024) 35295–35304. https://doi.org/10.1021/jacs.4c12705.

[26] N. Žoglo et al., Intersite geometry controls activity and selectivity in the oxygen reduction reaction on dual-atom-site catalysts, ChemRxiv preprint (2026). https://doi.org/10.26434/chemrxiv.15001712/v1.

[27] S. Jia, L. Yang, C. Wu, B. Xiao, J. Tian, H. Zhu, Q. Tan, Y. Li, A. Li, Machine learning reveals role-asymmetric electronic cooperation in Fe-based dual-atom catalysts, Adv. Mater. (2026) e74833. https://doi.org/10.1002/adma.74833.

[28] L. Jia, Z. Jin, Y. Tan, Z. Zhang, Y. Pu, Y. Wang, L. Huang, From Data to Discovery: Crafting Data-Driven Frameworks for Advancing OER Electrocatalysts, Adv. Funct. Mater. 36 (2026) e77325. https://doi.org/10.1002/adfm.77325.

[29] X. Chen, Y. Xu, D. Ye, J. Xu, Y. Wang, G. Jia, X. Cui, J. Zhao, Leveraging DFT and machine learning for accelerated screening of cluster-modified single-atom catalysts in oxygen reduction reactions, ACS Catal. 16 (2026) 14399–14410. https://doi.org/10.1021/acscatal.6c02383.

[30] A. Benarbia, A. Alshami, A. Mustafa, O. S. Tomomewo, Can machine learning uncover viable non-platinum catalysts for hydrogen evolution? An unsupervised clustering approach to transition metal–ligand complexes, RSC Adv. 16 (2026) 42403–42417. https://doi.org/10.1039/d6ra03405e.

[31] Q. Li, Q. Zhao, A. Pedersen, Z. Lin, M. Zhang, D. Di Tommaso, Y. Xu, M.-M. Titirici, C. R. Jones, Investigating the effect of the coordination environment and bridging atoms in Fe–N₄ macrocycles applied to alkaline oxygen reduction reaction, ACS Catal. 16 (2026) 9913–9929. https://doi.org/10.1021/acscatal.6c00046.

[32] S. Razzaq, K. S. Exner, Materials screening by the descriptor Gmax(I⁺): the free-energy-span model in electrocatalysis, ACS Catal. 13 (2023) 1740–1758. https://doi.org/10.1021/acscatal.2c03997.

[33] [dataset] Zenodo record 23408498 (2026). https://doi.org/10.5281/zenodo.23408498.

[34] EActa_2026_AI-acceleration project repository. https://github.com/doublelayer/EActa_2026_AI-acceleration.
