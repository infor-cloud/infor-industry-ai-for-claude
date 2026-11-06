# M3 tool conventions and known tool behaviour

Shared reference. Tool names are `M3_<PROGRAM>_<Transaction>` as the M3 connector shows them; the client adds its own
prefix, which differs per install. Always check the live tool list: a tool can be missing or defined differently in a
given system. Inputs marked required must be sent.

<!-- contents:start -->
**Contents**

- General
- Purchasing (PPS)
- Items, stock and planning (MMS)
- Customer orders (OIS)
- Manufacturing (PMS)
- Messages and jobs (CRS, MNS)
<!-- contents:end -->

## General

- **Load tools by their exact name**, the ones the step needs, in one tool search, and use the exact parameter names
  you get back. Some transactions only load when
  searched by their exact name; a loose search often loads unrelated tools, including write tools. Loading a write tool is
  not permission to use it.
- **Use `Search…` transactions for lists** (for example `SearchLine`, `SearchHead`, `SearchPOP`, `SearchMaterial`) and
  filter on what you need. Use `Lst…` transactions only where a skill names them. List transactions usually cannot be
  filtered to a specific set of data and return too much or the wrong rows; if a search transaction exists for the data,
  prefer it, even when a `Lst…` one is named in a loose way.
- **Status filters** take names, in the exact form of each tool: names with the code in brackets on
  `PPS200MI_SearchLine` (for example `LowestPurchaseOrderStatus_LessThan` = `GoodsReceived (50)`); plain names on
  `PPS200MI_SearchHead` (for example `Printed`) and on `PMS100MI_SearchMO` (`WorkOrderStatus_LessThan` = `OrderCompleted`).
  Results can come as a name, as a name with the code in brackets, or as a number: read the code.
- **Dates** are `YYYY-MM-DD`. M3 returns both `20261022` and `2026-10-22`; read both, show one format. M3 can hold both a
  warehouse-time and a customer-destination version of a date (`...AtDestination`).
- **Search tools cut their results off silently** (about 30 rows on some tools, 100 on others). A list that ends on a
  round number may be incomplete: narrow the search and say so.
- **A call can return nothing and still have worked, or fail and still have saved.** Most write tools return `{}` on
  success. Always read back.
- **Some updates are processed in the background**: a read straight after a write can still show the old values. Wait a
  moment and read again before concluding (examples below).
- **Metadata errors.** If a tool returns "metadata is misconfigured" (the error says "do not retry"), stop calling that
  tool, tell the user in one line that an administrator must fix the tool definition, and use the alternative.
- **Orders change between sessions**: re-read before acting on anything read earlier.
- **Authority is checked per transaction.** A tool returns an error when the signed-in user has no authority for it
  (for example `PPS170MI_CrtPOP`, `PPS170MI_RelPOP`, `PPS370MI_*`, `PPS001MI_ConfirmLine`). Reads and writes can differ,
  and so can two tools of the same program. See `write-protocol.md`, "When M3 refuses for lack of authority". A tool
  missing from the connector is not the same thing.
- **Numbers can come as strings** (for example the balances from `MMS200MI_LstItmWhsByItm`): convert them.
- Order numbers are 10 characters.
- **"Record does not exist" on a list or a search is an empty result, not a failure.** M3 answers a list or search
  transaction with this message when nothing matches: for example `MMS020MI_LstItemRelation` for a replacement type that
  has no relations for the item (type 5 often has none), `PPS115MI_LstAltSupplier` for an item with no agreement, or a
  search with no hits. Treat it as an empty list, keep the other results and carry on. It is an error only on a read of
  one named record (a `Get`, such as the MO itself) or when the text is anything else.

## Purchasing (PPS)

- **`PPS200MI_LstLine` fails** with a metadata error (a price field is defined as an integer but returns a decimal). Do not
  use it and do not retry it. To list a PO's lines use `PPS200MI_LstLine2`; to read one line use `PPS200MI_SearchLine`
  with `PurchaseOrderLineNumber_ExactSearch`.
- **`PPS200MI_GetLine` takes no line number** (only the PO number) and fails with "line does not exist".
- **`PPS200MI_SearchLine`** has no order date in its output (it comes from `SearchHead`). `ConfirmedDeliveryDate` is a
  filter, and appears in the output only once it is set. It is updated with a slight delay: right after a write it can
  miss a new line, or show only some of the lines of a new PO; `LstLine2` shows them all.
- **Date filters on `PPS200MI_SearchLine` are unreliable.** `Buyer_ExactSearch` with `RequestedDeliveryDate_LessThan`
  returned nothing although a matching line existed. If a date filter returns nothing, search on the other filters and
  compare the dates yourself.
- **`PPS200MI_UpdLine` cannot change the item** (no item field). It changes name and description text, price, dates,
  terms, and similar. Never present it as a substitution.
- **`PPS200MI_AddLine` and `PPS200MI_DltLine` return an empty result on success.** `DltLine` returns an error if M3 does
  not allow the delete for that status.
- **`PPS200MI_GetHead`** (`PurchaseOrderNumber`) returns the PO currency and totals (see `m3-concepts.md`, Currency).
- **`PPS200MI_LstReceiptsByPO`** (`PurchaseOrderNumber`) lists goods receipts with `TransactionDate`, quantity, line and
  suffix: the source for receipt dates. `LstLineTrans` needs a transaction type.
- **`PPS001MI_ConfirmLine`** takes `PurchaseOrderNumber`, `PurchaseOrderLineNumber`, `PurchaseOrderLineSuffix` (0 for an
  unsplit line) and optionally `ConfirmedDeliveryDate`, `ConfirmedQuantity`, `ConfirmedPurchasePrice` and `FinishMark`
  (send 1 to mark the line complete, so the unconfirmed rest is dropped). The connector's tool definition may not list
  `FinishMark`: send it anyway. **A confirmed quantity below the ordered quantity splits the line unless `FinishMark` = 1 is
  sent:** the confirmed part stays on suffix 0 (its ordered quantity is cut to the confirmed one, status 35) and the rest
  becomes suffix 1 at its old status and date, still counted as supply in the plan. It returns no data. Read the result back
  with `SearchLine` on the whole PO (status 31, 32, 33 or 35); it updates with a slight delay, and a read with the line number
  can show only suffix 0 for a while.
- **`PPS001MI_FinishMark`** takes `PurchaseOrderNumber` and closes the order (or line) as complete. Use it only to close a
  full line or order that is no longer wanted. Never use it to drop the rest of a line after a smaller confirmation: that is
  `FinishMark` on `ConfirmLine`, in the same call. Its definition lists only the PO number, so with it a whole PO can be
  closed: see the buyer's PO-actions flow before calling it.
- **`PPS170MI_Select`**: never use it (it returned nothing when `SearchPOP` returned the planned POs).
- **`PPS170MI_SearchPOP` ignores `PlannedOrderStatus_ExactSearch`**: read the status in the rows.
- **`PPS170MI_CrtPOP` requires `PlannedOrderStatus`.** The planner always sends `Pur/planMan` (status 20, firm planned
  order); `PlanOrdMan` (10) and lower can be removed or recalculated by the next MRP run. Check the status after creating with
  `PPS170MI_GetPlannedPO` (exact read by planned order number), falling back to `SearchPOP`; the only status correction
  allowed is `UpdPlannedPO` with `Pur/planMan`, in the planned-PO flow.
- **Releasing a planned PO is two steps:** `PPS170MI_UpdPlannedPO` to status `Released` (60), then `PPS170MI_RelPOP`.
  `RelPOP` runs as a batch job: the PO appears after a moment. `UpdPlannedPO` refuses a planned PO with a user that does
  not exist. Details in the buyer's planned-PO flow.
- **`PPS600MI_PrintPO`** returns a job number: the print runs as a job, and the job queue cannot be read.
- **`PPS115MI_LstAltSupplier`** (alternate suppliers per item) works. Pass `ItemNumber`; the result includes `Currency`,
  `NetPriceLocalCurrency`, `LocalCurrency` and `SupplyLeadTime` (0 = not maintained). If it returns a metadata error, stop
  and say so.

## Items, stock and planning (MMS)

- **`MMS200MI_LstItmWhsByItm` without `Warehouse` returns every warehouse for the item** (very long). Pass `Warehouse`
  when you need one warehouse.
- **`MMS200MI_LstSumWhsBal` needs an alias number**, so it does not fit a stock check per warehouse.
- **`MMS020MI_LstItemRelation`** returns no quantity factor and no price, and mixes substitutes with accessories and
  cross-sell items. Which relation types count as alternatives is a persona rule (see `known-inconsistencies.md`, K1).
- **`MMS120MI_AllocateOrdLine` and `MMS120MI_DeAllocateOrLne`** take `OrderNumber` (M3's reference order number; for a customer order, the order number), `OrderLineNumber`,
  `AllocationOrigin` (the code for manual allocation, asked once, `settings.md`) and `StockTransactionType` (`CustomerOrderIssue`,
  transaction type 31, for a customer order). De-allocate removes the whole allocation of the line (there is no quantity).
  Both answer success even when nothing changed: read the line back. Automatic allocation can allocate freed stock to
  another order at once.

## Customer orders (OIS)

- **`OIS100MI_GetLine`** needs the line number.
- **`OIS100MI_SearchLine_LimitedOutput`** searched on the item alone returns the whole history (invoiced and completed
  lines too). Filter on `ItemNumber_ExactSearch` and, when the tool accepts it, on open order status; otherwise filter the
  result yourself and keep only open lines.
- **`OIS100MI_UpdCOPlanDates`** does not write at once: it queues a batch update and returns a job id; `GetUpdateSts` and
  the batch order list show it. On some systems the update is processed but the dates do not change, or the autojob does
  not run. Always read the line back.
- **Do not use:** `OIS100MI_DltLnInfo` (it deletes only the extra information of a line, not the line),
  `OIS100MI_UpdCnfDlyDate` (removed in M3), `OIS100MI_ReleaseOrder` (only for locks made with LockOrder).

## Manufacturing (PMS)

- **`PMS100MI_Get` has no responsible user** (see `m3-concepts.md` for who is responsible for an MO's material).
- **`PMS100MI_SelOrderHead`**: `TimestampDateFilter` selects MOs changed on or after that date, so pass a date well before
  today; `SchedulingHorizonDays` did not visibly change the result in tests: filter by date yourself.
- **`PMS100MI_SearchMO` searched on the product only returned nothing**: search by responsible user, facility, warehouse
  and status.
- **`PMS100MI_LstByRORN`** (MOs by reference order) found no linked lower-level MOs in tests ("Record does not exist"): use
  the semi-finished component's own MO instead.
- **`PMS100MI_Reschedule`** takes one date, start or finish, never both; it is processed in the background (status
  "...-ChangeInProgress") and raises the MO's priority to high. Details in the planner's reschedule flow.
- **`PMS170MI_SetStatus`** (`Released`) turns an MO proposal into an MO; the new MO can appear a few minutes later.
- **Search operators are `_LargerThan` and `_LessThan`** (and `_ExactSearch`, `_NotEqualTo`). A name that doesn't exist, such as
  `_GreaterThan`, is ignored without an error, so the filter silently does nothing.
- **Unfiltered `PMS100MI_SearchMO` and `PMS170MI_SearchMOP`** return the oldest first and are cut off (about 30 rows), so
  years-old open orders fill the list. Add a bound, and expect a date bound or an order-number floor alone to miss some
  orders: merge several searches by number.
- **`PMS100MI_SelOrderHead`** returns, for each MO, its product structure type, responsible user, order type, process code
  and M3's action message (for example `DeleteOrder`), which `PMS100MI_Get` and `PMS100MI_SearchMO` do not.
- **`PMS170MI_CrtPlannedMO`** (create an MO proposal) returns the planned order number and subnumber. M3 refuses a blank
  `ProductStructureType` when structure types are in use, although the tool lists it as optional; `SimulationId` 0 and
  `PlanningTime` 0 were accepted and gave a real proposal. It has no responsible input: M3 sets the item and warehouse
  responsible user, and an unlisted `ResponsibleUser` field is accepted without an error and ignored. Status `Pur/planMan` (20) shows as a firmed planned MO, `PlanOrdMan` (10) as a planned order. Read it
  back with `PMS170MI_Get`; a search by planned order number or by product can miss it for a few reads.
- **`PMS100MI_CrtMO`** (create an MO) returns the MO number. M3 refuses without `ManufacturingUnitOfMeasure` ("Manufacturing
  U/M does not exist"), although the tool lists it as optional, and needs the structure type. The new MO is not readable
  for about a minute ("Record does not exist"); its components and operations show as soon as it is. `ResponsibleUser` and
  `Description` are accepted.

## Messages and jobs (CRS, MNS)

- **Application messages** (`CRS420MI`): see `application-messages.md`.
- **`MNS320MI_Search` (batch jobs) fails** with "Related table CJBCTL is not indexed": do not retry; find the result of a
  batch job instead.
