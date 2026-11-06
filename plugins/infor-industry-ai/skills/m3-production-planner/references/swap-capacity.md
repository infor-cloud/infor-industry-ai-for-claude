# Swap an operation's work center resource (machine or labor capacity)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_UpdOperation`, `M3_PMS100MI_Reschedule`, `M3_PDS010MI_LstRelPerWC`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstOperations`, `M3_PMS100MI_GetOperation`, `M3_PDS010MI_Get`, `M3_CPS100MI_SelTotalLoad`

<!-- contents:start -->
**Contents**

- What this does and doesn't do
- 1. When to offer a swap (all four must hold)
- 2. Find the related resources
- 3. Is there capacity on the alternative
- 4. Offer it (advice only)
- Confirm before writing
- 5. Read back and report: Result line
- Next step
- Edge cases
<!-- contents:end -->

Guided write, two calls on one card and one yes: identify the operation -> confirm its resource is over capacity and
that nothing else fixes it -> find the other type 6 resources under the same main work center -> check their free
capacity -> recommend -> one card -> change the operation's work center -> read it back -> reschedule the MO on its
**current start date** (no date change) -> read back and report. **One yes covers both calls. Do not mention the reschedule to the planner (not in the card, the report or the next
step): it is part of the swap. Say something only if it fails (step 4).**

## What this does and doesn't do

- **Does:** moves **one operation of one MO** from its work center resource (**resource type 6**) to **another type 6
  resource that hangs under the same main work center (resource type 1)** and has room for it
  (`M3_PMS100MI_UpdOperation`), then **reschedules that MO on its current start date, so no date changes**, so that M3
  recalculates it on the new resource (`M3_PMS100MI_Reschedule`).
- **Machine or labor, never across.** The operation has a capacity type (`MachineHours` = machine capacity, `ManHours` =
  labor capacity; `capacity-types.md`). The alternative must have the **same capacity type**. Machine load is compared
  with machine load, and labor load with labor load: never mixed.
- **Only a related resource.** The alternative must be a type 6 resource that `M3_PDS010MI_LstRelPerWC` lists under the
  same main work center as the original. Never swap to a work center the planner names that isn't listed there: say so,
  and point to the routing or the work center setup in M3.
- **Only when the swap is the fix.** It is offered when the original resource is over its capacity for this operation and
  rescheduling doesn't help (step 1). When a finite-capacity reschedule meets every date, recommend that and offer the
  swap only if the planner asks for it.
- **Nothing but the work center changes.** Run time, setup time, machines, workers, quantity and every date stay as they
  are. The reschedule sends the MO's **current ordered quantity** and its **current start date** (M3 refuses a reschedule
  without a date); M3 itself may recalculate the times and the finish.
- **One operation at a time.** The same overload on several MOs is offered one after another, each with its own check and
  card: the first swap uses up the alternative's room, so the next check starts again from the load.
- **Calendars, shift patterns and capacity ratings are never changed here.** When no related resource has room, a temporary double shift on the work center is its own flow with its own card (`shift-pattern.md`).
- **From a dashboard.** A Confirm click on a board may run this, as in chat: the board shows the same card, re-reads the operation and the resource first, makes the same two calls in the same order and reads the result back. A board never runs it without that Confirm click.

## 1. When to offer a swap (all four must hold)

Read the MO (`M3_PMS100MI_Get`) and its operations (`M3_PMS100MI_LstOperations`), then the operation
(`M3_PMS100MI_GetOperation`): work center, **`CapacityType`**, `RemainingTimeHours` (the hours the operation still needs),
start and finish date, status. Read the work center (`M3_PDS010MI_Get` `{ Facility, WorkCenter }`): its **`ResourceType`**
and **`SuperiorWorkCenter`**.

| # | Condition | How it is judged |
|---|---|---|
| A | **The original is a type 6 resource** | `ResourceType` is `W/cResource` (type 6; if M3 returns the code, 6). Its `SuperiorWorkCenter` is the main work center, which `M3_PDS010MI_Get` shows as `Operation` (type 1). If the operation's work center is a type 1 or has no superior, say so and stop: this flow doesn't apply. |
| B | **Not enough capacity on the original** | `M3_CPS100MI_SelTotalLoad` `{ Facility, WorkCenter, FromDate: <operation start>, ToDate: <operation finish> }`: in at least one week the operation spans, the load of the operation's capacity type (machine time for `MachineHours`, man time for `ManHours`; manufacturing orders and planned orders, category A and B, as `capacity-types.md` says) is **above `CapacityPerUnitAndShift`**. Name the week, the load and the rating. Under the rating in every week: not a swap case; say so. |
| C | **Rescheduling the MO does not help** | Use the logic of `reschedule-mo.md` (capacity short). It does **not** help when (i) no week on the original resource, up to the date the MO must finish by, has free capacity for the operation's remaining hours; or (ii) moving the operation to the first week that has room makes the MO finish after its due date or after the requested date of a customer order it covers; or (iii) a lower-level order feeding the operation is itself late or blocked. If a finite-capacity reschedule would meet every date, this is not a swap case: recommend the reschedule. |
| D | **An alternative has room** | At least one related type 6 resource of the same capacity type with enough free capacity (steps 2 and 3). |

Also don't offer it, and say why in one line, when: the MO is completed or on hold; the operation is **started or later**
(status `Started`, `PartlyReported`, `Completed` or `Closed`), or it has reported quantity or time (`ManufacturedQuantity`,
`UsedMachineRunTime`, `UsedLaborRunTime` above zero); the operation is a **parallel or split operation**
(`AppPrimaryOperationNumber` differs from `OperationNumber`, or it has a split method); the capacity type is neither
`MachineHours` nor `ManHours`. M3 validates the change strictly: let it decide the rest and report its error plainly.

## 2. Find the related resources

1. Main work center: `SuperiorWorkCenter` from the original (condition A).
2. `M3_PDS010MI_LstRelPerWC` `{ Facility, AppWorkCenter: <the main work center> }` -> the resources related to it, with
   their description, scheduling priority, efficiency factor, and the forced, preferred and norm indicators if M3
   returns them. Keep every row except the original.
3. For each remaining resource (up to 5; say how many were left out), `M3_PDS010MI_Get` `{ Facility, WorkCenter }` and keep
   it only if **`ResourceType` is `W/cResource`**, **`SuperiorWorkCenter` is the same main work center**, and
   **`CapacityType` equals the operation's**. Show anything dropped with the reason in the coverage line.
4. Keep for each: name, department, planning area, number of machines or persons, and from the relation row the
   preferred and norm flags and the efficiency factor.

**If `M3_PDS010MI_LstRelPerWC` returns an error:** quote it in one line, say the related resources couldn't be listed and
that the swap isn't offered, and **don't retry it** in this turn and **don't guess resource names** (not from the naming of
the original, not from other MOs). It failed in the first test with a metadata error on `LastModifiedDate`
(`m3/known-inconsistencies.md`, K21): that needs an administrator, not another call.

## 3. Is there capacity on the alternative

For each alternative: `M3_CPS100MI_SelTotalLoad` over the **same weeks** as the operation (the same `FromDate` and
`ToDate`). For each week it returns `CapacityPerUnitAndShift` and the loads; use only the fields of the operation's
capacity type (`capacity-types.md`).

- **Load** per week = manufacturing orders (category A and B) + planned orders (category A and B, groups 1 and 2) of that
  type. Show firm MO load and planned-order load separately.
- **Free** per week = rating minus load, never below zero. **Free in the span** = the sum over the weeks the operation spans.
- **Needed** = the operation's `RemainingTimeHours`. The same hours are assumed on the alternative; if the relation row
  gives an efficiency factor other than 1, show it and say the hours may differ.
- **Utilisation after the swap** per week = (load + the operation's hours placed in that week) / rating. Spread the hours
  over the weeks the operation spans in proportion to its dates; if it can't be spread, use the single week it starts in
  and say so.

| Result | Label |
|---|---|
| Free in the span covers the hours, and every week stays at or under 95% after the swap | ✅ Room |
| Covers the hours, but a week would go above 95% after the swap | ⚠️ Tight: <week> at <x>% |
| Covers only part of the hours | ❌ Not enough (<free> of <needed> h): not offered |
| Load not returned for the weeks | ⚠️ Capacity not checked: not offered |

Rules:
- **The rating is per unit and shift**: a resource with more machines or persons or more shifts has more room than it
  shows. Say so when the comparison is close (as `at-risk-orders.md` does).
- Planned orders are proposals, not firm load; if the room depends on a planned order not being released, say it.
- **If the load can't be read for the original or the alternative**, say "capacity not checked" for it; never call it fine.
- **A resource with room only in weeks after the MO must finish** is ❌ for this purpose.

## 4. Offer it (advice only)

Show up to three alternatives, best first: ✅ before ⚠️; then the most free hours in the span; then the preferred or norm
resource. Nothing is applied by showing the options.

> **Option: move operation <op> of MO <n> from <original> to <alternative>** (<machine | labor> capacity)
> Why: <original> is over its rating in week <w> (<load> of <rating> h); <reason from condition C: for example the first
> week with room finishes the MO <n> days after <the date it is needed>>.
> <Alternative>: <label>; <free> h free in <weeks>, <x>% after the swap. Same main work center <main>, same capacity type.
> Confidence: <High when the load of both resources was read for every week; Medium when the room depends on planned
> orders or an efficiency factor other than 1; Low when part of the load was not read>.
> What would change it: <planned orders that may be released, a week not read, department or planning area that differ>.

Several alternatives: a small table (resource, label, free hours in the span, utilisation after the swap, preferred or
norm, department) and one recommendation. If the alternative's department or planning area differs from the
original's, say so on the option (M3 may or may not update them: `m3/known-inconsistencies.md`, K22).

## Confirm before writing

One card for the two calls. Re-read first (write protocol step 3): the MO is open and unchanged, the operation still sits
on the original, it has no reported quantity or time, the original is still over its rating, and the alternative's load
still leaves room. If anything differs, don't show the card: say what changed.

> **Swap <machine | labor> resource on MO <number>**
> <product> - facility <f> - operation <op> (<description>), <hours> h of <machine | labor> capacity
> Work center <original, name> -> <alternative, name>, both resources under <main work center, name>. Capacity type
> <MachineHours | ManHours> (unchanged). Run time, setup time, machines, workers and quantity on the operation: unchanged.
> Why: <the overload and why nothing else closes it, one line>. <Alternative>: <label>, <free> h free in <weeks>.
> On this one yes I will change the operation's work center: `M3_PMS100MI_UpdOperation`, work center only.
> Not changed: other operations, other MOs, the capacity ratings and calendars of both work centers. I can't undo this
> from here: going back means another swap or a change in M3.
> Reply **yes** to swap.

Only after an explicit yes to this card:

1. **Snapshot the lower levels** as `reschedule-mo.md` step 2 does (the MOs that make semi-finished components, with
   their dates), and the **load of both resources** you just read, before the first call.
2. **Call `M3_PMS100MI_UpdOperation` once** with `{ Facility, ManufacturingOrderNumber, ProductNumber, OperationNumber,
   WorkCenter: <alternative> }`. Send nothing else: every other field of the operation stays as it is (no `RunTime`, no
   `SetupTime`, no `PlannedMachines`, no workers, no `Department` or `PlanningArea`). On an error, report it plainly and
   stop: no reschedule, no retry (M3 validates against the operation status, reporting, the routing and the work center
   setup, and may refuse). Read the operation first to see whether it saved.
3. **Read the operation back** with `M3_PMS100MI_GetOperation` `{ Facility, ManufacturingOrderNumber, ProductNumber,
   OperationNumber }`. If it still shows the original, wait a moment and read again (up to four reads). **Only when it shows
   the alternative**, go on. If it doesn't, say so and stop without the reschedule.
4. **Re-read the MO** (`M3_PMS100MI_Get`) for its current quantity and start date, then **call `M3_PMS100MI_Reschedule`
   once** with `{ Facility, ManufacturingOrderNumber, ProductNumber, OrderedQuantityAltUom: <the MO's current ordered
   quantity, the same as on the MO>, FiniteCapacityPlanning: false, StartDate: <the MO's current start date, as just
   read> }` and **no `PlannedFinishDate`**. (M3 refuses a call with no date: `m3/tool-conventions.md`.) The yes on the card
   covers this call: don't ask again and don't mention it. Never send any date other than the current start date, and
   keep capacity planning infinite so the dates stay put.
   If M3 refuses it anyway, report M3's message: **the swap still stands**, the MO is not recalculated, and the planner can
   reschedule in M3 or with `reschedule-mo.md` on a date the planner chooses. Don't retry, and don't pick a date.

## 5. Read back and report

1. **The operation:** a small table (field, before, now): work center, capacity type, run time, setup time, planned
   machines, planned workers, department, planning area, remaining hours. ✅ for what changed as the card said, ⚠️ for
   anything unexpected (for example a department or planning area that M3 changed or didn't).
2. **The MO:** `M3_PMS100MI_Get`: wait while the status reads "...-ChangeInProgress" (it took about a minute in the material
   swap test and under 40 seconds in the capacity swap test; read every 20 to 30 seconds, up to six times), then give the start
   and finish date. Don't mention the reschedule, the times or the priority. If M3 moved the start date, say so with both values.
3. **The load,** with `M3_CPS100MI_SelTotalLoad` over the same weeks for both resources, against the figures from before the
   swap: the original's load should have gone down and the alternative's up by about the operation's hours (in the test it
   moved at once: 10 -> 0 h and 8 -> 18 h of manufacturing-order load; planned-order load stays). If M3's figures haven't
   changed yet, say so: give the read time.
4. **The lower levels** against the snapshot, in the block `reschedule-mo.md` step 4 describes (affected, unchanged,
   conflict, none found). Don't change any of them.
5. Give the MO's new capacity verdict in one line: ✅ no week over its rating on the new resource, ⚠️ <week> at <x>%, or
   ❌ still over.

### Result line

```
MO <n>, operation <op>: <original> -> <alternative> (<machine | labor> capacity, <hours> h); run time, setup and quantity unchanged
MO dates: start <d>, finish <d>[; start moved from <old> - only when M3 moved it]
Load now: <original> <load> of <rating> h (was <x>); <alternative> <load> of <rating> h (was <y>). Lower levels: <moved | unchanged | none found>
```

## Next step

- More MOs over the same resource: "MO <m> loads <original> the same week; want to check it for a swap?" (one at a time).
- "Want the capacity picture for both resources?" (`capacity-types.md`, `planner-kpis.md`).
- The alternative is now near its rating: say which week and offer to re-read the load later.
- "Which customers does this affect?" (`customer-impact.md`) when dates were exposed.

## Edge cases

- **The original isn't a type 6 resource, or has no main work center** - say so and stop; no swap.
- **No other resources under the main work center** - "No other resource is related to <main work center>." Offer the
  other options (`at-risk-orders.md` step 5). Never suggest a work center from outside the relations.
- **Related resources exist but none has the same capacity type, or none has room** - show them with the reason (✅ ⚠️ ❌
  labels) and don't offer a swap.
- **`M3_PDS010MI_LstRelPerWC` fails** - say so, don't retry, don't guess names (step 2).
- **The alternative's department or planning area differs** - show it; send only the work center; report what M3 did
  (not yet seen: both were the same in the first test).
- **The MO reads "...-ChangeInProgress" before the write** - don't write. Read again after 30 to 45 seconds; if it still shows it
  after about two minutes, say so: another M3 program the planner has open can hold the MO. Ask them to close it, then re-read.
- **M3 refuses the operation change** - report its message; nothing was changed; don't try another route or tool.
- **The operation changed but the reschedule failed or was refused** - report both results separately; the swap stands.
- **MO or operation changed since the options were shown** - don't write; re-read and re-offer.
- **Several operations on the MO over capacity** - one operation at a time, each with its own card; the reschedule runs
  after each swap.
- **Several matches** (MO, operation, resource) - list and ask; never pick.
- **Can't see it / not permitted** - report; don't retry.
- **A tool is missing** - say which (`M3_PMS100MI_UpdOperation`, `M3_PMS100MI_Reschedule`, `M3_PDS010MI_Get` or
  `M3_PDS010MI_LstRelPerWC`) and that the swap isn't offered; don't use another write tool.
