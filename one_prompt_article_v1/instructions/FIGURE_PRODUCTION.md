# Reusable scientific figure production

## Inputs

Obtain the figure's scientific purpose, data sources, selection rules, dimensions, typography, marker meanings, color mapping, labels, and export requirements from the article packet. This guide supplies production and verification procedures, not a specific article design.

Distinguish immutable supplied artwork from figures to regenerate. Copy supplied artwork without altering its pixels, proportions, labels, or typography when preservation is required. A source slide or an earlier reconstruction does not override a designated immutable asset.

## Artist role contract

Receive the approved figure brief, exact artwork or generation source, verified result table, scientific input provenance, selected visual profile, and requested output versions. Identify the scientific message and the quantity or process each panel represents before changing its appearance. Work only on the figures requested by the task.

Preserve the approved design and scientific selection during reproduction. Changes to data filtering, intermediate selection, corrections, fitting, or model output require the responsible scientific role and task authorization. A clearer visual result must come from presentation of the supplied evidence, with every plotted point attached to its scientific identity. Record exclusions and displayed populations under their actual definitions.

Use the established category order, colors, marker meanings, line styles, axis direction, tick formatting, and label text from the brief. Carry matching meanings across related figures. The brief authorizes its stated design changes; obtain explicit direction for a materially different design rather than silently adding encodings or changing labels. Preserve additional scientific and interactive analyses in the supplied notebook.

Check physical dimensions and typography in the exported artifact as well as in the code. Inspect transformations that can scale text or alter proportions, and separate path-only transforms from text when the design requires it. Check lines, markers, opacity, and labels at publication size; inspect graphical abstracts at their declared display size. Apply the chosen cropping, background, and panel-label rules explicitly.

Return caption content that describes the actual panels and visual key to the Author for integration. Check the integrated caption against the exported image, including colors, symbols, fitted and reference curves, special points, quantities, and data provenance. Keep plotting instructions and execution notes outside the caption.

Use the Programmer for source or dependency repairs and the Scientific auditor for data or numerical discrepancies. Hand the Builder the exact approved figure files and embedding dimensions; hand the Release auditor the matching sources, data identities, export checks, and actual visual inspection results. Record the scope of regeneration and preserve historical releases under the requested version policy.

## Production

Keep the current source independently executable. Inputs may be databases, result tables, author-supplied artwork, and ordinary installed software; an earlier plotting script or notebook is not an input. When consolidating a historical chain, compare the new render with the approved image at publication size and keep the approved release untouched until the replacement passes.

Set physical width and height and the chosen font size before plotting. Set axis-label, tick-label, annotation, and panel-label sizes explicitly so inherited settings cannot change them. Position panels by their plotting areas; use the aspect ratio requested by the figure brief. Inspect readability at the final physical size.

Keep data and display transformations explicit. A reversed axis changes presentation, not the stored sign of a quantity. Read units and category order from the article packet. Use consistent semantic mappings across related figures. Draw reference and fitted lines behind observations. Sample each line over its declared display range and explain extrapolation where scientifically relevant.

Choose marker size and opacity to reveal overlap while retaining isolated observations. A marker must remain recognizable at export size. Keep overlays clipped to the marker if required. Avoid extra visual encoding without a scientific purpose. Use caption explanations for any omitted legend.

Place panel labels outside the axes when the profile requires croppable labels. Reserve margins for labels and axis titles. Check collisions and clipping before export. Keep the background and borders consistent across related panels.

Interactive views must preserve observation identity and expose the quantities underlying each point. Generate static and interactive views from the same verified result table. Preserve additional analyses in an existing notebook when adding a final publication figure.

## Outputs and checks

Export formats, DPI, background, and font embedding follow the article packet and journal profile. Set PNG facecolor and transparency explicitly. Check both nominal physical size and actual output dimensions; a tight bounding-box export can change the intended size. Version generated outputs without overwriting an earlier release.

Link each caption to the actual figure content. Explain panels, quantities, units, symbols, colors, fitted/reference curves, and special points as relevant. Keep file format and plotting instructions outside the manuscript caption.

The release check covers source-table identity, plotted counts, physical dimensions, typography, ranges, units, visual mappings, clipping, background, and correct embedding. Do not claim visual inspection unless an image or render was actually inspected. Preserve the figure source and scientific input provenance.


## Selected run policy

PROMPT.txt supplies current facts and the execution contract. Local scientific inputs are used without GitHub downloads; relevant web research remains authorized. Preserve supplied notebooks and use working copies for execution. The root `Electrochimica_Acta_research_article_refernce.docx` is reserved for comparison after generation and excluded from drafting inputs. Any historical offline examples in a reusable profile yield to this selected run policy.
