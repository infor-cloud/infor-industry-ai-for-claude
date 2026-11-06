# Set up demo data for an item and a customer

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`,
`M3_ARS200MI_ServerTimeZone`, `M3_OIS100MI_SearchLine_LimitedOutput`, `M3_MMS200MI_GetItmBasic`, `M3_MMS200MI_GetItmWhsBasic`,
`M3_CRS610MI_GetBasicData`, `M3_CRS610MI_GetOrderInfo`, `M3_OIS010MI_LstOrderTypes` (only if the customer has no default order type), `M3_OIS100MI_AddBatchHead`, `M3_OIS100MI_SndBatchLine`,
`M3_OIS100MI_Confirm`, `M3_OIS100MI_LstErrMsgOrder`, `M3_OIS100MI_GetOrderHead`

Commands, with the item and the customer typed by the user. The item and the customer are all the user has to enter: the order type comes from the customer. The rules in `SKILL.md` apply (typed target, read first, **one
card and one yes**, re-read before writing, facility, refusals, read back).

| The user types | Scenario |
|---|---|
| "Set up demo data for swap material for item <item> and customer <customer>" | Swap material |
| "Set up demo data for double-shift for item <item> and customer <customer>" | Double shift |
| "Set up demo data for extra shift for item <item> and customer <customer>" | Double shift (same scenario, other wording) |

"Double shift", "double-shift" and "extra shift" all mean the same scenario. If the command names the item and the customer
but not the scenario, ask which one, once. If it names the scenario but not the item or not the customer, ask for the
missing one, once.

Both scenarios create **one customer order with one line** for the item. They create nothing else: no manufacturing
orders, proposals, purchase orders or shift patterns. M3's own planning may add supply for the order afterwards; this
command does not wait for it and does not touch it. (The shift pattern itself is made later, in the planner's own
flow.)

## What is the same in both scenarios

| Field | Value |
|---|---|
| Facility | The signed-in user's facility (normally A01), from `M3_MNS150MI_GetUserData_CurrentUser` |
| Warehouse | The signed-in user's warehouse (normally 001), from the same call |
| Quantity | 10, in the item's basic unit of measure |
| Responsible user | The signed-in user |
| Order type | The customer's default order type from the customer record (CRS610), read in step 4 below. Never asked, unless the customer has none |
| Price | Not sent. M3 takes it from the item file or the price list |

## What differs: the requested delivery date

**Today** is the M3 system date from `M3_ARS200MI_ServerTimeZone`; fall back to the conversation date. Work out the
weekday of that date, not of any date carried over from earlier work. A week runs Monday to Sunday.

**Swap material:** today + 7 working days (Monday to Friday). Count the next working day after today as day 1: if today is a
Saturday or Sunday, day 1 is the Monday after. The result is always a working day. Public holidays are not skipped (M3's
calendar is not read for this); say so on the card only if the user asks.

**Double shift (and extra shift):**

| Today is | Requested delivery date |
|---|---|
| Monday, Tuesday or Wednesday | The Wednesday of next week |
| Thursday, Friday, Saturday or Sunday | The Wednesday of the week after next ("Wednesday in two weeks") |

Examples: today Monday 2026-11-02 or Wednesday 2026-11-04 gives 2026-11-11. Today Thursday 2026-11-05, Friday
2026-11-06 or Sunday 2026-11-08 gives 2026-11-18. For swap material: today Friday 2026-10-30 + 7 working days is Tuesday
2026-11-10; today Monday 2026-11-02 gives Wednesday 2026-11-11; today Wednesday 2026-11-04 gives Friday 2026-11-13; today
Saturday 2026-10-31 gives Tuesday 2026-11-10 (day 1 is Monday 2026-11-02).

Send the date as the plain requested delivery date (`YYYY-MM-DD`) on the batch header and on the batch line. Do not send
the `...AtDestination` version as well.

## Read (nothing is changed yet)

1. **User, facility, warehouse, today.** `M3_MNS150MI_GetUserData_CurrentUser` and `M3_ARS200MI_ServerTimeZone`. If M3
   can't give the facility or the warehouse, ask; never guess.
2. **Existing customer orders for the item.** `M3_OIS100MI_SearchLine_LimitedOutput { ItemNumber_ExactSearch: <item> }`.
   This returns the item's whole history, so filter it yourself and group by `OrderNumber`.
   - Ignore lines at status 90 (deleted).
   - **A line in the user's facility with a status below 66 blocks the setup.** These are the lines the cleanup deletes.
   - Lines at status 66 or higher (delivered, invoiced) and lines in another facility do not block, because the cleanup
     leaves them alone. Mention them in one short line on the card ("Not counted: ...") so nothing is hidden.
   - A list that ends on a round number may be cut off (`SKILL.md`, rule 8): say so and narrow the search.
3. **Validate.**
   - The item: `M3_MMS200MI_GetItmBasic { ItemNumber }` gives the name and the basic unit of measure. If M3 says the item
     doesn't exist, say that and stop. If the unit of measure is not in the answer, ask the user once; M3 refuses a line
     without it.
   - The item in the warehouse: `M3_MMS200MI_GetItmWhsBasic { ItemNumber, Warehouse }`. If the item is not set up in the
     user's warehouse, say so and stop.
   - The customer: `M3_CRS610MI_GetBasicData { CustomerNumber }` gives the name. If M3 says the customer doesn't exist,
     say that and stop.
4. **Order type.** Read the customer's default with `M3_CRS610MI_GetOrderInfo { CustomerNumber }`; the field is
   `CustomerOrderType`. Use it as it is and show it on the card, with "(from the customer)". Never take it from an example,
   from another order or from earlier in the conversation. If the field is blank or missing, ask the user once which order
   type to use, showing the types from `M3_OIS010MI_LstOrderTypes` as choices if M3 returns them, and keep the answer for
   that customer for the rest of the conversation. If the user names an order type in the command, use that one instead.
5. **The date**, from "What differs" above.

## If a customer order already exists for the item

Create nothing. Say, in a few lines:

> There are already customer orders for <item name> (<item>) in <facility>: <order numbers, at most 10, then "+<n> more">.
> Clean the demo data for this item first ("Clean production demo data for item <item>"), then ask me again.

Do not start the cleanup yourself: a yes to a setup card never covers a delete, and the cleanup has its own card and its
own yes. Do not offer to skip the check.

## Card

> **Set up demo data for <scenario> for <item name> (<item>) and <customer name> (<customer>)**
> **Customer order to create:** facility <facility>, warehouse <warehouse>, order type <type> (from the customer), <10> <unit> of <item name> (<item>), requested delivery <YYYY-MM-DD> (<weekday>), responsible <user name> (<user>).
> Today is <YYYY-MM-DD> (<weekday>), so <the date rule that applied, in one short phrase>.
> Not counted: <order/line, status, why> (only if there are any).
> Nothing else is created. Reply **yes** to create it.

## After the yes

Re-read the existing customer orders for the item just before writing (`SKILL.md`, rule 3). If one has appeared, create
nothing and show the "already exists" message instead. Load the write tools only now. Then, **in this order**:

1. `M3_OIS100MI_AddBatchHead`: customer, order type, facility, warehouse, requested delivery date, responsible user. It
   returns a temporary batch number.
2. `M3_OIS100MI_SndBatchLine`: item, the temporary number, quantity 10, **the unit of measure** (without it M3 refuses the
   line), requested delivery date, warehouse. This call gives no error even if the line is wrong: M3 checks it at confirm.
3. `M3_OIS100MI_Confirm` on the temporary number. It returns the firm order number. If it fails, read the error log with
   `M3_OIS100MI_LstErrMsgOrder` and report M3's own messages. Do not use any lock release for this.

If a step fails after the header exists, stop and report what exists. Delete nothing without a new yes, and never retry
with other values without asking (`SKILL.md`, rules 9 and 10). If M3 refuses the order because the item has no price
("Sales price must be entered"), say so; do not invent a price.

## Read back and report

Read the new order with `M3_OIS100MI_SearchLine_LimitedOutput { OrderNumber_ExactSearch: <order> }` and
`M3_OIS100MI_GetOrderHead`. Report in a few lines what M3 shows, not what was sent: the order number, customer, item,
quantity and unit, requested delivery date, status, facility and warehouse. If a value differs from the card (for
example the date), say so plainly. End with one line: to remove the order and anything M3 plans for it, say "Clean
production demo data for item <item>".
