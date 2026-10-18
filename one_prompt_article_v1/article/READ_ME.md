# Package layout

The root contains PROMPT.txt, AGENTS.md, four figure-generation notebooks, `Figure_0_graphical_abstract_v33.py`, and Electrochimica_Acta_research_article_refernce.docx. The reference is reserved for human comparison after generation and excluded from drafting inputs.

instructions/ contains role and writing guidance. article/ contains facts, bibliography, sentence plan and the manifest. journal/, literature/ and environment/ contain their declared supporting inputs. tools/ contains package checks. `Figure_0_graphical_abstract_v33.py` is the sole TOC generator at the package root. source_data/ contains the supplied publication-page image. The five databases and `figure4/predictions.csv` are supplied in the workspace root and its `figure4/` subfolder; scripts read them directly using relative paths. inputs/ starts empty and receives every generated file.

Run `python tools/verify_package.py` to verify the supplied package. Run `python tools/prepare_manifest.py` only after intentional source-input changes. Execute the four root notebooks and then `python Figure_0_graphical_abstract_v33.py` from this directory, as directed in PROMPT.txt. An independent article-generation test has not yet run.
