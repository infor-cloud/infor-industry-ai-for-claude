# Reading the M3 material plan

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MMS080MI_LstMtPlByItmWhs`, `M3_MMS080MI_LstPOHBalance`, `M3_MWS150MI_SelSupplyChain`, `M3_MWS121MI_LstDmdByAcqOrd`, `M3_OIS100MI_GetLine`, `M3_OIS100MI_GetOrderHead`, `M3_CRS610MI_GetBasicData_CustomerName`, `M3_PMS100MI_Get`, `M3_MMS100MI_LstLines`

Shared reference. Category and status codes are in `status-codes.md` ("Material plan").

## `M3_MMS080MI_LstMtPlByItmWhs` (item and warehouse)

Lists every planned or actual movement for one item in one warehouse, **all order types in one list**: customer orders,
distribution orders, purchase orders, manufacturing order materials, planned orders, forecasts and so on. Fields per
record:

| Field | Meaning |
|---|---|
| `PlanningDate`, `TransactionTime` | When M3 expects the movement. Sort on both. |
| `TransactionQuantity` | **Positive = supply** (goods coming in), **negative = demand** (goods going out). |
| `ProjectedOnHandBalance` | Projected stock after this record. |
| `CumulativeAtpQuantity`, `NonCumulativeAtpQuantity` | Available-to-promise. |
| `OrderCategory` | The kind of order, as a **name** (for example `CustomerOrder`, `PurchaseOrder`, `ManufacturingOrder2`, `PlannedPo`, `PlannedDo2`, `DistributionOrder`), not a number. |
| `Status` | Number. Means different things per category (`status-codes.md`). |
| `ActionMessage` | For example `Delayed`: M3's own flag that the order is late; `RescheduleIn`: M3 wants it earlier. |
| `AlternatePlanningDate` | The date M3 suggests for the supply: a suggestion, not a promise. |
| `OrderNumber`, `OrderLineNumber`, `LineSuffix`, `DeliveryNumber` | Which order. |
| `PreallocatedQuantity`, `AllocatedQuantityBasicUom`, `ReservedQuantity` | Allocation on the record. |
| `ReferenceText` | Customer or supplier reference. For an MO record, the product. For distribution orders it shows the transfer as "from=>to" (for example "<from>=><this warehouse>" incoming, "<this warehouse>=><to>" outgoing). |
| `LevelMark` | Planning level mark. |

Rules:
- **Starting stock** = the first record's `ProjectedOnHandBalance` minus its `TransactionQuantity`.
- **An empty answer is not an answer about supply.** If the plan comes back empty for an item that clearly has supply,
  say that the call answered nothing; never conclude there is no supply, and never read an empty plan as "enough". Use
  the order lists and balances instead, and say the plan gave no lines.
- If the item's own record (the PO or the order you are asking about) is not in the plan, say that the impact could not
  be checked from the plan.
- Records with planning dates far in the past are stale: say so instead of treating them as urgent.
- Other records with `ActionMessage` = `Delayed` are late too (for example incoming distribution orders): mention them,
  since they also affect the balance.
- Reuse one result when several questions share the same item and warehouse; re-read when the data is more than a few
  hours old, because planning data goes stale fast.
- A new planned order may not show in the plan until M3's next planning run.

## `M3_MMS080MI_LstPOHBalance` (projected on-hand on one date)

Gives the projected on-hand balance per item and warehouse for a single `PlanningDate` per call. A balance below zero on a
date means demand exceeds stock plus planned supply on that date. To scan a window, sample several dates (see the
planner's shortage radar).

## Other ways to confirm a link between supply and demand

Use alongside the material plan:
- `M3_MWS150MI_SelSupplyChain` for a PO: the chain of orders it supplies. Call it with `OrderCategory` = `PurchaseOrder`,
  `OrderNumber`, `LineNumber` and `LineSpecification` (the line suffix). If it returns only the PO line itself (level 0),
  nothing is pegged to the PO: say so.
- `M3_MWS121MI_LstDmdByAcqOrd`: demand lines pre-allocated from this order.
- The linked reference order on a PO line or MO (`ReferenceOrderCategory`, `ReferenceOrderNumber`).

## Details per order found in the plan

- **Customer order:** `M3_OIS100MI_GetLine` (needs `OrderNumber` and `LineNumber`; returns value and currency) and
  `M3_OIS100MI_GetOrderHead` for customer, priority and requested dates; the customer name with
  `M3_CRS610MI_GetBasicData_CustomerName`.
- **Manufacturing order:** `M3_PMS100MI_Get` (facility, MO number, product from `ReferenceText`), or
  `M3_PMS100MI_SearchMaterial` for status, priority and dates. It has no value, and no
  link to a customer order unless `ReferenceOrderCategory` says so: say "value not available".
- **Distribution order:** `M3_MMS100MI_LstLines` for the DO line and destination.
- **Orders change between sessions.** A customer order read yesterday may be Deleted today (a replacement order may
  exist). Re-run the plan before acting, and read the header with `M3_OIS100MI_GetOrderHead`.
