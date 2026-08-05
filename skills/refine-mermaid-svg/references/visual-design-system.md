# Visual design system

Use this as a starting point, not a mandatory brand. Adapt it to the subject and user-provided identity.

## Canvas and spacing

- Prefer a 16:9 canvas such as 1920×1080 for architecture infographics; choose another viewBox when the content demands it.
- Use an 8-unit spacing grid. Common gaps: 8, 16, 24, 32, 48, and 64.
- Keep outer margins at least 48 units on a 1920-wide canvas.
- Give card text 20–32 units of horizontal padding and 16–24 units of vertical padding.

## Type

- Use a portable UI stack: `Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif`.
- Suggested 1920×1080 scale: title 34–44, stage heading 13–16 with tracking, card title 17–21, body 13–16, badge 11–13.
- Use weight and color before adding more font sizes.
- Keep body line height near 1.35–1.5. Wrap card copy to two or three lines when possible.

## Color roles

A dark technical starting palette:

- canvas: `#071522`
- elevated panel: `#0D2133`
- card: `#14283F`
- strong text: `#F4F8FF`
- secondary text: `#A8BCD2`
- structural stroke: `#42617F`
- primary flow: `#59D5FF`
- trusted/success: `#48E0B2`
- credential/warning: `#F4B858`
- error/destructive: `#FF6B86`

Use opacity to create depth, but preserve sufficient contrast. Do not communicate meaning with color alone; pair semantic colors with labels, icons, or line styles.

## Card grammar

Use one base component geometry across the diagram:

- radius: 18–24
- border: 1.5–2 units
- icon slot: 40–56 square
- title aligned to the icon's optical center or top grid
- body aligned with the title, never underneath the icon unless intentionally stacked
- subtle shadow with a short vertical offset

Use variants through semantic accent color, not unrelated shapes. Reserve pills for concise status or boundary labels.

## Icons

Draw icons on a shared 24×24 or 32×32 optical grid with round linecaps and linejoins. Use a consistent 1.75–2.25 stroke. Favor recognizable metaphors: shield for trust, key for credentials, globe/server for HTTP, terminal for local process, arrows for relay.

Avoid detailed pictograms that collapse at export size. Do not use emoji because their appearance varies by platform and they are difficult to edit coherently.

## Depth and texture

Use a restrained combination of:

- one subtle canvas gradient
- faint dot or line pattern at low opacity
- shallow shadows for elevation
- a small glow only around the focal boundary or primary flow

Effects must never reduce text contrast or make selection in Inkscape confusing. Keep effect definitions named and centralized in `<defs>`.

## Review checklist

At full-size raster preview, verify:

- the primary flow is understood within five seconds
- stage boundaries are distinct without overpowering their contents
- cards align to a visible grid
- no line appears to terminate accidentally
- badges and edge labels have enough breathing room
- icon weight is consistent
- body copy is readable without zooming
- whitespace feels intentional rather than merely unused
