# Create an MO proposal manually (exception)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS170MI_CrtPlannedMO`, `M3_PMS170MI_SearchMOP`, `M3_PMS100MI_SearchMO`, `M3_OIS100MI_SearchLine_Summary`, `M3_PMS100MI_SelOrderHead`, `M3_MMS200MI_GetItmWhsBasic`, `M3_OIS100MI_GetLine`, `M3_PMS170MI_Get`, `M3_PMS170MI_LstMaterials`, `M3_PMS170MI_LstOperations`

<!-- contents:start -->
**Contents**

- Scope: when this is the right route
- 1. Check that manual creation is needed
- 2. Collect the inputs
- 3. Validate before any yes
- Confirm before writing
- 4. Read back
- Show it: Result line
- Next step
- Edge cases
<!-- contents:end -->

Guided write: check that no proposal or MO already covers the need -> collect and validate the inputs -> card and yes ->
create the proposal once -> read back -> offer the check and, separately, the release.

## Scope: when this is the right route

- **This is exception handling.** Normally MRP creates MO proposals (`mo-proposals.md`) and the planner releases them
  (`release-mo-proposal.md`). Create one by hand only when the planner asks for it in words ("create an MO proposal
  for ...", "plan an MO manually") or chooses it as the last option when nothing else covers the need. Never offer it
  first: in an at-risk or shortage answer it comes after an existing proposal, a reschedule and a purchase, and it is
  worded as an exception.
- **A proposal is a plan, not an order.** It counts in material planning, but nothing is made until it is released.
  Creating and releasing are two actions, each with its own card and yes: a yes to create never covers the release.
- **Real proposals only.** Simulated proposals are not covered here; say so if asked.
- **One proposal per call.** A short list (at most 5) gets one list card and one yes; each proposal still gets its own
  check, its own `M3_PMS170MI_CrtPlannedMO` call and its own read-back. Never a range, "all like this one" or a bulk load.
- Facility and warehouse are the user's own (`m3/settings.md`) unless the planner names others.

## 1. Check that manual creation is needed

1. **An existing proposal.** `M3_PMS170MI_SearchMOP` `{ Facility_ExactSearch, Warehouse_ExactSearch,
   ProductNumber_ExactSearch: <product> }` with **no** responsible filter (a proposal of another planner counts). If one
   covers the quantity and the date, say so and offer `release-mo-proposal.md`.
2. **An existing MO.** `M3_PMS100MI_SearchMO` with facility, warehouse, status below `OrderCompleted` and `SortBy:
   "PlannedFinishDate"`, then pick the product's rows yourself (a product-only search has returned nothing). Say that a
   duplicate can't be fully ruled out.
3. **Create anyway.** If either read found a cover, create only after a card that says so and a reply of "create
   anyway". Never inferred from a plain "create".
4. **Waiting customer orders.** `M3_OIS100MI_SearchLine_Summary` `{ ItemNumber_ExactSearch: <product>, SortBy:
   "RequestedDeliveryDateAtDestination" }`: list the open orders (order, quantity, requested date); with none, say the
   proposal builds stock. Drop deleted, completed and delivered lines.

## 2. Collect the inputs

Ask for what is missing in one short message, never one question at a time. Take what you can from the request.

| Input | Tool field | Where it comes from |
|---|---|---|
| Product | `ProductNumber` | The planner. Checked in step 3. |
| Quantity | `PlannedQuantity` | The planner, above 0. The tool has no unit input: the item's own unit applies; say the unit M3 shows after creation. |
| Facility, warehouse | `Facility`, `Warehouse` | The user's own, from M3. |
| Planning date | `PlanningDate` | The planner: the date the proposal counts against material requirements, normally the date the output is needed. M3 derives the start and finish. |
| Planning time | `PlanningTime` | Required by the tool. Use 0 unless the planner gives a time; show it on the card. |
| Status | `PlannedOrderStatus` | **`Pur/planMan` (code 20, shown by M3 as a firmed planned MO) by default**: the planner's rule, so that MRP leaves the proposal alone. `PlanOrdMan` (code 10, an ordinary planned order that the next MRP run can remove or recalculate) only when the planner asks for it. Never `Released`: releasing is its own flow. |
| Product structure type | `ProductStructureType` | **Required in practice**: M3 refuses a blank one when structure types are in use, although the tool lists it as optional. Read it from the MOs: `M3_PMS100MI_SelOrderHead` `{ Facility, Warehouse, FromStatus: "Definite", ToStatus: "Definite", TimestampDateFilter: <a date well before today>, SchedulingHorizonDays: <the review window> }` returns it for each MO (`at-risk-orders.md` step 2a explains the date filter). Use the value of an MO of the same product; if the product has none in the list, the value all listed MOs share; if they differ or none comes back, ask once (`m3/settings.md`). Show it on the card. Never guess it or take it from an example. |
| Simulation | `SimulationId` | Required by the tool. Use 0: M3 accepted it and created a real proposal. Show it on the card. |
| Reference order | `ReferenceOrderCategory`, `ReferenceOrderNumber`, `ReferenceOrderLine` | Optional, only when the planner gives it. Checked in step 3. |

**Not set unless the planner asks or a setting names it:** `OrderType`, `ProcessCode`, `Process`, `ScheduleNumber`,
project fields, `ExternalReference*`, `AlternateRoutingId`, `ConfigurationNumber`, `CopyFromPlannedMo` (copying a
proposal is a separate request: confirm the source first).

**The tool has no reason field and no responsible field.** Put the reason on the card and in the chat so it is on
record; if the planner wants it stored in M3, `ExternalReferenceDescription` can hold one short line (ask first). M3
sets the responsible user itself, to the item and warehouse responsible, so the proposal may not appear under the
planner's own scope: say so on the card.

## 3. Validate before any yes

Don't ask for a yes on something you already know is wrong.

1. **The item.** `M3_MMS200MI_GetItmWhsBasic` `{ ItemNumber, Warehouse }`: it exists in that warehouse. That read doesn't say whether
   the item is manufactured: if M3 refuses the create, report its message, and for a purchased item offer a planned
   purchase (`m3/create-planned-po.md`).
2. **The quantity and the date.** Quantity above 0. A planning date before today: say so and ask if it is intended.
3. **The reference order, if any.** `M3_OIS100MI_GetLine` `{ OrderNumber, LineNumber }`: it exists, is open and is for the
   same product. If it ships from another warehouse than the proposal, say so on the card.
4. **The structure type** is read or asked (step 2).

## Confirm before writing

> **Create MO proposal (manual, exception)** <product> <description>, <qty> <unit>
> Facility <f>, warehouse <w>, planning date <date>, planning time <time>, status <status and code>
> Product structure type <type>, simulation 0
> Reason: <the reason, in chat only | stored as the external reference>. Normally MRP creates this: <MRP has nothing
> that covers it | proposal <n> already covers it (create anyway)>.
> Waiting: <orders with quantity and requested date | no customer order, builds stock>
> Reference order: <order and line | none>
> This creates a real proposal in material planning. It is not an order: nothing is made until it is released. M3 sets
> the responsible user itself (the item's responsible user, not necessarily you). I can't delete it from here.
> Reply **yes** to create.

Only after an explicit yes: re-read once (step 1.1 and the item), then call `M3_PMS170MI_CrtPlannedMO` **once** with
exactly the fields on the card. One yes covers only this card. Never retry a write blindly, and never retry with
other values without asking.

## 4. Read back

1. Take the planned order number (and subnumber) from the response.
2. `M3_PMS170MI_Get` `{ OrderNumber: <number> }`. It answers at once: compare product, quantity, start and finish, and the
   status (M3 names the status with its code). Report M3's values, not what was asked.
3. `M3_PMS170MI_SearchMOP` `{ Facility_ExactSearch, Warehouse_ExactSearch, ProductNumber_ExactSearch }` for the responsible
   user. Right after creation a search can miss the new proposal and show it on a later read: read up to three times,
   and never conclude "not created" while `Get` finds it. Mark ⚠️ when the responsible user is not the planner.
4. Components and operations: `M3_PMS170MI_LstMaterials` `{ OrderNumber }` and `M3_PMS170MI_LstOperations` `{ OrderNumber }`. They can
   take a few minutes: if empty, say "the proposal exists, its components aren't visible yet", never "it has no
   components".
5. If the response had no number, search proposals for the product and match product and quantity. Never claim success
   without finding the proposal.

## Show it

Chat: the card, then the result line, then a table of field, asked and M3 now, with ✅ for what matches and ⚠️ for
anything different (the responsible user, a date M3 derived differently).

### Result line

```
Proposal created: <product> x <qty> <unit> -> planned order <number> (<start>-<finish>), status <status>, responsible <user>
```

## Next step

"Want me to check whether it is ready to release?" (the checks in `release-mo-proposal.md` step 2); "Want the full check
on its material?" (`material-shortage-check.md`). Releasing is a separate yes.

## Edge cases

- **Product not found in the warehouse** - say so; don't try a similar product.
- **A proposal already covers it** - offer `release-mo-proposal.md`; create only on "create anyway".
- **Simulated proposal asked for** - not covered here.
- **The create fails or answers unclearly** - report the error text. An error is not proof that nothing was created:
  read back first and say if a proposal exists. Never retry with other values without asking.
- **Wrong proposal created** - this skill has no delete for MO proposals. Tell the planner to delete it in M3.
- **Can't see it / not permitted** - report; don't retry; don't try another route.
