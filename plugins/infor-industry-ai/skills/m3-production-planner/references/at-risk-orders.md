# At-risk manufacturing orders

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_PMS100MI_SelOrderHead`, `M3_PMS100MI_SearchMO`, `M3_PMS170MI_SearchMOP`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstMaterials`, `M3_MMS200MI_GetItmWhsBal_Subname`, `M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`, `M3_OIS100MI_SearchLine_Summary`, `M3_OIS100MI_GetOrderHead`, `M3_PMS100MI_GetOperation`, `M3_CPS100MI_SelTotalLoad`, `M3_PMS170MI_LstMaterials`, `M3_MMS200MI_LstItmWhsByItm`, `M3_MMS200MI_GetItmWhsBal`

<!-- contents:start -->
**Contents**

- Checklist
- 1. Set the scope
- 2. Find the MOs: 2a. By APS policy · 2b. By responsible user · 2c. All (every responsible)
- 3. Read (cap 25 MOs; state the cap)
- 4. Make sense of it
- 5. Options per MO (the planner chooses; nothing is applied)
- Show it
- Next step
- Edge cases
<!-- contents:end -->

The planner's daily board: window and APS policy -> find the MOs -> read each MO's components ->
check every component against stock, incoming supply and competing MOs, level by level ->
check capacity where it can be read -> rank -> options.

## Checklist

Work through these in order and confirm each one before you answer. Track them yourself; don't show the checklist in the reply.

- [ ] 1. Scope set and stated at the top: facility, warehouse, route (responsible user, APS policy if named, or all responsibles), review window, MO lookback
- [ ] 2. MOs found by the route asked for (responsible user by default; all responsibles when the prompt says all); overdue MOs kept and labelled
- [ ] 3. Read for up to 25 MOs, cap stated: header, materials, component stock, open and planned supply, customer order lines, work center load
- [ ] 4. Every MO has a verdict (At risk, Tight, OK, Can't tell) with its cause and root cause
- [ ] 4b. Full chain read for an MO with a short made component (only when there are levels below level 0)
- [ ] 5. Options per MO: only those whose check says they can help; every at-risk level of the chain in one list; nothing applied
- [ ] Show it: one line, the ranked table, the full chain (only with levels), the options (one list for the whole structure), supply and customer orders, capacity (machine, labor), the coverage line, "Next:"
- [ ] Next step offered

## 1. Set the scope

Take the settings from M3 (`m3/settings.md`) or the user's prompt, which wins: **facility** and **warehouse**
(default: the signed-in user's own, from `M3_MNS150MI_GetUserData_CurrentUser`), **APS policy** (only when the user names
one), **review window** (default 14 days) and **MO lookback** (default 90 days). Say which values you used at the top of
the result. The review window starts today: MOs count when their **planned finish
date** is from today through today + the review window. Use the real current date from the
conversation context; never assume it.

## 2. Find the MOs

There are three ways; use the one the user asked for, one at a time: the routes are never merged with each other (only the all route merges its own searches by MO number, step 2c). **All responsibles** (step 2c, the default); by **responsible user** (step 2b) when the user says "mine" or names a user; by **APS policy**
(step 2a) only when they name a policy.

### 2a. By APS policy

Call `M3_PMS100MI_SelOrderHead` with `{ TimestampDateFilter: <today minus the lookback, YYYY-MM-DD>,
SchedulingHorizonDays: <the review window in days>, ApsPolicy: <policy> }`, with `Facility` and
`Warehouse` from the settings. Example: lookback 90 and window 14 on 20 Oct 2026 -> `2026-07-22` and `14`.

**`TimestampDateFilter` selects MOs changed on or after that date.** In tests, yesterday's date returned only the MO changed
that day, and a date a few days earlier returned all of them, with a horizon of 14 or of 90 alike. So pass a date well before today (the lookback), or older MOs are
missed. `SchedulingHorizonDays` did not visibly change the result in any test; pass the review
window as the owner specified, and don't rely on it: filter yourself. Keep MOs whose planned
finish date falls from today through today + the review window (default 14 days), **and every open MO
whose planned finish date is already before today**: label those **Overdue** and rank them with the
at-risk ones (a late MO the planner hasn't closed is the most urgent kind). Status filters, if
used, are names (`Preliminary`, `Definite`, `Closed`).

### 2b. By responsible user

Use it when the prompt says "mine", "I am responsible for" or names a user. The user is the one named, else the signed-in user (`M3_MNS150MI_GetUserData_CurrentUser`; never
assume another person's ID). Call `M3_PMS100MI_SearchMO` `{ Responsible_ExactSearch: <user>,
Facility_ExactSearch, Warehouse_ExactSearch, PlannedFinishDate_LessThan: <today + the review window +
1 day, YYYY-MM-DD>, WorkOrderStatus_LessThan: "OrderCompleted", SortBy: "PlannedFinishDate" }`. It has
no lower date bound on purpose, so MOs already past their finish date come back too (they are
Overdue). It returns product, quantity, status, start and finish date and MO number for each; read the
header (step 3) for the due date and M3's message. In tests this found MOs the APS-policy
route missed. If it returns nothing, say so and offer the APS-policy route or MO numbers.

If the user is responsible for MO proposals too, mention the count and offer `mo-proposals.md`.

Keep each MO's facility, number, product, description, dates, quantity, status, reference order
and the **action message** M3 planning attached (for example `DeleteOrder`). An action message
is M3's own signal that planning thinks the order isn't needed or needs changing; show it next
to the verdict and don't override it, but note that it may predate new demand.

If the call errors or returns nothing, say so plainly and ask for MO numbers (and products) to check;
carry on with those.

### 2c. All (every responsible)

Use it **by default**, and whenever the prompt says "all production orders", "all MOs", "all manufacturing orders" or similar: **every open MO and
every MO proposal in the user's facility and warehouse, whatever the responsible user.** The window is the same (default
14 days, plus overdue). Say "all responsibles" in the scope line and add a **Responsible** column to the tables. Don't
mix it with the user or APS-policy routes.

No single search returns all of them. Run these and **merge by MO number**; each search alone has been seen to miss MOs
that another one found:
1. The signed-in user's own MOs (step 2b), so nothing the user owns is lost.
2. `M3_PMS100MI_SearchMO` `{ Facility_ExactSearch, Warehouse_ExactSearch, PlannedFinishDate_LargerThan: <today minus 1 day>,
   PlannedFinishDate_LessThan: <today + the review window + 1 day>, WorkOrderStatus_LessThan: "OrderCompleted", SortBy:
   "PlannedFinishDate" }`. The operator is `_LargerThan`: a name that doesn't exist (`_GreaterThan`) is ignored without an
   error.
3. `M3_PMS100MI_SearchMO` with `ManufacturingOrderNumber_LargerThan: <a number a little below the lowest MO number found so
   far>` instead of the date bound, and the same facility, warehouse and status filters. It returns the recent MOs of
   other planners.
4. Optionally `M3_PMS100MI_SelOrderHead` without `ApsPolicy` (the call of step 2a): it also returns each MO's responsible
   user, product structure type and M3's action message. Not yet shown to be complete.

Why: with no bound the list comes back oldest first and is cut off after about 30 rows, so years-old open MOs fill it and
the current ones never appear; and each bound alone dropped some MOs.

**Stale MOs.** Open MOs whose planned finish is further back than the MO lookback (default 90 days) are stale: count them,
give the oldest planned finish date, show one housekeeping line, and don't read or rank them as risks unless the user
asks. Why: they are old data and would bury the real ones.

**Proposals.** `M3_PMS170MI_SearchMOP` `{ Facility_ExactSearch, Warehouse_ExactSearch, PlannedFinishDate_LargerThan: <today
minus the MO lookback>, SortBy: "PlannedFinishDate" }` with no `ResponsibleUser` filter; unbounded it also returns the oldest
first and is cut off. Check each proposal as `mo-proposals.md` says. A Blocked proposal in the window goes in the table next
to the MOs (marked as a proposal), and a proposal past its start date is "overdue to release". Show each proposal's
responsible user. Releasing someone else's proposal is still the planner's own decision and yes (`release-mo-proposal.md`).

**Reading.** The cap stays at 25 MOs, and with every responsible it bites sooner. Rank as in step 4 (**Rank**: MOs that cover an exposed
customer order first, then earliest finish date, then the size of the shortfall; an overdue MO has the earliest finish, so it comes first within its group) and say how many remain. The coverage line names
the searches run and says that completeness can't be guaranteed.

## 3. Read (cap 25 MOs; state the cap)

For each MO, in parallel:
1. `M3_PMS100MI_Get` `{ Facility, ManufacturingOrderNumber, ProductNumber }` -> dates, quantity,
   status, warehouse, reference order (customer order link if any).
2. `M3_PMS100MI_LstMaterials` with the same keys -> components with needed quantity,
   reservation date, acquisition code, operation number.

For each distinct component with remaining quantity above zero, in parallel:
3. `M3_MMS200MI_GetItmWhsBal_Subname` -> on-hand, ordered (incoming), reserved, available.
4. `M3_PPS200MI_SearchLine` for purchased components -> open PO lines with dates and status; and
   `M3_PPS170MI_SearchPOP` `{ ItemNumber_ExactSearch, Warehouse_ExactSearch }` -> planned purchase
   orders (proposals). Show them as "proposed, not released"; never count them as safe supply.

For each distinct finished product among the MOs, in parallel: `M3_OIS100MI_SearchLine_Summary`
`{ ItemNumber_ExactSearch: <product>, SortBy: "RequestedDeliveryDateAtDestination" }` -> open customer
order lines (order, line, quantity, requested date, status; skip deleted, completed or delivered
lines). Match each to the MOs: customer demand is covered by the earliest MO finishing on or before
the requested date, in date order, using the MO quantities. A customer order the MOs can't cover in
time, or whose covering MO is At risk, is **customer exposed**; for its customer, use
`M3_OIS100MI_GetOrderHead` `{ OrderNumber }`.

For each distinct work center (from `M3_PMS100MI_GetOperation` on an operation number found in
the material lines): `M3_CPS100MI_SelTotalLoad` `{ Facility, WorkCenter, FromDate: <today>,
ToDate: <today + the review window> }` (dates `YYYY-MM-DD`, the same window as the MOs; leave
`IncludeHeldManufacturingOrders` out unless the user asks). It returns one record per calendar
week with the rated capacity per unit and shift and the load from manufacturing orders and
planned orders (man time and machine time). If it returns nothing, say capacity wasn't checked
for that work center; don't call it fine. Read each operation's `CapacityType` from the same `GetOperation`
result and keep **machine capacity** (type 1) and **labor capacity** (type 2) apart, as `capacity-types.md` says.

## 4. Make sense of it

Apply the same per-component logic as `material-shortage-check.md`, across all MOs together so
competing demand is visible:
- Needed quantity and date per component (the reservation date); sum all MOs' needs for the
  same component in date order.
- Supply: on-hand, open PO lines (unconfirmed lines flagged, not safe), and MOs in the set that
  make the component (finish date versus the date it is needed).
- A component's running balance goes below zero on some date -> **Short** from that date;
  covered only by unconfirmed supply -> **Tight**.
- A semi-finished component whose own MO has a Short component passes the shortage up: the
  root cause is the lowest level (follow up to three levels). Why: the planner must act where
  the chain breaks.

**The full chain (the same as the dashboard's "Full chain").** Level 0 is the MO itself. When it has a made
(semi-finished) component that is short, follow it down: level 1 is the open MO or proposal that makes that component
(`M3_PMS100MI_SearchMO` and `M3_PMS170MI_SearchMOP` by product, in the facility; skip orders finished more than 90 days
ago), level 2 the order that makes a short made component of level 1, and so on, **up to three levels below level 0 and about ten
orders in all**. For each order read its components (`M3_PMS100MI_LstMaterials`, or `M3_PMS170MI_LstMaterials` for a
proposal, whose lines carry no acquisition code: read it from `M3_MMS200MI_LstItmWhsByItm` with the warehouse), check each
against stock (`M3_MMS200MI_GetItmWhsBal`, allocatable) and, for a short purchased component, its open PO lines and PO
proposals (`M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`). Rules:
- A level is ❌ At risk when a component is short with no safe supply, when the orders that make a short made component
  are at risk, too small or finish after the parent needs it (say how many days), or when nothing makes it. It is ⚠️
  when only a proposal, an unconfirmed PO or a planned PO covers it (⏳ Proposal: not released yet); ✅ when
  everything it needs is covered. A proposal and an unconfirmed PO never count as safe supply.
- The **root cause** is the lowest level that carries a problem of its own. Name it with its level and order.
- Stock is checked per line and not shared between levels (the top level keeps the competing-MO check).
- **Only levels below level 0 count.** When the MO has no made component, or every made component is covered from stock,
  there is no chain: write nothing about it and show no section for it.
- Capacity: for each week in the window, add the manufacturing-order and planned-order load of the
  operation's capacity type (machine time for type 1, man time for type 2; category A and B) and compare
  it with the capacity per unit and shift. Do machine capacity and labor capacity separately
  (`capacity-types.md`). Over the capacity ->
  **Capacity** risk for the MOs that load that work center that week; show the load and the capacity. An MO counts for every week
  from its start (today when the start has passed) to its finish, and so does each order of its chain; the worst week gives the risk.
  Under it -> say so ("<work center> week <w>: 16 of 40 hours"). The capacity figure is per unit and shift, so
  a work center with several machines or shifts has more room than it shows; say that when the
  comparison is close. Planned orders are proposals; show them separately from firm MO load.

**Customer exposure:** list each exposed customer order beside the MO that covers it (customer,
requested date, quantity). Why: it tells the planner which MO matters most.

**Late against its own due date.** If an MO's planned finish date is after its due date, the MO is
scheduled late: flag it At risk even when material looks fine, and list MOs whose *due* date falls in
the window but whose planned finish is outside it, with M3's action message (for example
"RescheduleIn", which asks planning to bring the order forward). Why: the review window is by
planned finish, but a planner also needs the orders M3 already knows are behind.

**Customer order warehouse.** A customer order is supplied from the warehouse on its header; if it
differs from the MO's warehouse, say the match is by product and date only and the link between the
two warehouses isn't confirmed (a distribution order may be needed).

**MO risk** = At risk (any Short component or broken chain), Tight, OK, or Can't tell.
**Cause** = **Material** or **Capacity**, or both; no other value (the same as the dashboard). A short component is Material
whether it is bought, made (a semi-finished component with no or late supply), taken first by competing MOs or covered only
by unconfirmed supply, and so is an MO that finishes after its customer order needs it. The **root cause** line says which:
"late" (the finish date has passed, or the MO finishes N days after customer order <no> needs it), "tight" (covered only by
unconfirmed supply: name the PO line, planned PO or MO proposal), "competes with MO <no>, MO <no>" (enough stock overall, not
enough for all; name the orders that take it first, up to three, then "+n more") or "made" (a semi-finished component: when the MO that makes it finishes after the parent needs it, say so: "because MO <no> that makes it finishes <date>, <n> days after it is needed").
Never write Late, Tight, Competing MO or Semi-finished as the cause. Tight stays an MO status (⚠️ Tight).
**Rank** by finish date (earliest first), with MOs that cover an exposed customer order first, then by the size of the shortfall. Every row shows the
component, quantity and date behind the claim.

**Orders overdue to release.** A planned purchase order whose release date is today or earlier (M3's
message "Rel-ReschedIn" or "ReleaseOrder") should already have been released. List those
separately, with delivery date versus the date the component is needed, and offer
`inform-buyer-of-late-order.md`. Planned orders change whenever M3 planning runs, so always show the
read time.

Do not trust the material flag "all materials allocated" when the allocated quantity is 0.

## 5. Options per MO (the planner chooses; nothing is applied)

**Show an option only when its check says it can help.** This is the same rule as on the dashboard; an option the check
rules out is not listed at all.
- Reschedule: only for an MO that is **At risk**. Never offer it for an MO that is OK or only "Can't tell".
- Swap a material: only when an alternative item (replacement type 3, 4 or 5) is quicker than the original (`swap-material.md`).
- Move an operation to another resource: only when a related resource of the same capacity type has room (`swap-capacity.md`).
- Temporary double shift: only when no other resource can take the work; **shown even when it clears only part of the
  overload, with a ⚠️ "Will not solve everything" warning** that names the weeks that stay over the rating (`shift-pattern.md`).
- Split the MO: only for an At risk MO where a customer order needs less than the MO makes and the urgent part is estimated to make
  the date (`split-mo.md`). It does not matter whether a reschedule could also fix it: **a split that solves the date problem is
  ranked above Reschedule** (see "A split that solves the date problem goes first" below). On the dashboard the Split button runs
  the same checks, then splits after the planner's own Split click in its dialog (`split-mo.md`).
- Hold another MO: when a donor frees something; ⚠️ Partly when it frees only part, with the warning that it will not close
  the gap on its own (`hold-mo.md`).
- **Earlier actions never hide an option.** Options follow the state in M3 now: an MO you swapped and then swapped back in
  M3 gets the swap option again. Every write re-reads the record and checks it first, so offering it again is safe.
- **A split that solves the date problem goes first.** When the split check says the urgent part is estimated to make the requested
  date (material and capacity for it covered), show the split as the first "Recommended" option, above Reschedule, the swap, the
  resource move and the double shift. Reschedule is still listed, under "Other options". A split that does not solve the date
  problem is not shown at all. The same order applies on the dashboard.
- **Recommended fix first; the rest go under "Other options".** The swap (material), the resource move and the double shift
  (capacity) are the recommended fixes. When at least one of them solves its part of the problem, show every one that applies at the top as
  "Recommended", in this order: split (when it solves the date problem), swap, resource move, double shift. A swap solves the material shortage when its best alternative is
  available on or before the need date (when the need date has already passed, available today counts) and not from supply that is
  "not safe"; a resource move solves a capacity problem when another resource has room; a double shift solves it when every week gets
  under the rating. A recommended option that does not solve its part alone says so (for example a swap whose alternative is still
  late, or a double shift with the ⚠️ "Will not solve everything" warning). Every other option follows under one line,
  "Other options (<n>)" (a collapsed dropdown on the dashboard). When none of them solves anything, list all options, with the swap
  first, then the resource move, then the double shift.
- **Short, with names.** Describe each option in one line: the risk and how the option solves it. Always show an item as
  <name> (<item number>) and a work center as <description> (<code>), never the number alone; name an operation by its number and
  description, for example "operation 10 (SF Assembly)".

**One options list for the whole structure.** When the MO has levels below it (the full chain), apply the same option
logic to **every at-risk order of the chain**: level 0 and each level below it (the chain shows up to three). For each, read
its operations and capacity, its short components, their POs, planned POs, alternative suppliers and MO proposals, as for
any MO. Show **one** list, not one per level: the swap and capacity options (swap, move operation, double shift) of every
level come first, each marked with its level and order ("Level 1, MO <no>: ..."); every other option, from any level, goes
under one line, "Other options (<n>)". An option on a lower level acts on that order, not on the selected MO: say so on the
option, and if that order itself waits on a level below, advise fixing the lowest level first. The write flows are the same
(one card and one yes each).

Reschedule the MO (`reschedule-mo.md`; only for an MO that is At risk): the skill recommends a start and finish date from the confirmed
component supply (with its basis and a confidence), a quantity the components allow, or a finite-capacity
recalculation; the planner decides. It changes one date and/or the quantity, never both dates, and it reports
afterwards whether lower-level orders moved.
Pull in the PO (days to move, drafted supplier request); tell the buyer that a purchase order or planned
purchase order is late (`inform-buyer-of-late-order.md`) **or deal with it yourself**: release the planned PO, create a
Planned PO or a PO, or record the supplier's confirmation (`handle-po-or-inform-buyer.md`; offer both as options side by
side, and if M3 refuses for lack of authority, advise the buyer); buy from another supplier
(find one with `m3/alternate-suppliers.md`, then `m3/create-planned-po.md`); swap the material for an alternative item (replacement type 3, 4 or 5) when the original can't arrive in time and
rescheduling doesn't help (`swap-material.md`; check it only for the root-cause component of an At risk MO whose cause is
Material, up to 10 components, and show the option only when an alternative is quicker than the original); move an operation to another resource under the same
main work center when its own resource is over capacity and rescheduling doesn't help (`swap-capacity.md`; check it only for
the over-rating work center of an At risk MO whose cause is Capacity, up to 10 operations, and show the option only when a
related resource of the same capacity type has room); hold another MO of the planner's that shares the constraint and has no
urgent customer demand (`hold-mo.md`; check it only for an At risk MO whose customer order is exposed and where the
other options don't close the gap, up to 3 MOs, and show the option when a donor frees something, with a ⚠️ warning when it frees only part); split the MO when a customer order it covers needs less than the MO makes and the
MO finishes after the requested date (`split-mo.md`; check it only for an At risk MO whose exposed customer quantity is below its
quantity, up to 5 MOs, and show the option, ranked above Reschedule, only when the urgent part is estimated to make the date); make or release the semi-finished MO; free material from a
competing MO; move the order or tell the customer (`customer-impact.md`). Labor capacity is handled like machine capacity: a move to another labor resource (`swap-capacity.md`) and a temporary double shift (`shift-pattern.md`) are offered the same way, each against labor capacity only. Overtime is available as that double shift. Outsourcing isn't offered yet (`m3/not-available.md`).

## Show it

**In chat** (the default). Same content and order as the dashboard, so the two never give different answers. The planner may also ask in chat for things the dashboard does not show; answer those as asked:
1. One line: *MOs in window*, *At risk*, *Earliest failure* (date and MO), with the window, route (user, APS policy or all responsibles),
   facility and as-of time.
2. A table, one row per MO, ranked: MO, product, finish date, responsible user (all route only), status (❌ At risk / ⚠️ Tight / ✅ OK / ℹ️ Can't tell),
   cause (Material or Capacity), the root cause in one line ("<component>: nothing on hand or on order, needed <date>, short <qty>",
   plus "late", "tight: covered only by <supply>" or "competes with MO <no>" where it applies), and the
   first option. About 8 rows; summarise the rest in one line.
3. **For the top at-risk MO** (the one the dashboard selects first) **or the MO the planner names**:
   a. **Full chain**, only when there are levels below level 0. A one-line verdict ("❌ The chain is at risk, root cause at
      level 2"), the path ("MO <a> needs <item> → Proposal <b> needs <item> → MO <c> needs <item>"), the root cause line, then
      **one small block per level**: "Level <n> · <order> makes <product>" with its status, quantity, dates, what it feeds and
      when the parent needs it, and a table of its components (needed, by, available, status with the reason). One line at
      the end says how to read it: level 0 is the MO itself, each next level makes a short component of the one above, read
      from the top down, the problem usually sits at the lowest level. No section at all when there are no levels.
   b. **Options**, one list for the whole structure (step 5, "Options by level"): the swap and capacity options of every
      level first, the others under "Other options" (each with who does it and its button where the skill can act).
   For the other MOs the table's first option stands; offer "ask for the options of MO <n>".
4. **Late or unconfirmed supply, tell the buyer:** the PO lines and planned POs behind the short purchased components,
   grouped by buyer, with what is wrong (unconfirmed, arrives after it is needed, overdue, release date passed). A line
   when there are none. The option reads "Tell the buyer that <component> is short" and gives the shortage (quantity, date) and the reason
   per order; its button is always the short "Draft e-mail…", and the buyer's name is shown only when several buyers are involved.
5. **Customer orders exposed:** open customer order lines (status below 66) of products with an at-risk MO, requested on or
   before the last at-risk finish date or confirmed later than requested, with the customer name (`customer-impact.md`). Keep it apart from the MO's components, which have their own **Material** heading.
6. Capacity, in two parts: **Machine capacity** (type 1) and **Labor capacity** (type 2), each with its work centers,
   load against capacity and any week over it (`capacity-types.md`). A part with no work centers is one line. For the selected MO, list the
   weeks from its start to its finish (the start week always; later weeks only when they carry load), each work center with its **Type** tag
   (👷 Labor or ⚙️ Machine).
7. Coverage line: MOs checked, cap, demand lines seen versus reserved, work centers whose load couldn't be read,
   operations whose capacity type was neither 1 nor 2, work centers whose capacity type was not read.
8. "Next:" the first option to act on.

**A page or dashboard of the at-risk MOs is the bundled dashboard.** Open it through `workspace.md`; never build a separate page for this view. A page for anything the dashboard does not cover (a capacity or shortage report, or a dashboard of the planner's own design) is built only when the planner asks, following `m3/page-style.md`.

Empty state: "No manufacturing orders finish in the next <N> days for <user or policy>. I checked <what>."

## Next step

"Want the full check on MO <no>?" (`material-shortage-check.md`); "Want me to tell the buyer about the late order for <component>?" (`inform-buyer-of-late-order.md`); "Want to plan a purchase for
<component>?" (`m3/create-planned-po.md`); "Want to release the planned PO, or create the PO, yourself? M3 checks your authority; if you don't have it I'll help you tell the buyer" (`handle-po-or-inform-buyer.md`); "Which customers would be affected?"
(`customer-impact.md`); "Want me to check a swap to an alternative item for <component> on MO <no>?"
(`swap-material.md`); "Want me to check another resource for operation <op> of MO <no>?" (`swap-capacity.md`); "Is there an MO of mine we could hold to free up <capacity | material> for MO <no>?" (`hold-mo.md`); "The customer needs only <n> of the <q> on MO <no>: want me to check a split?" (`split-mo.md`).

## Edge cases

- **Nothing found** - the empty state; offer a longer window or another policy.
- **Several matches** - never pick a facility or policy; ask.
- **Can't see it** - name the facility or MO that isn't visible; don't retry.
- **Part of the data missing** - render the rest; name what wasn't checked (for example capacity).
- **Large result** - check the first <cap> MOs by finish date and say how many remain.
- **All route, incomplete** - say which searches ran and that MOs of other planners may be missing; offer the user's own
  route or MO numbers.
