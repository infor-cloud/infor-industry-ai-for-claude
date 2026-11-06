# Customer impact

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_Get`, `M3_OIS100MI_SearchLine_Summary`, `M3_OIS100MI_GetOrderHead`, `M3_CRS610MI_GetBasicData`, `M3_CMS055MI_LstByCustomer`, `M3_CRS618MI_Get`

Customer service's view of a late manufacturing order: find the customer orders the MO (or the
short item) serves -> add customer and contact -> draft the notice -> render.

## 1. Resolve what is late

Start from an MO when you can: the facility, MO number and product (reuse them from an
`at-risk-orders.md` or `material-shortage-check.md` result in this conversation, or ask). If the user
gave only an item and warehouse, use that path in step 2b. Never guess a number.

## 2. Read

**2a. From an MO (preferred).** `M3_PMS100MI_Get` `{ Facility, ManufacturingOrderNumber,
ProductNumber }` -> keep planned finish date, ordered quantity and the **reference order**
(category, number, line). If the reference order is a customer order, that is the customer
order the MO serves. If the category is blank or "use varies", this MO isn't linked to a
customer order in M3 (it may be made to stock); say so and stop: don't invent a customer.

**2b. From the product (also use it with 2a).** `M3_OIS100MI_SearchLine_Summary`
`{ ItemNumber_ExactSearch: <finished product>, SortBy: "RequestedDeliveryDateAtDestination" }` ->
open customer order lines: order, line, quantity, requested and confirmed date, status. Drop
deleted, completed and delivered lines. Cover them with the MOs in date order (an MO covers
customer demand when it finishes on or before the requested date); the rest, or those whose
covering MO is at risk, are affected. A made-to-stock MO carries no customer link in M3, so this
match is by product and date, not an order reference; say so.

For each customer order found (at most 10, earliest first; state the cap), in parallel:
- `M3_OIS100MI_GetOrderHead` `{ OrderNumber }` -> customer number, **warehouse**, requested
  delivery date, order status, stop code. If the order's warehouse differs from the MO's, say the match
  is by product and date and the supply link between the warehouses isn't confirmed.
- For each distinct customer: `M3_CRS610MI_GetBasicData` `{ CustomerNumber }` -> name, and
  `M3_CMS055MI_LstByCustomer` `{ CustomerNumber }` -> contact person ids; then
  `M3_CRS618MI_Get` `{ ContactPerson }` for the first one or two -> name and email or phone.

If a contact lookup fails or none is on file, say "no contact on file". Don't show credit or
financial data; it isn't needed here.

## 3. Make sense of it

An order is **affected** if it is the customer order an at-risk MO serves, or draws on a short
item on or after its run-out date, and the shortage isn't covered in time. The material plan lists demand in date order, and stock
runs out in that order, so the *earliest* orders after the run-out date are the first
starved; later ones may still be fed if supply arrives. Rank by requested delivery date,
earliest first, and say which are certain (they fall before any supply that arrives) and
which are possible (supply arrives before them but the quantity may not stretch).

A semi-finished MO deep in the chain usually has no customer order of its own; the customer
link sits on the top-level MO. Say on the page which MO the link came from, so nobody reads it as
a complete list of every customer touched through semi-finished goods.

## Show it

**In chat** (the default): one line (*Orders affected*, *Customers*, *Earliest requested date*, with item, warehouse,
run-out date and as-of time); a table: customer, order number, requested date, quantity, certainty (❌ Certain /
⚠️ Possible), contact name and e-mail or phone, or "no contact on file"; then a copy-ready **draft notice per customer**
in a customer-service voice: what is delayed (the order and item), the earliest date you can state only if the user
supplied one, an apology without blame, and what happens next. Don't invent a new delivery date; leave "<new date>" as a
visible blank for the planner to fill. Drafted, not sent. End with the limits line: the cap on orders, and which MO the
customer link came from.

**As a page, only when the user asks** (follow `m3/page-style.md`): titled "Customers affected - <item>"; it contains customer names and contacts, so say it is
private until shared. Hero band (item, warehouse, run-out date, as-of time); three tiles (*Orders affected* with the
accent, *Customers*, *Earliest requested date*); the table; the draft notices; the limits line; footer ("M3 + Claude",
as-of time; nothing was changed in M3).

## Next step

"Want me to plan a purchase to close the gap?" (`m3/create-planned-po.md`); "Want to
re-check the shortage once the purchase order is confirmed?" (`material-shortage-check.md`).

## Edge cases

- **Nothing found** - "No customer orders draw on <item> after <date>." Offer a longer horizon.
- **Several matches** - show candidate warehouses and ask.
- **Can't see it** - if a customer or contact isn't visible to them, say that and continue
  with the rest; don't retry.
- **Part of the data missing** - render the rest; one line on what's absent.
