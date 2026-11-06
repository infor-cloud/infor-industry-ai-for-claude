# Buyer impact check (M3 material plan)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MMS080MI_LstMtPlByItmWhs`, `M3_OIS100MI_GetOrderHead`, `M3_CRS610MI_GetBasicData_CustomerName`, `M3_PMS100MI_Get`, `M3_MMS200MI_GetItmWhsBasic`, `M3_OIS100MI_SearchLine_LimitedOutput`, `M3_PMS100MI_SearchMaterial`, `M3_MMS100MI_LstLines`

<!-- contents:start -->
**Contents**

- What this does
- 1. Find the orders
- Show it
<!-- contents:end -->

## What this does

Given a **delayed PO line**, an **overdue planned PO** or any PO line, finds the orders that depend on it
(customer orders, manufacturing order material, distribution orders, forecasts), with their need
dates, slack and short quantity. It is used by `morning-view.md`, `needed-earlier.md` and
`delayed-po.md`.

**Input:** item, warehouse, and the order number (and line) of the PO or the planned order number.

For each item, summarise: number of affected orders, **earliest need date**, total short quantity,
whether anything is actually short, and how many days until the first order is affected. For each affected
order keep: category, number, planning (need) date, quantity, the item as `<item number> · <item name>` and, when cheap to get, value. For a customer order that is
late or will be late, also keep the customer name (step 1, item 6c). **Slack** = need date minus the planned arrival date of
the supply (the new date if the supplier gave one).

If the item's own record is not in the plan, say that the impact could not be checked from the plan.

## 1. Find the orders

**Primary method: the material plan.** `M3_MMS080MI_LstMtPlByItmWhs` (item and warehouse of the PO line) lists every
planned or actual movement for that item in that warehouse, **all order types in one list**. Its fields are in
`m3/material-plan.md`. If it returns nothing for the item and warehouse, say so (an empty answer is not an answer
about supply) and use the fallback below.

How to find what the late PO affects:

1. Call the tool for the PO line's item and warehouse. Sort the records by **planning date only**. Ignore the time of day
   (`TransactionTime`) everywhere in the impact analysis: compare dates, never hours. Supply and demand on the same date
   count as the same day, so supply arriving on a date covers demand with that date. `ProjectedOnHandBalance` follows M3's
   own time order, so on a date with several records, add up all supply and demand of that date before you call anything short.
2. Find the PO's own record (`OrderCategory` = `PurchaseOrder`, the PO number and line). Note its
   quantity and planning date. The planning date is when M3 expects the goods. If its action message
   is `Delayed`, M3 agrees the PO is late.
3. **Starting stock** = the first record's `ProjectedOnHandBalance` minus its `TransactionQuantity`.
4. Take the PO quantity **out** of the projected balance from the PO's planning date onwards. Walk
   forward in date order. Every demand record (negative quantity: customer order, manufacturing order
   material, outgoing distribution order, forecast) where the balance, or ATP, falls **below zero**
   without the PO depends on it. These are the affected transactions.
5. Compare each affected record's date with the PO's new arrival date (or with today if there is no
   new date). Slack = need date minus arrival date. Negative slack means the order will be late.
6. Name the order category in plain words (customer order, distribution order, manufacturing order,
   forecast) and list the order numbers. Forecast records are not firm orders: show them separately.
6b. **Coverage and the real supply.** State how much of the total short quantity this PO covers. If the
   starting stock is 0 and the PO is small against the demand, every order is short with or without it:
   say that, and name any larger open supply in the plan (for example another PO that is stopped at
   status 12 or planned much later) as the lever that matters. Flag demand records dated before today.
6c. **Customer of a late customer order.** For each customer order that is already late (need date before today) or that
   the new date makes late, read the order header with `M3_OIS100MI_GetOrderHead` (it returns the customer number), then
   the name with `M3_CRS610MI_GetBasicData_CustomerName`, once per customer. Show the name next to the order number. If no
   name comes back, write "customer name not available". In the morning view, do this only for the items shown in detail.
6d. **Customer demand behind an affected manufacturing order.** For each affected MO (a demand record whose category is a
   manufacturing order, step 4), read it with `M3_PMS100MI_Get` (facility, MO number, and the product from the record's
   `ReferenceText`). Keep the MO's planned finish date, quantity, warehouse and reference order. Read the product's name with `M3_MMS200MI_GetItmWhsBasic` (product and the MO's warehouse), in the same batch as the MO, unless an earlier result already has it.
   - **Reference order is a customer order:** that order is affected. Treat it as in 6c.
   - **No reference order (blank or "use varies"):** the MO is made to stock, but customers may still depend on its output.
     **Do not stop here, and never write "no customer to warn" because the link is missing.** Read the material plan of
     the MO's **finished product** in the MO's warehouse (`M3_MMS080MI_LstMtPlByItmWhs`). Take the MO's quantity out of
     the projected balance from the MO's **current planned finish date** and walk forward as in steps 3 to 5. A customer
     order record whose balance falls below zero without that MO is **possibly affected**. **List these orders with their
     need dates only: do not estimate a new finish date for the MO, and do not give a slack for them.**
   - Run this only for MOs the delay actually affects (negative slack in step 5). If a covered or swapped MO loses nothing,
     leave it out.
   - Label every order found this way "possible, matched by product and date; M3 has no order link". Show at most 10
     orders, earliest first, and state the cap. Name the customer as in 6c.
   - If the plan is empty, use `M3_OIS100MI_SearchLine_LimitedOutput` with `ItemNumber_ExactSearch` = the finished product,
     open lines only (the fallback below).
   - If none are found, say "No customer orders draw on <product> after <date>" and nothing more.
7. Demand that stays above zero without the PO is covered by stock and is **not** affected. Say so, and
   say how much of the projected balance the late PO accounts for.
8. Other records with `ActionMessage` = `Delayed` are late too (for example incoming distribution
   orders). Mention them, since they also affect the balance.
9. Records with planning dates far in the past are stale. Say so instead of treating them as urgent.

Read the category and status of each record with `m3/status-codes.md` ("Material plan"); statuses on PO headers and
lines are a different list. Details per affected order (customer order, MO, DO), and other ways to confirm a link to the
PO (supply chain, pre-allocation, reference order), are in `m3/material-plan.md`.

**Fallback when the material plan is empty:**

- `M3_OIS100MI_SearchLine_LimitedOutput`: customer order lines. **Filter hard.** Searched on the item
  alone it returns the whole history (invoiced and completed lines too). Filter on
  `ItemNumber_ExactSearch` and, when the tool accepts it, on open order status; otherwise filter the
  result yourself and keep only open lines. Order status comes as a name with a code:
  `Allocated (33)`, `PickingList (44)`, `Invoiced (77)`, `FlaggedAsComp (99)`; invoiced (77) and
  completed (99) lines are closed. A customer order line is **short** only when
  `RemainingQuantityBasicUom` is above 0 (not yet allocated). Fully allocated lines are covered by
  stock and are not affected by the delay.
- `M3_PMS100MI_SearchMaterial` / `LstByRORN`: manufacturing orders that need the item.
- `M3_MMS100MI_LstLines`: distribution orders.
- Say in the answer that the material plan was empty and that the list comes from the fallback,
  which is less complete (it does not show forecasts or the projected balance).

Present the overall impact in three sections, always in this order: Manufacturing orders (MO), Customer orders (CO),
Distribution orders (DO), one table each, as set out in `delayed-po.md` step 2. Columns: status icon, order (a customer
order with its customer name), need date, short quantity, value (customer orders only, when known), slack (need date
minus new arrival date). Forecasts: one line below the sections.

## Show it

Present the result as the three sections above (MO, CO, DO), with a status icon per order (❌ already past or short, ⚠️ tight slack, ✅ covered), after one line with the coverage sentence. Follow "Answer layout" in `SKILL.md`: every item is shown as `<item number> · <item name>`. In the morning view the result stays one row per item (the "Affects" column of `morning-view.md`); the three sections are for an answer about one PO line or one item.
