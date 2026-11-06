# Reschedule one manufacturing order (a date and/or the quantity)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_Reschedule`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstByRORN`, `M3_PMS100MI_LstMaterials`, `M3_PMS100MI_SearchMO`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`

<!-- contents:start -->
**Contents**

- What this does and doesn't do
- 1. Identify the MO
- 2. Snapshot the lower levels
- 3. Recommend a date or a quantity (advice only)
- Confirm before writing: When the planner reschedules from the dashboard board
- 4. Read back and report on the lower levels
- Show it: Result line
- Next step
- Edge cases
<!-- contents:end -->

Guided write: identify one MO -> read it, its components and its lower-level orders -> recommend a
realistic date (and a quantity the components allow) -> confirmation card -> one call -> read back and report what
happened to the lower levels.

## What this does and doesn't do

- **Does:** change one MO in one of three ways, each explicit: a new **start date** or a new **finish date** (**one,
  never both**: M3 refuses a reschedule with both dates, "Either start or finish date should be entered, not both"), a new
  **ordered quantity**, or a date **and** a quantity together. M3 then recalculates the schedule with infinite (default)
  or finite capacity planning (`M3_PMS100MI_Reschedule`). At least one thing must change.
  **One exception:** right after a material swap or a capacity swap, `swap-material.md` or `swap-capacity.md` reschedules the MO with its current quantity and its
  **current start date** (no date changes), so that M3 recalculates it with the new component. That call runs only inside
  that flow, on the same yes as the swap.
- **Quantity is allowed, but only when the planner asks for it.** The tool always needs an ordered quantity, so when the
  quantity isn't changing, send the order's **current** quantity, read from M3 just before. A changed quantity changes the
  material every component line needs, so check the components against the new quantity before the card (step 3) and say
  what changes. Refuse a quantity that isn't a positive number, or that is below the quantity already reported or
  received.
- **Dates only, no times.** Start and finish times and the priority aren't exposed. Say so if asked.
- **One date, never two.** M3 works out the other date from the routing, and the read-back shows what it did. If the
  user (or a board request) gives both a start and a finish, don't send both and don't pick one yourself: say M3
  takes only one, show what each choice would give (a start on <date> finishes about <date>; a finish on <date>
  starts about <date>), and ask which to fix. Sending a date the planner didn't confirm is not allowed.
- **Lower-level orders are not rescheduled by this skill**, and that is accepted. But a reschedule at the top
  can still move lower-level orders (M3 can carry the change down), and a changed quantity changes what they are asked to
  supply, so this skill always checks them afterwards and tells the user (step 4).
- **Scope:** one MO at a time. Refuse "reschedule all at-risk orders" and offer them one after another, each
  with its own card. Purchase orders are never changed here; moving this order later doesn't move when its
  components arrive.

## 1. Identify the MO

You need facility, MO number and product number. Take them from an `at-risk-orders.md` or
`material-shortage-check.md` result in this conversation, or from the user; never guess. Read it:
`M3_PMS100MI_Get` `{ Facility, ManufacturingOrderNumber, ProductNumber }` -> status, start and finish
date and time, ordered and received quantity (keep it: it is what you send back when the quantity isn't changing, and
the "before" when it is), unit, warehouse. Stop and say so if the order is completed; if quantity has been reported or
received, a quantity change can't go below it.

## 2. Snapshot the lower levels

Before changing anything, find the orders below this MO and note their dates, so you can compare afterwards:
- `M3_PMS100MI_LstByRORN` `{ ReferenceOrderCategory: "ManufactOrder", ReferenceOrderNumber: <this MO>,
  ReferenceOrderLine: 0 }` -> manufacturing orders linked to this one as their reference (created from the
  bill-of-material explosion).
- Components with acquisition code Manufacturing (from `M3_PMS100MI_LstMaterials`): the MOs that make them,
  taken from the MOs already in this conversation, or from `M3_PMS100MI_SearchMO` `{ Facility_ExactSearch,
  Warehouse_ExactSearch, Responsible_ExactSearch: <the MO's responsible user>, WorkOrderStatus_LessThan:
  "OrderCompleted", SortBy: "PlannedFinishDate" }`, matching the product.

For each, `M3_PMS100MI_Get` -> start and finish date, quantity, status. If you find none, say so (it may be that
the order has no semi-finished components, or that M3 doesn't link them as a reference); don't invent any.

## 3. Recommend a date or a quantity (advice only)

The planner decides whether, when and how many; this skill only recommends. Never reschedule because a
recommendation exists, and never present a recommendation as decided. Offer it as:

> **Recommended: start <date>.** (or **finish <date>**, see below). One date only: M3 works out the other.
> Basis: <the limiting component and the date it is confirmed, or the capacity week that is free>.
> Confidence: <High when the supply dates are confirmed and the lower-level order is on track; Medium when a
> date is only requested; Low when data is missing>.
> What would change it: <the unconfirmed PO, the blocked lower-level order, the capacity not read>.

How to work it out:
- Read the components if you don't have them (`M3_PMS100MI_LstMaterials`; for each component
  `M3_MMS200MI_GetItmWhsBal_Subname`, and `M3_PPS200MI_SearchLine` for purchased items).
- **Material short, supply later:** the earliest start = the day after the last **confirmed** supply of the
  limiting component (unconfirmed supply doesn't count; say so and lower the confidence); if that day is a Saturday or Sunday, use the next Monday. Recommend that **one** start date only; M3
  then works out the finish (you may say what finish to expect, as an estimate, never as a second recommendation).
  Recommend a **finish** date instead only when a date must be met (a customer's requested date or a need date): then
  recommend the latest finish that still meets it. If a lower-level order supplies the component, use its finish
  date; if it is itself late or blocked, say the move doesn't help and name the blocker.
- **Capacity short:** recommend a finite-capacity recalculation so M3 places the order where capacity is free;
  the new dates are known only after the read-back. When that would miss a date, offer moving the operation to another
  resource with room (`swap-capacity.md`). When the customer needs less than the MO makes and the start can't move earlier,
  offer splitting the MO (`split-mo.md`).
- **A quantity the components allow.** When material is short and the planner wants to build what can be made, work out
  the most the MO can make: for each component, available inventory plus **confirmed** supply by the start date, divided
  by the quantity needed per unit; the smallest of those is the answer, with the limiting component named. If it is
  zero, say reducing the quantity doesn't help. When the planner gives a quantity, check it the same way: say if the
  components don't cover it, and what a larger or smaller quantity changes (each component line's requirement), and if
  a customer order or a parent MO needs more than the new quantity.
- **No reliable data** (nothing confirmed, supply not traceable): say there is not enough to recommend a date,
  and what is missing (for example a confirmed supplier date), rather than guessing.
- **The user's own date or quantity:** use it, and say if it is before what the components allow or if the new finish is
  after a date a customer or the planner needs.
Reject a date in the past, a finish before the start, or a quantity that is zero, negative or below what is already
reported, before asking for a yes.

## Confirm before writing

> **Reschedule MO <number>**
> <product> - facility <f>
> <Start | Finish> <old> -> <new> (one date: M3 works out the other, expected about <date>) or "date unchanged";
> quantity <old> -> <new> <unit> or "quantity <q> (unchanged)"; capacity planning <infinite | finite>.
> M3 recalculates the schedule and the times, and raises the order's priority to high. A changed quantity changes the
> material each component line needs (<what changes, from step 3>). Lower-level orders are not rescheduled by me; I'll
> check them afterwards and tell you if M3 moved any. Purchase orders are not changed. I can't undo this from here.
> Reply **yes** to reschedule.

Only after an explicit yes to this card, call `M3_PMS100MI_Reschedule` **once** with `{ Facility,
ManufacturingOrderNumber, ProductNumber, OrderedQuantityAltUom: <the new quantity, or the current quantity from step 1 when it isn't changing>,
FiniteCapacityPlanning: <true or false>, StartDate: <YYYY-MM-DD, only if changing>, PlannedFinishDate:
<YYYY-MM-DD, only if changing> }`. Leave a date field out when it isn't changing. Use infinite planning (`false`)
unless the user asks for finite or the cause is capacity. On an error, report it plainly and stop; don't retry
(check with the read-back whether it happened). A yes to an earlier question never covers this one.

### When the planner reschedules from the dashboard board

The board's reschedule dialog re-reads the MO, shows the chosen date (one date, never two) and the quantity, and asks for a Confirm for that MO only: one MO, one call. Before the change it reads the orders below the MO (step 2); after it, it reads the MO back
while M3 reports "...-ChangeInProgress" and reports before and after for the MO and the lower levels (step 4). It changes no lower-level order, and it does not save requests for chat to run. In chat, run this whole file.

## 4. Read back and report on the lower levels

1. `M3_PMS100MI_Get` on the MO again. M3 processes the change in the background: while the status reads
   "...-ChangeInProgress" the old dates are still shown, so wait a moment and read again (up to four reads, a few
   seconds apart) before concluding anything. In tests it took under a minute. Show before and after for
   start and finish **date and time**, the **priority**, the status and the **quantity** (it must equal what the card said:
   the new quantity, or unchanged).
   Report what M3 did beyond the dates: it recalculates the times, and it raises the order priority to high on a
   reschedule (the owner wants this; it is expected, not a fault). Show the new times and the priority as part of
   the result; don't change either.
   If the quantity differs from the card, say so prominently and stop; don't try to fix it. After a quantity change, also
   read `M3_PMS100MI_LstMaterials` for the MO and show the new needed quantity of the limiting component.
   If nothing changed after the reads and the status is no longer ChangeInProgress, say so plainly; don't claim
   success. If it is still ChangeInProgress, say the change is still being processed and when to re-check.
2. `M3_PMS100MI_Get` on each lower-level order from step 2 and compare with its snapshot. Report, in one short
   block:
   - **Affected:** "Lower-level MO <n> (<product>) moved: start <old> -> <new>, finish <old> -> <new>."
   - **Unchanged:** "Lower-level MO <n> (<product>) is unchanged: finishes <date>."
   - **Conflict:** if a lower-level order now finishes after this MO's new start (or it didn't move and the new
     start is earlier than it finishes), say so: this order can't start on its new date.
   - **Quantity:** if the quantity changed, say what the lower-level orders are now asked to supply (the component line of
     the parent) against what they make, and flag a shortfall or a surplus.
   - **None found / not checked:** say which you couldn't check and why.
   End with whether the lower levels need attention, and offer `at-risk-orders.md` or `material-shortage-check.md`
   to re-check the chain. Don't change any lower-level order.
3. Say whether the new finish date meets the need (the component or customer date).

## Show it

Chat only: the card, then the before-and-after and the lower-level report.

### Result line

```
MO <n> rescheduled: start <old> -> <new>; finish <old> -> <new>; priority <old> -> high; qty <old> -> <new> (or unchanged)
Lower levels: <MO a> moved <old>-<new> | <MO b> unchanged | none found
```

## Next step

"Want the full check on the new dates?" (`material-shortage-check.md`); "Which customers does this affect?"
(`customer-impact.md`); "Want to tell the buyer about the late order?" (`inform-buyer-of-late-order.md`).

## Edge cases

- **Nothing found** - "I can't find MO <n> in <facility>." Check the product number.
- **Several matches** - list and ask; never pick.
- **Can't see it / not permitted** - report; don't retry; don't try another route.
- **Quantity requested** - allowed: check it (step 3), show it on the card, send it. A quantity below what is already
  reported or received, or not above zero, is refused with the reason.
- **Quantity only, no date** - allowed: M3 recalculates the schedule with the new quantity; say the dates may move, and
  read back.
- **Time or priority requested** - say they aren't exposed; offer the date change.
- **Past date, or finish before start** - say so and ask for a valid one.
