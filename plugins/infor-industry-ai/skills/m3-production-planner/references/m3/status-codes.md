# M3 status codes and what they mean


Shared reference. Never show a raw code to the user: translate it. If a code is not in these tables, say
"status <code>" and ask the user what it means; do not guess.

<!-- contents:start -->
**Contents**

- Purchase orders: How to use the PO codes
- What "delayed" means
- Planned purchase orders (proposals): Planned PO status (field PSTS / PlannedOrderStatus) · Action message (field AM / ActionMessage) · Warning message (field MSGC / warning code)
- Material plan: order categories and statuses
- Customer order lines
- Credit stops
- Manufacturing orders
<!-- contents:end -->

Contents: purchase orders · what "delayed" means · planned POs (status, action messages, warning codes) ·
material plan (order categories and statuses) · customer order lines · credit stops · manufacturing orders.

## Purchase orders

Official M3 status codes for purchase orders (Part 1 of the status list). Results from the tools return the **numeric
code as text** (for example "35"); search **filters** accept the status **name** (see `tool-conventions.md` for the exact
form per tool). Compare by number.

| Stage | Code | Meaning |
|---|---|---|
| Not sent | 00 | New entry in progress |
| | 05 | Work in progress (becomes 10 when done) |
| | 06 | Work in progress (becomes 12 if authorization is required, otherwise 15) |
| | 10 | Manually set status, order cannot be printed |
| | 15 | Ready for printout |
| Stopped | 11 | Order stopped, value is below minimum |
| | 12 | Order stopped, authorization required |
| | 13 | Order stopped, accounting string required |
| | 14 | Order stopped, budget for the accounting string exceeded |
| Sent | 20 | Document printed and sent: **the supplier has the order**. Awaiting confirmation. (Whether a released order is sent automatically is a setting on the order type.) |
| Claim | 25 | Claim activated but not ready |
| Confirmed | 31 | Delivery date confirmed (price not yet) |
| | 32 | Purchase price confirmed (date not yet) |
| | 33 | Price and delivery date confirmed, **not approved** |
| | 35 | Price and delivery date confirmed and approved. **Confirmed** |
| On the way | 40 | Advised for shipment |
| | 45 | Notified for transportation |
| Received | 50 | Goods received |
| | 51 | Put away, but not quality inspected |
| Quality | 60 | Quality inspection partially performed |
| | 64 | Rejected after quality inspection, course of action not determined in claim routine |
| | 65 | Quality inspection completed |
| | 69 | Rejected after quality inspection, course of action determined in claim routine |
| Put away | 70 | Put-away partially completed |
| | 75 | Put-away complete |
| Invoicing, closed | 80 | Invoice reporting started |
| | 85 | Invoice reporting completed |
| | 90 | Monitoring still active |
| | 99 | Purchase order deleted |

Delivery schedules use 15 (ready for printing), 20 (printed), 30 (within locked planning period) and 99 (deleted).
Delivery notes (`PPS360MI`) use 29 (invalid data), 44 (catch weight missing for sublot), 46 (advised for shipment), 47
(notified for transport), 48 (staged quantity), 50 (goods received) and 90 (closed). Inquiry statuses do not apply to
purchase orders.

### How to use the PO codes

Status can come as a name with the code in brackets, for example "Printed (20)". Read the number in the brackets and
apply the rules below.

- **Delayed (supplier)** = status 20 to 49 and the date has passed. Only these are supplier delays.
- **Not yet sent to the supplier** = below 20 (for example 15 ReadyForPrintout) or stopped (11 to 14). The supplier does
  not know about the order, so a passed date is **our** delay, not the supplier's. Show it as its own category: the buyer
  must release and send it (or fix the date) first.
- **Received, not yet put away** = 50 to 70. The goods have arrived, so it is **not** the supplier's delay: the wait is on
  the company's side (put-away, quality inspection). Never call these late deliveries and never list them with the
  delayed lines. Show them as their own category, because the buyer needs to see them and chase internally (warehouse,
  quality). Quantity waiting = `ReceivedQuantity` − `StoredQuantity` when both are returned.
- **Awaiting confirmation** = 20. **Partly confirmed** = 31 or 32. **Needs your approval** = 33. **Confirmed** = 35. A line
  below 31 that has been sent (20 or 25) counts as unconfirmed.
- **Blocked** = 11, 12, 13 or 14. Show these separately and say why (value, authorization, accounting string, budget).
  They need a buyer action whatever the due date.
- **Not sent** = 00 to 15. Not a supplier delay; the order is still with the buyer.
- **Quality problems** = 64 and 69 (rejected after inspection). They belong to the "received, not put away" category, but
  mark them as rejected there: the goods are in but not usable, so the buyer may need a replacement or a claim.
- **On the way** = 40 and 45. Check the advised date against the need date.
- **Ignore for delays**: status 75 and above (put-away complete, invoicing, closed, deleted).
- Name filters work. For example, `LowestPurchaseOrderStatus_ExactSearch` = `Confirmed` returns orders whose lowest status
  is 35. Do not filter lowest and highest to the same name unless the user wants orders where *everything* is at that
  status.

## What "delayed" means

- **Delayed (supplier):** status 20 to 49 and the confirmed date (or the requested date, if there is no confirmation) has
  passed.
- **Late but not sent (our side):** status below 20 or stopped (11 to 14) and the requested date has passed.
- **Received, not put away (our side):** status 50 to 70. Not a supplier delay.
- **Ignore for delays:** status 75 and above.
- **Overdue planned PO:** a planned PO whose `ReleaseDate` is before today.

## Planned purchase orders (proposals)

These apply to planned purchase orders from `M3_PPS170MI_SearchPOP`. The search returns **names** for status and action
message (for example `AutoWarning`, `Rel-ReschedIn`). Translate them using the tables below. Never show a raw code or name
without its meaning. A planned PO is a proposal, not an order with the supplier: never count it as safe supply.

### Planned PO status (field PSTS / PlannedOrderStatus)

For a firm planned order the status is at least 20, except for errors and warnings (00 and 05).

| Code | Name in the tool | Meaning |
|---|---|---|
| 00 | `AutoError` | Assigned automatically for database errors or stops, as defined in the message code |
| 05 | `AutoWarning` | Assigned automatically for a database warning, as defined in the message code |
| 10 | `PlanOrdMan` | Planned orders and manual status |
| 15 | `PlanOrdAuto` | Planned orders where the item has several suppliers; automatic rescheduling of quantity not performed |
| 20 | `Pur/planMan` | Purchase requisitions, planned work orders and manually defined status |
| 30 | `PlanPolicy` | Set when the planning policy says status 60 (proposal, planned order) and the action is A1; can also be set manually |
| 40 | `ManualStatus` | Manual status |
| 50 | `ManualOrAuto` | Manual or automatic; the amount requires authorization processing |
| 55 | `AutoAssigned` | Assigned automatically when inquiries are created |
| 60 | `Released` | Manual or automatic; released to create a purchase or work order |

The tool also has a status `Closed`; its code is not in the status list we have. The code-to-name pairing above follows
the order of both lists and matches the test data (`Pur/planMan` = 20, `AutoWarning` = 05); treat it as reliable but not
officially confirmed.

How to use it: 00 means a stop (letter code); the planned PO must be changed before release, so read the warning message.
05 means a warning (numeric code); the planned PO can be released. 50 means authorization is needed first. 60 is already
released.

### Action message (field AM / ActionMessage)

An action message suggests a planning action. Categories: **A** release actions, **B** rescheduling actions, **C** delayed
orders, **D** external supply plan actions.

| Code | Meaning |
|---|---|
| A1 | Release and reschedule in the order (name in the tool: `Rel-ReschedIn`; matches by meaning) |
| A2 | Release order |
| A3 | Transform to firm planned order |
| A4 | Release distribution order return |
| A5 | Increase the period production quantity (inside lead time) |
| B1 | Reschedule in, released order (name in the tool: `RescheduleIn`; matches by meaning) |
| B2 | Reschedule in, planned order |
| B3 | Reschedule out, released order |
| B4 | Reschedule out, planned order |
| B5 | Increase the period production quantity |
| B6 | Maximum balance exceeds planning time fence |
| B7 | Delete order |
| B8 | Increase the planned quantity (only for order policy 15) |
| C1 | Released order is delayed |
| C2 | Released order will be delayed |
| C3 | Firm planned, order-initiated order with finish day within lead time |
| D1 | Target safety stock from external supply plan is not met |
| D2 | Additional required supply not covered by the external supply plan |
| D3 | Capacity may be exceeded |

Only A1 and B1 have tool names so far (`Rel-ReschedIn` and `RescheduleIn`). Other names seen: `ReleaseOrder`,
`DeleteOrder` (M3 suggests deleting the planned PO: the need has gone), `Delayed`. For other names the tool returns, say what
the name looks like it means and add "(name as given by M3)", or ask the user.

In plain words, `Rel-ReschedIn` (A1) says: release this planned PO, and the delivery date moves earlier. C1 and C2 mean a
released order is or will be delayed. An action message is M3 planning's own signal; show it next to your verdict and
don't override it, but note that it may predate new demand.

### Warning message (field MSGC / warning code)

The code explains a warning or stop on a planned PO. `SearchPOP` does not return it. To read it for a specific planned PO
use `M3_PPS170MI_GetPlannedPO` (not yet verified that it returns the code). **Numeric versus letter codes decide whether
release is possible:**

- **Numeric code** (02, 10, 15 … 70): a warning. The planned PO **can still be released**. Tell the user what the warning
  says and let them decide.
- **Letter or letter+number code** (D, E, F … Y, K1, X1 to X5): a **stop**. The planned PO **cannot be released** until it
  is changed. Say what has to change (for example F: get authorization; E: add a purchase price; V: not allowed to release
  per planning settings) and who normally acts. Never suggest releasing a planned PO with a stop code.

This matches the status: 05 (`AutoWarning`) carries a numeric warning and is releasable; 00 (`AutoError`) carries a stop
and is not.

| Code | Meaning |
|---|---|
| 02 | Budget for the account entry string will be exceeded by this transaction |
| 10 | Purchase order line amount is greater than the limit in the planning policy |
| 15 | Proposed order quantity is not a multiple of the order multiple |
| 20 | Item name or description is not correct according to the purchase order type settings |
| 30 | Proposed order quantity is less than the minimum order quantity for the item/supplier |
| 40 | Proposed order quantity is greater than the maximum order quantity for the item/warehouse |
| 50 | Order quantity exceeds the maximum quantity for this agreement |
| 55 | Order quantity is larger than the replenishment quantity or amount |
| 56 | Purchase order type is not defined in the PO type table, or the PO type category is not permitted (PO type check 2) |
| 60 | Planning parameters are manual (manual order quantity method, manual reorder point method, or both) |
| 65 | Item is not returnable to the supplier |
| 70 | Minimum line or order amount defined for the supplier has not been reached |
| 80 | A forecast alarm is activated for this item |
| 90 | The proposed order quantity has been changed since the planned order was created |
| 95 | The shipping calendar does not allow delivery on this date |
| 98 | The standard cost for this item is zero |
| 99 | Ordered by telephone |
| A | Supplier is not defined in the supplier file |
| A1 | Consolidation group (PPS019) does not include purchase organization and/or country as consolidation objects; these are mandatory on centrally procured planned POs (only if purchase organizations for planning are activated in CRS780/H) |
| A2 | Purchase organization is not valid, for example not connected to the warehouse (PPS199) (only if purchase organizations for planning are activated in CRS780/H) |
| A3 | Purchase organization is missing; it is mandatory if purchase organizations for planning are activated in CRS780/H |
| B | Item/supplier record is missing; the PO type parameters show whether this should be checked |
| C | Item/supplier record is not released according to its status (the status is not 20) |
| D | Item record or item/warehouse record is not released according to its status (status below 10 or above 40) |
| E | Purchase price does not exist and the price text code is blank |
| F | Authorization is required according to the authorization table |
| G | Error in communication definition: communication code missing; retrieve a value from the media profile |
| H | PO type is not defined in the PO type table, or the PO type category is not permitted |
| I | Error when the purchase order was created; may be a missing or undefined number series |
| J | Goods receiving method is missing |
| K | Incorrect agreement number (delivery schedules) |
| K1 | Purchase price is manually specified and different from the agreement price |
| L | Item does not belong to a delivery group defined for the supplier (PPS012) |
| N | Revision number is not valid |
| M | Planned order is connected to a customer order that is on credit stop |
| O | A manually entered account entry string is required according to setting 620 on the order type (F11 in PPS171) |
| P | Budget for the account entry string will be exceeded by this transaction |
| Q | Planned order is connected to a manufacturing or work order that is preliminary |
| R | Planned order is connected to a service order quotation or estimate that has not been released |
| S | Item does not exist as a variant (MPDVAN) |
| T | Order quantity exceeds the maximum agreed quantity for this agreement with purchase commitment 4 |
| U | Connected to a customer order that has not been paid, or that uses price guidance with a manual or copied sales price that must be approved |
| V | Planned order may not be released per purchase planning settings (PPS195) |
| W | Manufacturer is not approved for the item |
| X1 | Customer number for internal sales is not defined for the receiving warehouse |
| X2 | Item is not valid for internal sales (for example only sales items with category 00 "Normal item" can be used) |
| X3 | Supplying warehouse of the internal supplier is the same as the PO warehouse |
| X4 | Supplying warehouse of the internal supplier does not exist (MMS002) |
| X5 | Supplying warehouse of the internal supplier has an invalid status (MMS002) |
| Y | Planned order is connected to a work order that is inventory managed but the item is non-stocked |

**Possibly incomplete.** The list has the numeric warnings 02 to 70 and 80 to 99, then the stop codes A to Y. M3's own
heading for the letter codes is "warning messages for errors or stops". The source we have jumps from 70 to 80, so codes
between 71 and 79 may exist. If a code is not in the table, say "warning code <code>" and ask the user; do not guess.

## Material plan: order categories and statuses

The `Status` number in `M3_MMS080MI_LstMtPlByItmWhs` means different things depending on `OrderCategory`. Always read the
category first, then the status. Translate both ("customer order, allocated"), and never show only a number. The category
numbers come from M3's own list; the tool returns the category **names**, so use the name and the sign of the quantity to
find the row (for example `PlannedPo` is 250).

| Category | Name | Role | Status codes |
|---|---|---|---|
| 250 | Planned purchase order (`PlannedPo`) | supply | 10 Planned, 20 Firm, 30 Planning policy, 40 Manual status, 50 Manual or auto, 55 Auto assigned, 60 Released. Also seen: 05 (auto warning, from the planned PO status list) |
| 251 | Purchase order (`PurchaseOrder`) | supply | 10 Preliminary, 15 Registered, 20 Definitive, 35 Confirmed. A PO record can also carry a stopped status, for example **12 stopped, authorization required** (also 11, 13, 14): the PO is not yet with the supplier |
| 100 | Planned manufacturing order | supply | 10 Planned, 20 Firm |
| 110 | Planned manufacturing order | demand (material) | 10 Planned, 20 Firm |
| 101 | Manufacturing order | supply | 10 Preliminary, 20 Definitive, 50 Scheduled, 60 Started |
| 111 | Manufacturing order (`ManufacturingOrder2`) | demand (material) | 10 Preliminary, 20 Definitive, 33 Allocated, 44 Picking list |
| 311 | Customer order (`CustomerOrder`) | demand | 22 Reserved, 23 Res/Alloc, 24 Res/Pickl, 26 Res/Del, 27 Res/Inv, 29 Res/Compl, 33 Allocated, 34 Alloc/Pickl, 36 Alloc/Del, 37 Alloc/Inv, 39 Alloc/Compl, 44 Picking list, 46 Pickl/Del, 47 Pickl/Inv, 49 Pickl/Compl |
| 500 | Planned distribution order | supply | 10 Planned, 20 Firm, 60 Released |
| 510 | Planned distribution order (`PlannedDo2`, seen as outgoing, for example "<from>=><to>", status 10) | demand | 10 Planned, 20 Firm, 60 Released |
| 501 | Distribution order (`DistributionOrder`) | supply | 22 Definitive, 33 Allocated, 44 Picking list, 66 In transit |
| 511 | Distribution order (`DistributionOrder`) | demand | 22 Definitive, 33 Allocated, 44 Picking list |

Reading the customer order codes: 22 to 29 are *reserved* (stock set aside but not yet allocated to a pick; "Reserved",
status 22, holds nothing), 33 to 39 are *allocated*, 44 to 49 are *on a picking list*. The second part of the label (Pickl,
Del, Inv, Compl) shows how far the order has progressed (picking list, delivered, invoiced, completed).

How to use it:
- **Supply or demand:** the table gives the role per category (500, 501, 100, 101, 250, 251 are supply; 510, 511, 110,
  111, 311 are demand). Confirm it with the sign of `TransactionQuantity`: positive is supply, negative is demand. For
  distribution orders `ReferenceText` shows the transfer ("from=>to").
- A distribution order **in transit (66)** is supply on its way into the warehouse (category 501). If its planning date is
  old, it is stale or delayed too.
- Categories that are not in the list (for example forecasts) come with their own names and statuses. Do not guess:
  report "<category name>, status <code>" and ask the user, or look the order up with its own tool. A status not in the
  table for its category gets the same treatment.
- Statuses on PO headers and lines (above) are a different list from these.

## Customer order lines

- Line status text: "Reserved", "Allocated", "Delivered". Plan row status for customer orders: 22 = reserved (nothing
  allocated), 33 = allocated.
- In order line searches the status comes as a name with a code: `Allocated (33)`, `PickingList (44)`, `Invoiced (77)`,
  `FlaggedAsComp (99)`; invoiced (77) and completed (99) lines are closed. Skip deleted, completed and delivered lines when
  you look for open demand.
- A customer order line is **short** only when `RemainingQuantityBasicUom` is above 0 (not yet allocated). Fully allocated
  lines are covered by stock.
- Whether a line stays allocated (status 33), is delivered at once, or stays reserved until close to its date depends on
  the order type settings: do not assume. Where the order type allocates automatically, a line with free stock is
  allocated close to its date; far-dated ones stay reserved.

## Credit stops

`M3_OIS120MI_GetCOStopInfo` returns the stop code and the credit room. Stop codes 1 to 8 are credit stops; 9 is released
by hand.

## Manufacturing orders

- Status filters on MO searches are names: `WorkOrderStatus_LessThan` = `OrderCompleted` on `M3_PMS100MI_SearchMO`;
  `Preliminary`, `Definite`, `Closed` on `M3_PMS100MI_SelOrderHead`.
- While a change is being processed the status reads "...-ChangeInProgress" and the old dates are still shown.
- Do not trust the material-line flag "all materials allocated" when the allocated quantity is 0: use the quantities.
