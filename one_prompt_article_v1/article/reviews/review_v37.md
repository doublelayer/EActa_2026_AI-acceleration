# DOCX review record for manuscript version 37

This record preserves a text projection of the complete archived DOCX, including inline tracked insertions and deletions, followed by all embedded Word comments and their anchor paragraphs. The source DOCX remains authoritative for page layout and visual details; embedded figures are marked in the text projection.

- Source DOCX: `../manuscript_versions/Electrochimica_Acta_research_article_draft_v37.docx`
- Source DOCX SHA-256: `817b2c77226e92b7847ccd2d888bc53f291ceac101d0fa629df11d3fc9650b4c`
- Embedded document XML SHA-256: `563240a5e1e5f216a5068203866874a791149c4df705ff88d2b48e8dd1063688`
- Embedded comments XML SHA-256: `35dba8a8bf102da37447c0e023e99f9439353985770d481a7e178105beace14c`
- DOCX text paragraphs: 113
- DOCX text projection SHA-256: `5323ed43e796fce6c281c016380a579473a5cc345f091471be1e11765c842e2e`
- Word review comments: 4
- Tracked insertions: 19
- Tracked deletions: 13

## Full DOCX text and tracked changes

Each paragraph is shown in document order. `[[INSERT ...]]` and `[[DELETE ...]]` retain the revision text, Word revision ID, author, and timestamp.

~~~~~text
<!-- BEGIN FULL DOCX TEXT -->
P00001  Accelerating Catalyst Discovery[[DELETE id=0; author=Vladislav Ivanistsev; date=2026-10-12T05:55:55Z:  and Design]] with Artificial Intelligence: Molecular Dual-Atom Site Catalysts as a Case Study
P00002  Bruno Inácio da Silva Roux Leite,1 Denis Savchenko,1 Timmo-Henrik Pukk,1 Ba Long Nguyen,1 Vladislav Ivanistsev,2† Nadezda Kongi,1†
P00003  1 Institute of Chemistry, University of Tartu, Ravila 14a, 50411 Tartu, Estonia
P00004  2 Department of Chemistry, University of Latvia, Jelgavas iela 1, Riga, LV-1004, Latvia
P00005  Corresponding authors: vladislav.ivanistsev@lu.lv; nadezda.kongi@ut.ee
P00006  Abstract
P00007  Artificial intelligence (AI) can accelerate catalyst discovery and design when it connects reliable data to scientific decisions and clear communication. We demonstrate this general role through molecular dual-atom site catalysts[[INSERT id=1; author=Vladislav Ivanistsev; date=2026-10-12T05:52:51Z:  (DASC)]] for the oxygen reduction reaction. We used density functional theory (DFT) to establish adsorption scaling and thermodynamic activity[[DELETE id=2; author=Vladislav Ivanistsev; date=2026-10-12T05:52:31Z:  at identified metal sites]] and[[INSERT id=3; author=Vladislav Ivanistsev; date=2026-10-12T05:52:34Z: , then,]] machine learning (ML) to extend the analysis across the molecular[[INSERT id=4; author=Vladislav Ivanistsev; date=2026-10-12T05:53:11Z:  DASCs']] library. We then asked a large language model (LLM) to follow the same traceable record into analysis code, figures, and the complete article. At every stage, we could inspect the record behind its output and accept only what the science supported. The result shows where the acceleration comes from: once the scientific record is reusable, AI can carry it from one research task to the next without forcing us to reconstruct the work each time. [[INSERT id=5; author=Vladislav Ivanistsev; date=2026-10-12T05:54:24Z: Authors]][[DELETE id=5; author=Vladislav Ivanistsev; date=2026-10-12T05:54:24Z: We]] remain responsible for deciding what to ask, what the evidence means, and what the article may claim.
P00008  Keywords: AI; DFT; ML; LLM; oxygen reduction reaction; molecular dual-atom site catalysts
P00009  1. Introduction
P00010  Accelerating catalyst discovery and design with artificial intelligence (AI) means more than predicting a property faster. A result must travel from molecular structures and calculations into comparisons, decisions, and eventually a form that another scientist can test. Each transition takes time and can separate a conclusion from the evidence that produced it. We use AI to keep that chain moving while the scientific record remains explicit and researchers continue to direct the work.
P00011  The oxygen reduction reaction (ORR) gives us a concrete test. Its four electron pathway depends on the binding of O, OH, and OOH, so correlations among their adsorption free energies constrain thermodynamic activity [10.1021/jp047349j]. Molecular dual-atom site catalysts provide a defined chemical space in which metal identity, bridge, diamine, and adsorption site vary, see Figure 1. Related molecular catalysts show how binding geometry and the second metal can change oxygen intermediate energetics [10.1021/jacs.4c12705; 10.26434/chemrxiv.15001712/v1]. This combination of chemical variation and site resolved data lets us ask where AI can assist and where scientific judgment remains decisive.
P00012  Scientific publishing has made the coherent story a measure of a successful paper. Editors have described story as the organizing principle of an article, asked authors to build discussion around a single theme, and called figures the backbone or even the most persuasive part of the paper [10.1038/nphys724; 10.1021/acsenergylett.8b02322; 10.1038/s44160-022-00067-8; 10.1038/s41567-021-01332-x]. We accept the need for clarity and question the labor assigned to producing it. When data are structured, methods are explicit, and sources remain linked, a guided large language model (LLM) can compose much of the scientific story and return researchers' attention to the science.
P00013  That transfer of labor is useful only when fluent prose remains answerable to evidence. Storytelling can hide an inconvenient result even without generative AI [10.1038/nmeth.2726], and inexpensive polished text makes such failures easier to multiply. Ifargan and colleagues showed that interacting LLM agents can move from annotated data to human verifiable papers, with human guidance becoming more important as the research question grows more complex [10.1056/aioa2400555]. We adopt the same essential standard: the story must answer the record. We test it here by following density functional theory (DFT) data through adsorption scaling and thermodynamic analysis in Figure 2, extending the analysis with machine learning (ML) in Figure 3, and directing the LLM to write the complete article. We still decide what question to ask, how to test it, and what the evidence permits us to say.
P00014  2. Computational methods
P00015  2.1. Catalyst structures
P00016  We assembled the molecular catalysts from the components shown in Figure 1. Following the notation introduced in our data article [10.1016/j.dib.2026.112806], A2 denotes the fixed dialdehyde and B1 and B2 denote the two diamines. Each molecule contains two metal centers chosen from Cr, Mn, Fe, Co, Ni, and Cu and bridge atoms selected from N, O, or S. The same article describes the molecular assembly and initial structure preparation. We fully optimized all structures used in the DFT analysis, including the clean catalysts and structures containing adsorbed intermediates. The clean database used here contains 88 molecular catalysts.
P00017  We retained the catalyst identity, metal positions, ligand components, and charge metadata in the Atomic Simulation Environment (ASE) database.
P00018  2.2. DFT calculations and adsorption structures
P00019  We performed spin polarized DFT calculations with GPAW 26.7 and ASE 3.29.0 software [10.1063/5.0182685; 10.1088/1361-648X/aa680e]. We used the projector augmented wave method, the revised Perdew–Burke–Ernzerhof functional, and the D4 dispersion correction [10.1063/1.5090222]. The calculations used a plane wave cutoff of 550 eV, a real space grid spacing of 0.16 Å, and 6.00 Å vacuum. We fully optimized every atomic structure until the maximum force was below 0.05 eV Å⁻¹. We previously used the same calculation setup for related molecular catalysts [10.26434/chemrxiv.15001712/v1].
P00020
P00021  We placed O, OH, and OOH at the metal adsorption sites identified in Figure 1 and fully optimized each structure. We calculated gas phase H₂ and H₂O with the same settings. We joined all total energies by catalyst name and adsorption site label, so each reaction pathway refers to one metal atom in one molecular catalyst.
P00022  We obtained the adsorption energies of O, OH, and OOH from the total energies of the corresponding adsorbed structure, clean catalyst, H₂, and H₂O:
P00023
P00024  	(1)
P00025
P00026  	(2)
P00027
P00028  	(3)
P00029  In Eqs. (1)–(3), the left side is the adsorption energy of the named intermediate. The terms on the right are the total energies of the adsorbed catalyst, the clean catalyst, gas phase H₂, and gas phase H₂O; * denotes the adsorption site. We used the supplied corrected adsorption free energies for scaling and thermodynamic analyses.
P00030  2.3. Adsorption free energies and ORR thermodynamics
P00031  We converted adsorption energies to adsorption free energies by adding the zero point and entropic corrections:
P00032
P00033  	(4)
P00034  In Eq. (4), X denotes O, OH, or OOH; E and G denote electronic energy and Gibbs free energy; T is temperature; S is entropy; and ZP identifies the zero point contribution. The supplied adsorption free energies already include these corrections. We evaluated the four reduction potentials for the associative four electron ORR pathway with the computational hydrogen electrode (CHE) method [10.1021/jp047349j]:
P00035
P00036  	(5)
P00037  Equation (5) lists the positive step reduction potentials for four reductions: O₂ to OOH, OOH to O, O to OH, and OH to H₂O; e is the elementary charge. The limiting potential is the lowest of the four step potentials:
P00038
P00039  	(6)
P00040  The symbol on the left of Eq. (6) is the limiting potential. We evaluated the ORR overpotential relative to the 1.23 V equilibrium potential:
P00041
P00042  	(7)
P00043  Equation (7) gives the ORR overpotential. Chemical subscripts in Eqs. (5)–(7) identify the adsorbed intermediate or the reaction quantity.
P00044  2.4. Scaling and thermodynamic activity analyses
P00045  We described the correlations of O and OOH adsorption free energies with OH adsorption free energy by ordinary least squares:
P00046
P00047  	(8)
P00048  In Eq. (8), α and β are the slope and intercept for the intermediate identified by the subscript. The curves in Figures 2 and 3 propagate the corresponding global fits through the four reaction steps. We also considered the electrochemical step symmetry index and free energy span as complementary thermodynamic interpretations [10.1016/j.coelec.2018.03.025; 10.1021/acscatal.2c03997]. For comparison, we defined an ideal relation with an OOH–OH free energy separation of 2.46 eV and the corresponding two-branch overpotential:
P00049
P00050  	(9)
P00051  In Eq. (9), OH removal defines the left branch and OOH formation the right branch. They meet at an OH adsorption free energy of 1.23 eV and zero overpotential. This reference represents balanced binding; the catalyst points and fitted curves use all four reaction steps. Thermodynamic rankings describe reaction free energies, while kinetic activity also depends on activation barriers.
P00052  2.5. ML regression analysis
P00053  For the ML analysis, we used fitted ridge regression models for OH, O, and OOH adsorption free energies. Their clean catalyst descriptors represent Bader charge and electron population, local spin, and ligand charge distribution. The supplied models contain eight predictors for OH and O and six for OOH. We applied the saved training medians, means, standard deviations, and coefficients to all available catalyst and adsorption site records. We then joined the three predictions at each site and evaluated the overpotential with Eqs. (5)–(7).
P00054  Figure 3 shows predicted trends across the molecular library, including sites used for model fitting. The supplied validation predictions confirmed that the saved models were reproduced; the figure containing all predicted sites does not measure independent predictive accuracy.
P00055  2.6. AI assisted manuscript generation
P00056  We used an LLM accessed through OpenAI Codex to generate the complete manuscript and to assist with analysis and figure code. We designed this part of the study around a direct question: can an LLM write a coherent scientific article when a traceable research record sets the boundary of every claim? Related work has shown that LLM agents can move from annotated data to human verifiable papers [10.1056/aioa2400555]. Evidence of widespread LLM assisted writing makes those boundaries and their verification increasingly important [10.1126/sciadv.adt3813].
P00057  We supplied the research question, databases, regression coefficients, literature, and writing instructions. From this record, the LLM drafted analysis and figure code and successive versions of the article. Each revision began and ended with our scientific judgment. We chose which quantities belonged together and which interpretations deserved testing, then traced the resulting code, figures, citations, and prose back to their evidence. Whenever the language outran that evidence, we corrected it. The manuscript is therefore both the report of the study and the object of this test.
P00058  3. Results and discussion
P00059  3.1. Molecular design space and site identity
P00060  Figure 1 gives us a common molecular structure in which to compare the effects of changing individual components. Both metal positions draw from the same six elements, while the bridge and diamine provide further variation and the dialdehyde remains fixed. We define an adsorption site as the metal atom within the organic ligands to which an ORR intermediate binds. Keeping that atom identifiable lets us distinguish the two possible pathways in the same molecule.
P00061  [embedded figure/image]
P00062  Figure 1. Modular molecular structure of the catalyst library. The metal list gives the elements available at the two metal positions; bridge atoms are N, O, or S. A2, B1, and B2 follow the dialdehyde and diamine notation introduced in our data article [10.1016/j.dib.2026.112806]. The arrows identify the metal region, bridge, diamine, and lower aromatic ring assigned to A2.
P00063  The clean database contains 88 catalyst structures. Exact matching of the raw adsorption databases produced 123 complete pathways across 82 catalysts. Figure 2 contains 118 pathways across 79 catalysts, and Figure 3 contains 144 predicted sites across 87 catalysts.
P00064  3.2. Adsorption scaling and calculated ORR thermodynamics
P00065  Figure 2a compares O and OOH adsorption free energies with OH adsorption free energy. The OOH–OH relation has a slope of 0.69 and an intercept of 2.98 eV; the O–OH relation has a slope of 1.66 and an intercept of 1.20 eV. The adsorption site families occupy different parts of these trends, with scatter around the global relations. Related molecular catalysts can alter OOH binding geometry and adsorption scaling through their paired metal centers [10.1021/jacs.4c12705; 10.1002/adma.202403549]. The present trends provide a basis for examining such structural effects within a common molecular structure.
P00066  [embedded figure/image]
P00067  Figure 2. Adsorption scaling and oxygen reduction thermodynamics from DFT. Figure 1 defines the structural components. (a) O and OOH adsorption free energies versus OH adsorption free energy. Color and marker shape identify the metal at the adsorption site; the centered vertical stroke denotes O. Solid and dashed lines are OOH–OH and O–OH scaling fits. (b) CHE overpotential for the same catalyst and adsorption site combinations. The solid curve follows the global scaling fits through all four reaction steps. The dotted ideal reference assumes an OOH–OH separation of 2.46 eV, with OH removal and OOH formation defining its left and right branches. The star marks zero overpotential at 1.23 eV. Lower overpotential appears higher on the reversed axis.
P00068  Figure 2b shows the calculated conventional computational hydrogen electrode overpotential, with the vertical axis reversed. The lowest value in the plotted dataset is 0.34 V at the Mn adsorption site of a Cr–Mn catalyst with S bridge atoms and B1 diamine. Its adsorption free energies are 0.89 eV for OH, 1.99 eV for O, and 3.41 eV for OOH. The corresponding step potentials are 1.51, 1.42, 1.10, and 0.89 V, so reduction of OH to water determines the limiting potential. This Mn site approaches the balance required by the CHE volcano more closely than the other plotted sites. Establishing a causal role for the bridge or diamine requires comparisons across matched structures. The ranking applies to the present structures, corrections, matching rules, and plotted dataset.
P00069  3.3. Scaling and activity from regression predictions
P00070  We next used regression to carry the adsorption analysis across the molecular library. Figure 3 applies the same relations to predicted adsorption free energies for 144 sites across 87 catalysts. The predicted OOH–OH slope and intercept are 0.67 and 2.98 eV, while those for O–OH are 1.73 and 1.14 eV. Their proximity to the DFT relations in Figure 2 shows that the descriptors retain the broad adsorption trends represented in the available data.
P00071  The predicted volcano places its lowest overpotential, 0.30 V, at the Fe adsorption site of an Fe–Mn catalyst with S bridge atoms and B1 diamine. This site gives us a concrete candidate for further DFT calculations or experimental study. More generally, Figure 3 turns the stored descriptors into a map of where additional work may be most informative. The plotted predictions include records used to fit the models, so they describe the represented molecular library and do not establish transfer to new chemical families.
P00072  [embedded figure/image]
P00073  Figure 3. Adsorption scaling and oxygen reduction thermodynamics from ML predictions. (a) Predicted O and OOH adsorption free energies versus predicted OH adsorption free energy. (b) Overpotentials derived from the three predictions for 144 catalyst and adsorption site combinations. Colors, markers, and the ideal reference follow Figure 2. The solid and dashed lines in (a) are the OOH–OH and O–OH fits; the solid curve in (b) follows those fits through the four reaction steps. All trend lines extend across the displayed descriptor range. The figure includes sites used for model fitting.
P00074  3.4. From reusable data to the next research question
P00075  Reusable site matched data let us change the scientific question without rebuilding the dataset. The conventional CHE overpotential, the Calle-Vallejo electrochemical step symmetry index, and the Exner free energy span emphasize different features of the same reaction energetics [10.1016/j.coelec.2018.03.025; 10.1021/acscatal.2c03997]. Once each energy remains attached to its molecule and adsorption site, we can implement another activity measure directly or ask an LLM to draft the code and then inspect the result. Questions that change geometry, charge state, or adsorption structure still require new DFT calculations.
P00076  We will release the structures and results as an ASE database and machine readable JSON, together with code that reconstructs the analysis. These formats support findable, accessible, interoperable, and reusable data practices [10.1038/sdata.2016.18]. They also make our interpretation open to revision: another researcher can choose a different descriptor, regenerate the figures, and identify where the conclusions change. The value of the record grows when it can answer a question that we did not originally ask.
P00077  We developed the project instructions over about two weeks and estimate that an integrated draft can be generated from them in less than one hour. In our experience, writing comparable articles without LLM assistance has taken months. These times describe this project rather than a controlled comparison. Their practical meaning is simple: when analysis and explanation share the same record, we can revise both together and devote more attention to the assumptions and decisions that determine what the result means.
P00078  4. Conclusions
P00079  Using molecular dual-atom site catalysts as a case study, we show how AI can accelerate catalyst discovery[[DELETE id=6; author=Vladislav Ivanistsev; date=2026-10-12T05:55:48Z:  and design]] from electronic structure calculations through regression analysis and publication. Site resolved DFT records revealed OOH–OH and O–OH scaling and identified a Mn adsorption site with the lowest calculated ORR overpotential of 0.34 V in the present dataset. Regression preserved the broad scaling relations across 144 molecular and site combinations and converted stored catalyst descriptors into priorities for further study. Because every quantity remains connected to its molecul[[INSERT id=7; author=Vladislav Ivanistsev; date=2026-10-12T05:57:59Z: ar structure]][[DELETE id=7; author=Vladislav Ivanistsev; date=2026-10-12T05:57:59Z: e and adsorption site]], the same record can support another thermodynamic analysis without reconstructing the data.
P00080  The broader [[INSERT id=8; author=Vladislav Ivanistsev; date=2026-10-12T05:58:44Z: insight of this article]][[DELETE id=8; author=Vladislav Ivanistsev; date=2026-10-12T05:58:44Z: result]] concerns how research becomes a paper. [[INSERT id=9; author=Vladislav Ivanistsev; date=2026-10-12T05:59:06Z: It is a consensus ]][[INSERT id=9; author=Vladislav Ivanistsev; date=2026-10-12T05:59:06Z: that]][[INSERT id=9; author=Vladislav Ivanistsev; date=2026-10-12T05:59:06Z:  ]][[DELETE id=9; author=Vladislav Ivanistsev; date=2026-10-12T05:59:06Z: Editors are right that ]]readers need a coherent scientific story. [[INSERT id=11; author=Vladislav Ivanistsev; date=2026-10-12T05:59:02Z: Here, ]][[DELETE id=11; author=Vladislav Ivanistsev; date=2026-10-12T05:59:02Z: W]][[INSERT id=11; author=Vladislav Ivanistsev; date=2026-10-12T05:59:02Z: w]]e show that researchers do not need to spend the same share of their intellectual time drafting that story sentence by sentence. We directed an LLM to write the complete article from a traceable record and traced its account back to the evidence from which it arose. This is how AI accelerated the work: it carried the evidence across analysis and[[INSERT id=12; author=Vladislav Ivanistsev; date=2026-10-12T05:59:43Z:  scientific]] writing while we concentrated on the [[INSERT id=13; author=Vladislav Ivanistsev; date=2026-10-12T05:59:49Z: research itself]][[DELETE id=13; author=Vladislav Ivanistsev; date=2026-10-12T05:59:49Z: science]]. A reusable record gives the model something real to follow, and human responsibility determines what survives. Scientific storytelling remains essential, while its composition can become delegated work. Researchers can then give more attention to planning the study, producing reliable data, and testing interpretations. [[INSERT id=14; author=Vladislav Ivanistsev; date=2026-10-12T06:02:12Z: In such collaboration with the AI, ]][[DELETE id=14; author=Vladislav Ivanistsev; date=2026-10-12T06:02:12Z: R]][[INSERT id=14; author=Vladislav Ivanistsev; date=2026-10-12T06:02:12Z: r]]esearchers[[INSERT id=15; author=Vladislav Ivanistsev; date=2026-10-12T06:02:21Z:  remain responsible in deciding]][[DELETE id=15; author=Vladislav Ivanistsev; date=2026-10-12T06:02:21Z:  must decide]] which questions and conclusions matter.
P00081  CRediT authorship contribution statement
P00082  Bruno Inácio da Silva Roux Leite: investigation, data curation, formal analysis, and generation of DFT results. Denis Savchenko: methodology, software, formal analysis, visualization, and development of the regression model. Timmo-Henrik Pukk: investigation, data curation, formal analysis, and generation of DFT results. Ba Long Nguyen: investigation, software, data curation, formal analysis, visualization, and generation of DFT results. Vladislav Ivanistsev: conceptualization, supervision, [[DELETE id=16; author=Vladislav Ivanistsev; date=2026-10-12T06:03:06Z: and ]][[INSERT id=16; author=Vladislav Ivanistsev; date=2026-10-12T06:03:06Z: LLM prompting, LLM outputs ]][[INSERT id=16; author=Vladislav Ivanistsev; date=2026-10-12T06:03:06Z: verification]][[INSERT id=16; author=Vladislav Ivanistsev; date=2026-10-12T06:03:06Z: ]][[DELETE id=16; author=Vladislav Ivanistsev; date=2026-10-12T06:03:06Z: funding acquisition]]. Nadezda Kongi: conceptualization, supervision, and funding acquisition. Validation of the manuscript text: all authors. All authors approved the final text.
P00083  Declaration of competing interest
P00084  The authors declare no competing interests.
P00085  Data availability
P00086  The parent molecular dual-atom site catalyst dataset is available from Zenodo [10.5281/zenodo.18601379]. The final adsorption databases, processed site matched data, machine readable JSON records, analysis notebooks, and model predictions will be deposited with the final article. The databases used for the present working analysis are provisional.
P00087  Declaration of generative AI and AI assisted technologies in the manuscript preparation process
P00088  We used OpenAI Codex with an LLM to generate the complete manuscript text and to assist with analysis and figure code from our project records and instructions. We reviewed each output against the data, methods, and sources, revised it where needed, and take full responsibility for the published content.
P00089  Acknowledgments
P00090  This work was supported by the Estonian Ministry of Education and Research (TK210) and the Estonian Research Council (PRG3174). We acknowledge the University of Latvia Artificial Intelligence and Computing Center and the High Performance Computing Center of the University of Tartu for providing computational resources.
P00091  References
P00092  S. Jia et al., Machine Learning Reveals Role-Asymmetric Electronic Cooperation in Fe-Based Dual-Atom Catalysts, Advanced Materials 36 (2026) e74833. [10.1002/adma.74833]
P00093  Z. Zhang et al., Design and Synthesis of Electrocatalysts Based on Catalysis-Unit Engineering, Advanced Materials 36 (2024) 2403549. [10.1002/adma.202403549]
P00094  X. Chen et al., Leveraging DFT and Machine Learning for Accelerated Screening of Cluster-Modified Single-Atom Catalysts in Oxygen Reduction Reactions, ACS Catalysis 16 (2026) 14399–14410. [10.1021/acscatal.6c02383]
P00095  J. K. Nørskov, J. Rossmeisl, A. Logadottir, L. Lindqvist, J. R. Kitchin, T. Bligaard, H. Jónsson, Origin of the Overpotential for Oxygen Reduction at a Fuel-Cell Cathode, Journal of Physical Chemistry B 108 (2004) 17886–17892. [10.1021/jp047349j]
P00096  Q. Sun et al., Well-Defined Co₂ Dual-Atom Catalyst Breaks Scaling Relations of Oxygen Reduction Reaction, Journal of the American Chemical Society 146 (2024) 35295–35304. [10.1021/jacs.4c12705]
P00097  N. Žoglo et al., Intersite Geometry Controls Activity and Selectivity in the Oxygen Reduction Reaction on Dual-Atom-Site Catalysts, ChemRxiv preprint (2026). [10.26434/chemrxiv.15001712/v1]
P00098  L. X. Chen, P. Christopher, F. De Angelis, S. Jin, Y.-S. Hu, N.-G. Park, D. Das Sarma, Y.-K. Sun, P. V. Kamat, We Editors Are Authors, Too, ACS Energy Letters 4 (2019) 249–250. [10.1021/acsenergylett.8b02322]
P00099  Elements of style, Nature Physics 3 (2007) 581. [10.1038/nphys724]
P00100  C. M. Biegel, P. V. Kamat, Five common pitfalls to avoid while composing scientific figures, ACS Energy Letters 6 (2021) 4309–4310. [10.1021/acsenergylett.1c02401]
P00101  Storytelling in research, Nature Biomedical Engineering 2 (2018) 53. [10.1038/s41551-018-0202-5]
P00102  Should scientists tell stories?, Nature Methods 10 (2013) 1037. [10.1038/nmeth.2726]
P00103  B. L. Nguyen, T. K. Madsen, V. Ivanistsev, N. Kongi, Dataset of molecular dual-atom site complexes for catalysis, Data in Brief 66 (2026) 112806. [10.1016/j.dib.2026.112806]
P00104  J. J. Mortensen et al., GPAW: An open Python package for electronic structure calculations, Journal of Chemical Physics 160 (2024) 092503. [10.1063/5.0182685]
P00105  A. H. Larsen et al., The Atomic Simulation Environment—A Python Library for Working with Atoms, Journal of Physics: Condensed Matter 29 (2017) 273002. [10.1088/1361-648X/aa680e]
P00106  E. Caldeweyher, S. Ehlert, A. Hansen, H. Neugebauer, S. Spicher, C. Bannwarth, S. Grimme, A generally applicable atomic-charge dependent London dispersion correction, Journal of Chemical Physics 150 (2019) 154122. [10.1063/1.5090222]
P00107  N. Govindarajan, J. M. García-Lastra, E. J. Meijer, F. Calle-Vallejo, Does the breaking of adsorption energy scaling relations guarantee enhanced electrocatalysis?, Current Opinion in Electrochemistry 8 (2018) 110–117. [10.1016/j.coelec.2018.03.025]
P00108  S. Razzaq, K. S. Exner, Materials screening by the descriptor Gmax(η): The free energy span model in electrocatalysis, ACS Catalysis 13 (2023) 1740–1758. [10.1021/acscatal.2c03997]
P00109  M. D. Wilkinson et al., The FAIR guiding principles for scientific data management and stewardship, Scientific Data 3 (2016) 160018. [10.1038/sdata.2016.18]
P00110  [dataset] B. L. Nguyen, T. K. Madsen, V. Ivanistsev, N. Kongi, Dataset of molecular dual-atom site complexes for catalysis, Zenodo, version 1.0, 2026. [10.5281/zenodo.18601379]
P00111  D. Kobak, R. González-Márquez, E.-Á. Horvát, J. Lause, Delving into LLM-assisted writing in biomedical publications through excess vocabulary, Science Advances 11 (2025) eadt3813. [10.1126/sciadv.adt3813]
P00112  T. Ifargan, L. Hafner, M. Kern, O. Alcalay, R. Kishony, Autonomous LLM-Driven Research: from Data to Human-Verifiable Research Papers, NEJM AI 2 (2025). [10.1056/aioa2400555]

[word/footer1.xml]

P00113
<!-- END FULL DOCX TEXT -->
~~~~~

## Tracked-change authors

- Vladislav Ivanistsev: 32 tracked insertions/deletions

## Word comments

### DOCX-v37-C1

- Author: Vladislav Ivanistsev
- Timestamp: 2026-10-12T05:57:31Z
- Anchored paragraph(s):

~~~~~text
Using molecular dual-atom site catalysts as a case study, we show how AI can accelerate catalyst discovery[[DELETE id=6; author=Vladislav Ivanistsev; date=2026-10-12T05:55:48Z:  and design]] from electronic structure calculations through regression analysis and publication. Site resolved DFT records revealed OOH–OH and O–OH scaling and identified a Mn adsorption site with the lowest calculated ORR overpotential of 0.34 V in the present dataset. Regression preserved the broad scaling relations across 144 molecular and site combinations and converted stored catalyst descriptors into priorities for further study. Because every quantity remains connected to its molecul[[INSERT id=7; author=Vladislav Ivanistsev; date=2026-10-12T05:57:59Z: ar structure]][[DELETE id=7; author=Vladislav Ivanistsev; date=2026-10-12T05:57:59Z: e and adsorption site]], the same record can support another thermodynamic analysis without reconstructing the data.
~~~~~

- Comment text:

~~~~~text
Instead of "records" (strange work) use  calculations. For ML use predictions.
~~~~~

### DOCX-v37-C3

- Author: Vladislav Ivanistsev
- Timestamp: 2026-10-12T06:01:38Z
- Anchored paragraph(s):

~~~~~text
The broader [[INSERT id=8; author=Vladislav Ivanistsev; date=2026-10-12T05:58:44Z: insight of this article]][[DELETE id=8; author=Vladislav Ivanistsev; date=2026-10-12T05:58:44Z: result]] concerns how research becomes a paper. [[INSERT id=9; author=Vladislav Ivanistsev; date=2026-10-12T05:59:06Z: It is a consensus ]][[INSERT id=9; author=Vladislav Ivanistsev; date=2026-10-12T05:59:06Z: that]][[INSERT id=9; author=Vladislav Ivanistsev; date=2026-10-12T05:59:06Z:  ]][[DELETE id=9; author=Vladislav Ivanistsev; date=2026-10-12T05:59:06Z: Editors are right that ]]readers need a coherent scientific story. [[INSERT id=11; author=Vladislav Ivanistsev; date=2026-10-12T05:59:02Z: Here, ]][[DELETE id=11; author=Vladislav Ivanistsev; date=2026-10-12T05:59:02Z: W]][[INSERT id=11; author=Vladislav Ivanistsev; date=2026-10-12T05:59:02Z: w]]e show that researchers do not need to spend the same share of their intellectual time drafting that story sentence by sentence. We directed an LLM to write the complete article from a traceable record and traced its account back to the evidence from which it arose. This is how AI accelerated the work: it carried the evidence across analysis and[[INSERT id=12; author=Vladislav Ivanistsev; date=2026-10-12T05:59:43Z:  scientific]] writing while we concentrated on the [[INSERT id=13; author=Vladislav Ivanistsev; date=2026-10-12T05:59:49Z: research itself]][[DELETE id=13; author=Vladislav Ivanistsev; date=2026-10-12T05:59:49Z: science]]. A reusable record gives the model something real to follow, and human responsibility determines what survives. Scientific storytelling remains essential, while its composition can become delegated work. Researchers can then give more attention to planning the study, producing reliable data, and testing interpretations. [[INSERT id=14; author=Vladislav Ivanistsev; date=2026-10-12T06:02:12Z: In such collaboration with the AI, ]][[DELETE id=14; author=Vladislav Ivanistsev; date=2026-10-12T06:02:12Z: R]][[INSERT id=14; author=Vladislav Ivanistsev; date=2026-10-12T06:02:12Z: r]]esearchers[[INSERT id=15; author=Vladislav Ivanistsev; date=2026-10-12T06:02:21Z:  remain responsible in deciding]][[DELETE id=15; author=Vladislav Ivanistsev; date=2026-10-12T06:02:21Z:  must decide]] which questions and conclusions matter.
~~~~~

- Comment text:

~~~~~text
It sounds like "record" is used in many senses. Please use calculations for DFT, predictions for ML, and records for something else ... which you might define so clearly and use in such obvious context that the readers will naturally understands what it means. Extend your list of allowed terms with the regireous definitions. Keep using them coherently.
~~~~~

### DOCX-v37-C0

- Author: Vladislav Ivanistsev
- Timestamp: 2026-10-12T05:56:30Z
- Anchored paragraph(s):

~~~~~text
Accelerating Catalyst Discovery[[DELETE id=0; author=Vladislav Ivanistsev; date=2026-10-12T05:55:55Z:  and Design]] with Artificial Intelligence: Molecular Dual-Atom Site Catalysts as a Case Study
~~~~~

- Comment text:

~~~~~text
It is difficult to read "discovery and design". Please simplify to just "Discovery" throughout the text
~~~~~

### DOCX-v37-C2

- Author: Vladislav Ivanistsev
- Timestamp: 2026-10-12T05:58:29Z
- Anchored paragraph(s):

~~~~~text
Using molecular dual-atom site catalysts as a case study, we show how AI can accelerate catalyst discovery[[DELETE id=6; author=Vladislav Ivanistsev; date=2026-10-12T05:55:48Z:  and design]] from electronic structure calculations through regression analysis and publication. Site resolved DFT records revealed OOH–OH and O–OH scaling and identified a Mn adsorption site with the lowest calculated ORR overpotential of 0.34 V in the present dataset. Regression preserved the broad scaling relations across 144 molecular and site combinations and converted stored catalyst descriptors into priorities for further study. Because every quantity remains connected to its molecul[[INSERT id=7; author=Vladislav Ivanistsev; date=2026-10-12T05:57:59Z: ar structure]][[DELETE id=7; author=Vladislav Ivanistsev; date=2026-10-12T05:57:59Z: e and adsorption site]], the same record can support another thermodynamic analysis without reconstructing the data.
~~~~~

- Comment text:

~~~~~text
Instead of decomposing molecule into sites, just say molecular structure
~~~~~
