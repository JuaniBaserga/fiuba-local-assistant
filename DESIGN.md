# FIUBA Study UI - DESIGN.md

> Estado: `Referencia vigente` · Ultima revision documental: `2026-06-22`

Reference style:
- Inspired by the Notion profile from `VoltAgent/awesome-design-md`.
- Source reference: `https://getdesign.md/notion/design-md`.

## 1) Visual theme
- Warm minimal workspace.
- Academic, calm, and precise.
- High readability over decorative complexity.

## 2) Color palette
- `bg`: `#f6f5f4`
- `surface`: `#ffffff`
- `text`: `#161514`
- `muted`: `#5d5853`
- `line`: `#dfdbd7`
- `primary`: `#0075de`
- `primary-active`: `#005bab`
- `success`: `#2a9d99`

Use cases:
- Primary actions and links use `primary`.
- Passive metadata uses `muted`.
- Dividers and input borders use `line`.

## 3) Typography
- Primary UI font: `"IBM Plex Sans", "Avenir Next", "Segoe UI", sans-serif`.
- Headings: serif display (`"Fraunces", "Iowan Old Style", "Times New Roman", serif`).
- Strong contrast between heading and body to separate hierarchy.

Scale:
- H1: bold, compact line-height (~1.05).
- Body: 15px-16px, line-height ~1.5.
- Labels and metadata: 12px-14px.

## 4) Layout
- Two-panel desktop layout:
  - Left: controls/configuration.
  - Right: question + answer + sources.
- Mobile collapses to one column.
- Spacing rhythm: 8, 12, 16, 22 px.

## 5) Components
- Inputs:
  - Rounded corners (`12px`), visible focus ring in blue.
  - Neutral background, no heavy shadows.
- Cards:
  - Soft border + subtle elevation.
  - Distinct cards for answer and sources.
- Status pill:
  - Color-coded (`ready`, `loading`, `error`).
- CTA button:
  - Solid blue gradient with light motion feedback.

## 6) Motion
- Keep motion subtle and useful only:
  - Button press micro-motion.
  - Fast focus/hover transitions (~140-180ms).
- No continuous decorative animations.

## 7) Response formatting in UI
- Preserve structured assistant output:
  1. Respuesta corta
  2. Desarrollo
  3. Chequeo de parcial
  4. Fuentes
- Always show sources block below response.

## 8) Do and do-not
Do:
- Favor clear hierarchy and reading comfort.
- Keep source traceability visible.
- Keep interaction latency visible via status pill.

Do not:
- Overuse bright accents.
- Hide source metadata.
- Use dense dashboard visuals for study content.
