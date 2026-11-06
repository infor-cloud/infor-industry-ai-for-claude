# Hold an MO to free capacity and material

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_HoldMO`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstMaterials`, `M3_PMS100MI_LstOperations`, `M3_PMS100MI_GetOperation`, `M3_PMS100MI_SearchOperation`, `M3_PMS100MI_SearchMaterial`, `M3_CPS100MI_SelTotalLoad`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PMS100MI_RelHeldMO`

<!-- contents:start -->
**Contents**

- What this does and doesn't do
- 1. The target and what it lacks
- 2. Find MOs that share it
- 3. Can each one be held
- 4. What a hold would free
- 5. Offer it (advice only)
- Confirm before writing
- 6. Read back and report
- Show it
- Next step
- Edge cases
<!-- contents:end -->

Guided write: identify the MO that can't finish on time (the
**target**) and what it lacks -> find other MOs that use the same capacity or the same material (the **donors**) -> check
that a donor has no urgent customer demand and can be held -> work out what a hold would free -> recommend -> one card ->
`M3_PMS100MI_HoldMO` -> read back and report. Releasing a held MO is a separate action with its own card
(`release-held-mo.md`).

## What this does and doesn't do

- **The scenario.** A customer order is exposed because an MO (the target) can't finish on time, for lack of **capacity**
  (machine or labor) or of **material**. Another MO, for another product with **no urgent customer demand**, uses some of
  the same operations (work center resource) and/or the same components. Holding that MO takes its load and its demand off
  the shared resource and stock, so the target can use them.
- **Only to free capacity and material.** The reason on the card is always the shortage or overload it frees, for a named
  target. If the planner asks to hold an MO with no target, say so on the card ("no target named") and show what the hold
  frees; the checks below still apply.
- **A hold moves nothing by itself.** It does not move the target's dates or place it on the freed capacity. After the hold
  is read back, offer the target's own reschedule as a **separate** action with its own card (`reschedule-mo.md`; a
  finite-capacity recalculation lets M3 place it where room is free).
- **Hold type: long-term by default (the owner's rule, after the first tests).** `M3_PMS100MI_HoldMO` takes `HoldMoStatus`: **`"2"`
  long-term** (the default) or **`"1"` short-term**, used **only when the planner asks for it**. A long-term hold needs **no date**,
  moves **nothing** (the order keeps its dates and operations) and takes the order's component demand **out** of the material plan
  (tested, K23). **A short-term hold** reschedules the order, and M3 may also move its lower-level orders; **M3 refuses it without a date**
  ("Start or finish date must be entered": tested), so **the planner gives the date the order is held until**: ask once ("hold until
  which date?"), never pick or invent it, and you may suggest one with its reason, **only after checking where the donor's operations
  land** (step 4: in the tests a start on 2026-10-30, a Friday of the target's week, put the donor's 50 h of labor into that week, and
  its component demand only moved to a later date instead of going away). The date is sent as the order's new start date, and goes on
  the card as a **date change of the donor** with its old and new dates. Nothing else is sent.
- **Nothing else changes.** The donor's quantity, dates, operations, materials and priority stay as they are. Its
  lower-level orders are not touched (they may now have no demand: say so). Purchase orders, customer orders and other MOs
  are not touched.
- **A hold doesn't end by itself.** Nothing releases it later and this flow can't set a reminder; the **MOs on hold** KPI (KPI K21,
  `kpi-catalogue.md`) lists held MOs and the ones past their hold date, and the planner can ask for it any time. The reason isn't stored
  in M3 (no tool for it): it is in the chat and in the result line. Say so, and offer the release (`release-held-mo.md`) when the target
  is done.
- **Only the planner's own MOs** are offered as donors (responsible = the user; all responsibles only when the prompt says
  all MOs). Never hold an MO the user doesn't own on your own initiative; if the planner names one, say whose it is.
- **From a dashboard.** A Confirm click on a board may run a hold or a release, as in chat: the board shows the same card, re-reads the MO first, makes the one call and reads the result back. A hold or a release is never combined with another write.


## 1. The target and what it lacks

Start from the MO that can't finish on time: the one named, or one from an `at-risk-orders.md` or `material-shortage-check.md`
result in this conversation (reuse its figures, with the read time). Read it: `M3_PMS100MI_Get`, `M3_PMS100MI_LstMaterials`,
`M3_PMS100MI_LstOperations`, and for each operation that matters `M3_PMS100MI_GetOperation` (work center, `CapacityType`,
`RemainingTimeHours`, dates). Find the customer order it exposes with `customer-impact.md` step 2 (order, customer, requested
date). If no customer order is exposed, say so: the hold is then not for a customer, and the planner decides whether it still
matters.

Name what the target lacks, each as a constraint:
- **Material:** each Short component (`material-shortage-check.md`): item, warehouse, quantity short, date needed.
- **Capacity:** each work center and week over its rating for the operation's capacity type (`capacity-types.md`): work
  center, week, load, rating, **machine or labor**.

A hold is offered only when **the target has at least one constraint** and **other options don't close it in time**: if a
reschedule, a pulled-in PO, an alternative item or another resource (`reschedule-mo.md`, `swap-material.md`,
`swap-capacity.md`) meets every date, recommend that and offer the hold only if the planner asks for it.

## 2. Find MOs that share it

Scope: the planner's open MOs in the same facility (`at-risk-orders.md` step 2b with the user as responsible; keep the list
of MO numbers). Then find the ones that use the same constraint:

- **Same capacity.** For each over-rating work center: `M3_PMS100MI_SearchOperation` `{ WorkCenter_ExactSearch:
  <work center>, Facility_ExactSearch, StartDate_LargerThan: <week start minus 1 day>, StartDate_LessThan: <week end plus 1
  day> }`. Keep operations of MOs in the planner's list, other than the target. **Same work center code only**: an
  operation on a sibling resource under the same main work center frees nothing here (offer `swap-capacity.md` instead).
  The capacity type must match (machine against machine, labor against labor).
- **Same material.** For each Short component: `M3_PMS100MI_SearchMaterial` `{ ComponentNumber_ExactSearch: <item>,
  Warehouse_ExactSearch: <warehouse>, Facility_ExactSearch }`. Keep lines of MOs in the planner's list, other than the
  target, whose reservation date is on or before the target's need date plus the review window (default 14 days).

A donor may share both. Cap at **10 donors** (the ones with the largest shared hours or quantity first) and say how many
were left out.

## 3. Can each one be held

Read each donor (`M3_PMS100MI_Get`, `M3_PMS100MI_LstOperations`, `M3_PMS100MI_LstMaterials`). **Don't offer a hold, and say
why in one line,** when:
- the MO is completed, **already held**, or **started**: any operation started or reported, or reported quantity or time above
  zero, or material already issued (M3 would refuse, or the work would be stranded);
- **it has urgent customer demand.** Urgent means an open customer order line for its product with a requested delivery date
  **on or before today + the review window (default 14 days)**, or its reference order is a customer order that falls in that
  window (`customer-impact.md` step 2a and 2b: by reference order, then by product and date; a made-to-stock MO carries no
  customer link, so say that match is by product and date). A customer order further out is **not** urgent, but is named on
  the card and in the options;
- **it feeds a higher-level order:** its reference order category is another manufacturing order (the parent would starve).
  Name the parent;
- it is the target itself, or the planner doesn't own it (scope);
- the facility of the shared work center or the warehouse of the shared component differs from the target's.

## 4. What a hold would free

For each remaining donor, work out what the target gains. **Count only what M3 will show as freed; say what is uncertain.**

- **Capacity.** For each over-rating week: freed hours = the donor operation's remaining hours that fall in that week (if it
  can't be split, the week it starts in; say so). New load = load minus freed hours (firm MO load; planned-order load is
  unchanged). The week is **cleared** when new load is at or below the rating. Then compare the target's hours:
  free in the week = rating minus new load; the target fits when that covers its remaining hours there.
  **A short-term hold doesn't remove load, it moves it.** In the first test the held MO's operations were scheduled from the new
  start date, and M3 kept their load in the load table at the new dates (the hold's `IncludeHeldManufacturingOrders` default of 0 did
  not drop it): each operation's whole hours showed in the week it starts. So for a short-term hold work out **where each of the donor's
  operations will land** (operations run in sequence from the new start date, with the durations they have now) and check the load
  **there** too: the hold must not put an over-rating week, or the target's own week, over its rating. Put the landing weeks and
  their load on the card.
- **Material.** Run the component's running balance again (`material-shortage-check.md` step 3) with the donor's demand
  removed. Freed quantity = the donor line's reserved quantity **not yet allocated**. Quantity already **allocated** to the
  donor is shown separately and **not counted** (M3 may keep it allocated until it is deallocated; this skill can't
  deallocate: `m3/known-inconsistencies.md`, K23).
- **Result per donor:** ✅ **Closes the gap** (every constraint of the target is cleared or covered); ⚠️ **Partly**
  (<x> of <y> h or units); ❌ **No effect** (not offered). Combining two donors may close it: say so and offer them one at a
  time, each with its own card.
- **Cost of the hold.** The donor's own finish date doesn't move, but it won't run while held. Name its planned finish, its
  customer orders (and the earliest requested date), and the lower-level orders that will lose their demand.

## 5. Offer it (advice only)

Show up to three donors, best first: ✅ before ⚠️; then the donor with the **latest** customer requested date (or none);
then the least work already done. Nothing is applied by showing the options. A ⚠️ Partly donor is still shown, with the
warning that it will not close the gap on its own.

> **Option: hold MO <donor> (<product>) to free <capacity | material | both> for MO <target>**
> Why: <target> is short <qty> of <item> on <date> / over its rating on <work center> in week <w> (<load> of <rating> h); its
> customer order <n> (<customer>, due <date>) is exposed. <Donor> uses the same <work center / item>: <freed h / qty>.
> Effect: <✅ closes the gap | ⚠️ partly: <x> of <y>>. It also frees <the other constraint, if any>.
> Cost: <donor> (planned finish <date>) stops until released; customer demand: <none | order <n>, due <date>, not urgent>.
> Hold type: <long-term (default) | short-term until <date>, if the planner asked>.
> Confidence: <High when the load and the balance were read for every week and no allocated quantity is in the count; Medium
> when allocated quantity or a week that couldn't be split is involved; Low when part of the data wasn't read>.
> What would change it: <allocated material that M3 may keep, planned orders that may be released, a week not read>.

Several donors: a small table (donor, product, what it frees, effect, its customer demand, planned finish) and one
recommendation.

## Confirm before writing

Re-read first (write protocol step 3): the donor is open and unchanged (status, dates, quantity), nothing has been started or
reported, the customer demand check still holds, and the target still has the constraint. If anything differs, don't show
the card: say what changed.

> **Hold MO <number>**
> <product> (<n>), facility <f>, quantity <q>, planned <start> to <finish>, status <status>
> Hold type: **<long-term | short-term, held until <date>>** (`HoldMoStatus` <2 | 1>)
> Why: to free <capacity on <work center>, week <w>: <freed> h | <qty> of <item> | both> for MO <target>, whose customer
> order <n> (<customer>, due <date>) is exposed. Effect on the target: <✅ closes the gap | ⚠️ partly: <x> of <y>>.
> Cost: this MO stops until released. Customer demand on it: <none | order <n>, due <date>, not urgent>. Its lower-level
> orders: <none | <list>>, left as they are.
> <For a short-term hold: "This order moves from <old start> to <new start>; M3 may also reschedule its lower-level orders at once; I can't control that.">
> <If allocated material is involved: "<qty> of <item> is allocated to this MO; M3 may keep it allocated, so that part
> may not be freed.">
> Not changed: its quantity, dates, operations, materials and priority; the target; other MOs; customer and purchase orders.
> A hold does not end by itself; to bring it back I release it (separate action). I can't undo this from here other than by that release.
> Reply **yes** to hold.

Only after an explicit yes: **call `M3_PMS100MI_HoldMO` once** with `{ Facility, ManufacturingOrderNumber, ProductNumber,
HoldMoStatus: "2" }` and nothing else (or, only when the planner asked for a short-term hold, `HoldMoStatus: "1", StartDate: <the date the
planner gave>`). The tool
now lists `StartDate`, `PlannedStartTime`, `PlannedFinishDate`, `PlannedFinishTime` and `RescheduleLowerLevels` (before that was added,
M3 refused the call as the date didn't reach it: K23); send **only `StartDate`**, never the times, the finish date or the lower-level
flag unless the planner asks. If M3 refuses it, report the message, and offer the long-term hold (`"2"`, no date) or doing it in M3.
Don't retry with another parameter name without a new yes. On an error, report it
plainly and stop; don't retry with another date or type without a new yes, and read the MO first to see whether it saved.

## 6. Read back and report

1. **The donor:** `M3_PMS100MI_Get`. Wait while the status reads "...-ChangeInProgress" (read every 20 to 30 seconds, up to six
   times), then show before and after for status, start and finish date and time, quantity and priority. ✅ if it now reads
   as held and the dates are unchanged (a short-term hold may have moved them: say so with both values). Show the held status
   exactly as M3 returns it.
2. **What it freed:** `M3_CPS100MI_SelTotalLoad` for each shared work center over the same weeks (a short-term held MO's load stayed in the
   table at its new dates in the tests, so read the load rather than assuming it dropped; the table can lag after a release) and the shared components' balances (`M3_MMS200MI_GetItmWhsBal_Subname`,
   and the plan if needed). Show before and after. If M3's figures haven't changed yet, say so with the read time and offer to
   read again. If the donor's load stayed in the figures, say that a hold didn't remove it.
3. **The target:** re-run its constraints with the new figures and give its verdict in one line: ✅ no week over its rating
   and no component short, ⚠️ <what remains>, or ❌ unchanged. Say plainly that its dates have not moved.
4. **The donor's dependants:** its lower-level orders (listed, untouched) and its customer orders (named, not urgent).

## Show it

```
Hold: MO <donor> (<product>) <status before> -> <status now>; <short-term until <date> | long-term>; dates <unchanged | old -> new>
Freed: <work center> week <w>: load <x> -> <y> of <rating> h | <item>: <qty> freed (<qty> allocated, not counted) | not yet visible in M3
Target MO <target>: <✅ cleared | ⚠️ <what remains> | ❌ unchanged>; dates not moved. Customer order <n> due <date>: <exposure now>
```

## Next step

- After a hold: "Want me to reschedule MO <target> now that <work center / item> is freed?" (`reschedule-mo.md`, its own card; a
  finite-capacity recalculation lets M3 place it where room is free).
- "Want the sales rep told that <order> is at risk or that <donor>'s customer order <n> may move?" (`warn-sales-rep.md`).
- "Want me to release MO <donor> when MO <target> is done?" (`release-held-mo.md`). Say plainly that nothing releases it
  automatically.

## Edge cases

- **No donor shares the constraint** - "No other MO of yours uses <work center / item> in that period." Offer the other options.
- **Donors exist but all have urgent customer demand, feed a parent, or are started** - list them with the reason; don't offer a hold.
- **The hold would free only part of the gap** - show ⚠️ with the numbers; offer it only as a partial step, or with a second donor.
- **Allocated material** - count it as not freed; show it. Don't try to deallocate (no tool in this skill for it).
- **Long-term hold (the default)** - send `"2"` with no date; say the order's dates stay as they are. **Short-term hold requested** -
  ask for the date once and don't call the tool without one (M3 refuses); say the order moves. After either, read back the order's
  dates and its lower-level orders' dates.
- **The MO is already held** - say so; offer the release.
- **M3 refuses the hold or the release** - report its message; nothing was changed unless the read-back says so; don't try
  another route or tool.
- **MO changed since the options were shown** - don't write; re-read and re-offer.
- **The MO shows "...-ChangeInProgress" before a write** - don't write. Read again after 30 to 45 seconds; if it still shows
  it after about two minutes, another M3 program the planner has open can hold the MO: ask them to close it.
- **Several matches** (MO, product) - list and ask; never pick.
- **Can't see it / not permitted** - report; don't retry.
- **A tool is missing** - say which (`M3_PMS100MI_HoldMO` or `M3_PMS100MI_RelHeldMO`) and that the hold or release isn't
  offered; don't use another write tool.
