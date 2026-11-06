# Capacity types: machine capacity and labor capacity

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_CPS100MI_SelTotalLoad`, `M3_PMS100MI_GetOperation`, `M3_PMS170MI_LstOperations`

Shared rule for every capacity check in this skill (`at-risk-orders.md`, `material-shortage-check.md`,
`planner-overview.md`, `planner-kpis.md`, `kpi-catalogue.md`, `release-mo-proposal.md`).

Every operation has a **capacity type**. Keep the two types apart: never add machine load to labor load, and never
show them in one table.

| Capacity type on the operation | Called | Load to read from `M3_CPS100MI_SelTotalLoad` |
|---|---|---|
| 1 (Machine hours) | **Machine capacity** | The `...MachineTimeLoad...` fields: manufacturing orders (category A and B) and planned orders (category A and B, groups 1 and 2) |
| 2 (Man hours) | **Labor capacity** | The `...ManTimeLoad...` fields, the same orders and categories |
| Any other value, or blank | Not checked | None; say the operation wasn't checked and why |

## How to read it

1. Read the capacity type from the operation: `M3_PMS100MI_GetOperation` returns `CapacityType` and `WorkCenter` for an
   MO operation (for example `MachineHours`, work center `MB_A_1`); `M3_PMS170MI_LstOperations` does the same for a
   proposal.
2. Read the weekly load for each distinct work center with `M3_CPS100MI_SelTotalLoad` (one read returns both the man-time
   and the machine-time fields). Pick the fields that match the operation's capacity type.
3. Compare the load with `CapacityPerUnitAndShift` for the same week. The rating is per unit and shift, so a work center
   with more units or shifts has more room; say so when the comparison is close.
4. A work center used with both types appears once in each part, with only the operations of that type counted.

## Show it

Two separate parts, in this order, every time capacity is shown:

- **Machine capacity** (type 1): work center, load in hours, capacity in hours, free %, peak week %, alert.
- **Labor capacity** (type 2): the same columns.

For the **selected MO** (the dashboard's panel and the chat answer for one MO), use one table with a **Type** tag per work center:
👷 Labor or ⚙️ Machine (ℹ️ Not read when the capacity type isn't known), then load, rating, week and status. List the weeks from the
MO's start to its finish: the start week always, later weeks only when the work center has load in them.

If a part has no work centers, replace its table with one line ("No operation in scope uses labor capacity"). Show firm MO
load and planned-order load separately inside each part. Say in the coverage line which operations weren't checked
because their capacity type was neither 1 nor 2.

KPIs K10, K18 and K19 are evaluated separately for each part, and an alert names its type ("ALERT, machine capacity,
MB_A_1: 8% free").

**Moving an operation to another resource.** When a type 6 resource is over its rating for an operation, the planner can swap
the operation to another type 6 resource under the same main work center (`swap-capacity.md`). The alternative must have
the same capacity type, and its load is compared with the same fields as above.
