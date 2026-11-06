# Release MO proposals

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS170MI_SearchMOP`, `M3_PMS170MI_LstMaterials`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`, `M3_PMS170MI_LstOperations`, `M3_CPS100MI_SelTotalLoad`, `M3_OIS100MI_SearchLine_Summary`, `M3_PMS170MI_SetStatus`, `M3_PMS100MI_SearchMO`, `M3_PMS100MI_Get`

<!-- contents:start -->
**Contents**

- Scope
- 1. Identify the proposal(s)
- 2. Check each proposal before any yes: Refuse when blocked, unless "release anyway"
- Confirm before writing: When the planner releases from the dashboard board
- 3. Read back (each proposal)
- Show it: Result line
- Next step
- Edge cases
<!-- contents:end -->

Guided write: identify the proposal(s) -> check material, capacity and waiting customer orders -> refuse or
warn -> confirmation -> set the status to Released once per proposal -> read back.

## Scope

- **One proposal per call.** Releasing several is allowed (below), but each proposal gets its own check, its own
  `SetStatus` call and its own read-back.
- **A short list is fine** ("release all the ones that are ready"): one
  list card and one yes for the whole list (step 2b). Never a range or "everything" without showing the list first.
- Only the planner's own proposals (the responsible user) unless they name others.

## 1. Identify the proposal(s)

Take the planned order number(s) from the user, from a pasted request (such as "Release planned MO <number>
(<product>, <qty> pcs, finishes <date>)": use the number, and check that product, quantity and date match what M3
shows), from a `mo-proposals.md` result, or from confirmed board requests. Read each:
`M3_PMS170MI_SearchMOP` `{ PlannedOrderNumber_ExactSearch: <n>, Facility_ExactSearch, Warehouse_ExactSearch }`.
- **No rows:** say so; it may already be released. Offer `mo-proposals.md`.
- **More than one row:** list them and ask; never pick.
- **One row:** keep planned order number, product, quantity and unit, start and finish date, responsible user.
For "release the ones that are ready": read the user's proposals (`M3_PMS170MI_SearchMOP` with the responsible user),
check each (step 2) and take only those that are Ready.

## 2. Check each proposal before any yes

1. **Material.** `M3_PMS170MI_LstMaterials` `{ OrderNumber }`, then per component `M3_MMS200MI_GetItmWhsBal_Subname`
   (and `M3_PPS200MI_SearchLine` for purchased items). **Ready** if every component is covered by available
   inventory or confirmed supply by the start date; **Blocked** otherwise (name the component, the quantity short
   and what is on the way; unconfirmed and planned orders don't count).
2. **Capacity.** `M3_PMS170MI_LstOperations` `{ OrderNumber }` -> the work centers and their capacity types; for each,
   `M3_CPS100MI_SelTotalLoad` `{ Facility, WorkCenter, FromDate: <proposal start>, ToDate: <proposal finish> }`.
   If a week's load is above the rated capacity, **warn**: "work center <wc> is at <x> of its <y> rating in week
   <w>" (the rating is per unit and shift, so a work center with more units or shifts has more room). Use the load that matches the capacity type (machine time for type 1, man time for type 2) and name it in the
   warning (machine capacity or labor capacity; `capacity-types.md`). The warning
   never blocks a release. If either read fails, say capacity wasn't checked.
3. **Customer orders waiting.** `M3_OIS100MI_SearchLine_Summary` `{ ItemNumber_ExactSearch: <product>, SortBy:
   "RequestedDeliveryDateAtDestination" }`: list the open orders (order, quantity, requested date); say there are
   none if there are none (the product then builds stock). Drop deleted, completed and delivered lines.

### Refuse when blocked, unless "release anyway"

- **Ready:** go to the confirmation.
- **Blocked:** do **not** release. Say why (the component, the quantity short, what is on the way) and that releasing
  would create an order that can't start. Offer: fix the supply first (`inform-buyer-of-late-order.md`), or **release
  anyway** if the planner wants it (for example for a test).
- **Release anyway:** only when the planner says so in words ("release it anyway") or a board request is marked
  *release anyway*. The card then states plainly that the proposal is Blocked, with the blocker. The planner approves
  their own changes, so this is allowed, but never the default and never inferred from a plain "release".

## Confirm before writing

> **Release MO proposal <n>** (<product>, <qty> <unit>, <start> to <finish>, responsible <user>)
> Material: <Ready | BLOCKED (release anyway): <component> short <qty>, <what is coming>>
> Capacity: <ok | warning: <wc> (machine | labor) over its rating in week <w> | not checked>
> Waiting: <orders with quantity and requested date | no customer order, builds stock>
> Sets the status to Released (code 60). This is expected to create a manufacturing order; I can't undo it from here.
> Reply **yes** to release.

**For a list,** one card listing every proposal with its Ready or Blocked state, capacity warning and waiting
orders, and one yes for the whole list. Blocked ones are left out unless the planner said "release anyway" for them,
and are shown as "not released: blocked".

Only after an explicit yes: call `M3_PMS170MI_SetStatus` **once per proposal** with `{ PlannedOrderNumber: <n>,
PlannedOrderStatus: "Released" }` (a named status, not a number; `Released` is the name for code 60). One at a
time, in the order listed, each followed by its own read-back. If a call is refused as invalid, stop and tell the
user what it said; for a list, stop at the first failure and say which proposals were not attempted. Never retry a
write blindly. A yes to an earlier question never covers this one.

### When the planner releases from the dashboard board

The board's Release dialog follows this file: it re-reads the proposal, runs the checks of step 2 (material, capacity, waiting customer orders), refuses a Blocked proposal unless the
planner clicks **Release anyway**, asks for a tick when the proposal belongs to another responsible user, calls `M3_PMS170MI_SetStatus` once, and looks for the new MO (section 3) before it
logs the release as done. The board does not save requests for chat. In chat, run this whole file.

## 3. Read back (each proposal)

`M3_PMS170MI_SearchMOP` `{ PlannedOrderNumber_ExactSearch: <n> }`: the proposal should be gone. M3 may keep it listed
for a moment: read again once or twice before concluding. The new order can also appear a few minutes after the
proposal has gone (in the test it took a few minutes the second time): keep looking over a few minutes, and if you
can't find it yet, say the release ran, the proposal is gone, and the order isn't visible yet; set a board request to
`unverified`, not `done`, and look again when asked. Then find the new manufacturing order:
1. `M3_PMS100MI_SearchMO` `{ Responsible_ExactSearch: <the proposal's responsible user>, Facility_ExactSearch,
   Warehouse_ExactSearch, WorkOrderStatus_LessThan: "OrderCompleted", SortBy: "PlannedFinishDate" }`, and pick the
   order with the same product and quantity. **Don't require the same start date:** M3 schedules the new order itself
   (in a test, the new MO started a day earlier than the proposal). Don't use a product-only search (it returned nothing).
2. If it isn't listed, the new order may not carry the responsible user yet: take the highest MO number you know and
   read the next few with `M3_PMS100MI_Get` `{ Facility, ManufacturingOrderNumber: <next number>, ProductNumber:
   <product> }` until one matches the product and quantity.
3. Show it: number, product, quantity, start and finish (dates and times), status. If you still can't find it, say
   the proposal is gone but the order isn't visible yet, and suggest checking in M3. Never claim success without
   finding the order.

## Show it

Chat: the card(s), then a short result per proposal. After a release, say what is still open: the new MO now
belongs on the at-risk list if it was blocked, and any waiting customer order still depends on it.

### Result line

```
Proposal <n> released: <product> x <qty> -> MO <number> (<start>-<finish>), status <status> [blocked: <component>]
```

## Next step

"Want the full check on MO <number>?" (`material-shortage-check.md`); "Want to see your other proposals?"
(`mo-proposals.md`); for a blocked release, "Want the buyer told what is short?" (`inform-buyer-of-late-order.md`).

## Edge cases

- **Nothing found** - "No proposal <n> for <user>."
- **Several matches** - list and ask.
- **Can't see it / not permitted** - report; don't retry; don't try another route.
- **Blocked** - refuse unless "release anyway" (above).
- **Capacity or waiting orders couldn't be read** - say so on the card; they never block.
- **Pasted request doesn't match M3** (product, quantity or date differs) - say what differs and ask which is right.
