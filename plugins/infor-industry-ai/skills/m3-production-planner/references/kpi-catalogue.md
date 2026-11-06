# KPI catalogue

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_SelOrderHead`, `M3_CPS100MI_SelTotalLoad`, `M3_PDS016MI_GetDailyCap`, `M3_PMS100MI_SearchMO`, `M3_PMS100MI_Get`, `M3_PDS016MI_LstDailyCap`

<!-- layout: reference -->

Each KPI is one row. To add a KPI, add a row with all the columns; the skill reads this file. "Status" says whether the
connector can compute it today. Direction says which way is better. A **target** is blank until the planner or owner sets
one; never invent a target. An **alert** is a rule the owner has set on a KPI (see "Alert rules").

| ID | KPI | The question it answers | Definition (numerator / denominator) | Data and where it comes from | Status | Better | Target | Alert | Act with |
|---|---|---|---|---|---|---|---|---|---|
| K1 | **MOs at risk** | Will my orders be ready? | MOs verdict At risk / all MOs in the window (plus overdue) | MO list, materials, balances, purchase and planned orders (screening in `planner-overview.md` step 3) | Available | lower | blank | none set | `material-shortage-check.md` |
| K2 | **Clear to build** | Can I start what is due? | MOs Clear to build / all MOs in the window | same | Available | higher | blank | none set | `at-risk-orders.md` |
| K3 | **Overdue MOs** | What is already late? | MOs whose planned finish is before today and not completed: count, and the largest days overdue | MO list and header dates | Available | lower | blank | none set | `reschedule-mo.md` |
| K4 | **Scheduled after due date** | What does M3 already plan late? | MOs whose planned finish is after their due date: count and average days | MO header (due and planned finish) | Available | lower | blank | none set | `reschedule-mo.md` |
| K5 | **Customer orders at risk** | Will the customer get it on time? | Customer orders At risk or No cover / open customer orders for my products, measured against the Requested Delivery Date; also the quantity | Customer order lines and headers, matched to MOs by product and date | Available (product and date match; warehouse caveat) | lower | blank | none set | `warn-sales-rep.md` |
| K6 | **Blocked proposals** | What can't I release? | MO proposals Blocked / all my proposals | MO proposals, their materials, balances | Available | lower | blank | none set | `mo-proposals.md` |
| K7 | **Proposals past start** | What did I leave unreleased? | Proposals whose start date is before today and that are still proposals | MO proposal list | Available | lower | blank | none set | `release-mo-proposal.md` |
| K8 | **Planned POs overdue to release** | What is the buyer behind on? | Planned purchase orders for my components whose release date is today or earlier | Planned PO search | Available | lower | blank | none set | `inform-buyer-of-late-order.md` |
| K9 | **Components on unconfirmed or late supply** | Where is supply unreliable? | Distinct components of my MOs and proposals in the window whose only supply is unconfirmed, late, or planned only | Purchase order lines, planned orders, MO materials | Available | lower | blank | none set | `inform-buyer-of-late-order.md` |
| K10 | **Work-centre weeks over rating** | Is capacity a problem? | Count of work-centre weeks in the window with total load above the rated capacity, and the highest load as a percentage of the rating, counted separately for machine capacity (type 1) and labor capacity (type 2) | Capacity load by week for the work centers of my MOs | Available (rating is per unit and shift; units and shifts not visible) | lower | blank | none set | add an extra shift in M3, then re-read |
| K11 | **MOs with M3 planning messages** | What does planning want me to change? | MOs with an action message (for example RescheduleIn, DeleteOrder) / MOs in the list | APS-policy route only (`M3_PMS100MI_SelOrderHead` returns it) | Partly: not on the responsible-user route | lower | blank | none set | `reschedule-mo.md` |
| K12 | **On-time MO finish rate** | Do I hit my dates? | MOs finished on or before the due date / MOs finished in the last 30 days | Finished MOs with actual finish dates | Not available yet: the MO search returns no actual finish date | higher | blank | - | - |
| K13 | **On-time in full, customer orders** | Do customers get what they ordered when they asked? | Customer orders delivered in full on or before the requested date / orders delivered in the period | Delivery history | Not available yet | higher | blank | - | - |
| K14 | **Reschedule churn** | Is my plan stable? | Reschedules per MO in the last 30 days | Change history | Not available yet: no change history on the connector | lower | blank | - | - |
| K15 | **Supplier on-time delivery** | Do suppliers deliver when confirmed? | Receipts on or before the confirmed date / receipts in the period | Receipt history | Not available yet | higher | blank | - | - |
| K16 | **Days of supply, critical components** | How long does my stock last? | Available inventory / average daily use of a component | Balances and consumption history | Not available yet: no consumption history | higher | blank | - | - |
| K17 | **Time from risk to action** | Am I acting quickly? | Hours from the risk first shown to the first action taken | The conversation only | Partly: within one conversation | lower | blank | - | - |
| K18 | **Available capacity per work center** | Do I have room in the horizon? | For each work center: (rated capacity minus load) / rated capacity over the whole horizon, as a percentage free. Use the weeks the capacity read returns for the window (whole weeks that overlap it) and say which weeks. Load = manufacturing-order plus planned-order load of the work center's capacity type (machine time for type 1, man time for type 2); computed and shown separately for machine capacity and labor capacity | Weekly capacity and load per work center (`M3_CPS100MI_SelTotalLoad`, FromDate today, ToDate today + the window) | Available (whole weeks, rating per unit and shift) | higher | blank | **ALERT if any work center has less than 10% free** | add an extra shift in M3, then re-read; `reschedule-mo.md` |
| K19 | **Bottleneck utilisation on a day** | Is a work center overloaded on any single day? | For each work center and day in the horizon: load that day / capacity that day. **ALERT if any work center is above 95% on any day.** | Capacity per day is readable (`M3_PDS016MI_GetDailyCap` by date and start time; a working day is typically the shifts' nominal hours). **Load per day is not readable**: the load read is weekly | Partly: see "K19: what can and cannot be known" | lower | blank | **ALERT if above 95% on any day** | add an extra shift in M3, then re-read; `reschedule-mo.md` |
| K20 | **Late sub-assembly MOs** | Are the parts my orders wait for late? | MOs that make a semi-finished component of another MO, and whose planned finish is after the date the parent needs it, or already past. Also list the ones that are **blocked** (their own components are short) as at risk of being late | MO list, material lines (acquisition code Manufacturing, reservation date), the sub-assembly MO's planned finish; the risk screening in `planner-overview.md` step 3 | Available (for the MOs in this conversation's scope) | lower | blank | none set | `material-shortage-check.md`, `reschedule-mo.md` |
| K21 | **MOs on hold** | What have I parked, and have I forgotten to bring it back? | Held MOs / all my open MOs in the scope (plus overdue). Also: held MOs **overdue to release** (a short-term hold whose hold date, the order's planned start date, is before today), and held MOs with **no hold date** (long-term holds), counted separately. Show for each held MO what it frees (hours on its work centers by capacity type, quantity of its shared components) and which customer orders its product serves | MO list and header (`M3_PMS100MI_SearchMO`, `M3_PMS100MI_Get`: status, planned start and finish), operations and materials of each held MO, customer order lines for its product (`hold-mo.md`) | Available for the count (tested: the usual MO search returns held MOs, status "Definite-Short-held" or "Definite-Long-held"; `m3/known-inconsistencies.md` K23). **How long an MO has been held and why are not stored in M3** and aren't shown; the hold date of a short-term hold is read from the MO's planned start date | lower | blank | none set | `hold-mo.md` (Part B: release) |

## Alert rules

An **alert** is a rule on a KPI that makes it stand out. Show alerts first, labelled ALERT, with the work center or order
behind them. Today there are two, set by the owner: K18 (any work center with less than 10% free capacity over the horizon)
and K19 (any work center above 95% utilisation on any day). Other KPIs have no alert until the owner sets a rule; don't
invent one. K10, K18 and K19 are evaluated separately for machine capacity (capacity type 1) and labor capacity
(type 2), and an alert says which (`capacity-types.md`).

## K19: what can and cannot be known

The connector gives the **weekly** load, not the daily load, so a single day's utilisation can't be read. Apply this rule:

- If a work center's **weekly** utilisation (load / capacity) is above 95%, then at least one working day that week must
  be above 95% (the average of the days exceeds 95%): report **ALERT, confirmed from the weekly figure**, with the week.
- If the weekly figure is at or below 95%, report **no alert from the weekly data**, and say that a single peak day can't
  be ruled out because the daily load isn't readable. Never state a daily percentage you have not read; you may give an
  estimate only if you say how it was made (for example spreading each of the user's own MO operations evenly over its
  days) and that it covers only those MOs.
- Daily capacity: `M3_PDS016MI_LstDailyCap` returns the calendar from January with no date filter and is cut off, so it
  can't be used for the window; use `M3_PDS016MI_GetDailyCap` for a given date and start time if you need to confirm the
  hours of a day.

## Notes for computing

- Everything is computed from reads in this conversation; say which time the data is as of. Planned data changes when M3
  planning runs, so re-read before comparing with an earlier figure.
- The window is the review window (default 14 days from today) plus overdue MOs.
- Always show the denominator ("3 of 5"), never a bare percentage, and say what was capped (the first 15 MOs, 15
  proposals, 10 customer orders).
- A KPI marked "Not available yet" is listed with what it needs, not computed and not estimated.
