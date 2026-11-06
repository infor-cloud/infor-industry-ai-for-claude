# Planner overview

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_PMS100MI_SelOrderHead`, `M3_PMS100MI_SearchMO`, `M3_PMS100MI_Get`, `M3_PMS170MI_SearchMOP`, `M3_OIS100MI_SearchLine_Summary`, `M3_OIS100MI_GetOrderHead`, `M3_PMS100MI_LstMaterials`, `M3_PMS170MI_LstMaterials`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`, `M3_PMS100MI_GetOperation`, `M3_PMS170MI_LstOperations`, `M3_CPS100MI_SelTotalLoad`

<!-- contents:start -->
**Contents**

- 1. Scope
- 2. Read the lists (in parallel)
- 3. Screen every MO and proposal for risk
- 4. Check each customer order against its requested date
- 5. A few KPIs
- 6. Issues and the recommended next action
- 7. After a fix
- Show it: The planner dashboard's action buttons
- Edge cases
<!-- contents:end -->

The start of the planner's day: scope -> list the MOs and proposals -> add the customer orders for those
products -> screen every MO for risk -> check each customer order against its requested date -> a few KPIs ->
the top issues, each with a recommended next action.

## 1. Scope

Take the settings from M3 (`m3/settings.md`) or the user's prompt, which wins: facility, warehouse, review window
(default 14 days from today, plus MOs already overdue), and the route.

- **Default route: the signed-in user's responsibility.** Read the user with
  `M3_MNS150MI_GetUserData_CurrentUser` (user ID, default facility and warehouse). The overview covers the MOs and the MO
  proposals this user is responsible for. Another person's ID only if the user names it.
- **APS policy on request only**, when the user names one ("overview for policy <code>"). Use `M3_PMS100MI_SelOrderHead`
  as `at-risk-orders.md` step 2a describes. Don't merge the two routes in one overview: one at a time.
- **All responsibles on request**, when the prompt says "all" production orders, MOs or manufacturing orders (or
  similar): every open MO and MO proposal in the user's facility and warehouse, whatever the responsible user. Find them
  as `at-risk-orders.md` step 2c describes (several searches merged by MO number, stale items counted apart). Don't merge
  it with the other two routes.
- Say at the top which user, policy or all responsibles, facility, warehouse and window you used, and the read time.

## 2. Read the lists (in parallel)

1. **MOs:** by responsible user, `M3_PMS100MI_SearchMO` `{ Responsible_ExactSearch, Facility_ExactSearch,
   Warehouse_ExactSearch, PlannedFinishDate_LessThan: <today + the window + 1 day>, WorkOrderStatus_LessThan:
   "OrderCompleted", SortBy: "PlannedFinishDate" }` (no lower date bound, so overdue MOs come back); by APS policy,
   `M3_PMS100MI_SelOrderHead`. Then `M3_PMS100MI_Get` for each (cap 15; state the cap) for the due date and
   status.
2. **Proposals:** `M3_PMS170MI_SearchMOP` `{ ResponsibleUser_ExactSearch, Facility_ExactSearch,
   Warehouse_ExactSearch, SortBy: "PlannedFinishDate" }` (cap 15). For the APS-policy route, proposals aren't
   selected by policy: say so and show none unless the user also asks for a user's proposals. For the **all** route, read
   MOs and proposals as `at-risk-orders.md` step 2c says (no responsible filter), and add the responsible user to each
   table.
3. **Customer orders for the products:** for each distinct finished product among the MOs and proposals,
   `M3_OIS100MI_SearchLine_Summary` `{ ItemNumber_ExactSearch, SortBy: "RequestedDeliveryDateAtDestination" }`;
   drop deleted, completed and delivered lines (cap 10 orders). For each customer order,
   `M3_OIS100MI_GetOrderHead` `{ OrderNumber }` for customer, **warehouse**, requested delivery date, stop code
   and the **salesperson**.

## 3. Screen every MO and proposal for risk

For each MO (`M3_PMS100MI_LstMaterials`) and each proposal (`M3_PMS170MI_LstMaterials`), in parallel, then for each
distinct component `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine` and `M3_PPS170MI_SearchPOP` for
purchased items; manufactured components are supplied by the MOs and proposals in this overview. Apply the rules
of `material-shortage-check.md` in short form:

- **Clear to build** - every component is covered by available inventory or confirmed supply by the MO's start
  date, level by level.
- **At risk** - some component is not; name the lowest-level component, the quantity short and what is on the
  way (unconfirmed purchase orders and planned orders never count as safe supply).
- **Can't tell** - a read failed.
Proposals get **Ready** or **Blocked** the same way. Capacity: for **every** distinct work center used by the MOs
and proposals in scope, at-risk or not (`M3_PMS100MI_GetOperation`, `M3_PMS170MI_LstOperations`),
`M3_CPS100MI_SelTotalLoad` over the window; weeks over the rating are flagged. Split the work centers by the
operation's capacity type into **machine capacity** (type 1) and **labor capacity** (type 2) and report them
separately (`capacity-types.md`). Read capacity again whenever the user says they have added a shift in M3.

## 4. Check each customer order against its requested date

The standard is the customer's **Requested Delivery Date** on the order, not the MO's due date. A customer
order is:
- **Covered by stock** - the finished product's available inventory in the order's warehouse covers it.
- **Covered by MO <n>** - the earliest MO (or Ready proposal) for that product that is **Clear to build** and
  finishes on or before the requested date, in date order, using quantities.
- **At risk** - the covering MO is At risk or Blocked, or finishes after the requested date. Say by how many days.
- **No cover** - no MO, proposal or stock for it.
If the order's warehouse differs from the MO's, say the cover is by product and date and the link between the
warehouses isn't confirmed.

## 5. A few KPIs

The full set is in `planner-kpis.md` (say "show my KPIs"). Here, compute these from what you read, each with its count and the denominator:
- MOs at risk of all MOs in the window; MOs Clear to build (share).
- Overdue MOs and the largest number of days overdue.
- Proposals Blocked, and proposals past their start date and not released.
- Planned purchase orders overdue to release; components with unconfirmed supply in the window.
- Work centers with weeks over their rating (machine capacity and labor capacity counted separately), and the capacity alerts: any work center with less than 10% free over the
  horizon, or above 95% utilisation on a day (confirmed from the weekly figure; see `planner-kpis.md`). Late
  sub-assembly MOs.
- Customer orders at risk or without cover (count and quantity).

## 6. Issues and the recommended next action

Rank the issues: customer orders at risk first (earliest requested date), then overdue MOs, then the rest. For
each, give the root cause, the **recommended next action**, why, and a confidence (High with confirmed supply,
Medium when a date is only requested, Low when data is missing). Pick from, in order of what closes the gap:

| Root cause | Recommend |
|---|---|
| A semi-finished component has no or late supply | Release a Ready proposal for it (`release-mo-proposal.md`), then reschedule the MO |
| A purchase order is late or unconfirmed | Ask the buyer to confirm or pull it in (`inform-buyer-of-late-order.md`), or record the date the supplier gave (`handle-po-or-inform-buyer.md`, 4.3), then reschedule to the confirmed date |
| Only a planned PO exists | Release it yourself, or ask the buyer to (`handle-po-or-inform-buyer.md`; if M3 refuses, ask the buyer) |
| No supply at all | Create a planned PO or a PO yourself, or ask the buyer to raise one (`handle-po-or-inform-buyer.md`; if M3 refuses, ask the buyer) |
| A competing MO takes the material | Reschedule the lower-priority MO (`reschedule-mo.md`) |
| A component has no supply in time and a reschedule won't help | Swap the line to an alternative item (replacement type 3, 4 or 5) that is in stock or arrives sooner (`swap-material.md`), then reschedule |
| A customer order is exposed by date, and needs less than the MO makes, and the start can't move earlier | Split the MO so the part the customer needs finishes on time (`split-mo.md`); a reschedule of the whole MO (`reschedule-mo.md`) when the split can't make the date |
| A customer order is exposed because the MO lacks capacity or material that another, non-urgent MO also uses | Hold that other MO to free it (`hold-mo.md`), then reschedule the exposed MO; release the hold when it is done |
| Capacity is over the rating | Move the operation to another resource under the same main work center that has room (`swap-capacity.md`), then reschedule; or, when no other resource has room, switch the work center to a double shift for a from date and a to date (`shift-pattern.md`) |
| A customer order is exposed (at any point; you choose when) | Warn the sales rep (`warn-sales-rep.md`); customer contacts and a customer notice draft are in `customer-impact.md` |

The planner decides; show the action, never apply it. Give the first two or three issues in full and offer the
rest ("say 'next' for the others"). Every action goes through its own skill's card and yes.

## 7. After a fix

When the planner has acted (a proposal released, an MO rescheduled, a shift added, a message sent), re-read only
what it touches: that MO, its components, its customer orders and the work center. Show **before and after** and
**what is still wrong**; don't rebuild the whole overview unless asked. State that planned data changes whenever M3
planning runs.

## Show it

Chat. Order: one-line headline (counts and the single most urgent issue), the scope line, the MO table, the
**material-lines table for the MOs at risk**, the proposal table, the customer-order table, the **work-centre tables (Machine capacity, then Labor capacity)**,
the KPIs as one short block, then the top issues with their recommended actions. Tables: MO (number, product, qty, due, planned finish, responsible user (all route only), status ❌ At risk / ✅ Clear / ❌ Overdue, root cause), proposals (number, product, qty, start, finish, responsible user (all route only), ✅ Ready /
❌ Blocked), customer orders (order, customer, product, qty, requested date, cover). If there are more than 15 rows in a table, show the 15 that matter most and say how many
remain.

**Material-lines table** (for each MO that is At risk or Overdue, one row per component line that is Short or Tight, most
urgent first): MO, product, component and name, needed quantity and the date it is needed (the line's reservation date),
on hand, what is coming (the purchase order, planned order or MO, with its date and whether it is confirmed; planned and
unconfirmed supply is never counted as safe), the status (Short or Tight) and the cause (Material), with the reason
in words: "made", "tight: covered only by <supply>" or "competes with MO <no>". Components that are covered are left out; say how many lines were left out. Show the lowest-level cause on
its own row (for a semi-finished component, the row for its own missing component), so a chain reads from the MO down.

**Work-centre tables** (two tables, **Machine capacity** for capacity type 1 and **Labor capacity** for type 2; one row
per work center that the MOs and proposals use, in the table for the type of its operations; a table with no rows is
replaced by one line saying so; `capacity-types.md`): work center, load in hours, capacity in
hours, free capacity as a percentage over the horizon (negative when overloaded), the peak week's utilisation, and an
Alert column. Use the same figures as K18 and K19 in `kpi-catalogue.md`: free = (capacity minus load) / capacity over the
whole weeks that overlap the window; ALERT if less than 10% free, and ALERT if a week is above 95% (a weekly figure above
95% means some day is above it; the daily load itself isn't readable). Under it, the load by week for any work center
that has an alert.

Empty state: "You have no manufacturing orders or proposals in <facility>/<warehouse> for the next <N> days."

### The planner dashboard's action buttons

The bundled dashboard writes to M3 itself. Each button opens a dialog that re-reads the record, runs the skill's checks, shows the exact change and runs it only after the planner clicks
Confirm: one call, then a read-back, then a line in the board's resolution log. It does not save requests for chat to run. When the user asks chat to "run the confirmed actions" or
similar, say that the board runs its own actions and that nothing is waiting here; offer to read the resolution log, or to do the action in chat with its own card.

## Edge cases

- **Nothing found** - the empty state; offer another warehouse, user or window.
- **Several matches** - for an ambiguous user, facility or policy, ask; never pick.
- **Can't see it** - say which read was refused; don't retry.
- **Large result** - check the first 15 by date and say how many remain.
- **Part of the data missing** - show the rest; name what wasn't checked (for example capacity, or a read that failed).
- **Warehouse mismatch** - say so on the customer order (step 4).
