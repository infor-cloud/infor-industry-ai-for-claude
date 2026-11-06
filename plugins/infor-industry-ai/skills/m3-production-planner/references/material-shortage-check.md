# Material shortage check

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MMS200MI_LstItmWhsByItm`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstMaterials`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`, `M3_PMS100MI_GetOperation`, `M3_CPS100MI_SelTotalLoad`, `M3_MMS080MI_LstMtPlByItmWhs`

<!-- contents:start -->
**Contents**

- 1. Resolve what to check
- 2. Read (parallel where independent)
- 3. Make sense of it
- 4. Options (the planner chooses; never auto-apply)
- Show it
- Next step
- Edge cases
<!-- contents:end -->

Planner's answer in one page: an MO (or an item) -> its components -> for each, stock and
incoming supply against the date it is needed -> follow semi-finished goods down to their own
MOs -> name the root cause -> options -> render.

## 1. Resolve what to check

- **An MO:** you need the facility, the MO number and, if the read asks for it, the product
  number. Facility defaults to the one on the item-warehouse record. Never guess a number.
- **An item only:** you need the item and warehouse (resolve the warehouse with
  `M3_MMS200MI_LstItmWhsByItm` `{ ItemNumber }`; one match proceeds, several: ask). Without an
  MO the check can only see stock and incoming supply; say so.
- **Other MOs for the same material:** to judge competing demand and to follow a
  semi-finished component to the MO that makes it, you need those MO numbers. Use the MOs
  already in this conversation (for example from `at-risk-orders.md`). If the user knows more,
  ask for them; never invent.
- The date window is the MO's own dates; for an item-only check use today through today +
  the review window (default 14 days).

## 2. Read (parallel where independent)

For each MO in scope (cap 10):
1. `M3_PMS100MI_Get` `{ Facility, ManufacturingOrderNumber, ProductNumber }` -> status,
   start and finish date and time, ordered and received quantity, warehouse, reference
   order category and number (a customer order link if there is one).
2. `M3_PMS100MI_LstMaterials` with the same keys -> each component: number and name,
   operation number, reserved (needed) quantity, remaining quantity, reservation date (the
   date it is needed), acquisition code (Purchase or Manufacturing), warehouse, safety time.

For each distinct component with remaining quantity above zero (in parallel):
3. `M3_MMS200MI_GetItmWhsBal_Subname` `{ ItemNumber, Warehouse }` -> approved on-hand,
   allocatable, **ordered quantity** (incoming), **reserved quantity** (all demand),
   available inventory.
4. `M3_PPS200MI_SearchLine` `{ ItemNumber_ExactSearch, Warehouse_ExactSearch, SortBy:
   "ConfirmedDeliveryDate" }` -> open PO lines: PO and line, supplier, ordered, received,
   requested date, confirmed date, status.

5. `M3_PPS170MI_SearchPOP` `{ ItemNumber_ExactSearch, Warehouse_ExactSearch }` -> planned purchase
   orders (proposals): planned order number, supplier, quantity, delivery date, M3 action message.
   These are **not** supply you can rely on: they aren't purchase orders yet.

For the work center: `M3_PMS100MI_GetOperation` with an operation number taken from a material
line -> work center, capacity type and remaining hours; then `M3_CPS100MI_SelTotalLoad` `{ Facility, WorkCenter,
FromDate: <today>, ToDate: <the MO's planned finish or today + the review window, whichever is
later> }` (`YYYY-MM-DD`) -> weekly rated capacity per unit and shift against manufacturing-order and
planned-order load of the operation's capacity type (machine time for type 1, man time for type 2;
`capacity-types.md`). If it returns nothing, say capacity wasn't checked.

`M3_MMS080MI_LstMtPlByItmWhs` (the time-phased material plan) may be used; treat an empty result as "no plan data"
(`m3/material-plan.md`), never as "enough".

If a read fails, carry on without that part and say so in one line.

## 3. Make sense of it

The planner's rule: *check on-hand for each material or semi-finished good on the MO; if it
is below the demand, check incoming purchase orders or manufacturing orders; check competing
MOs for the same material; it is a risk if any component won't be enough to run the MO on
time.* Apply it per component:

**Needed:** remaining quantity, on the reservation date (that is when the component must
exist; the MO starts earlier).

**Supply by that date:**
- On-hand (approved, allocatable) now.
- Purchase-order lines: open quantity (ordered minus received) arriving on the confirmed date.
  If the confirmed date is `0`/blank, the line is **unconfirmed**: use the requested date for
  timing but flag it, and don't count it as safe.
- Planned purchase orders are listed separately as "proposed, not released" and are never counted
  as safe supply, even when their delivery date is in time. One whose release date is today or
  earlier is **overdue to release**; say so and offer `inform-buyer-of-late-order.md`.
- Semi-finished goods: the MO that makes the component, if it is in scope: its planned
  finish date and its ordered quantity. If it finishes after the date the parent needs it,
  it's too late.
- Quantity "on order" from the balance read that you cannot match to a visible PO line or
  MO: say "<qty> on order that I can't trace to an order".

**Competing demand:** other MOs in scope that reserve the same component: add their remaining
quantity on their reservation dates. Also compare the balance's reserved quantity with the
demand you can see; the difference is "reserved by orders I can't see". Walk demand and
supply in date order to find the first date the running balance goes below zero.

**Per component verdict:** *OK*, *Tight* (covered only by unconfirmed supply), *Short* (balance
below zero on a date on or before the need date; give date, shortfall, and what arrives too
late), or *Can't tell* (data missing).

**Root cause across levels.** If a semi-finished component is Short because its own MO can't
start (its components are Short), the root cause is the lower-level component. Follow it to a
depth of three levels and report the chain in one line, for example "MO A needs SF2 <- MO B
makes SF2 <- SF3 has nothing on hand, nothing on order". Why: fixing the top of the chain does
nothing; the planner needs to know where to act.

**MO verdict:** At risk when any component is Short or the chain below it is; Tight when only
unconfirmed supply holds; OK otherwise. Say how many demand lines you could see versus total
reserved.

**Capacity.** Add the weekly load (manufacturing orders and planned orders; machine time for capacity type 1,
man time for type 2) and compare it with the capacity per unit and shift. Show machine capacity and labor
capacity separately (`capacity-types.md`); over it is a **Capacity** cause, shown with the figures. The
rating is per unit and shift, so a work center with more units or shifts has more room; say so when
close. Planned-order load is shown separately from firm load.

**Do not trust** the material-line flag "all materials allocated" when the allocated quantity
is zero; use quantities.

## 4. Options (the planner chooses; never auto-apply)

Order them as a planner works down a shortage; for each show how much of the shortfall it covers:
1. *Pull in an existing purchase order* - for a Short purchased component with an open PO later
   than the need date or unconfirmed: days to move; a drafted supplier request (copy-ready). You
   can't change the PO; the buyer does that in M3 (you may record a confirmation the supplier gave, see 1c).
1b. *Tell the buyer* - if the only supply for a Short purchased component is a late purchase order or
   a planned purchase order (a proposal): offer `inform-buyer-of-late-order.md`, which drafts a notice
   to the buyer with the dates and the ask. The buyer chases the order and normally releases it.
1c. *Deal with the purchase yourself* - release the planned PO, create a planned PO or a new PO, or record the
   supplier's confirmed date (`handle-po-or-inform-buyer.md`). Show it as an option next to 1b. M3 checks the planner's
   authority when the card is confirmed; if it refuses, stop and advise the buyer (hand-over message).
2. *Buy from another supplier* - find candidates with `m3/alternate-suppliers.md` (or the user names the supplier), then
   plan the purchase with `m3/create-planned-po.md`.
3. *Make or move the semi-finished component* - for a Short manufactured component: name the
   MO that makes it (or say none exists) and that the planner must release or create it in M3.
4. *Free material from competing MOs* - name the competing MOs and quantities.
4b. *Swap to an alternative item* - for a Short component whose supply comes too late and where rescheduling won't help:
   offer `swap-material.md`. It finds the items related with replacement type 3, 4 or 5 that are in stock or on a PO or planned PO
   and quicker than the original, and swaps the material line on the planner's yes. The buyer's wider substitute list
   (m3-buyer, delayed PO option B) is not used here (`m3/known-inconsistencies.md`, K1 and K19). Never change an MO's
   material any other way.
5. *Reschedule the order* - offer `reschedule-mo.md`, which recommends a date from the confirmed supply, a quantity the components allow, or a
   finite-capacity recalculation, for the planner to decide.
6. *Tell the customer* - offer `customer-impact.md`.

## Show it

**In chat** (the default):
1. One line: the MO verdict (❌ At risk / ⚠️ Tight / ✅ OK), the root cause (component and level) and the earliest failure
   date, with MO, product, dates, quantity and as-of time.
2. A component table, lower levels indented: item, needed (quantity, date), on hand, incoming (source, date, and
   ✅ In time / ❌ Too late N days / ⚠️ Unconfirmed / ℹ️ Not traced), competing demand, verdict, cause.
3. The root-cause chain in one line.
4. The options (2 to 4), each with how much of the shortfall it covers and what it needs; a copy-ready supplier message
   under the purchase-order option.
5. Coverage line: "Based on <n> demand lines I could see; <m> reserved in total." Then "Next:".

If every component is OK, keep it short: the verdict line and one warm line.

**As a page, only when the user asks** (follow `m3/page-style.md`): titled "Material check - MO <number>" (or "- <item>, <warehouse>"): hero band (MO, product,
dates, quantity, as-of time, "M3 + Claude"); three tiles (*MO verdict* with the accent when At risk, *Root cause*,
*Earliest failure*); the component table; the chain line; option cards with a "Copy supplier message" block; the coverage
line; footer ("M3 + Claude", as-of time; nothing was changed in M3).

## Next step

Short component with an alternative item: "Want me to check a swap to <alternative>?" (`swap-material.md`).
Short purchased component: "Want me to plan a purchase from another supplier?"
(`m3/create-planned-po.md`). A PO is the lever: `open-purchase-orders.md`. Nothing closes the
gap: `customer-impact.md`. Several MOs to look at: `at-risk-orders.md`.

## Edge cases

- **Nothing found** - "I can't find MO <number> in <facility>." Check the facility and product.
- **Several matches** - show them and ask; never pick.
- **Can't see it** - say which read was refused; don't retry.
- **Empty plan / no data** - no verdict from that source; state what the balance and orders say.
- **Part of the data missing** - render the rest; one line on what's absent.
- **Dates** - M3 returns both `20261022` and `2026-10-22`; read both, show one format.
