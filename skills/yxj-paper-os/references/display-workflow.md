# Claim-Bearing Displays

Read this when designing or revising a nontrivial figure or table.

Treat each display as a claim-bearing reader surface, not decoration. Build a temporary
display contract containing its identifier and manuscript locator; one reader question
and one-sentence takeaway; authoritative evidence locators and the allowed claim; a
panel or component map with one distinct job per part; exact versus schematic elements
and their visual encodings; the canonical editable source or generator and its derived
outputs; intended final width and legibility floor; and affected labels, subreferences,
caption, body text, tables, translations, and exports. Keep it only through verification
unless an active constraint or unfinished item qualifies for the canonical brief.

Resolve the active figure bundle from repository authority; a similar filename is not
enough. When an editable TikZ, Python, R, or other generator exists, edit and regenerate
that source rather than patching a derived PDF, PNG, or SVG. Use the smallest matching
repository-native backend. An AI-generated or raster draft may guide composition, but
it is neither project evidence nor final claim-bearing scientific artwork unless the
author explicitly authorizes that use and it passes the same evidence checks.

Render standalone panels and any production parent or composite at the intended
manuscript size. Apply two independent gates:

- **Scientific gate:** trace every quantitative or logical element to current data,
  equations, proofs, or scripts; check units, statistics, legends, exact-versus-schematic
  status, and adverse, null, or limiting evidence.
- **Visual gate:** inspect actual renders for overlap, crop, geometry, text and line
  legibility, panel and caption mapping, legend coverage, and redundant color-plus-style
  encoding where color alone would be fragile.

Neither gate substitutes for the other. After both pass, integrate the display by
updating affected labels, subreferences, caption, body text, float layout, translations,
and related tables; then rebuild the current-source manuscript and inspect the affected
page plus neighboring pages. Compile success, a caption-only edit, or a new candidate PDF
is not display acceptance. Do not fix pagination by blindly shrinking the display;
repair the content, composition, or layout at readable final size. Prefer deletion,
combination, or simplification when a display or panel has no distinct reader job.
