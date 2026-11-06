# Open purchase orders

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PPS200MI_SearchLine`, `M3_PPS200MI_SearchHead`, `M3_PMS100MI_LstMaterials`, `M3_PPS170MI_SearchPOP`

Buyer's view: take the filters the user gave -> read PO lines (and headers if needed) ->
compare with the date the material is needed -> flag late -> draft the chase -> render.

## 1. Understand the filter

Use what the user gave: an item, a supplier number, a buyer, a warehouse, a date range, or
a single PO number. Supplier names can't be searched here; ask for the supplier number if
only a name is given. If nothing narrows the search, ask for at least an item, supplier,
buyer or date range so the list is useful and not truncated. Default date range for "this
week": today through today + 7 days, on the confirmed delivery date.

## 2. Read (one turn, in parallel)

1. `M3_PPS200MI_SearchLine` with the filters that apply: `ItemNumber_ExactSearch`,
   `SupplierNumber_ExactSearch`, `Buyer_ExactSearch`, `Warehouse_ExactSearch`,
   `ConfirmedDeliveryDate_LargerThan` / `_LessThan`, `RequestedDeliveryDate_LessThan`,
   `SortBy: "ConfirmedDeliveryDate"`. Keep: PO number and line, item, supplier, buyer,
   warehouse, requested date, confirmed date, ordered, confirmed and received quantity,
   status, reference order (category and number, which can point at the manufacturing
   order or customer order the line serves).
2. If the user asked about one PO number: `M3_PPS200MI_SearchHead` with
   `{ PurchaseOrderNumber_ExactSearch }` for the header (supplier, buyer, order date,
   status) alongside the lines.
3. If the user ties the question to a manufacturing order (a number from this conversation, or
   given by them): `M3_PMS100MI_LstMaterials` `{ Facility, ManufacturingOrderNumber,
   ProductNumber }` -> the date each component is needed (reservation date) and the quantity.
   That is the *needed-by* date for lines on those items. Otherwise use the date the user gives;
   if there is none, judge lateness only against the requested date.

4. `M3_PPS170MI_SearchPOP` with the same item, supplier or buyer filters (`ItemNumber_ExactSearch`,
   `SupplierNumber_ExactSearch`, `Buyer_ExactSearch`, `Warehouse_ExactSearch`) -> planned purchase
   orders (proposals): planned order number, supplier, buyer, quantity, release date, delivery date,
   M3 message. Show them in their own group, never as open orders.

Treat a line as open when received quantity is below ordered quantity and the status is
not closed, deleted or invoiced-complete. If the result is very large, state the cap on
the page.

## 3. Make sense of it

A line is **late** (flag it, with the reason) when any of these is true:
- Its confirmed date (or, if unconfirmed, requested date) is after the needed-by date (the
  component's reservation date on the MO, or the user's date).
- Its confirmed date is after the requested date: the supplier slipped it; show the days.
- It has no confirmed date (M3 shows it as `0`): the supplier hasn't committed, so the requested
  date is only a hope.
- Its confirmed date is already past and the received quantity is still below ordered:
  overdue; show the days overdue and the open quantity.

Why: the buyer acts on promises, not wishes; a requested date that nobody confirmed gives no
protection, and a slip matters only relative to when the plant needs the material.

A **planned order** is late when its release date is today or earlier (it should already be released) or
its delivery date is after the needed-by date. Say that it is a proposal.

Group by supplier because chasing is done per supplier call. Rank within a supplier by
days late, then by open quantity. Show the open quantity (ordered minus received), not
only the ordered.

## Show it

**In chat** (the default): one line (*Open lines*, *Late or unconfirmed*, *Open quantity*, with the filter, date range and
as-of time); then one table per supplier: PO/line, item, requested, confirmed, open quantity, status (✅ On time /
⚠️ Slipped N days / ⚠️ Unconfirmed / ❌ Overdue N days / ❌ Too late for need); under each supplier a copy-ready chase
message listing that supplier's late lines (PO, line, item, current date, needed date, open quantity) with a polite
request to confirm or pull in, and to reply in writing. Drafted, not sent. Say that PO dates are changed in M3 by the
buyer; this view doesn't change them. If the result was capped, say so.

**As a page, only when the user asks** (follow `m3/page-style.md`): titled "Open purchase orders - <filter summary>": hero band (filter, date range, as-of time);
three tiles (*Open lines*, *Late or unconfirmed* with the accent, *Open quantity*); the board grouped by supplier with
sort and filter chips by status and rows that open their full detail; the chase message per supplier; footer ("M3 +
Claude", as-of time; nothing was changed in M3).

## Next step

To tell a buyer an order is late: `inform-buyer-of-late-order.md` (a drafted notice, not sent). To record a date the
supplier gave, or release or create the purchase yourself: `handle-po-or-inform-buyer.md` (M3 checks your authority; if it
refuses, the buyer is told instead).
"Want the full shortage picture for <item>?" (`material-shortage-check.md`); "If the supplier
can't move, want me to plan a purchase from another supplier?" (`m3/create-planned-po.md`).

## Edge cases

- **Nothing found** - "No open purchase-order lines match that." Offer a wider date range or
  dropping one filter.
- **Several matches** - for a PO number that exists in more than one company or warehouse,
  show them and ask.
- **Can't see it** - say which supplier or warehouse isn't visible; don't retry.
- **Part of the data missing** - render the rest; one line on what's absent.
