---
name: refine-mermaid-svg
description: Convert Mermaid diagrams into polished, presentation-ready SVG infographics that remain easy to edit in Inkscape. Use when an agent must render or redesign a Mermaid flowchart, architecture diagram, sequence, or process map; fix overflowing or awkward SVG text; add coherent visual styling and icons; organize SVG objects into meaningful named layers and groups; or validate an SVG for text bounds, structure, portability, and clean raster export.
---

# Refine Mermaid SVG

Turn Mermaid into a semantic reference, then reconstruct it as deliberately authored SVG. Preserve the diagram's meaning while improving hierarchy, spacing, typography, iconography, routing, and editability.

## Required workflow

1. Locate the Mermaid source and understand the intended audience, canvas, and emphasis. If the user only provides Mermaid in chat, save it beside the intended output as `<name>.mmd`.
2. Read [references/svg-authoring-contract.md](references/svg-authoring-contract.md) completely before authoring. Read [references/visual-design-system.md](references/visual-design-system.md) when choosing or revising the visual treatment.
3. Run the reference render:

   ```bash
   python3 <skill-dir>/scripts/render_mermaid.py input.mmd reference.svg
   ```

4. Inspect the reference render. Use it to recover nodes, labels, edges, direction, and grouping—not as the final editable object tree.
5. Copy [assets/inkscape-diagram-template.svg](assets/inkscape-diagram-template.svg) to the final destination and replace its examples with the real diagram. Keep the template's namespaces, metadata pattern, standard filters, and layer conventions.
6. Build the final SVG in semantic passes: background; header; stage panels; cards; connectors; annotations; legend. Use meaningful stable IDs and `inkscape:label` values throughout.
7. Lay out text as pure SVG `<text>` and `<tspan>` elements. Wrap intentionally, never rely on browser-only automatic wrapping, and bind every contained text object to its visible container using `data-container` and `data-padding`.
8. Render and inspect after each material layout pass:

   ```bash
   python3 <skill-dir>/scripts/render_svg.py final.svg final.png --width 1920
   ```

9. Run the complete structural and geometric validation:

   ```bash
   python3 <skill-dir>/scripts/validate_svg.py final.svg --require-inkscape --require-text-bounds
   ```

10. Inspect the final raster at full size. Fix collisions, cramped labels, ambiguous arrows, low contrast, and unbalanced whitespace. Repeat render and validation until clean.
11. Deliver the `.mmd`, final `.svg`, and optionally the preview `.png`. State what was validated and which renderer was used.

## Text layout rules

- Treat text wrapping as layout, not decoration. Decide line breaks before finalizing box height.
- Use separate `<text>` objects for title, body, metadata, and badges when they need independent alignment.
- Put each line in a `<tspan x="…" dy="…">`; avoid `foreignObject`, HTML, and CSS-only wrapping.
- Add `data-container="surface-id"` and `data-padding="N"` to every text object that must remain inside a box. The referenced surface must have a stable ID.
- Add `data-role="free-text"` only to genuinely uncontained labels such as the main title or a stage heading.
- Prefer expanding a card or shortening copy over shrinking body text below a legible size.
- Re-run geometric validation after every copy, font, padding, or box-size change.

## Editable SVG rules

- Make each major stratum a top-level Inkscape layer with both `id` and `inkscape:label`.
- Group each reusable visual object—card, icon, badge, connector, callout—with a descriptive ID and label.
- Separate connectors from cards so routes can be selected and revised without ungrouping content.
- Keep shapes, icons, and text as SVG primitives. Do not flatten them into paths or embedded raster images.
- Put reusable markers, gradients, filters, clip paths, and symbols in `<defs>` with descriptive IDs.
- Use standard SVG filter primitives. Avoid renderer-specific filter shortcuts when a portable primitive chain is available.
- Use explicit coordinates and a `viewBox`; do not depend on runtime JavaScript.

## Visual refinement rules

- Establish one visual thesis: restrained technical, editorial, playful, or another coherent direction.
- Use a small semantic palette with explicit roles for primary flow, trust/security, warnings, neutral structure, and background.
- Make the reading order apparent from position first and arrows second.
- Use a consistent card grammar: radius, stroke, fill, internal grid, icon slot, title baseline, and body rhythm.
- Use simple custom vector icons with a shared stroke width and optical size. Avoid unrelated emoji or mixed icon families.
- Prefer orthogonal or gently curved routes with clear ports. Keep labels off paths and arrowheads away from card borders.
- Use glow, gradients, texture, and shadows sparingly to reinforce grouping or focus.

## Bundled examples

Inspect the example pair when a task benefits from a concrete before-and-after reference:

- [assets/examples/mermaid-to-polished-svg.mmd](assets/examples/mermaid-to-polished-svg.mmd) is the semantic source.
- [assets/examples/mermaid-to-polished-svg.reference.svg](assets/examples/mermaid-to-polished-svg.reference.svg) is the automatic Mermaid render. It intentionally demonstrates why the generated DOM is only an intermediate reference.
- [assets/examples/mermaid-to-polished-svg.svg](assets/examples/mermaid-to-polished-svg.svg) is the handcrafted, layered, text-bound-validated Inkscape result.

Do not copy the example's composition mechanically. Reuse its object conventions and validation annotations while adapting the layout and visual thesis to the user's diagram.

## Tool behavior and fallback

- Prefer an installed `mmdc`; otherwise `render_mermaid.py` uses a pinned Mermaid CLI through `npx`, which can require network access on first use.
- Require Inkscape for trustworthy text-bound checks because SVG text metrics depend on the actual renderer and installed fonts.
- If Inkscape is unavailable, still run structural validation, explain that geometric text containment was not verified, and do not claim the SVG is text-safe.
- Use `xmllint` when available as an additional XML check; the validator also parses XML with Python.
- Preserve the user's unrelated working-tree changes. Only update source and outputs in the requested scope.

## Completion criteria

Do not call the result finished until all of these are true:

- The final diagram communicates the same intended flow as the Mermaid source.
- Text is legible, intentionally wrapped, padded, and geometrically contained.
- Connectors do not cross text and have unambiguous direction.
- Inkscape exposes meaningful layers and selectable component groups.
- IDs are unique and descriptive; no placeholder labels remain.
- The SVG contains no `foreignObject`, embedded raster fallback, or unsupported filter shortcut.
- XML parsing, structural validation, text-bound validation, and final raster export succeed.
