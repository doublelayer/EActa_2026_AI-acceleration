# Inputs

The manifest lists the supplied generation inputs. Four notebooks are at the root. The TOC generator is tools/create_graphical_abstract_v32.py and its publication-page image is source_data/reference_EActa_open_article_2020_page1.png. Instructions, article facts, literature summaries and journal guidance occupy their named subfolders.

This clean-start package contains no downloaded databases or CSV tables. Figure 2, Figure 3 and the TOC resolve the latest GitHub main commit (or inherit EACTA_DATA_COMMIT from the run), refresh the exact DASC_...db files, validate SQLite integrity and the ASE systems table, and record observed SHA-256 hashes. All scientific inputs for one article run use the same resolved commit. Figure 4 downloads its declared GitHub CSV/JSON inputs. Local downloads go in source_data/; Colab databases retain /content/ behavior. All generated outputs go under inputs/. The root reference DOCX is excluded from generation and retained for later human comparison.
