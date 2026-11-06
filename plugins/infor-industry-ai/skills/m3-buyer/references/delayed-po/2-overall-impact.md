<!-- Part of references/delayed-po.md (UC3). Read the index first. -->

## 2. Find the overall impact

Run `impact-check.md` for the PO line's item and warehouse. It returns the affected orders with
need dates, slack, short quantity and which demand is covered by stock. Present the overall impact in **three
sections, always in this order**, one table each (a status icon first, at most 6 columns):

- **Manufacturing orders (MO):** MO · product as `<item number> · <item name>`, need date, short quantity, priority (`M3_PMS100MI_Get`), slack.
- **Customer orders (CO):** order · customer name, need date, short quantity, value with currency, slack. Customer
  orders found through an affected MO go here too, marked "possible" (see "Customers behind manufacturing orders" below).
- **Distribution orders (DO):** DO · from and to warehouse, need date, short quantity, slack.

A section with no orders is a one-row table ("No distribution orders affected"), not left out. Forecasts are not firm orders:
one line below the three sections, not a section. MOs and DOs have no value in M3 here: say so once, in one line.
Slack = need date minus new arrival date.

Also say, in one sentence each:
- **Coverage:** how much of the short quantity this PO line covers (for example "10 of 725 pcs"). If it
  is small, the delay is not the real problem: say so and point to the supply that is (a larger PO, a
  stopped PO such as status 12, a planned PO).
- **Already past:** any need date before today. That order is already late whatever the supplier does.
- **Value and priority:** customer order value and currency come from `M3_OIS100MI_GetLine` (order and line
  number both required). Manufacturing orders and planned DOs have no value in M3 here, and a customer order line has
  no priority field: say "not available", never estimate. MO priority comes from `M3_PMS100MI_Get` (needs
  facility, MO number and product).
- **Customer:** for every customer order that is already late, or that the new date makes late, name the customer. Read the
  order header with `M3_OIS100MI_GetOrderHead` (`OrderNumber`; it returns the customer number), then the name with
  `M3_CRS610MI_GetBasicData_CustomerName`, once per customer. Show it in the table and in the sentences about the order
  ("customer order <order>, <customer name>, is already <n> days late"). If no name comes back, write "customer name not
  available".
- **Customers behind manufacturing orders:** for each affected MO, include the customer orders found in `impact-check.md` step
  6d, marked "possible" when the link comes from product and date and not from a reference order. List them in the
  Customer orders (CO) section with their
  need dates only; do not estimate a new finish date for the MO. Name the customer. A made-to-stock MO without a
  reference order is not a reason to say that no customer is affected.
