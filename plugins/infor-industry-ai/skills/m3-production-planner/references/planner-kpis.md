# Planner KPIs

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_PMS100MI_SearchMO`, `M3_PMS100MI_SelOrderHead`, `M3_PMS100MI_Get`, `M3_PMS170MI_SearchMOP`, `M3_PMS100MI_LstMaterials`, `M3_PMS170MI_LstMaterials`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`, `M3_OIS100MI_SearchLine_Summary`, `M3_OIS100MI_GetOrderHead`, `M3_PMS100MI_GetOperation`, `M3_CPS100MI_SelTotalLoad`

Scope -> reuse or read the data -> compute each KPI from the catalogue -> compare with a target if there is one ->
show the numbers with what drives them and what to do.

## The catalogue

The KPIs and their definitions live in `references/kpi-catalogue.md`: id, question it answers, numerator and
denominator, where the data comes from, status (Available, Partly, Not available yet), which direction is better,
target, and which skill acts on it. Read it first; compute exactly what it says; never compute a KPI marked "Not
available yet" and never estimate one. When the user asks for a KPI that isn't in the catalogue, say so, say what
data it would need, and offer to add it to the catalogue as a row (the owner decides; don't invent a definition).

## 1. Scope

Same as `planner-overview.md`: the signed-in user's responsibility by default (read with
`M3_MNS150MI_GetUserData_CurrentUser`), an APS policy only on request, one route at a time; facility, warehouse and
review window from the prompt (default 14 days plus overdue MOs). Say at the top which scope, and the
read time.

## 2. Reuse or read the data

If a `planner-overview.md` or `at-risk-orders.md` result for **this same scope** is in this conversation and the user hasn't
asked to refresh it, compute from it and say it is as of its read time; offer to refresh. Otherwise read it, in
parallel where independent:

1. MOs: `M3_PMS100MI_SearchMO` (responsible user: `Responsible_ExactSearch`, facility, warehouse, `PlannedFinishDate_LessThan:
   <today + window + 1 day>`, `WorkOrderStatus_LessThan: "OrderCompleted"`, `SortBy: "PlannedFinishDate"`) or
   `M3_PMS100MI_SelOrderHead` (APS policy); then `M3_PMS100MI_Get` for each (due date, status), cap 15.
2. Proposals: `M3_PMS170MI_SearchMOP` (responsible user), cap 15.
3. Components: `M3_PMS100MI_LstMaterials` and `M3_PMS170MI_LstMaterials`; then per distinct component
   `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine` and `M3_PPS170MI_SearchPOP`.
4. Customer orders: `M3_OIS100MI_SearchLine_Summary` per finished product, `M3_OIS100MI_GetOrderHead` per order (cap 10).
5. Capacity: `M3_PMS100MI_GetOperation` for the work center and its capacity type, then `M3_CPS100MI_SelTotalLoad` `{ Facility, WorkCenter,
   FromDate: <today>, ToDate: <today + window> }`. Split the result into machine capacity (type 1) and labor
   capacity (type 2) as `capacity-types.md` says.
Apply the risk rules of `planner-overview.md` steps 3 and 4 (Clear to build, At risk, Ready, Blocked; customer orders
checked against the Requested Delivery Date). Unconfirmed purchase orders and planned orders are never safe supply.

## 3. Compute

**Alerts first.** The catalogue's Alert column holds the rules the owner set: today K18 (any work center with less than
10% free capacity over the horizon) and K19 (any work center above 95% utilisation on any day). Evaluate them for every
work center, separately for machine capacity and labor capacity, and report each as ALERT with the work center and the figure behind it, before the rest. K19 follows the rule
in the catalogue: the connector gives weekly load only, so an alert is confirmed from the weekly figure when it is above
95%, and a single peak day below that can't be ruled out; never state a daily percentage you did not read. K20 (late
sub-assembly MOs): from the MOs that make a semi-finished component of another MO, compare each one's planned finish with
the date its parent needs it, and list separately the ones that are blocked. K21 (MOs on hold): take the MOs whose status reads as
held ("Definite-Short-held", "Definite-Long-held"), exactly as M3 returns it. The usual MO search (step 2, with the status bound) returns
held MOs (tested), so no extra read is needed to find them. Count them against all open MOs in scope; count separately the ones **overdue to release**
(planned start date before today, which is the hold date of a short-term hold) and those with **no hold date** (long-term). For each
held MO list what it frees and the customer orders its product serves (`hold-mo.md`). Don't state how long an MO has been held or why:
M3 doesn't keep it. No alert is set on K21.

For each catalogue KPI with status Available (and Partly where the route allows it): the value as "n of m" (and the
percentage), and its **drivers**: the two or three records that account for most of it (for example the MOs behind
K1, the work center and week behind K10). For a KPI with a known target, mark it **On target** or **Off target** and
by how much; with no target, show the value only, and don't colour it. List the unavailable KPIs once, each with what
it needs.

## Show it

Chat. Order: one-line headline (the two numbers that matter most today), the scope line, the KPI table (id, KPI, value,
target and status if set, top driver, what to do), then the "Not yet available" list, then offers. Put the **alerts**
first, then, when K10, K18 or K19 are shown, a **work-centre table for each capacity type**, Machine capacity and Labor capacity (work center, load, capacity, free %, peak week %,
alert) with the weekly load under any work center in alert. Group the KPI table by the question: *Will I deliver on
time?* (K1 to K5, K20), *Is my plan healthy?* (K4, K6, K7, K11, K21), *Will material be there?* (K8, K9), *Do I have
capacity?* (K10, K18, K19). Show what was capped. Empty state: "You have no manufacturing orders
or proposals in <facility>/<warehouse> for the next <N> days, so there is nothing to measure."

## Next step

"Want the detail behind K1?" (`at-risk-orders.md`); "Want to act on the top issue?" (the skill named in the catalogue);
"Which KPIs would you like added?" Don't create a target; if the user gives one, use it for this conversation and
say it isn't saved.

## Edge cases

- **Nothing found** - the empty state; offer another warehouse, user or window.
- **Several matches** - for an ambiguous user, facility or policy, ask; never pick.
- **Can't see it** - say which read was refused; don't retry.
- **Part of the data missing** - compute what you can; name the KPIs you couldn't compute and why.
- **Large result** - compute on the first 15 and say how many remain.
- **Warehouse mismatch on a customer order** - K5 notes the cover is by product and date.
