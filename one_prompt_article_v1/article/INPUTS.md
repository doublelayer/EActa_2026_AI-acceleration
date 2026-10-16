# Inputs

The manifest lists the supplied generation inputs, including the scientific data outside this package folder. Four notebooks are at the root. The TOC generator is tools/create_graphical_abstract_v32.py and its publication-page image is source_data/reference_EActa_open_article_2020_page1.png. Instructions, article facts, literature summaries and journal guidance occupy their named subfolders.

The five ASE databases are read directly from the parent project root. Figure 4 reads `predictions.csv`, `structure_model_roles.csv`, `model_structure_descriptors.csv`, and `split_config.json` from `../figure4/`. The input manifest records their relative paths, sizes, and SHA-256 hashes; database loaders check the SQLite signature and the TOC loader checks its expected local hashes. No scientific input is downloaded or copied into `source_data/`. All generated outputs go under inputs/. The root reference DOCX is excluded from generation and retained for later human comparison.
