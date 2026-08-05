# SVG authoring contract

Use this contract for SVGs that must be attractive, portable, text-safe, and pleasant to edit in Inkscape.

## Document structure

Include the SVG, XLink only if needed, Inkscape, and Sodipodi namespaces. Give the root a `viewBox`, width, height, descriptive `aria-labelledby`, and a `<title>` plus `<desc>`. Add a Sodipodi named view for Inkscape document settings.

Order the root children as:

1. metadata (`title`, `desc`, optional metadata)
2. `<sodipodi:namedview>`
3. `<defs>`
4. top-level Inkscape layers

Use top-level layers shaped like:

```xml
<g id="layer-cards"
   inkscape:groupmode="layer"
   inkscape:label="04 Cards">
  <!-- semantic component groups -->
</g>
```

Number layer labels to preserve a predictable stacking order. A useful default is Background, Header, Stage Panels, Cards, Connectors, Annotations, and Legend. Split or combine layers to match the actual diagram.

## Components and IDs

Give every editable component a semantic wrapper:

```xml
<g id="card-authentication" inkscape:label="Card — Authentication">
  <rect id="card-authentication-surface" .../>
  <g id="icon-authentication" inkscape:label="Icon — Authentication">...</g>
  <text id="card-authentication-title"
        data-container="card-authentication-surface"
        data-padding="20">...</text>
</g>
```

Use lowercase kebab-case IDs. Prefer role and meaning over drawing-order names: `connector-proxy-to-server`, not `path37`; `badge-trust-boundary`, not `group12`.

Label groups that a human might select in Inkscape. Primitive children only need labels when their purpose is not obvious from the parent and ID.

## Text containment

SVG 1.1 has no dependable automatic paragraph layout. Author explicit lines using `<tspan>`:

```xml
<text id="card-authentication-body"
      x="184" y="280"
      data-container="card-authentication-surface"
      data-padding="20">
  <tspan x="184" dy="0">Inject the named authorization</tspan>
  <tspan x="184" dy="20">header only at request time</tspan>
</text>
```

The validator evaluates the rendered bounding box of the entire `<text>` element against the referenced container, inset by `data-padding`. Use numeric user units for padding. If an asymmetric inset is necessary, use `data-padding-x` and `data-padding-y`; these override the corresponding axis of `data-padding`.

Mark uncontained text explicitly:

```xml
<text id="diagram-title" data-role="free-text">...</text>
```

Every `<text>` element must use exactly one of these models. Do not place `data-container` on a group that also contains an icon because the icon would distort the measured bounds.

Text can be visually clipped as a last line of defense, but clipping is not a substitute for correct layout. If a clip path is used, keep the geometric text-bound validation passing without relying on the clip.

## Connectors

Place connectors in their own layer. Wrap each logical connector so the visible path, optional halo, arrowhead, and label stay selectable together.

Define arrow markers in `<defs>` and use `marker-end`. Keep routes outside card interiors except at intentional ports. Put connector labels in a small backed label group so lines do not reduce legibility.

## Filters and portability

Build shadows from portable primitives such as `feGaussianBlur`, `feOffset`, `feFlood`, `feComposite`, and `feMerge`. Avoid `feDropShadow` if the target Inkscape version warns about it.

Do not use `foreignObject`, embedded HTML, base64 raster images, or runtime scripts. Keep icons as paths, lines, circles, rectangles, and reusable `<symbol>` elements.

## Validation annotations

The bundled validator recognizes:

- `inkscape:groupmode="layer"` for layers
- `inkscape:label` for human-readable objects
- `data-container="id"` on contained text
- `data-padding`, `data-padding-x`, and `data-padding-y` for required inset
- `data-role="free-text"` for intentionally uncontained text

Use these annotations consistently; they are also useful documentation for future editors.
