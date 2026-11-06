# Create an MO manually (exception)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS170MI_SearchMOP`, `M3_PMS100MI_SearchMO`, `M3_OIS100MI_SearchLine_Summary`, `M3_PMS100MI_Get`, `M3_PMS100MI_SelOrderHead`, `M3_MMS200MI_GetItmWhsBasic`, `M3_OIS100MI_GetLine`, `M3_PMS100MI_CrtMO`, `M3_PMS100MI_LstMaterials`, `M3_PMS100MI_LstOperations`

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
create the MO once -> read back -> offer the full check.

## Scope: when this is the right route

- **This is exception handling.** Normally an MO comes from an MRP-created MO proposal (`mo-proposals.md`, then
  `release-mo-proposal.md`). Create an MO by hand only when the planner asks for it in words ("create an MO for ...",
  "make a manufacturing order by hand") or chooses it as the last option when no proposal can cover the need. Never
  offer it first: in an at-risk or shortage answer it comes after an existing proposal, a reschedule, a purchase and a
  manual proposal (`create-mo-proposal.md`), and it is worded as an exception.
- **If the planner hasn't said which they want,** offer the proposal route first: a proposal can be checked and
  released later, while an MO exists on the shop floor at once.
- **One MO per call.** A short list (at most 5) gets one list card and one yes; each MO still gets its own check, its own
  create call and its own read-back. Never a range, "all like this one" or a bulk load.
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
   MO builds stock. Drop deleted, completed and delivered lines.

## 2. Collect the inputs

Ask for what is missing in one short message, never one question at a time. Take what you can from the request.

| Input | Tool field | Where it comes from |
|---|---|---|
| Product | `ProductNumber` | The planner. Checked in step 3. |
| Quantity | `OrderedQuantityAltUom` | The planner, above 0. |
| Manufacturing unit of measure | `ManufacturingUnitOfMeasure` | **Required in practice**: M3 refuses without it ("Manufacturing U/M does not exist"), although the tool lists it as optional. Read it from an MO of the same product (`M3_PMS100MI_Get` returns it) or from a proposal (`M3_PMS170MI_SearchMOP` returns it). Never guess it or hard-code it. If the product has neither, ask once. |
| Facility, warehouse | `Facility`, `Warehouse` | The user's own, from M3. |
| Product structure type | `ProductStructureType` | Required by the tool. Read it from the MOs: `M3_PMS100MI_SelOrderHead` `{ Facility, Warehouse, FromStatus: "Definite", ToStatus: "Definite", TimestampDateFilter: <a date well before today>, SchedulingHorizonDays: <the review window> }` returns it for each MO (`at-risk-orders.md` step 2a explains the date filter). Use the value of an MO of the same product; if the product has none in the list, the value all listed MOs share; if they differ or none comes back, ask once (`m3/settings.md`). Show it on the card. Never guess it or take it from an example. |
| Initial status | `WorkOrderStatus` | Ask: **Definite** (a normal firm order) or **Preliminary**. Never chosen silently. |
| One date | `PlannedFinishDate` (default) or `StartDate` | The planner gives **one** date. M3 schedules the other; the read-back shows both. |
| Responsible | `ResponsibleUser` | The user who triggers the order: always the signed-in user, unless the planner names another user. M3 accepts it on this tool, so the MO belongs to that user and shows in their list. |
| Reason | `Description` | **Required.** One short line saying why this is manual. No personal data. |
| Reference order | `ReferenceOrderCategory`, `ReferenceOrderNumber`, `ReferenceOrderLine` | Optional, only when the planner gives it. Checked in step 3. |

**Not set unless the planner asks or a setting names it:** `ExplosionIndicator` (it creates MOs for semi-finished
components: say so on the card when it is set, and never set it by default), `SkipAutoJobTrigger`,
`WarningIndicator1` to `8`, the print counts, batch and expiry fields, `OrderType`, `ProcessCode`, `ProductionLine`,
`ScheduleNumber`, project fields, `ExternalReference*`, `AlternateRoutingId`.

## 3. Validate before any yes

Don't ask for a yes on something you already know is wrong.

1. **The item.** `M3_MMS200MI_GetItmWhsBasic` `{ ItemNumber, Warehouse }`: it exists in that warehouse. That read doesn't say whether
   the item is manufactured: if M3 refuses the create, report its message, and for a purchased item offer a planned
   purchase (`m3/create-planned-po.md`).
2. **The quantity and the date.** Quantity above 0. A date before today: say so and ask if it is intended (the MO is
   then overdue from the start).
3. **The reference order, if any.** `M3_OIS100MI_GetLine` `{ OrderNumber, LineNumber }`: it exists, is open and is for the
   same product. If it ships from another warehouse than the MO, say so on the card (the link is by order and line;
   moving the goods is a separate step).
4. **The responsible user** is the planner or a user the planner named; never assume another person's ID.
5. **The unit of measure and the structure type** are read or asked (step 2).

## Confirm before writing

> **Create MO (manual, exception)** <product> <description>, <qty> <unit>
> Facility <f>, warehouse <w>, product structure type <type>, manufacturing unit <unit>
> Status <Definite | Preliminary>, <finish | start> <date>, responsible <user>
> Reason (stored in the MO description): <the reason line>. Normally this comes from an MRP proposal: <no proposal
> covers it | proposal <n> already covers it (create anyway)>.
> Waiting: <orders with quantity and requested date | no customer order, builds stock>
> Reference order: <order and line | none>
> M3 builds the components and operations from the product structure; <no MOs are created for semi-finished
> components | MOs are also created for semi-finished components (explosion)>.
> This creates a real order that the shop floor sees. I can't delete it from here.
> Reply **yes** to create.

Only after an explicit yes: re-read once (step 1 and the item), then call `M3_PMS100MI_CrtMO` **once** with exactly the
fields on the card. One yes covers only this card. Never retry a write blindly, and never retry with other values
without asking.

## 4. Read back

1. Take the MO number from the response.
2. **The new MO is not readable at once** ("Record does not exist"): wait about a minute and read again, up to a few
   times. `M3_PMS100MI_Get` `{ Facility, ManufacturingOrderNumber, ProductNumber }`: compare product, quantity, unit,
   status, start and finish. M3 schedules the other date itself: report M3's dates, and mark ⚠️ if the finish differs
   from what was asked.
3. The responsible user is not on that read: confirm it with `M3_PMS100MI_SearchMO` `{ Facility_ExactSearch,
   ManufacturingOrderNumber_ExactSearch, Responsible_ExactSearch: <user> }`.
4. Components and operations once the MO is readable: `M3_PMS100MI_LstMaterials` and `M3_PMS100MI_LstOperations` with the same
   keys. They showed at once in tests; if empty, say "the order exists, its components aren't visible yet", never "it
   has no components". New material lines are usually reserved but not yet allocated.
5. If the response had no number, find the order with the known-good `SearchMO` filters and the same product and
   quantity. Never claim success without finding the order.

## Show it

Chat: the card, then the result line, then a table of field, asked and M3 now, with ✅ for what matches and ⚠️ for
anything different. Where useful, compare with an existing MO of the same product (status, dates, operation, work
centre).

### Result line

```
MO created: <product> x <qty> <unit> -> MO <number> (<start>-<finish>), status <status>, responsible <user>
```

## Next step

"Want the full check on MO <number>?" (`material-shortage-check.md`: it was made by hand, so nothing has checked its
material or capacity yet); "Want the sales rep told?" (`warn-sales-rep.md`) when a customer order waits.

## Edge cases

- **Product not found in the warehouse** - say so; don't try a similar product.
- **A proposal already covers it** - offer `release-mo-proposal.md`; create only on "create anyway".
- **The create fails or answers unclearly** - report the error text. An error is not proof that nothing was created:
  read back first (step 4.5) and say if an order exists without components. Never retry with other values without
  asking.
- **Wrong MO created** - this skill has no delete for MOs. Tell the planner to delete or close it in M3.
- **Can't see it / not permitted** - report; don't retry; don't try another route.
