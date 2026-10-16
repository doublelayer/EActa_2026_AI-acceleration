# Reusable Word manuscript generation

## Inputs and generation modes

Read the article's text, fixed metadata, approved figures, equation definitions, document profile, citation convention, and output filename from the declared input packet. For fresh generation, create a new document and standalone generator. For revision, use only the designated predecessor and preserve human edits according to the revision contract. Never use a predecessor to supply hidden prose during a fresh-generation test.

Internal review checkpoints do not consume public manuscript version numbers. Preserve prior releases unless the user explicitly requests replacement. A test run leaves the current manuscript shortcut unchanged until its result is accepted.

## Builder role contract

Receive the Author's approved current text checkpoint, fixed metadata, numerical and evidence maps, equation definitions, registered figure files, selected document profile, author-edit protections, and requested release filename. Confirm that these inputs belong to the same manuscript checkpoint. Obtain exact figure versions from the approved manifest rather than selecting an image by modification time or version suffix alone.

The Builder constructs the document from those inputs. Return a missing fact, disputed wording, or figure mismatch to the responsible role. Preserve approved prose, quantities, terminology, citation ownership, and article structure during conversion. Keep technical repairs and editorial decisions identifiable in the external issue log.

Before changing a formatting property, identify the selected style rule or explicit author exception that permits it. Apply the existing style defaults and authorized semantic properties. A technical cleanup removes a conflicting override while retaining the text and meaning. Decorative elements, size changes, and extra documents require authorization in the output contract.

Create a generator whose manuscript construction is self-contained and whose declared dependencies are data, text, artwork, document assets, and installed packages. During fresh generation, preserve the Author's text as an explicit run artifact and build from it; exclude predecessor documents and historical build scripts. For an ordinary revision, use the designated predecessor and declared protection utilities. Register any utility required at runtime rather than loading an undeclared historical dependency.

Build into an internal checkpoint, validate it, and publish under the requested filename and version. Preserve the prior artifact according to the version policy when replacement is explicitly requested. If an open file prevents replacement, retain the generated candidate and report the exact save dependency; keep the requested public version number.

## Construction

Define page layout and paragraph styles from the selected profile. Apply formatting by those styles and semantic text properties; use direct formatting only for explicit profile exceptions. Avoid decorative elements unless required. Superscripts and subscripts inherit surrounding font size unless the profile explicitly specifies otherwise.

Use editable native Word math only for displayed equations. Mathematical expressions within prose must be ordinary Word text runs with semantic subscript and superscript where needed; never insert an inline Microsoft Equation object. Distinguish physical quantities, chemical species, units, operators, functions, and descriptive indices at the symbol level, using the selected typography convention. Keep a numbered displayed equation and its number in the same paragraph and line; implement the requested centering and right alignment without a number-only paragraph.

Create real external hyperlink relationships for DOI and email links and apply the built-in Hyperlink character style. Validate targets as well as visible text. Apply the article's explicit citation and cross-reference conventions. Preserve identifiers, URLs, years, and DOI strings when applying numerical formatting.

Place images at the specified physical width while preserving aspect ratio. Keep supplied artwork unchanged. Bind every image to the appropriate caption and check figure numbering throughout grouped references. Keep captions inside the article when that is the requested output.

Handle author names, affiliation markers, correspondence, and protected text as separate semantic elements according to the article profile. Keep punctuation outside protected names when requested. Protection controls are editing signals, not visible fields or factual evidence.

Treat imported empty or whitespace-padded content controls as editing artifacts. Remove their wrappers and redundant spaces, but preserve meaningful text, equations, hyperlinks, and artwork in their original order. Retain only controls expressly required by the active author-edit contract. Audit displayed text before and after cleanup and preserve useful fields such as automatic page numbers.

## Revisions and audit

Compare the document's accepted reading with the Author's text checkpoint after construction. Check numerical strings and units, chemical identities, abbreviations, citation associations, heading sequence, and caption placement. Check equation content as well as numbering and native editability. Figure hashes and relationships must identify the approved artwork at its specified dimensions. Author-name punctuation and protected text follow the supplied profile.

Track substantive changes when the task requests tracked revision. For fresh generation or an expressly requested clean release, do not invent a predecessor or revision history. Preserve required author-decision protections in the new output. Remove resolved comment anchors from a clean release and retain the resolution log outside it.

Validate ZIP/XML integrity, permitted styles and exceptions, equation placement, image relationships and dimensions, hyperlinks, page numbers, and citation/reference correspondence. When a renderer is available, inspect the result at reading size. State structural-only validation accurately if rendering is unavailable.

Reproduce the final document from its declared inputs and generator. Preserve the final text checkpoint, source metadata, and output hashes so a later review can identify the exact artifact checked. Run only relevant checks and keep editorial logs outside the manuscript.

Hand the Release auditor the DOCX, matching generator, source checkpoint, input/output identities, permitted formatting exceptions, and actual verification results. Distinguish a generated document from a successfully rerun generator and a structurally checked file from an inspected rendering. Route prose corrections through the Author, rebuild the affected artifact, and verify the repair. Update current-version navigation only under the task's declared release policy.


## Selected run policy

PROMPT.txt supplies current facts and the execution contract. GitHub input downloads and relevant web research are authorized. Preserve supplied notebooks and use working copies for execution. The root `Electrochimica_Acta_research_article_refernce.docx` is reserved for comparison after generation and excluded from drafting inputs. Any historical offline examples in a reusable profile yield to this selected run policy.
