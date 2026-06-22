# Interfaz de estudio FIUBA — guía de diseño

> Estado: `Referencia vigente` · Ultima revision documental: `2026-06-22`

Esta guía es el contrato visual y de lenguaje para todas las pantallas, incluidas
las actividades. Las variaciones por materia pueden usar un color identificatorio,
pero no redefinir tipografía, espaciado, navegación ni componentes.

## 1) Tema visual
- Espacio de trabajo cálido y minimalista.
- Académico, calmo y preciso.
- La legibilidad prevalece sobre la decoración.

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

## 8) Lenguaje
- Nombre del producto: `Asistente FIUBA`.
- Secciones: `Asistente`, `Calendario`, `Actividades`, `Administración`.
- La interfaz general se escribe en español rioplatense y usa voseo.
- Los términos técnicos sin traducción clara se explican la primera vez.
- Las siglas de formatos o tecnologías (`API`, `ICS`, `FTS`) se conservan.
- Todos los textos visibles respetan tildes y puntuación.

## 9) Navegación y actividades
- La navegación principal conserva el mismo orden y tratamiento visual.
- Las actividades usan los tokens globales y los mismos botones, campos y tarjetas.
- El color de una materia sólo puede aparecer como acento secundario en iconos,
  etiquetas o progreso; las acciones principales permanecen azules.
- Radio de controles: `12px`. Radio de tarjetas: `12px` o `18px`.
- No se usan barras laterales oscuras como identidad paralela del producto.

## 10) Qué hacer y qué evitar
Hacer:
- Favor clear hierarchy and reading comfort.
- Keep source traceability visible.
- Keep interaction latency visible via status pill.

Evitar:
- Overuse bright accents.
- Hide source metadata.
- Use dense dashboard visuals for study content.
