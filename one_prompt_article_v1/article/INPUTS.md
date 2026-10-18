# Inputs

The manifest lists the supplied generation inputs. Four notebooks and the sole TOC generator, `Figure_0_graphical_abstract_v33.py`, are at the package root. Its publication-page image is `source_data/reference_EActa_open_article_2020_page1.png`. Instructions, article facts, literature summaries and journal guidance occupy their named subfolders.

The five DASC_...db files are supplied in the workspace root, one directory above this package. Figure 2, Figure 3, Figure 4 and the graphical-abstract script read those existing databases through relative parent paths; they do not download, validate, checksum or copy them. Figure 4 and the graphical-abstract script both read the current prediction table directly from `../figure4/predictions.csv`; they do not download or copy it. All generated outputs go under inputs/. The root reference DOCX is excluded from generation and retained for later human comparison.
