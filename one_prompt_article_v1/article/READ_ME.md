# Package layout

The root contains PROMPT.txt, AGENTS.md, four figure-generation notebooks and Electrochimica_Acta_research_article_refernce.docx. The reference is reserved for human comparison after generation and excluded from drafting inputs.

instructions/ contains role and writing guidance. article/ contains facts, bibliography, sentence plan and the manifest. journal/, literature/ and environment/ contain their declared supporting inputs. tools/ contains package checks and the TOC generator. source_data/ contains the supplied publication-page image. The notebooks and TOC generator read databases from the parent project root and Figure 4 CSV/JSON files from `../figure4/`; none of these inputs are downloaded. inputs/ starts empty and receives every generated file.

Run `python tools/verify_package.py` to verify the supplied package. Run `python tools/prepare_manifest.py` only after intentional source-input changes. Execute the four root notebooks and then `python tools/create_graphical_abstract_v32.py` from this directory, as directed in PROMPT.txt. An independent article-generation test has not yet run.
