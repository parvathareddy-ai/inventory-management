---
name: vue-saas-redesign
description: Redesign a Vue 3 application's UI into a modern SaaS-style interface - a fixed vertical navigation sidebar on the left in place of the top nav bar, a design-token system for consistent spacing, and a polished professional look. Use this skill whenever the user asks to modernize, restyle, reskin or "make it look professional" for a Vue app, wants a left sidebar or side navigation instead of a top nav or header tabs, mentions SaaS or dashboard-style layout, design tokens, or inconsistent spacing in a Vue 3 UI, even if they never say "sidebar" or "redesign".
---

# Vue 3 SaaS redesign

Turn a Vue 3 app with a top navigation bar into a modern SaaS-style layout: a vertical sidebar on the left, a content area with a consistent spacing scale, and one cohesive visual system. The redesign is purely presentational. Routes, data loading, API calls, i18n and component logic must behave exactly as before; the user is asking for a new look, and any behavior change is a regression they did not ask for.

## Workflow

### 1. Survey before touching anything

Find out what already exists so the redesign extends the app instead of fighting it:

- The root layout (usually `App.vue`): where the top nav, filter bar and `<router-view>` live, and which components sit in the header (profile menu, language switcher, notifications).
- The router (`main.js` or `router/`): the real list of routes. The sidebar links come from here, not from guesses.
- Global styles: where `body`, cards, tables, badges and buttons are styled, and whether views also carry scoped CSS with hard-coded values.
- The existing palette and rules. Read `CLAUDE.md`, `README` and any design notes. If the project states colors, "no emojis", or "delegate .vue edits to a subagent", follow them. Keep the app's own palette; this skill defines structure and rhythm, not a new brand.
- How labels are produced (an i18n composable, plain strings) so sidebar labels reuse the same source. Hard-coded English labels in a translated app would be a visible regression.
- The build and dev command, so you can verify.

### 2. Add design tokens

Copy `assets/tokens.css` into the project's styles (for example `src/styles/tokens.css`) and import it once from the entry file. Then edit the color values at the top to match the app's existing palette. Tokens matter because consistency comes from one scale applied everywhere, not from careful eyeballing: spacing uses a 4px base (`--space-1` ... `--space-12`), plus tokens for radius, shadow, type size, borders and layout widths (`--sidebar-width`, `--content-max`).

Replace hard-coded padding, margins, radii, shadows and colors in the global styles with tokens. Do this for the shared building blocks (page header, stat cards, cards, tables, badges, buttons, form controls, loading and error states). Leave one-off view-scoped CSS alone unless it clashes with the new layout (fixed top offsets, `100vw` widths, its own max-width wrappers); rewriting every view is how a restyle turns into a regression-filled rewrite.

### 3. Build the sidebar

Copy `assets/AppSidebar.vue` into `src/components/` and adapt it. Defaults, chosen because they are what users expect from SaaS products:

- Fixed, full-height, about 240px wide; logo and product name at the top.
- Nav links in a vertical list, optionally grouped under small uppercase section labels (for example Operations, Finance, Insights). Group only when the app has enough routes for it to help; seven links usually read fine in one or two groups.
- An inline SVG icon on every link so the collapsed state stays understandable. Draw them as small `<svg>` elements with `currentColor`; do not add an icon library dependency and never use emoji.
- Active state from `router-link-active` / exact-active (a tinted background plus an accent bar), hover and keyboard focus-visible states.
- Footer pinned to the bottom holding the controls that used to sit in the top bar: profile menu, language switcher, and similar. Move the existing components as they are; do not rewrite them.
- A collapse toggle that shrinks to an icon rail (about 64px), remembering the choice in `localStorage` inside a try/catch. On narrow screens (900px and below) the sidebar is forced to icons-only and the toggle is hidden, without overwriting the stored preference. Give collapsed links an `aria-label` and `title`, since their visible text is hidden.
- Make sure the page toolbar or filter bar wraps (`flex-wrap: wrap`) at narrow widths; a nowrap toolbar is the usual cause of horizontal page scroll once the sidebar takes its share of the width.

Generate the link list from the router's real routes and the app's real label source. Keep each link's `to` path and any `active` logic equivalent to the old nav.

### 4. Restructure the layout

In the root layout, replace the header with the sidebar and wrap content so the sidebar stays put while the page scrolls:

```
.app            display: grid; grid-template-columns: var(--sidebar-width) 1fr
  AppSidebar    position: sticky; top: 0; height: 100vh
  .app-main     min-width: 0   (prevents wide tables from blowing out the grid)
    FilterBar / page toolbar   sticky at the top of the content area
    main.main-content          padding: var(--space-8); max-width: var(--content-max)
```

Keep the filter bar (or any page-level toolbar) as the first row of the content area rather than deleting it; it carries functionality. Check that modals and dropdowns still layer above the sidebar (`z-index`) and that the profile menu popover opens upward or sideways from the footer so it is not clipped.

### 5. Polish with restraint

A professional look comes from a few disciplined choices, not decoration:

- One accent color, used for active states, primary buttons and links. Neutrals do the rest.
- Cards: white surface, 1px border, a very light shadow, `--radius-lg`. Tables: sticky or clearly separated header row, generous row padding, subtle row hover, right-aligned numeric columns.
- A type scale with clear hierarchy: page title, section title, body, caption. Muted color for secondary text.
- Consistent gaps: page sections `--space-6`, card padding `--space-5` or `--space-6`, form controls aligned to the same heights.
- Keep status colors (green, blue, amber, red) as they are in the app; only soften their backgrounds into tinted pills if they are not already.

### 6. Verify

- Run the production build (`npm run build` or the project's equivalent) and fix any error.
- Open every route in the running app and take a screenshot. Check for: horizontal page scroll, content hidden under the sidebar, clipped popovers, tables overflowing their cards, and any view with leftover top padding from the old header.
- Check the browser console for new errors or warnings.
- Click through the sidebar links, toggle collapse, and tab through the sidebar to confirm focus styles are visible.
- If the app has multiple locales, switch locale once and confirm long labels do not break the sidebar.

## Guardrails

- Do not change routes, API calls, store/composable logic, or translation keys' meaning. Add a new key only when a new label is truly needed, in every locale file.
- If the project requires delegating `.vue` edits to a specific subagent, do that for the sidebar and layout work.
- Comment non-obvious CSS decisions (for example why `min-width: 0` is on the content column) so the next person does not undo them.
- Prefer editing existing files over creating parallel ones. If a nav component already exists, restyle and reposition it.
- Report what changed at the end: files touched, tokens added, and anything intentionally left alone (such as view-scoped CSS) so the user knows where remaining inconsistencies might live.
