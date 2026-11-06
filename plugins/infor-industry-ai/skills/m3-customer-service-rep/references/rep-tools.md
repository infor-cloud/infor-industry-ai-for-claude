# M3 tools used by the rep skill

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_MNS150MI_GetUserData`, `M3_CRS610MI_SearchCustomer`, `M3_MMS200MI_SearchItem`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS080MI_LstMtPlByItmWhs`, `M3_MMS020MI_LstItemRelation`, `M3_OIS100MI_SearchHead_LimitedOutput`, `M3_OIS120MI_GetCOStopInfo`, `M3_PPS200MI_SearchLine`, `M3_PMS100MI_Get`, `M3_DPS001MI_LstRelation`, `M3_OIS100MI_GetUpdateSts`, `M3_OIS275MI_SearchBatchLine`, `M3_OIS100MI_AddBatchHead`, `M3_OIS100MI_SndBatchLine`, `M3_OIS100MI_Confirm`, `M3_OIS100MI_LstErrMsgOrder`, `M3_OIS100MI_AddOrderLine`, `M3_OIS100MI_DelLine`, `M3_OIS100MI_DelHead`, `M3_MMS120MI_AllocateOrdLine`, `M3_MMS120MI_DeAllocateOrLne`, `M3_DPS170MI_CrtPlannedDO`, `M3_DPS170MI_DelPlannedDO`, `M3_OIS100MI_UpdCOPlanDates`, `M3_OIS010MI_LstOrderTypes`, `M3_OIS010MI_Get`, `M3_MNS150MI_LstUserData_ListUserData`

Names are as the M3 connector shows them (`M3_<PROGRAM>_<Transaction>`). Always check the live tool list: a tool can be missing or defined differently
in a given system. Inputs marked required must be sent. Outputs not listed here are not needed.

## 1. Conventions that matter

The shared conventions are in `m3/tool-conventions.md` (dates and `...AtDestination`, order numbers, search cut-offs, the
list-per-warehouse tool, reading back after every call) and `m3/status-codes.md` (customer order line and plan statuses).

## 2. Reading

| Purpose | Tool | Notes |
|---|---|---|
| Current user, company, division, facility, warehouse | `M3_MNS150MI_GetUserData_CurrentUser` | |
| A user's name | `M3_MNS150MI_GetUserData` (`User`) | Returns `UserName`; show people as "Name (CODE)" |
| Customer search | `M3_CRS610MI_SearchCustomer` | Wildcards with `*`; always sort. `GetBasicData`, `LstAddresses` for details and ship-to |
| Item search | `M3_MMS200MI_SearchItem` | Wildcards with `*`; exact search on the item number |
| Free stock in a warehouse | `M3_MMS200MI_GetItmWhsBal_Subname` | `AllocatableNet` is the free quantity |
| Stock per warehouse | `M3_MMS200MI_LstItmWhsByItm` | Give `Warehouse`; also returns acquisition code, supplying warehouse and the item's buyer |
| Material plan | `M3_MMS080MI_LstMtPlByItmWhs` | Rows by date: category (CustomerOrder, PurchaseOrder, ManufacturingOrder2, PlannedPo, PlannedDo...), status, quantity, projected balance, `AlternatePlanningDate` (M3's suggested date), allocated quantity |
| Alternative items | `M3_MMS020MI_LstItemRelation` | `ReplacementType` text carries the code; **types 1, 2, 3 and 4 = alternatives**, read from the line's item to the related item |
| Order headers / lines | `M3_OIS100MI_SearchHead_LimitedOutput`, `GetLine`, `SearchLine_LimitedOutput` | `GetLine` needs the line number; `SearchLine` also returns the picked-list quantity (0 until a picking list is printed) |
| Credit status | `M3_OIS120MI_GetCOStopInfo` | Stop code and credit room. Stop codes 1 to 8 are credit stops; 9 is released by hand |
| Purchase order lines | `M3_PPS200MI_SearchLine` | Status text, dates, supplier, buyer |
| Manufacturing order | `M3_PMS100MI_Get` | Needs facility, order number and product |
| Warehouse relation | `M3_DPS001MI_LstRelation` | Needs `RelationType` "Distr-TwoWhs (1)", `FromWarehouse`, `ToWarehouse`. An empty answer means no relation; a hit returns the transport days and hours |
| Batch update status | `M3_OIS100MI_GetUpdateSts` | |
| Batch order list | `M3_OIS275MI_SearchBatchLine` | Status "OrderCreated (90)" means processed |

## 3. Creating and changing orders

- **Create:** `M3_OIS100MI_AddBatchHead` (customer, order type, facility, warehouse, responsible user, requested date, order date for backdating),
  `M3_OIS100MI_SndBatchLine` per line (item, order number, quantity, **`AlternateUnitOfMeasure`**, requested date, warehouse; optionally a confirmed date),
  `M3_OIS100MI_Confirm` (returns the firm number). Error log: `M3_OIS100MI_LstErrMsgOrder`. A price sent is ignored: M3 uses the item file or price list.
- **Add a line to an existing order:** `M3_OIS100MI_AddOrderLine` (order, item, quantity, warehouse, unit). If M3 raises a warning it returns only a message
  code and adds nothing; send `IgnoreWarnings` = true only after the rep accepted the warning. The new line takes the order's requested date.
- **Delete one line:** `M3_OIS100MI_DelLine`. It leaves a gap in the line numbers: line readers must skip gaps.
- **Delete an order:** `M3_OIS100MI_DelHead`, only after a new explicit yes for that order, never as a default step
  (`m3/write-protocol.md`).
- **Do not use:** `M3_OIS100MI_DltLnInfo` (it deletes only the extra information of a line, not the line), `M3_OIS100MI_UpdCnfDlyDate` (removed in M3),
  `M3_OIS100MI_ReleaseOrder` (only for locks made with LockOrder).

## 4. Allocation

`M3_MMS120MI_AllocateOrdLine` and `M3_MMS120MI_DeAllocateOrLne`: see `m3/tool-conventions.md` (inputs, no quantity on
de-allocate, success even when nothing changed, automatic allocation of freed stock). The allocation origin is asked once and the stock
transaction type is M3's standard (`m3/settings.md`).

## 5. Distribution order proposals

`M3_DPS170MI_CrtPlannedDO`: `FromWarehouse`, `Warehouse` (the receiving one), `ItemNumber`, `PlannedQuantity`, `PlanningDate`, `PlannedOrderStatus` = `Pur/planMan` (status 20, firm; not `PlanOrdMan`, which gives status 10).
It returns the planned order number, and the proposal is visible at once in the receiving warehouse's plan (category PlannedDo, status 20, firm). It needs no
inbox step. `M3_DPS170MI_DelPlannedDO` deletes a proposal: only delete proposals that were made for the rep's own work, never the ones M3's planning made.
There is no tool to read a proposal's planner.

## 6. Dates

Changing dates uses `M3_OIS100MI_UpdCOPlanDates`: `OrderNumber`, **one** date field (`ConfirmedDeliveryDate` or `RequestedDeliveryDate`; M3 refuses both the warehouse and the destination version of the same date in one call), and `LineNumber` only when one line should change (empty = all lines). **Leave `UpdateMode` out:** with no mode M3 applies the change at once and the answer is empty. Mode "A" runs through autojob OIS960, which did not run in the test environment, and mode "S" returns a job id whose status (`GetUpdateSts`, "NotStock") says nothing about whether the dates changed. The confirmed date is kept on the order **lines**, not on the order header. It works only for customer order types where the field "Confirmed delivery date" is open for change: in OIS014 (field selection of the customer order type) its entries are blanked out, which opens the field in OIS101/I, and then the API change goes through too (reported by the tenant's M3 consultants). M3 gives no reason when a date does not change: point to possible directions (a field closed in OIS101/I, connected settings such as the delivery route and its departures, an availability check) without claiming one of them is the cause. On a type where it is not open, M3 accepts the call **without an error** and the date stays (tested: `m3/known-inconsistencies.md`, K26). **Always
read every changed line back, with the line numbers M3 gives (some order types number lines 10, 20, 30, not 1, 2, 3), and say plainly which line did not change.** Do not draft a customer update for a date M3 does not hold.

## 7. Application messages (alerts and reminders)

Follow `m3/application-messages.md`. The message type is asked once (`m3/settings.md`).

## 8. Reads only the dashboard makes

The dashboard (`assets/rep-dashboard.html`) reads three more things that no chat flow needs. They are listed here so the build check can confirm the connector offers them:
- `M3_OIS010MI_LstOrderTypes`: the customer order types (category 1) for the Create Order type picker; `M3_OIS010MI_Get` reads one type's description.
- `M3_MNS150MI_LstUserData_ListUserData`: the list of users for the "Responsible user" dropdown and the search for other sales reps (30 users per call).

## 9. Other notes

- How orders are allocated, automatically or by hand, depending on the order type: `m3/status-codes.md` (customer order lines).
- Two warehouses can be linked in both directions only if M3 allows it: an item cannot be supplied from a warehouse that is itself
  supplied from the first.
