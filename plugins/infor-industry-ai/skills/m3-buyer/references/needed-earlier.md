# Buyer: POs needed earlier (reschedule in)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MMS080MI_LstMtPlByItmWhs`

## What this finds

A PO line can be on time and still be a problem: after the order was placed, more demand for the
item arrived and the goods are now needed earlier. Such a line is **not** found by the past-due search
in `morning-view.md`, because its date has not passed. M3 flags it in the material plan: the PO record (category
`PurchaseOrder`, 251) carries the action message **`RescheduleIn`** (B1, reschedule in released
order) and an **`AlternatePlanningDate`** that is earlier than its `PlanningDate`. The PO line
search has no such field, so the material plan is the only place to find them.

## 1. How to find them

1. Take the buyer's open PO lines (status below 50, in any warehouse) that are not already in the
   delayed list. Collect the distinct item and warehouse pairs.
2. Call `M3_MMS080MI_LstMtPlByItmWhs` for each pair (reuse any result from the impact check). Check at
   most 20 pairs, taking the earliest planning dates and highest line values first, and say how many
   were checked and how many were not.
3. In each result, keep the records with `OrderCategory` = `PurchaseOrder`, the buyer's own PO number,
   and **`ActionMessage` = `RescheduleIn` or `AlternatePlanningDate` earlier than `PlanningDate`**
   (either one; use both as a check). The action message name seen in the test is `RescheduleIn`.
   Ignore the planned PO records here: they are handled in the planned PO list.
4. For each such PO line, compute:
   - **Days earlier needed** = `PlanningDate` minus `AlternatePlanningDate`.
   - **Orders waiting for it**: the demand records (negative quantity: customer orders,
     manufacturing order material, outgoing distribution orders, forecasts) dated **before the PO's
     `PlanningDate`** while the projected balance is below zero. These are the orders that cannot be
     supplied until the PO arrives (or until other supply does; say if a planned PO also supplies the
     item).
   - **Earliest need date** among them, **total short quantity** (the lowest projected balance before
     the PO record), and **slack** = earliest need date minus the PO's `PlanningDate` (negative:
     how many days late the first order will be).
5. Treat a need date that is already in the past as **already late**, and say so.

**Other supply after the PO.** Look at the supply records (planned POs, other POs) dated after the
PO's `PlanningDate` for the same item and warehouse, and at the projected balance right after the PO:

- If the balance is **still below zero after the PO**, the PO alone does not cover the demand. Say
  which later supply closes the gap and when (for example "the shortage stays at 920 until two
  planned POs arrive on <date>"), and that the planned POs must be released for that to happen.
- If the balance after the PO is **far above zero** and covers all later demand, later planned POs for
  the same item add little. Say so as an observation, and suggest the buyer checks whether they are
  needed.

What to suggest: ask the supplier to deliver earlier (offer a drafted message), or go to `delayed-po.md`
for the options (stock elsewhere, another supplier, and so on). Say if the PO is blocked or not
yet confirmed, because then the first step is to get it sent or approved (for example a
PO stopped for authorization).

This check runs only for **open PO lines the buyer owns**. It does not replace the delayed list.
Show both lists, and rank them together .

### Where the fields come from

The material plan record fields are in `m3/material-plan.md`, the category and status table in
`m3/status-codes.md`, and the walk-forward in `impact-check.md`. This skill uses them but restricts the walk to demand dated before the PO's
`PlanningDate`.

## 2. Confirmations and blocked POs

There is no waiting limit for confirmations (see `morning-view.md`): an unconfirmed sent line that is also on the
"needed earlier" list gets the action **ask for earlier delivery now**, with the reason.

- **Needed earlier, unconfirmed (status 20):** say: **call the supplier now** and ask for earlier delivery (offer a drafted
  message, or "call and confirm it here"). Say why: "orders have been waiting since <first need date>".
- **Blocked first.** If the PO is also blocked (status 11 to 14), the first action is to clear the block (remove the stop,
  complete the account string and so on), because the supplier has not received the order yet. Add the request for earlier
  delivery to send once it is released.
- **Already confirmed (status 31 to 35) but still needed earlier:** say "confirmed <ConfirmedDeliveryDate>, M3 still wants it
  from <alternate date>". The action is to ask the supplier for an **earlier date**; if they agree, record it with a
  re-confirmation (`po-actions.md`).

## Show it

List the lines in a table with a status icon (⚠️ unconfirmed and needed earlier, ❌ blocked, ⚠️ already confirmed but still wanted earlier: ask for an earlier date). Follow "Answer layout" in `SKILL.md`.
