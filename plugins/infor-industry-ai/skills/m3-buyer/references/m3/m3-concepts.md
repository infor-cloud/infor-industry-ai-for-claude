# M3 concepts used by every persona


Shared reference for the Infor Industry AI skills. Status code tables are in `status-codes.md`, tool behaviour in
`tool-conventions.md`, writes in `write-protocol.md`.

<!-- contents:start -->
**Contents**

- Who the user is, and today's date
- The three dates
- Lowest and highest status
- Split lines (suffix)
- Currency
- Stock: on hand, free, and lead time
- Manufacturing orders
- Who is responsible for what
<!-- contents:end -->

## Who the user is, and today's date

- Call `M3_MNS150MI_GetUserData_CurrentUser` once at the start and keep, for the whole conversation: **`User`** (the M3
  user id, USID; in M3 the buyer code *is* a user id), **`Warehouse`** (default warehouse, WHLO) and **`Facility`** (default
  facility, FACI). If a value is empty or the call fails, say which one is missing and continue without it instead of
  guessing; a field that isn't there is unknown.
- A user's name: `M3_MNS150MI_GetUserData` (`User`) returns `UserName`. Show people as "Name (CODE)".
- **Today** is the M3 system date from `M3_ARS200MI_ServerTimeZone`; fall back to the conversation date. Never assume a
  date or carry one over from earlier work.
- **Company and division** come from the user session. Add them only if a tool requires them; never guess or default them.
- Each persona decides what "mine" means (the buyer field, the MO responsible, the rep's customers): see that persona's
  skill. State in every answer which scope you used.

## The three dates

A delivery is about three different dates. Never mix them.

- **Requested delivery date:** when we want the supplier to send the goods, or when we should receive them, depending on
  the delivery terms. On a customer order: the date the customer asked for.
- **Planned (planning) date:** the date the goods should be available in our stock. It can differ from the requested
  date, for example because of delivery terms. For a customer, a planning date is a **projected** date: say "projected".
- **Confirmed date:** what the supplier has promised, or what was promised to the customer.

Rules:
- **Lateness of a PO line** is judged on the confirmed date, or the requested date if there is no confirmation. Do not use
  the planned date for that.
- **Arrival and slack** in the material plan are compared on the planned date, because that is when the goods are in
  stock: slack = need date of the affected order minus planned arrival date.
- In the material plan `AlternatePlanningDate` is the date M3 suggests for the supply. Show it as "M3 suggests moving this
  to <date>" and say it is a suggestion, not a promise from the supplier.
- Never state a date to the customer that M3 has not confirmed.

## Lowest and highest status

An order or line has a **lowest** and a **highest** status. If the user asks about "status" without saying highest or
lowest, use the **lowest** status: it shows what is still outstanding. Use the highest only when asked, and say which one
you used. A PO or line with lowest 35 and highest 75 is partly received: the open part is still confirmed and waiting.

## Split lines (suffix)

A PO line can appear more than once with different `PurchaseOrderLineSuffix` values (for example suffix 0 holds the part
already received and suffix 1 the confirmed rest).
- Group by PO number and line number. Judge delay on the **open part** (the suffix with status below 50), not on the
  received part. A suffix at 50 to 70 is "received, not put away".
- Open quantity = confirmed quantity − received quantity on the open suffix.
- Count a split line once in KPIs, and show each open suffix separately only when dates differ.

## Currency

- Never assume a currency and never convert. **Never write that a PO has no currency or that its currency is missing:**
  look it up as below. If an amount still comes back without a currency, show the number as it is, with no currency symbol
  or code; if you add or compare such amounts, say once that the currency is not given.
- **First source: the PO header.** The PO currency is on the header, the same on all its lines: read it with
  `M3_PPS200MI_GetHead` (`PurchaseOrderNumber`): `Currency` and `CurrencyName`, plus `NetOrderValue`, `TotalOrderCost`,
  payment terms, `DeliveryMethodName` and `ResponsibleUserName`. Use the header currency for every line of that PO.
  `PPS200MI_SearchLine` and `SearchHead` return no currency: that is a reason to read the header, not something to report.
- **Second source: the agreement.** If `GetHead` can't be read (a metadata error: do not retry), take the currency from
  `M3_PPS115MI_LstAltSupplier` (`ItemNumber` of the PO line): the `Currency` of the agreement with the PO's supplier. Use
  `Currency`, not `LocalCurrency`. Say in one line that the currency comes from the agreement. Only when neither source
  gives a currency, write "currency not available".
- `M3_PPS170MI_SearchPOP` (planned POs) returns a `Currency`: show it, because it is given.
- Customer order values carry their own currency (`M3_OIS100MI_GetLine`).
- **Agreement prices are in local currency, PO prices in the PO currency.** `M3_PPS115MI_LstAltSupplier` gives
  `NetPriceLocalCurrency` with `LocalCurrency` and the agreement `Currency`. Compare prices only in the same currency, and
  say which.
- M3 decides a sales price from the item file or price lists; a price sent on a customer order line is ignored.

## Stock: on hand, free, and lead time

- **Free stock** means on hand and not allocated (soft or hard) to another order.
- **Free to allocate in a warehouse** = `AllocatableNet` from `M3_MMS200MI_GetItmWhsBal_Subname` (or `GetItmWhsBal`).
- **Free for a distribution order from another warehouse** = `AvailableInventory` in that warehouse.
- `M3_MMS200MI_LstItmWhsByItm` (company and item) returns every warehouse that carries the item with
  `ApprovedOnHandBalance`, `ReservedQuantity`, `AllocatableNet`, `AvailableInventory`, `ProjectedOnHandEndOfLeadTime`,
  `SafetyStock`, `LeadTime`, `SupplyLeadTime`, acquisition code, supplying warehouse, the default supplier and the item's
  buyer. The numbers come back as strings: convert them. Pass `Warehouse` when you need one warehouse; without it the
  answer covers every warehouse and is very large.
- Stock above safety stock is what can be used without breaking the buffer.
- **Lead times come from M3, not from memory**: the item/warehouse `LeadTime` (`MMS200MI_LstItmWhsByItm`). A
  `SupplyLeadTime` of 0 means "not maintained", not "immediate": never present it as an arrival date.

## Manufacturing orders

- `M3_PMS100MI_Get` needs `Facility`, `ManufacturingOrderNumber` and `ProductNumber` (in the material plan the product
  is in `ReferenceText` of the MO's record). It returns status, priority, start and finish date and time, ordered and
  received quantity, warehouse and the reference order category and number (a customer order link if there is one). It
  has no value and no responsible user.
- Say "manufacturing order" the first time and "MO" after; say "semi-finished goods" for made components.

## Who is responsible for what

| Question | Where it comes from |
|---|---|
| The item's **buyer** | The item/warehouse record (`M3_MMS200MI_LstItmWhsByItm` returns it) |
| The buyer of a PO line or planned PO | `Buyer` on the line or planned PO |
| **"My MOs"** for a planner | `Responsible` on `M3_PMS100MI_SearchMO` (`Responsible_ExactSearch`) |
| Whom to ask about an **MO's material** (for example a substitute) | The `ResponsibleUser` of the MO product's item/warehouse record: `M3_MMS200MI_GetItmWhsBasic` (item = MO product, warehouse = MO warehouse) |
| The **customer order responsible** | `ResponsibleUser` from `M3_OIS100MI_GetOrderHead`. If that is the buyer himself, write to the **salesperson** on the order (`Salesperson`) and say which field you used |
| The **salesperson's name** | `M3_CRS100MI_Get` (`Salesperson`). The salesperson record carries no M3 user id and no email; check the code with `M3_MNS150MI_GetUserData` before sending anything, and never guess a user |
| The **planner** of a manufacturing order | The user named for the manufacturing order (`Responsible` on the MO); if there is none, ask (`settings.md`) |
| Is a person an M3 user? | `M3_MNS150MI_GetUserData` (`User`): nothing back, or "does not exist", means no |
