# Dashboards and pages

Shared reference. Answers are in chat. A dashboard or page is built **only when the user asks for one**. The action
buttons on recommendations (`action-buttons.md`) are part of the chat answer, not a dashboard.

## When the user asks for a dashboard

1. If the user has a **dashboard link** for this work (given in this conversation or in the Claude Project's
   instructions; if neither, ask once, `settings.md`), show that dashboard: use the Artifact tool's `open` action with
   the link when that is available; otherwise give the link. Add one or two lines on what it shows. Do not build a new
   one; changes to it go into the **same** artifact, so the link is always the latest version.
2. Otherwise build a page from the data this conversation already read; don't run extra M3 calls for it. Say it is a
   snapshot as of the time of the data, and that it is private until the user shares it (it can contain customer and
   supplier details).
3. "Show my orders" or "list my orders" is a chat request, not a dashboard request: answer in a table.
4. If you cannot tell what the user wants, ask once. Do not guess by building something.

Every number on a page comes from a tool result in this conversation; every control does something; a cap or a gap in
the data is stated in one plain line. Label generated pages "M3 + Claude" and never present one as an official Infor
communication.

## Look (interim)

**Pending:** all dashboards will share one branding that follows the Infor Design System, actionable and dynamic. Until
that kit is added, use this neutral theme so pages stay consistent.

- Copy `page-tokens.css` into the page's `<style>`. It defines every token on `:root`, redefines them for dark mode (system
  preference and a `data-theme` override), and gives `body` an explicit background.
- Palette: `--brand-primary` for headers, key figures and links; `--brand-surface` and `--brand-surface-alt` for page and
  cards; `--brand-dark` for the hero band and footer; `--brand-accent` for **one** highlight per view (the run-out date or
  the worst row), as a fill or marker only, with ink-coloured text on or beside it.
- Status colours (success, warning, danger) are always paired with a text label such as "Short", "Late", "Enough".
- Font stack: Inter, "Segoe UI", system sans-serif. Headings weight 600; numbers use tabular figures.
- 12px corner radius, 1px borders instead of shadows, rows about 36px, 16px minimum side gutter so phone widths work.
- Stat tiles: big number, small label above, one line of context below; three at most in the hero row.
- Charts: `--brand-primary` leads the projected-balance line; a dashed `--brand-muted` line for safety stock or zero;
  `--brand-danger` shading below zero; `--brand-accent` marks the single run-out point. Label axes in dates and units.
- No logo: set "M3 + Claude" as plain text in the footer, with the as-of time.
