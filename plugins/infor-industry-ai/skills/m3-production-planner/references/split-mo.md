# Split an MO so the part a customer needs finishes on time

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_SplitMO`, `M3_PMS100MI_TriggerJob`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstOperations`, `M3_PMS100MI_GetOperation`, `M3_PMS100MI_LstMaterials`, `M3_CPS100MI_SelTotalLoad`, `M3_PMS100MI_SearchMO`

<!-- contents:start -->
**Contents**

- What this does and doesn't do
- 1. When to offer a split (A, B and D must hold; C only ranks it)
- 2. Work out the two quantities
- 3. Will the urgent part make it
- 4. Offer it (advice only)
- Confirm before writing
- 5. Read back and report: Result line
- Next step
- Edge cases
<!-- contents:end -->

Guided write, one call: identify the MO and the customer order it can't serve in time -> work out how much the customer needs
and how much is left over -> check that the urgent part can make the date, with material and capacity -> recommend -> one card
-> `M3_PMS100MI_SplitMO` -> `M3_PMS100MI_TriggerJob` (starts M3's split job) -> find the new MO -> read both back and report.

## What this does and doesn't do

- **The scenario.** An MO makes more than the customer order needs on the date, and its planned finish is after that date. Example:
  MO <number> makes 10 EA and finishes on 2026-10-29, but customer order <number> needs only 5 EA on 2026-10-28. A smaller
  order runs for a shorter time, so **the part the customer needs can finish on time from the same start date**, and the rest
  follows as its own order.
- **One split, two orders.** `M3_PMS100MI_SplitMO` turns one MO into two: the **original keeps its number and the urgent quantity**,
  and a **new MO** gets the leftover. `OrderQuantity` on the call is the quantity of the **new** MO (the leftover), not the urgent
  part. A split never makes three orders; for more, split again, each with its own card.
- **Whole units only.** The tool takes `OrderQuantity` as an integer. If the product's unit allows decimals and the leftover isn't
  a whole number, say so and don't offer the split.
- **The start date doesn't change.** The point is to finish the urgent part sooner from the same start. Nothing in this flow moves a
  start date; the dates M3 gives each order are read back and reported, not chosen.
- **What is sent.** `Facility`, `ManufacturingOrderNumber`, `ProductNumber`, `OperationNumber`, `OrderQuantity` **and two dates**:
  **M3 refuses the call without them** ("Start or finish date must be entered", tested twice, K24; a new-MO finish date alone was not
  enough). What was accepted: **`NewOrderFinishDate`** (the new MO's finish, given by the planner) **and `OriginalStartDate`** (the
  original MO's **current start date**, so its start doesn't move). The other optional fields (times, the original's dates,
  `UseOriginalOrderDates`, priority, reclassification dates, subcontract order, job number) are **not** sent unless the planner asks, and
  then each one goes on the card.
- **The new MO's date is the planner's choice** (in chat, and in the board's Split dialog). Ask once; never pick it. Suggest, with the reason, the **old MO's planned finish date**
  as `NewOrderFinishDate`: the leftover then finishes no later than the whole order would have, and M3 schedules it backwards so it
  doesn't start on top of the urgent part. Say which date you suggest and what the new MO's start becomes after the read-back.
- **Lower-level orders and purchase orders are not split or touched.** Say so afterwards if the MO has any.
- **The board has a Split button too.** It runs the same checks (A, B, D, material and capacity), shows the two quantities and lets the
  planner choose the new MO's finish date. Its dialog is the card: the **Split** click is the yes. The board then re-reads the MO and the
  customer lines, stops without writing if anything changed, makes the same two calls in the same order (`SplitMO`, then `TriggerJob`
  with the job number it returned), waits for M3 and reports the read-back. If M3 returns no job number, the board does not start the job.

## 1. When to offer a split (A, B and D must hold; C only ranks it)

Read the MO (`M3_PMS100MI_Get`: quantity, start and finish date and time, status, reference order, priority), its operations
(`M3_PMS100MI_LstOperations`, `M3_PMS100MI_GetOperation`) and its materials (`M3_PMS100MI_LstMaterials`). Find the customer orders
it serves as `customer-impact.md` step 2 does (by reference order when it is a customer order, otherwise by product and date,
and say which).

| # | Condition | How it is judged |
|---|---|---|
| A | **A customer order is exposed by date** | The MO's planned finish is **after the requested delivery date** of an open customer order line it covers (state the days late). |
| B | **The customer needs less than the MO makes** | The **urgent quantity** is below the MO's ordered quantity (step 2). If it equals or exceeds it, a split can't help. |
| C | **Ranking against Reschedule** (not a gate) | A split that solves the date problem is **ranked above Reschedule**, even when an earlier start or a finite-capacity reschedule could also meet the date: the split keeps the start, moves no component and no work center load, and finishes the urgent part earliest. Say in one line that a reschedule is still available under "Other options". |
| D | **The urgent part would make the date** | Step 3: the estimated finish for the urgent quantity is on or before the requested date, with material and capacity for it. |

Also don't offer it, and say why in one line, when: the MO is completed, **on hold**, or **started** (any operation started or
reported, reported quantity or time above zero, material issued: M3 may refuse, and the order of the work matters); it is
**a sub-assembly** (its reference order is another MO: the parent's need decides, not a customer order); it has **no customer
order** (made to stock: then it isn't a split case); or the planner doesn't own it (scope).

## 2. Work out the two quantities

- **Urgent quantity (U)** = the sum of the open quantities of the customer order lines the MO covers whose requested date is
  **before the MO's planned finish** (the exposed lines), in date order, taken from the MO's quantity: **U = min(that sum, the MO
  quantity)**. Use `OrderedQuantityAltUom` less what is delivered; skip deleted, delivered and completed lines. Name each line.
- **Leftover (R)** = the MO quantity minus U. **R is what goes on the call as `OrderQuantity`.** R must be at least 1.
- **Later demand.** Customer order lines requested on or after the MO's planned finish are not exposed; list them against the
  leftover (the new MO will cover them, in date order) and say whether the new MO's expected finish meets their dates.
- **A quantity the planner names** instead of U wins (for example 6, to leave a buffer); say how it differs from the order and
  recompute step 3 for it.

## 3. Will the urgent part make it

**Finish date for U units (an estimate).** M3 schedules each operation from its hours: use each operation's `RemainingTimeHours` or
`RunTimeHours` times U / the MO quantity, and the work center's working hours per day, chained from the **current start**, in
operation order (`ProductionDays` is M3's own figure for the full quantity: it roughly scales with the quantity). Give the finish
as a date and say **this is an estimate and M3 recalculates it**. Don't state a finish time you did not compute.

**Material for U.** Each material line splits in proportion (U / MO quantity). Check the shortage logic of
`material-shortage-check.md` for U units on each component's reservation date (the urgent part needs **less** than before, so a
component that was just short may now be covered). A component that stays short for U: the split won't make the date; say which.

**Capacity.** The same hours are split between two orders, so the total load is unchanged, but the **leftover's** load lands
where M3 puts it. Read the load (`M3_CPS100MI_SelTotalLoad`, machine and labor kept apart, `capacity-types.md`) for the work
centers of the MO over the weeks the two orders may use, and flag a week that would go over its rating. Never state where the
leftover lands before the read-back: say "dates for the leftover are set by M3".

Confidence: **High** when the estimate has margin (the finish is at least a working day before the requested date), the
components are covered and capacity is under the rating; **Medium** when the margin is under a day or a component depends on
an unconfirmed supply; **Low** when part of the data wasn't read.

## 4. Offer it (advice only)

> **Option: split MO <number> (<product>): <U> for customer order <n> on <date>, <R> as a new MO**
> Why: the MO makes <Q> and finishes <date> (<n> days after customer order <n> is requested for <date>); the order needs <U>.
> Estimate: <U> units from the same start <date> finish about <date> (<on time | still <n> days late>); M3 recalculates it.
> Material: <covered | <item> short <qty> on <date>>. Capacity: <under the rating | <work center> week <w> over>.
> Later demand: <none | <order, date> goes to the new MO>.
> Confidence: <High | Medium | Low>. What would change it: <what is unconfirmed, a week not read>.
> Cost: one more MO to follow; the leftover <R> gets dates from M3 and may finish later than <Q> would have.

## Confirm before writing

Re-read first (write protocol step 3): the MO is open, unchanged, nothing reported or started, still exposed, and the customer
order quantity is the same. If anything differs, don't show the card: say what changed.

> **Split MO <number>**
> <product> (<name>), facility <f>, quantity <Q> EA, start <date time>, finish <date time>, status <status>
> Split at operation <first operation> (<description>): the **original MO <number> keeps <U> EA**, and a **new MO is created with <R> EA**.
> Why: customer order <n> (<customer>, <U> EA) is requested for <date>; this MO finishes <date>. The urgent part is estimated to
> finish about <date> from the same start (estimate; M3 recalculates it).
> New MO <R> EA: finish date **<the date you gave>** (M3 schedules its start). The original's start stays <date> (sent only because M3
> requires it); M3 sets the original's finish and both priorities. I send only the operation, the quantity <R>, that finish date and the
> original's current start date. Nothing else changes: no
> start date of the original, no other MOs, no purchase or customer orders; lower-level orders (<none | <list>>) are not split.
> I can't undo this from here: joining the two orders again is done in M3.
> If you reply yes I will split the order (`M3_PMS100MI_SplitMO`) and then start M3's split job (`M3_PMS100MI_TriggerJob`).
> Reply **yes** to split.

Only after an explicit yes, **two calls in this order**:

1. **Call `M3_PMS100MI_SplitMO` once** with `{ Facility, ManufacturingOrderNumber, ProductNumber,
OperationNumber: <the MO's first operation>, OrderQuantity: <R>, NewOrderFinishDate: <the date the planner gave>,
OriginalStartDate: <the MO's current start date, as just read> }` and nothing else. The response returns the **new MO number and a batch job
number** at once. This call only registers the split: the original reads "...-ChangeInProgress" and the new MO does not exist
("Record does not exist") until the job has run. The split operation is the first operation of an unreported MO (every unit sits at it);
if the planner wants another, ask for it and say why it matters (K24). On an error, report it plainly and stop: no `TriggerJob`, no retry;
read both orders first to see whether it saved.
2. **Call `M3_PMS100MI_TriggerJob` once**, only when the first call succeeded, with `{ TransactionName: "SplitMO", JobNumber: <the batch job
number SplitMO returned> }` and nothing else (in M3's own field names: TRXN and BJNO). It starts the split job for that job number. Never
use another transaction name or a job number you didn't get from this split. (Before this call existed in the connector, the job was
never started and the MO stayed in ChangeInProgress: K24.)

## 5. Read back and report

1. **Find the new MO.** `SplitMO` returned its number (it exists only once the job has run); use it. Otherwise `M3_PMS100MI_SearchMO` for the planner's MOs of the same
   product (`Responsible_ExactSearch`, facility, warehouse) and take the one that wasn't in the list before the split, with
   quantity R. If more than one fits, list them and ask; never pick.
2. **Wait** while either order reads "...-ChangeInProgress" (read every 20 to 30 seconds; the split job can take minutes: keep reading for
   about 5 minutes, then stop and tell the planner the job number, the time of the calls, and that the job may be queued or stuck in M3; don't call `TriggerJob` again on your own), then read both
   (`M3_PMS100MI_Get`): a small table, one row per order: number, quantity, status, start and finish date and time, priority,
   reference order. ✅ when the original now holds U and the new MO holds R and nothing else changed unexpectedly; ⚠️ for a start
   date that moved, a missing reference order, or a quantity that doesn't add up (U + R must equal Q).
3. **The date test.** Is the original's planned finish now on or before the customer order's requested date? ✅ on time /
   ⚠️ <n> days late / ❌ unchanged. If **M3 left the original's finish where it was** (the dates are copied from the old order),
   say so plainly: the split alone didn't shorten it, and offer the reschedule of the original on its current start date and
   current quantity, with infinite capacity planning, as a **separate action with its own card** (`reschedule-mo.md`), so that M3
   recalculates the smaller order.
4. **Materials and operations of both:** `M3_PMS100MI_LstMaterials` and `M3_PMS100MI_LstOperations` for each (quantities add up
   to the original's; operation hours add up). Say what is short for either.
5. **Capacity:** `M3_CPS100MI_SelTotalLoad` for the MO's work centers over the weeks both use: any week over its rating, machine
   and labor apart. Figures may lag; give the read time.
6. **The new MO's customer link:** which order it covers now (the later demand, if any) or "none: made to stock".

### Result line

```
MO <orig>: <Q> -> <U> EA; finish <old> -> <new> (<on time for order <n> due <date> | <n> days late>)
New MO <new>: <R> EA; start <d>, finish <d>; covers <order | none>
Material <ok | short <item>>. Capacity <ok | <work center> week <w> over>. Lower levels: <none | not split>
```

## Next step

- Offering order: when the split solves the date problem it comes before "Want me to reschedule MO <orig>?"; the reschedule stays
  available as the alternative.
- The original's finish didn't move, or is still late: "Want me to reschedule MO <orig> on its current start date so M3
  recalculates it for <U>?" (`reschedule-mo.md`, its own card).
- "Want the sales rep told that order <n> is now on time (or still late)?" (`warn-sales-rep.md`).
- The leftover finishes later than the old order did: say so; "Want me to check MO <new> against the later orders?"
  (`material-shortage-check.md`).

## Edge cases

- **Urgent quantity equals the MO quantity** - no split: "The customer order needs all <Q>."
- **Several exposed lines** - U is their sum in date order; show each line; a split at the first date only if the planner picks it.
- **The customer order is only partly open** (some delivered) - use the open quantity; say so.
- **Decimal unit, non-integer leftover** - not offered.
- **MO reported or started** - not offered; say what was reported.
- **Component short even for U** - say which; the split won't help; offer the other options (`material-shortage-check.md`).
- **M3 refuses the split** - report its message; nothing was changed unless the read-back says so; don't try another route or tool.
- **M3 sets dates you didn't expect** (for example the original's start moved) - report both orders' dates plainly with before and
  after; don't move anything yourself.
- **The new MO number can't be found** - say so; give the product, quantity R and the time; ask the planner to check in M3.
- **MO changed since the options were shown** - don't write; re-read and re-offer.
- **The MO shows "...-ChangeInProgress" before a write** - don't write. Read again after 30 to 45 seconds; if it still shows it after
  about two minutes, another M3 program the planner has open can hold the MO: ask them to close it.
- **Several matches** (MO, product) - list and ask; never pick.
- **Can't see it / not permitted** - report; don't retry.
- **`TriggerJob` fails or is refused after `SplitMO` succeeded** - the MO stays "...-ChangeInProgress" and the new MO doesn't exist. Say so, with the new MO number, the job number and the time; offer **one retry of `TriggerJob` only** as its own card and yes; never call `SplitMO` again for the same split.
- **A tool is missing** - say which (`M3_PMS100MI_SplitMO` or `M3_PMS100MI_TriggerJob`) and that the split isn't offered; if `TriggerJob` is the one missing, don't call `SplitMO` at all (it would leave the MO in ChangeInProgress); don't use another write tool.
