# Inputs

The manifest lists the supplied generation inputs. Four notebooks are at the root. The TOC generator is tools/create_graphical_abstract_v32.py and its publication-page image is source_data/reference_EActa_open_article_2020_page1.png. Instructions, article facts, literature summaries and journal guidance occupy their named subfolders.

This clean-start package contains no downloaded databases or CSV tables. Figure 2, Figure 3 and the TOC use exact GitHub v1 DASC_...db names; SQLite signature and SHA-256 are checked before reuse, with validated download on a cache miss. Figure 4 downloads its declared GitHub CSV/JSON inputs. Local downloads go in source_data/; Colab databases retain /content/ behavior. All generated outputs go under inputs/. The root reference DOCX is excluded from generation and retained for later human comparison.
