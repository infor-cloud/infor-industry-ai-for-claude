# Customer service rep: fix a short, at-risk or late line

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_PPS200MI_SearchLine`, `M3_PMS100MI_Get`, `M3_MMS120MI_AllocateOrdLine`, `M3_MWS411MI_LstDelLnByOrd`, `M3_OIS120MI_GetCOStopInfo`, `M3_MMS020MI_LstItemRelation`, `M3_OIS100MI_AddOrderLine`, `M3_OIS100MI_DelLine`, `M3_DPS001MI_LstRelation`, `M3_DPS170MI_CrtPlannedDO`, `M3_MMS120MI_DeAllocateOrLne`, `M3_OIS100MI_UpdCOPlanDates`, `M3_OIS100MI_GetLine`

<!-- contents:start -->
**Contents**

- What this does
- 1. Free stock
- 2. Existing supply
- 3. The fixes M3 accepts: Use an alternative item · Distribution order from another warehouse (distribution order proposal) · Take stock from another order · Alert the buyer or planner · New confirmed date and customer update
<!-- contents:end -->

## What this does

Work **one line at a time**. Check in this order and tell the rep what each shows. Offer an option only when M3 says it is possible, and say why
when it is not.

## 1. Free stock

Free stock in the line's warehouse and in the other warehouses.

**Tools:** `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_MMS200MI_LstItmWhsByItm`.

## 2. Existing supply

Existing supply from the material plan: purchase orders, manufacturing orders, planned orders and distribution orders, with dates and status.
The rep can only tell the buyer or planner about these, **by e-mail**.

**Tools:** `M3_MMS080MI_LstMtPlByItmWhs`, `M3_PPS200MI_SearchLine`, `M3_PMS100MI_Get`.

## 3. The fixes M3 accepts

Then the options below. Each option shows the **new date** it would give.

A fix is **offered only when M3 says it will work**, and every fix is **checked again right before the change**: the order is still open, still the user's,
still in the state the fix was offered for. After the write, read it back.

| Fix | Offer only when | How | Read back |
|---|---|---|---|
| Allocate a line | Free stock exists, and a manual allocation is safe for the item | Allocate the order line (allocation origin and stock transaction type: `m3/settings.md`) | Free stock fell; the line shows allocated |
| Swap to an alternative item | "Use an alternative item" below | Add line, check, delete old line | The order lines |
| Distribution order proposal | "Distribution order from another warehouse (distribution order proposal)" below | Create the planned distribution order | The proposal in the receiving warehouse's plan |
| Take stock from another order | "Take stock from another order" below | De-allocate, allocate, restore on failure | Both lines |
| E-mail to buyer or planner | A purchase or manufacturing order (or nothing) covers the shortage | E-mail draft (`m3/mail-delivery.md`); nothing is written to M3 | The text shows the order, item, quantity and date |
| Remind the warehouse | An allocated line is due soon and no picking list is printed | E-mail draft to the warehouse (`m3/mail-delivery.md`); nothing is written to M3 | The text shows the order, items, quantities and due date |
| New confirmed date | The order type allows it (check the order type setting first) | `UpdCOPlanDates` on the order line or lines: `ConfirmedDeliveryDate` only, no `UpdateMode`, `LineNumber` empty for all lines | Read the line or lines back; say so if unchanged |
| Credit stop | Never a rep action | Draft a request to the credit controller | none |
| Purchase or manufacturing order change | Never a rep action | E-mail the buyer or planner | none |

If a write tool is not in the tool list, the fix is not offered. Say which tool is missing.

**Tools for the fixes without their own section:** allocate `M3_MMS120MI_AllocateOrdLine`; check the picking list `M3_MWS411MI_LstDelLnByOrd`, `M3_OIS120MI_GetCOStopInfo`.

### Use an alternative item

Alternatives are the items related with **replacement type 1, 2, 3 or 4**, read from the item on the line to the related item
(1 = complete replacement, the old item may no longer be used; 2 = replaced, but the current balance is used first; 3 = interchangeable
under M3's defined rules; 4 = fully interchangeable; the buyer skill uses a wider set of types, see `m3/known-inconsistencies.md`, K1). Type 5 (only alternative material in a product structure) and
the Web Shop types 7, 8 and 9 (accessory, replaces at zero balance, sold together) are not alternatives. Show each with its free stock in the line's warehouse. The rep must check with the customer before substituting:
the alternative can differ in size or specification.

**Swapping on the existing order** (never a new order): (1) add the new line with the same quantity and warehouse; (2) read it back and check the
item and quantity; (3) only then delete the old line; (4) check that the old line is gone and read the order back. If M3 raises a warning on the new
line, nothing is added: show the warning and let the rep decide whether to accept it. If the new line does not look right, do **not** delete the old one. In the dashboard the first call is made without ignoring warnings; if M3 raises one, a second pop-up shows M3's own words and "Add anyway" repeats the call once with warnings accepted (cancel leaves everything as it was).
The new line takes the order's requested date and the price M3 finds.

**Tools:** `M3_MMS020MI_LstItemRelation`, `M3_OIS100MI_AddOrderLine`, `M3_OIS100MI_DelLine`.

### Distribution order from another warehouse (distribution order proposal)

Offer it when another warehouse has enough free stock **and** a distribution relation exists from that warehouse to the short one. Steps: check the
relation, create the proposal, then look it up in the receiving warehouse's plan to confirm it exists. It is a **proposal** created with `PlannedOrderStatus` = `Pur/planMan` (**status 20, firm**; never `PlanOrdMan`, which gives status 10). Leave it at status 20: the rep does not release it, the planner will.
Do not use the inbox steps of the distribution order tools: creating the proposal already does the job and the inbox step would duplicate it.
If there is no relation, an administrator must add it.

**Tools:** `M3_DPS001MI_LstRelation`, `M3_DPS170MI_CrtPlannedDO`, `M3_MMS080MI_LstMtPlByItmWhs`.

### Take stock from another order

Any order that is short of free stock may ask for stock from another customer order. **The order type plays no part**, neither for the one that receives nor for the one that gives; only the dates of the orders do. Rules (the dashboard applies the same ones, and checks them again right before it writes):
- The donor's line must be **allocated** (plan status 33; "Reserved", status 22, holds nothing) and have no picking list yet.
- The donor must be due **more than 3 days from today**. An order due sooner, or already late, is about to be picked and is never asked to give up its stock.
- The donor must be due **later than the order that needs the stock**. Stock only moves from a later order to an earlier one, so two orders can never take from each other back and forth.
- The donor must be able to be re-supplied: the plan shows a purchase, production or planned order that covers it, before or after its own date. Show when, and how many days later its
  customer would get it, or that it is in time. Credit-stopped donors are the best (they cannot ship anyway) and come first; then the donor due latest.
- The rep decides and confirms. The donor's customer must be told (draft the update from the donor order).
- Order of the steps: **first de-allocate the order line that holds the stock, then allocate it to the order line that needs it**, check both with a read-back,
  then allocate the donor line again so it keeps what is left. If the receiving line does not get its stock, restore the donor at once.
- If the stock exists but is allocated to other orders (the plan balance is not negative, free stock is less than needed), say so: the order is **"Stock held by other orders"**, and take stock is the first option, not "enough free stock to allocate".
- Risk: automatic allocation can hand freed stock to another order before the receiving line takes it, so always check.

**Tools:** `M3_MMS120MI_DeAllocateOrLne`, `M3_MMS120MI_AllocateOrdLine`.

### Alert the buyer or planner

For a late purchase order or manufacturing order (or when nothing covers the shortage) the rep sends an **e-mail** to the buyer
(the item's buyer) or the planner, with the order, the item, the quantity, the date and the question "reply with the date you can commit". It is a draft
the rep sends: in the dashboard, the Email button opens it in the rep's mail program. The rep never changes those orders and never creates a purchase
order or a planned purchase order. The exact text is shown only when the rep presses the Email button, and can be copied.

**Tools:** none. Nothing is written to M3 (`m3/mail-delivery.md`).

### New confirmed date and customer update

The confirmed date is kept on the order **lines**, not on the order header. Call `UpdCOPlanDates` with `OrderNumber` and `ConfirmedDeliveryDate` only:
- **One date field per call.** Never send both `ConfirmedDeliveryDate` and `ConfirmedDeliveryDateAtDestination` (M3 refuses: "Only one confirmed delivery date should be entered").
- **Leave `UpdateMode` out.** Mode A runs through an autojob that did not run in the test environment, so the job just waited. Without a mode M3 applies the change at once and the answer is empty.
- **`LineNumber` empty** changes all lines; set it to change one line.
- Do not use `OverrideAtp`, `UseAtpDate` or `PlanningDate`: they are not needed.
- `GetUpdateSts` is not needed, and its status ("NotStock") says nothing about whether the date changed.

Always read **every** changed line back, with the line numbers M3 gives (some order types number lines 10, 20, 30, not 1, 2, 3; a few tries over about 8 seconds). It works only for customer order types where the field "Confirmed delivery date" is open for change (OIS014, field selection of the customer order type: blank its entries; then it opens in OIS101/I and the API change goes through too; if the date does not change M3 gives no reason, so name possible directions only: a closed field, connected settings such as the delivery route and its departures, an availability check): on a type where it is not, M3 accepts the call without an error and the date stays (tested: `m3/known-inconsistencies.md`, K26). If any line did not change, say so and name the line,
and do not tell the customer a date M3 does not hold. Then draft the customer update (`customer-updates.md`).

**Tools:** `M3_OIS100MI_UpdCOPlanDates`, `M3_OIS100MI_GetLine`.

If nothing helps: the customer update with the real date.
