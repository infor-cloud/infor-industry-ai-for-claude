# MO proposals

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_PMS170MI_SearchMOP`, `M3_PMS170MI_LstMaterials`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`

Planner's view of what planning wants to make: find the user's proposals -> read each one's
components -> check stock and incoming supply -> say which can be firmed and which can't -> link
them to shortages on firm orders -> render.

## What a proposal is

A manufacturing order proposal is a planned order M3 suggests; it is not a manufacturing order
yet and consumes nothing until it is released. This skill only reads proposals; releasing one is done
by `release-mo-proposal.md`, after its own confirmation.

## 1. Who and what

- **Responsible user:** the user named in the request, else the signed-in user. Read the signed-in
  user with `M3_MNS150MI_GetUserData_CurrentUser` (user ID, default facility and warehouse). Never
  assume another person's ID.
- **Facility and warehouse:** from the user's prompt, else the current
  user's defaults, in that order. Say which you used.
- **All responsibles:** when the prompt says "all" proposals, MOs or production orders, leave out the responsible
  filter and read every proposal in the facility and warehouse (`at-risk-orders.md` step 2c). Unfiltered,
  `M3_PMS170MI_SearchMOP` returns the oldest first and is cut off at about 30 rows, so bound it with
  `PlannedFinishDate_LargerThan` (today minus the MO lookback), count the older ones apart as stale, and show the
  responsible user for each proposal.
- **Scope:** all proposals the user is responsible for, sorted by planned finish date. The review
  window (default 14 days from today, see `m3/settings.md`) is used only to mark which proposals start or
  finish soon; it doesn't hide the others.

## 2. Read

1. `M3_PMS170MI_SearchMOP` `{ ResponsibleUser_ExactSearch, Facility_ExactSearch,
   Warehouse_ExactSearch, SortBy: "PlannedFinishDate" }` -> keep for each proposal: planned order
   number, product, start and finish date, quantity and unit, responsible user. Add
   `ProductNumber_ExactSearch` or a date range (`PlannedFinishDate_LessThan` and so on) only if the
   user asked. State the cap if there are many (25).
2. For each proposal in the review window, and for any the user asks about (in parallel):
   `M3_PMS170MI_LstMaterials` `{ OrderNumber: <planned order number> }` -> components with item,
   description, quantity and warehouse. Proposal material lines carry no need date; use the
   proposal's start date as the need date and say so.
3. For each distinct component (in parallel): `M3_MMS200MI_GetItmWhsBal_Subname` -> on-hand,
   ordered (incoming), reserved and available inventory; `M3_PPS200MI_SearchLine` for purchased
   items -> open purchase orders with dates; `M3_PPS170MI_SearchPOP` -> planned purchase orders
   (proposals, never counted as safe supply).

## 3. Make sense of it

For each proposal, per component, compare the quantity it needs with what will be free by its start
date: available inventory (on hand minus everything already reserved, as M3 reports it), plus
confirmed firm purchase orders arriving by then. Unconfirmed and planned orders don't count.

- **Ready** - every component is covered by available inventory or confirmed supply.
- **Blocked** - at least one component is not; name it, the quantity short, and what is on the way
  (with its date and whether it is confirmed).
- **Can't tell** - a read failed; say which.

A component that is itself manufactured (it has its own manufacturing order or proposal) is blocked if
that supply is blocked; follow it up to three levels, using the orders in this conversation. Why: a
proposal that depends on a blocked semi-finished good can't be made either, and the planner should
fix the lowest level first.

**Link to firm orders.** If a firm manufacturing order in this conversation is short on this
proposal's product, say so: "Proposal <n> (finishes <date>) could cover <qty> of the <qty> short on MO
<m>, needed <date>", and whether the date works. Add that it only helps if the proposal is firmed and
itself Ready. Don't claim a proposal covers anything without that caveat.

## Show it

**In chat** (the default): one line (*Proposals*, *Blocked*, *Start or finish in the window*, with user, facility,
warehouse, window and as-of time); then a table, one row per proposal: planned order, product, quantity, start, finish,
status (✅ Ready / ❌ Blocked / ℹ️ Can't tell), the blocking component and quantity short, and "covers MO <m>" where it
applies. About 8 rows; summarise the rest in one line. Then "Next:".

**As a page, only when the user asks** (follow `m3/page-style.md`): titled "MO proposals for <user>": hero band (user, facility and warehouse, window, as-of time,
"M3 + Claude"); three tiles (*Proposals*, *Blocked* with the accent, *Start or finish in the window*); the board with
filter chips by status and rows that expand to their components; footer ("M3 + Claude", as-of time; nothing was changed
in M3).

Empty state: "You have no manufacturing order proposals in <facility>/<warehouse>."

## Next step

For a proposal that is Ready: "Want me to release proposal <n>?" (`release-mo-proposal.md`, one at a time).
For a Blocked one, fix the blocker first.
"Want the full check on <component>?" (`material-shortage-check.md`); "Want me to tell the buyer the
purchase order for <component> is late?" (`inform-buyer-of-late-order.md`); "Want the firm manufacturing
orders as well?" (`at-risk-orders.md`).

## Edge cases

- **Nothing found** - the empty state; offer another facility, warehouse or user.
- **Several matches** - for an ambiguous user or warehouse, ask; never pick.
- **Can't see it** - say which read was refused; don't retry.
- **Part of the data missing** - render the rest; one line on what's absent.
- **Dates** - proposal dates come as `YYYY-MM-DD`; show one format.
