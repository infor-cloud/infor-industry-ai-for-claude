# Shortage radar

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MMS080MI_LstPOHBalance`, `M3_MMS080MI_LstMtPlByItmWhs`

Planner's daily review: choose window -> sample projected balances on several dates ->
rank items that go negative -> look closer at the worst few -> render.

## 1. Set the window

The window is today through `end` = today + N days. Default N is 14; the user may
have set another (it is configurable by design). If a warehouse was
given, restrict to it; otherwise cover every warehouse the user can see.

## 2. Read (one turn, in parallel)

M3 gives projected on-hand for a single planning date per call, so sample the window.
Choose up to five dates evenly spaced from today to `end` (for 14 days: day 0, 3, 7, 10,
14). Call `M3_MMS080MI_LstPOHBalance` once per date with `{ PlanningDate: <date> }`
(add warehouse or item filters only if the tool accepts them and the user gave them).

Keep, per item and warehouse and date: the projected on-hand balance.

If a response is very large, use the rows returned, state the cap ("first N rows per
date") on the page, and say the scan is incomplete. If one date fails, continue with the
others and name the missing date.

## 3. Make sense of it

An item is **at risk** when its projected balance is below zero on any sampled date in
the window. Why: negative projected stock means demand exceeds stock plus planned supply
on that date; orders that need the material then can't start or finish on time.

- **First short date**: the earliest sampled date it is negative. Because only a few dates
  are sampled, the true run-out can be earlier; say "by <date>", not "on <date>".
- **Depth**: the most negative balance sampled.
- **Rank**: earliest first-short date first; within a date, deepest first. Earlier
  shortages leave less time to fix them.
- Ignore items that are negative only by rounding (smaller than a unit) and say how many
  you skipped.
- Note items that were short on an earlier date but recover later: label "recovers by
  <date>" - a short gap a PO or MO already fills is lower priority than a gap that never
  recovers.

**Look closer at the top five.** For each, call `M3_MMS080MI_LstMtPlByItmWhs` with
`{ ItemNumber, Warehouse }` (in parallel). If it returns no lines, don't guess (`m3/material-plan.md`): say the plan has no lines and that which orders
the shortage starves isn't known from here, and point to `at-risk-orders.md`, which reads the MOs
themselves. If it returns lines, keep demand lines (manufacturing orders, customer orders)
dated on or after the first short date and the supply lines, to state "starves: MO <n>, customer order <n>"
and the exact run-out date (the first line whose projected balance is below zero).

## Show it

**In chat** (the default): one line (*Items going short*, *Earliest run-out* (date and item), *Deepest shortfall*
(quantity and item), with whose view, the window, the sampled dates and as-of time); a ranked table: item, warehouse,
first short date, depth, recovers by (or "does not recover in window"), what it starves (top five only), status
(❌ Short / ⚠️ Recovers); under it a copy-ready prompt per row: "Check <item> in <warehouse> through <end>" (runs
`material-shortage-check.md`); and the limits line: "Sampled on <dates>; a dip between samples may be missed", and any cap.

**As a page, only when the user asks** (follow `m3/page-style.md`): titled "Shortage radar - next <N> days", pattern *command centre with an action board*: hero band
(whose view, window, sampled dates, as-of time); three tiles (*Items going short* with the accent, *Earliest run-out*,
*Deepest shortfall*); the ranked board with sort and filter by warehouse and rows that expand to the plan lines; the
prompt per row; the limits line; footer ("M3 + Claude", as-of time; nothing was changed in M3).

Empty state: "Nothing is projected to run short through <end>. I checked <dates> across <warehouses>."

## Next step

"Want the manufacturing orders behind this?" (`at-risk-orders.md`); "Want the full check on <top item>?" (`material-shortage-check.md`), and "Want to see which
customers the top three would hit?" (`customer-impact.md`).

## Edge cases

- **Nothing found** - the empty state above; offer a longer window.
- **Can't see it** - say which warehouses aren't visible to them; don't retry.
- **Part of the data missing** - render the dates you have; one line on what's absent.
- **Freshness** - balances reflect M3's last planning run; say so.
