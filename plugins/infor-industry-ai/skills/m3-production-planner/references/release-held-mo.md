# Release a held MO

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PMS100MI_RelHeldMO`, `M3_PMS100MI_SearchMO`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstOperations`, `M3_PMS100MI_LstMaterials`, `M3_CPS100MI_SelTotalLoad`

Guided write: identify the held MO -> check what it takes back -> one card -> `M3_PMS100MI_RelHeldMO` -> read back and
report. The hold itself is in `hold-mo.md`.

## 1. Identify the held MO

The MO the planner names, or the one just held in this conversation. Without a name, read the planner's MOs
(`M3_PMS100MI_SearchMO` with the user as responsible and no upper status bound) and keep those whose status reads as held; if
none can be told apart, ask for the number. Read it (`M3_PMS100MI_Get`, `M3_PMS100MI_LstOperations`,
`M3_PMS100MI_LstMaterials`). If it is **not held**, say what its status is and stop.

## 2. What it takes back

Release returns the order to normal planning. Check, and warn without blocking:
- **Capacity:** `M3_CPS100MI_SelTotalLoad` for its work centers over its weeks: would adding its hours put a work center
  back **over its rating**? Show the week, the load and the rating.
- **Material:** would its demand put a component short again, and for which MOs? Name the target MO of the earlier hold if
  this conversation has one: "MO <target> (customer order <n>, due <date>) was relying on this hold" is a strong warning, in
  plain words.
- **Dates:** if its planned start is **before today**, say it is overdue and that M3 may move its dates on release; offer
  `reschedule-mo.md` afterwards.

## Confirm before writing

> **Release the hold on MO <number>**
> <product> (<n>), facility <f>, quantity <q>, planned <start> to <finish>, status <held status>
> Effect: the order returns to normal planning. <Capacity: ✅ no work center goes over its rating | ⚠️ <work center> week
> <w>: <load> of <rating> h.> <Material: ✅ no component runs short | ⚠️ <item> short <qty> on <date>, affecting MO <n>.>
> <Dates: planned start <date> is before today; M3 may move the dates on release.>
> <If a target relied on the hold: "MO <target> (customer order <n>, due <date>) was relying on this hold.">
> Dates: start <current> -> <new> (the date you gave; M3 requires one on any release); M3 recalculates the finish.
> Not changed: its quantity, operations and materials; other MOs.
> Reply **yes** to release.

Only after an explicit yes: **call `M3_PMS100MI_RelHeldMO` once** with `{ Facility, ManufacturingOrderNumber, ProductNumber }` and
**the start date the planner gave** (`StartDate`) and nothing else (no times, no finish date, no reschedule flag). **M3 refuses a release
of a held MO without a date, short-term or long-term** ("Start or finish date must be entered", tested, K23): ask the planner once for the date the
order returns to, suggest one with its reason (its original start date from before the hold if known, or the order's current start
date if nothing should move), never pick it, and put the old and new dates on the card. On an error, report it plainly and stop;
don't retry.

## 3. Read back and report

1. **The MO:** `M3_PMS100MI_Get`; wait while it reads "...-ChangeInProgress" (up to six reads); show before and after for
   status, start and finish date and time, quantity and priority. If M3 moved a date, say so prominently with both values.
2. **The load and the material** as in `hold-mo.md` step 6: where they are now against what they were while the MO was held; the
   target's verdict if one is known.
3. If the dates are in the past, offer the reschedule (`reschedule-mo.md`); never move them yourself.

## Show it

```
Release: MO <number> <held status> -> <status now>; dates <unchanged | old -> new>
Back on: <work center> week <w>: <load> of <rating> h | <item> demand <qty>. Target MO <target>: <verdict>
```

## Next step

"Want me to check whether MO <target> is still on time?" (`material-shortage-check.md`).

## Edge cases

- **The MO is not held** - say what its status is; nothing is released.
- **M3 refuses the release** - report its message; nothing was changed unless the read-back says so; don't try another route
  or tool.
- **MO changed since the card was shown** - don't write; re-read and show the card again.
- **The MO shows "...-ChangeInProgress" before a write** - don't write. Read again after 30 to 45 seconds; if it still shows
  it after about two minutes, another M3 program the planner has open can hold the MO: ask them to close it.
- **Several matches** (MO, product) - list and ask; never pick.
- **Can't see it / not permitted** - report; don't retry.
- **A tool is missing** - say that `M3_PMS100MI_RelHeldMO` isn't available and that the release isn't offered; don't use
  another write tool.
