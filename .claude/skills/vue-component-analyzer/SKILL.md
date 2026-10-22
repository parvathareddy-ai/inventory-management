---
name: vue-component-analyzer
description: Analyze the structure of Vue 3 components and recommend concrete optimizations for rendering performance and code reuse - oversized components to split, duplicated modal/card/table markup and CSS to extract, repeated format/helper functions to move into composables or utils, reactivity and v-for pitfalls, and expensive work in templates. Use this skill whenever the user asks to review, audit, analyze, refactor, slim down or optimize Vue components or a Vue frontend, asks "what can be reused", "where is the duplication", "why is this view slow", or complains that a .vue file is too big, even if they never say "performance" or "code reuse".
---

# Vue component analyzer

Produce a prioritized, evidence-backed list of optimizations for a Vue 3 codebase. This skill reports; it does not edit. The user decides what to act on, and refactors that touch `.vue` files are delegated to the `vue-expert` subagent per `CLAUDE.md`. Recommendations without file and line evidence are noise, so every finding must point at code you actually read.

## Workflow

### 1. Scope

Default to `client/src` (views, components, composables). If the user names a file or directory, analyze only that, but still scan the rest of `src` for duplicates, because "is this reusable" can only be answered by looking at what already exists.

### 2. Run the scanner

```bash
python3 .claude/skills/vue-component-analyzer/scripts/scan_vue.py client/src
```

It prints per-file line counts by block (template/script/style), counts of refs, computed values, watchers and `v-for`s, template smells, and duplication candidates (CSS selectors and identical rule bodies repeated across files, helper functions redefined in several files). Add `--json` for machine-readable output.

The scanner is regex-based, so treat its output as a map of where to look, not as findings. Expect false positives (a `formatDate(x)` call in a template is usually harmless) and misses. Read the flagged files before claiming anything.

### 3. Read the hotspots

Open the largest files and every file the duplication section names. Look for the patterns in the checklists below. Read enough to quote line numbers; skim the rest.

### 4. Report

Use this structure, most valuable first. Rank by (lines or renders saved) x (how many files benefit) / (risk of behavior change), and say so in one line so the user can disagree with the ranking.

```
## Summary
2-3 sentences: overall shape, biggest win.

## Findings
### 1. <imperative title> - <Reuse | Performance | Structure> - impact: High/Med/Low, effort: S/M/L
Evidence: file:line references, counts (e.g. "same .modal-overlay block in 6 files")
Why it matters: one sentence
Suggestion: the concrete extraction or change (name the new component/composable and its props/API)

## Not worth changing
Things that look suspicious but are fine, so the user does not chase them.
```

Keep it to the findings that matter, typically 5-10. A long list of nitpicks buries the two changes that would actually pay off.

## What to look for

### Code reuse (usually the biggest win in this kind of app)

- **Duplicated modal shells.** Several `*DetailModal.vue` files repeating the overlay, container, header, close button and footer markup and CSS. Suggest a `BaseModal.vue` with a default slot plus `header`/`footer` slots, `v-model`-style open state, Escape and overlay-click handling, and `Teleport`. Name the files that would shrink and by roughly how many style lines.
- **Repeated helpers.** `formatCurrency`, `formatDate`, status-to-color/class functions defined per component. Suggest `src/utils/format.js` or a `useFormatters` composable. Check the implementations are actually identical before recommending a merge; if they differ, say how.
- **Repeated UI patterns.** Stat/summary cards, data tables with the same header-and-row structure, status badges, loading and error states, info grids. Suggest a small presentational component with props or slots, and name the call sites.
- **Repeated data-loading logic.** The same `loading`/`error`/`try-catch`/fetch-on-filter-change sequence in several views. Suggest a composable (`useAsyncData`, `useFilteredResource`) that returns `{ data, loading, error, reload }`.
- **Shared styles stranded in scoped blocks.** Identical rule bodies in 3+ components belong in the global stylesheet or a token/utility layer, not copy-pasted. In this project global styles live in `client/src/App.vue` and `client/src/styles/`.
- Do not recommend abstracting something used twice with different needs. Premature shared components with a growing list of boolean props are worse than two copies; require at least 3 near-identical call sites or a stated intent to add more.

### Structure

- Components past roughly 400 lines or with more than one distinct job (fetching, filtering, charting, table, detail drawer). Suggest the seams: which template region becomes a child component, which script section becomes a composable.
- Large inline SVG charts embedded in a view. Suggest a chart component that takes data as props, since charts are the most self-contained unit.
- Props drilled through several layers where `provide/inject` or a composable with shared state fits better; or the reverse, a global store used for state that is local to one view.

### Performance

Rank by how often the code runs, not by how scary it looks. A one-time mount cost on a 12-row table is not a finding.

- **Work in templates.** `.filter()/.sort()/.map()/.reduce()` inside `{{ }}` or directives re-runs on every render. Move to `computed`. Method calls that do real work (not simple formatting) in `{{ }}` or in `v-for` have the same cost.
- **Computed that should be, or are not.** Derived values kept in `ref` and updated by hand or by `watch` (should be `computed`; see the project's "raw data in refs, derived in computed" rule). The inverse, a `computed` with side effects.
- **Watchers.** `deep: true` on large objects, watchers that fire fetches without debounce on every filter keystroke, `watch` where a `computed` would do, missing cleanup of timers and listeners in `onUnmounted`.
- **`v-for` correctness and cost.** Missing `:key`, `:key="index"` on lists that reorder or filter (project rule: use `sku`, `month`, etc.), `v-if` on the same element as `v-for`, very long lists that would benefit from pagination or virtualization.
- **Reactivity overhead.** Large read-only datasets or chart point arrays in `ref`/`reactive` where `shallowRef`/`markRaw` avoids deep proxying.
- **Loading cost.** Heavy, rarely-opened components (modals, report views) imported eagerly where `defineAsyncComponent` or a lazy route import would defer them. Check `main.js` for route definitions.
- **Redundant requests.** The same endpoint fetched by several components on one page, or refetched when an unrelated filter changes.
- **Dead weight.** Unused imports, refs and computed values never read in the template.

## Project-specific context (this repo)

- Filters (Time Period, Warehouse, Category, Order Status) flow through `client/src/api.js` as query params; inventory does not support month. A composable for filtered loading must respect that.
- Design rules: slate/gray palette, custom SVG charts, CSS Grid layout, no emojis. Suggested extractions must not change visuals.
- Add a comment for any non-obvious logic in suggested code, per `CLAUDE.md`.

## Verifying suggestions

Before recommending an extraction, grep for the pattern to confirm the call-site count and read two of them side by side to confirm they are truly equivalent. If you can run the app and Playwright is available, you may confirm a performance claim by measuring (for example render counts or timing), but static reasoning with line evidence is enough for most findings; say clearly which findings are measured and which are inferred.
