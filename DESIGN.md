---
name: QuantEvo Skill
description: Restrained local paper-account monitoring with visible operational health.
colors:
  ink: "#152c40"
  muted: "#496479"
  accent: "#18715b"
  background: "#f4f7fa"
  surface: "#ffffff"
  line: "#d5dfe7"
  warning: "#8b4d0c"
  error: "#b12932"
  table-header: "#ecf1f5"
  selected-row: "#f0f7f3"
  button-hover: "#e5edf3"
  button-selected: "#e2eee9"
  alert-background: "#fff5e9"
  alert-border: "#edd5b7"
typography:
  body:
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    fontSize: "15px"
    lineHeight: 1.55
  headline:
    fontSize: "26px"
    letterSpacing: "-.025em"
  title:
    fontSize: "21px"
    letterSpacing: "-.02em"
  label:
    fontSize: "12px"
  metric:
    fontSize: "22px"
rounded:
  button: "5px"
spacing:
  main: "24px"
  mobile-main: "18px"
  detail-gap: "32px"
components:
  button:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.button}"
    padding: "7px 13px"
  button-hover:
    backgroundColor: "{colors.button-hover}"
  account-select:
    textColor: "{colors.accent}"
    padding: "0"
---

# Design System: QuantEvo Skill

## Overview

The implemented identity uses slate text, light surfaces and restrained teal, following the existing README identity described in PRODUCT.md. It fits an operational local tool: compact evidence, legible figures and explicit health states take priority over decorative expression.

This document is extracted from `skills/quantevo/scripts/quantevo_runtime/dashboard.html`. It records the implemented source, not a newly explored brand direction. No named creative metaphor has been confirmed. Screenshot verification was outside this documentation pass; exact rendered behavior remains subject to the implementation's browser checks.

**Key Characteristics:**
- Quiet light surfaces with thin dividers.
- Tabular figures and readable operational labels.
- English and Chinese using the same system font stack.
- Text accompanies semantic health colors.

## Colors

### Primary

Restrained teal (`accent`) marks account selection, the equity trace, healthy status and keyboard focus.

### Neutral

Slate `ink` carries primary text; `muted` carries metadata and labels. `background` surrounds white `surface` containers. `line` separates rows and surfaces. `table-header` adds a pale blue tonal step, and `selected-row` distinguishes the active account.

Warning and error colors carry operational exceptions. The alert uses its own pale background and border. These are semantic states, not additional brand accents.

## Typography

Use the platform system sans-serif stack; no web font or separate display face is implemented. Body text uses the frontmatter body role. The page heading is the headline role, section headings the title role, and compact labels the label role. Metrics use the larger metric role.

Tables and metric figures use tabular numerals. Numbers align right in desktop tables; account fields align left in the mobile labeled grid. At the mobile breakpoint the page heading becomes (22px), header supporting text and worker status (13px), and fill rows (13px).

## Layout

The main content is centered with a maximum width of (1208px), including its main padding. The header aligns to the same effective content width. Health information wraps before the account evidence. The monitor presents account rows first, selected-account metrics and equity second, and recent fills afterward.

The metric ledger has four equal columns with (22px) gaps. At widths up to (640px), it becomes two columns with (12px) gaps and uses the mobile-main padding. Account tables become two-column labeled rows with the strategy spanning both columns. The fill table retains horizontal overflow inside its container.

The equity plot is (220px) tall on desktop and (180px) on mobile. Vertical extrema labels sit beside horizontal guides; date endpoints sit below the plot. Chart insets reserve room for the vertical labels.

## Elevation & Depth

No shadows are implemented. White surfaces, pale headers, selected-row tint and thin borders provide separation. Keep this distinction clear when extending the monitor.

## Shapes

Tables and chart containers have straight rectangular edges. Buttons use the small button radius. Borders are thin (1px). Selection is primarily tonal and typographic rather than a raised card treatment.

## Components

### Buttons

Language and refresh controls use white surfaces, slate text, small rounded corners and compact padding. Hover uses the documented pale blue tone. Keyboard focus uses a teal outline (3px) with an offset (3px). Selected button state uses the selected-button tone and teal border.

### Account selector and ledger

Account names are teal, semibold text buttons; hover adds an underline. The source label sits underneath in muted small text. Active accounts have a selected-row tint and expose `aria-pressed`. Account buttons are retained across refresh so keyboard focus survives updates.

### Health and alerts

Worker health is a polite live status region, updated when its text changes. The last-update timestamp is outside that live region. Health labels remain textual; teal, warning and error colors reinforce their meaning. Connection failures use an alert region, and account errors use a bordered pale warning panel.

### Equity chart

A plain teal SVG trace shows up to the latest 300 observations. Its accessible label summarizes starting and ending equity. Vertical extrema labels and horizontal guides explain the scale. A note explains the observation limit and warmup treatment. The single-observation state uses a horizontal trace.

### Fills and empty states

The fill ledger uses the same ruled-table vocabulary, tabular numbers and recent-first ordering. Empty-state prose uses muted text with generous container padding. Execution copy explicitly describes CSV simulation and modeled fills.

## Do's and Don'ts

### Do:
- **Do** use text together with health colors.
- **Do** retain tabular figures, visible keyboard focus and stable account selectors during refresh.
- **Do** preserve the shared hierarchy across English and Chinese.
- **Do** make chart scale and timestamps explicit.

### Don't:
- **Don't** describe simulated ledger fills as exchange executions.
- **Don't** introduce shadows or decorative gradients when extending this flat monitor without a deliberate design change.
- **Don't** make operational meaning depend on color alone.
