# Temporary double shift on a work center resource (machine or labor), and removing it again

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_PDS010MI_AddShiftPatAdj`, `M3_PDS010MI_CrtCapacity`, `M3_PDS030MI_SelPatternLines`, `M3_PDS016MI_GetDailyCap`, `M3_PMS100MI_Get`, `M3_PMS100MI_LstOperations`, `M3_PMS100MI_GetOperation`, `M3_PDS010MI_Get`, `M3_CPS100MI_SelTotalLoad`, `M3_PDS010MI_DelShiftPatAdj`

<!-- contents:start -->
**Contents**

- What this does and doesn't do: Shift patterns: read them first
- 1. When to offer it (all five must hold)
- 2. Recommend the time span
- 3. Will it cover the load
- 4. Offer it (advice only)
- Confirm before writing
- 5. Read back and report: Result line
- 6. Removing a double shift (end it, or take it back)
- Next step
- Edge cases
<!-- contents:end -->

Guided write, two calls on one card and one yes: identify the work center resource that is over capacity -> confirm that
nothing else fixes it (no swap, no reschedule) -> read the facility's shift patterns and the work center's current shift -> recommend a double shift from a date to a date
-> one card -> add the shift pattern adjustment -> recreate the capacity for the same period -> read back and report.
**One yes covers both calls. Do not mention the capacity recreation to the planner (not in the card, the report or the next step): it is part of adding the shift. Say something only if it fails (step 3).**

## What this does and doesn't do

- **The scenario.** A resource (a machine or a labor resource, work center type 6, or any work center the operation uses) has
  more load than its rating in the weeks that matter, and **no other resource can take the work** (`swap-capacity.md` doesn't
  apply or found no room). The planner can then run the resource with a **double shift** for a limited time.
- **Two calls, in this order.** (1) `M3_PDS010MI_AddShiftPatAdj` adds a shift pattern adjustment for the work center:
  `{ Facility, WorkCenter, FromDate, ToDate, ShiftPattern }`. (2) `M3_PDS010MI_CrtCapacity` recreates the work center's
  capacity for the same period: `{ Facility, WorkCenter, FromDate, ToDate }` (add `CompanyNumber` only if M3 asks). The second
  call runs only when the first call succeeded; it is **on the same yes** because the card names it.
- **Temporary only.** The adjustment has an end date. The flow never makes a double shift open-ended and never changes the
  work center's normal shift pattern, calendar or rating on the work center itself.
- **Machine or labor, one resource at a time.** Machine and labor capacity are never mixed (`capacity-types.md`). A machine
  and the labor that runs it are two resources: if both are short, offer one after the other, each with its own card.
- **One adjustment per card.** Never change several work centers on one yes.
- **Nothing else changes.** No MO, operation, routing, run time, setup time, machines, workers or date is changed by this
  flow. Capacity is recreated, so M3's own planning will see the extra hours; **existing MOs are not rescheduled by this
  flow**. Say so afterwards and offer a reschedule as a separate action (`reschedule-mo.md`).
- **From a dashboard.** A Confirm click on a board may run this, as in chat: the board shows the same card with the facility's listed shift patterns, makes the two calls in the same order (the second only if the first succeeded) and reads the result back.
- **Cost people feel.** A double shift means people work the second shift or the machine runs longer. M3 can't tell whether
  anyone is available; say so on the option and leave that to the planner.

### Shift patterns: read them first

Never take a pattern number from memory or from this file: **read the facility's shift patterns first**, once per
conversation, and keep the result.

`M3_PDS030MI_SelPatternLines` `{ FromFacility, ToFacility }` (both the facility of the work center; `CompanyNumber` only if M3
asks). Per line it returns `ShiftPattern`, `Description` (for example "Day shift M-F, 7-16" or "2-shift M-F, 4-20"),
`ShiftModel` (for example DAY, 2SH), the validity `FromDate` and `ToDate`, and `NumberOfDays`. **It gives no hours per day and
doesn't say which pattern a work center runs.** Show the list to the planner whenever they ask which patterns exist.

| Question | How it is answered |
|---|---|
| **Which pattern does the work center run now (the normal shift)?** | `M3_PDS016MI_GetDailyCap` `{ Facility, WorkCenter, Date, StartTime }` on a normal working day returns `Shift` and `NominalHours` per block (try start times 700 and 1200; add the blocks of one day). **`Shift` is a shift inside the shift model, not the pattern**: for a day model it reads 001, for a 2-shift model AM and PM. Match the blocks to a pattern's model in the list. If you can't tell, ask. This company's default normal pattern is **001**, usually listed as model DAY. |
| **Which pattern is the double shift?** | A listed pattern **valid for every day of the span** (`FromDate` to `ToDate` covers it) with **more shifts per day** than the normal one, judged from its `ShiftModel` and `Description`. This company's default is **002** ("2-shift", model 2SH): **use it when it is listed, valid for the whole span and has more shifts than the normal pattern.** If the default isn't listed or isn't valid, don't use it: say so and show the candidates. If several patterns qualify, show them and let the planner pick. **A pattern the planner names always wins** ("use 003"), if it is listed and valid. |
| **How many hours a day?** | Not readable before the pattern is applied. Estimate: shifts per day under the new pattern x the nominal hours of one normal shift (a 2-shift model on an 8 h day = 16 h) and say it is an estimate. The clock span in the description (4-20) is a span, not nominal hours: breaks are left out. The read-back after the change gives the real hours. |

Show the pattern, its description, its shift model and its validity on every card.

## 1. When to offer it (all five must hold)

Read the MO (`M3_PMS100MI_Get`), its operations (`M3_PMS100MI_LstOperations`, `M3_PMS100MI_GetOperation`) for the work center,
**capacity type** and remaining hours, and the work center (`M3_PDS010MI_Get`: `ResourceType`, `SuperiorWorkCenter`,
`CapacityType`).

| # | Condition | How it is judged |
|---|---|---|
| A | **The resource is over its rating** | `M3_CPS100MI_SelTotalLoad` `{ Facility, WorkCenter, FromDate, ToDate }` over the weeks the at-risk operations span (and the next 14 days): in at least one week the load of the operation's capacity type (machine time for `MachineHours`, man time for `ManHours`; manufacturing orders and planned orders, category A and B, `capacity-types.md`) is **above `CapacityPerUnitAndShift`**. Name the week, the load and the rating. |
| B | **No other resource can take it** | `swap-capacity.md` conditions apply and found **no related resource with room** (none listed, none of the same capacity type, or none with room), or the work center isn't a type 6 resource. Say which. If a swap with room exists, recommend the swap and offer the double shift only if the planner asks. |
| C | **Rescheduling doesn't fix it** | The logic of `reschedule-mo.md` (capacity short): no week up to the date the MO must finish by has free capacity for the hours, or moving to the first week with room makes a customer order late. |
| D | **A double shift would cover the load** | Step 3, with a listed pattern that has more shifts per day and is valid for the whole span: the estimated rating under the double shift is at or above the load in every week of the span. |
| E | **No other adjustment is in the way** | The first day of the span reads the **normal pattern's** blocks and shift names (`M3_PDS016MI_GetDailyCap`, matched against the patterns read above): if it reads other blocks, a shift pattern adjustment or a calendar change may already apply. Say so and don't offer. **This connector can't list existing adjustments**; if the first day can't be read or doesn't match a listed pattern, say "current shift not read" and give Medium or Low confidence. |

Also don't offer it, and say why in one line, when: the work center can't be read; the capacity type is neither
`MachineHours` nor `ManHours`; the span would start in the past; or the planner doesn't own the MO (scope).

## 2. Recommend the time span

The recommendation is **a from date and a to date**, both `YYYY-MM-DD`, and the planner can change either.

- **From date** = the first day the extra capacity is needed, **never before today**. Start from the Monday of the first week
  over its rating (condition A), or the start date of the first at-risk operation if that is later, and never earlier than
  tomorrow when the shift change needs people to be told (say that on the card).
- **To date** = the last day the extra capacity is needed: the end of the last week that is over its rating, or the finish
  date of the last at-risk operation on the resource, whichever is later, but **the smallest span that brings every week
  in it to or under the rating** (step 3).
- **Whole weeks are the norm.** A double shift that starts mid-week is allowed; say which days of the week it covers. If the
  span is longer than **4 weeks**, show it but say it is long and ask whether to cover only the first 4; M3 can take more.
- **Give the reason in one line:** "week 44 is at 120% of 40 h on MB_LA1; week 45 at 95%; a double shift from 2026-10-27 to
  2026-11-06 brings both under 60%."
- **Never extend the span just in case.** Extra days cost money; the planner can ask for more.
- **No weekend dates.** Never propose a from date or a to date on a Saturday or Sunday: move it to the next Monday.

## 3. Will it cover the load

For each week of the span (from `M3_CPS100MI_SelTotalLoad`, the fields of the operation's capacity type):

- **Rating now** = `CapacityPerUnitAndShift` for the week.
- **Rating under the double shift (estimate)** = rating now x (double-shift hours per day / normal-shift hours per day), the hours estimated as in the
  table above. With 8 and 16 hours that is x 2. **This is an estimate**: this connector can't read the hours a shift pattern gives, and the rating
  per unit and shift may or may not scale in M3's load table (`m3/known-inconsistencies.md`: not yet seen). For a partial
  week, scale only the days in the span and say so.
- **Load** = manufacturing orders (category A and B) + planned orders (category A and B, groups 1 and 2) of that type; show
  firm MO load and planned-order load separately. Planned orders are proposals, not firm load.
- **Utilisation under the double shift** = load / estimated rating.

| Result | Label |
|---|---|
| Every week of the span at or under 95% | ✅ Covers it |
| Covers it, but a week is above 95% | ⚠️ Tight: <week> at <x>% |
| Some week stays over the rating | ❌ Not enough: not offered; say how much is still missing and offer the other options (`at-risk-orders.md` step 5) |
| Load not returned for the weeks | ⚠️ Capacity not checked: not offered |

Confidence: **High** when the current shift and its hours were read, the load was read for every week and the span is
covered with margin; **Medium** when the double-shift pattern was named by the planner or isn't the default 002 (the hours are always an estimate until the change is read back, so that alone doesn't lower it), or the room depends on a
planned order or an adjustment couldn't be ruled out; **Low** when part of the data wasn't read.

## 4. Offer it (advice only)

> **Option: double shift on <work center, name> from <from date> to <to date>** (<machine | labor> capacity)
> Why: <work center> is over its rating in week <w> (<load> of <rating> h) and no other resource can take the work
> (<reason from condition B>); rescheduling doesn't help (<reason from condition C>).
> Change: shift pattern <normal pattern> <description> (<h> h a day) -> <double-shift pattern> <description>, model <model>, valid <from> to <to> (about <h> h a day, estimate) for <n> days.
> Estimated rating <x> h a week, <load> h load -> <y>% utilisation.
> Confidence: <High | Medium | Low>. What would change it: <double-shift hours given by the planner, planned orders, an
> adjustment that couldn't be ruled out>.
> Cost: the second shift needs people (labor) or longer machine running time; M3 can't tell whether they are available.
> ⚠️ Will not solve everything (only when a week stays over the rating with the doubled rating): week <w> would still be at <y>% of
> the doubled rating (an estimate). Combine it with another option, such as a reschedule. When the span is covered but a week
> is between 95% and 100%, write "⚠️ Tight" with the same figures.
> The option is **still offered** when it clears only part of the overload; a partial double shift is valid, so it is never
> hidden for that reason, and the warning says what stays open.

Show nothing else as applied: the option changes nothing.

## Confirm before writing

Re-read first (write protocol step 3): the work center is still over its rating in the weeks named, the first day of the span
still runs the normal shift, and the MO and operations that made the shortage are unchanged. If anything differs, don't show
the card: say what changed.

> **Double shift on <work center, name>** (<machine | labor> capacity)
> Facility <f>. Shift pattern **<normal>** -> **<double>** from **<from date>** to **<to date>** (<n> days, <weekdays>).
> Why: <the overload and why nothing else closes it, one line>. Estimated utilisation under the double shift: <x>%.
> On this one yes I will add the shift pattern adjustment: `M3_PDS010MI_AddShiftPatAdj` for <work center>, <from date> to <to date>, pattern <double>.
> Not changed: the work center's normal shift pattern, calendar and rating; routings; any MO, operation or date. MOs already
> planned are not rescheduled by me. I can't undo this from here: removing the double shift is a separate card (step 6), or
> is done in M3.
> Reply **yes** to add the double shift.

Only after an explicit yes to this card:

1. **Snapshot** the load and the rating of the work center for the span (`M3_CPS100MI_SelTotalLoad`) and the daily capacity
   of the first day, from the reads you just made.
2. **Call `M3_PDS010MI_AddShiftPatAdj` once** with `{ Facility, WorkCenter, FromDate, ToDate, ShiftPattern: <double> }` and
   nothing else. On an error, report M3's message plainly and stop: no capacity recreation, no retry, no other pattern. A
   refusal for an existing adjustment or an overlap means one already applies: say so and ask the planner to check it in M3.
   Read the first day (`M3_PDS016MI_GetDailyCap`) to see whether it saved.
3. **Call `M3_PDS010MI_CrtCapacity` once** with `{ Facility, WorkCenter, FromDate, ToDate }` (the same dates) only when step 2
   succeeded. It returns no data. If M3 refuses or the call fails, report it: **the adjustment stands, the capacity is not
   recreated**, so the planner must recreate it in M3 (or ask for the call to be repeated once with a new yes). Don't retry.

## 5. Read back and report

1. **The first and last day of the span:** `M3_PDS016MI_GetDailyCap` for the first day (and the last working day) at the
   start times of the work center: `Shift`, `NominalHours` per interval, summed to a day. ✅ when the blocks and shift names are those of the double pattern's
   shift model and the hours match the estimate (state the real hours); ⚠️ when the shift names or hours differ; ⏳ when the capacity still shows
   the old shift: M3 may need a moment, read every 20 to 30 seconds for about 2 minutes, then say it hasn't changed and give
   the read time. **The capacity is rebuilt by a background function in some installs; say "M3 shows X now", not that it is
   done.**
2. **The weekly picture:** `M3_CPS100MI_SelTotalLoad` over the span: rating before and now, load, utilisation, for each
   week, against the snapshot. ✅ at or under 95%; ⚠️ tighter; ❌ still over. State whether `CapacityPerUnitAndShift`
   actually doubled; if the load table did not change, say so and give the read time.
3. **What is not done yet:** the MOs whose operations were short are **not rescheduled**: say which ones (names, the dates
   and the customer orders they serve, as `customer-impact.md` gives them) and offer the reschedule.

### Result line

```
<work center> (<machine | labor>): shift <normal> -> <double> from <from> to <to>; adjustment added
First day now <hours> h on shift <pattern>; weekly rating <before> -> <now> h
Load <load> h: utilisation <x>% -> <y>%. MOs to reschedule: <list | none>
```

## 6. Removing a double shift (end it, or take it back)

Guided write, two calls on one card and one yes, the mirror of the add: identify the work center and the adjustment ->
read that it is in force -> show what the load does without it -> one card -> delete the adjustment -> recreate the
capacity for the period it covered -> read back and report. **One yes covers both calls; don't mention the capacity recreation to the planner (only if it fails).**

- **When.** The planner asks to end or remove the double shift on a work center ("take <work center> back to one shift",
  "remove the double shift from <date>", "we don't need the second shift any more").
- **What identifies the adjustment.** `M3_PDS010MI_DelShiftPatAdj` takes `{ Facility, WorkCenter, FromDate }`: the **from
  date** of the adjustment. **This connector can't list adjustments**, so take the work center and from date from this
  conversation (the adjustment added earlier) or from the planner; if the planner doesn't know the from date, ask for it
  and say it is shown on the shift pattern adjustment in M3. The **to date** (needed to recreate the capacity) is read the
  same way; if unknown, ask. Never guess a date.
- **Check it is in force.** `M3_PDS016MI_GetDailyCap` for the work center on the from date (start times as in "Shift patterns: read them first"): it must show the blocks of the **double-shift pattern's shift model** (read the patterns first: the default 002 is model 2SH, shifts AM and PM). If it shows the normal shift or can't be read, don't show
  the card: say the adjustment wasn't confirmed and ask the planner to check it in M3. The check is only a sign, not proof,
  that this is the adjustment the planner means: say so.
- **What it does to the plan (advice).** Read `M3_CPS100MI_SelTotalLoad` for the span (from the from date, at least to the to
  date) and compute for each week the utilisation with the **normal** rating (the rating now divided by the double-shift
  factor; an estimate, as in step 3). List every week that would go back **over its rating** and the MOs whose operations on
  this work center fall in it (`M3_PMS100MI_LstOperations` for the MOs you already know; name them, with the customer
  orders they serve). Without any such week: ✅ "load fits one shift in every week". With some: ⚠️ say which, and that
  those MOs lose the extra hours; offer to remove it anyway, or to **shorten** it instead (remove it, then add a new double
  shift with the shorter span as a separate card from step 4).
- **Not for the past.** An adjustment whose to date has passed isn't removed (its period is over); say so. If it started in
  the past and runs on, removing it only affects capacity from **today**: recreate capacity from today (or the from date if
  it is later) to the to date, and say that days already worked keep their capacity.

> **Remove the double shift on <work center, name>** (<machine | labor> capacity)
> Facility <f>. Shift pattern adjustment from **<from date>** to **<to date>** (pattern <double>) is removed; the work center
> goes back to its normal shift <normal> (<h> h a day) for those days.
> Why: <the planner's reason, one line>. Without the double shift: <weeks over the rating and the MOs in them | no week over the rating>.
> On this one yes I will delete the adjustment: `M3_PDS010MI_DelShiftPatAdj` for <work center>, from date <from date>.
> Not changed: the work center's normal shift pattern, calendar and rating; any MO, operation or date; no MO is
> rescheduled by me. I can't undo this from here: adding the double shift again is a new card.
> Reply **yes** to remove the double shift.

Only after an explicit yes to this card:

1. **Re-read first** (write protocol step 3): the first day still reads the double shift, the load picture is unchanged.
2. **Call `M3_PDS010MI_DelShiftPatAdj` once** with `{ Facility, WorkCenter, FromDate }` and nothing else. On an error
   (for example "record does not exist") report M3's message plainly and stop: no capacity recreation, no retry; read the first
   day (`M3_PDS016MI_GetDailyCap`) to see whether it changed.
3. **Call `M3_PDS010MI_CrtCapacity` once** with `{ Facility, WorkCenter, FromDate: <recreate from>, ToDate }` only when step 2
   succeeded. If it fails, report it: **the adjustment is deleted but the capacity is not recreated**, so the capacity still
   shows the double shift until it is recreated in M3 (or the call is repeated once on a new yes). Don't retry.
4. **Read back** as step 5 does: the first day's `Shift` names and hours (✅ the normal pattern's blocks again; ⏳ still the double shift: read
   every 20 to 30 seconds for about 2 minutes, then say it hasn't changed and give the read time), the weekly rating and
   load against the snapshot, and the MOs that now sit in a week over its rating (offer `reschedule-mo.md`, one MO at a time).

```
<work center> (<machine | labor>): double shift <double> removed (was <from> to <to>); back to <normal>
First day now <hours> h on shift <pattern>; weekly rating <before> -> <now> h
Load <load> h: utilisation <x>% -> <y>%. Weeks over the rating again: <list | none>. MOs to reschedule: <list | none>
```

## Next step

- "Want me to reschedule MO <n> so M3 uses the extra hours?" (`reschedule-mo.md`, its own card, one MO at a time).
- "Want to check the other operations on <work center> that fall in the span?" (`at-risk-orders.md`).
- The span ends before an MO finishes: say which, and offer a longer span as a new card.
- "Which customers does this affect?" (`customer-impact.md`) when dates are still exposed.

## Edge cases

- **No weeks over the rating** - not a case: "<work center> is under its rating in every week: 28 of 40 h." Offer the other options.
- **A swap with room exists** - recommend the swap (`swap-capacity.md`); offer the double shift only if asked.
- **The work center is not a type 6 resource** - allowed here; say which kind it is. A machine and its labor are separate
  resources: say which one you are changing.
- **The double shift would still not cover it** - ❌, not offered; say how much is missing and what is left (a hold, a purchase, a split, or telling the sales rep).
- **The planner names the dates or the shift pattern** - theirs win if the pattern is listed and valid for the span; say how the span differs from your recommendation, and
  recompute step 3. A pattern that isn't listed or doesn't cover the span: say so and show the list. A pattern M3 refuses: report M3's message; don't try another.
- **The default 002 is not listed or isn't valid for the span** - don't use it; show the listed patterns that qualify, or say none does and stop.
- **`M3_PDS030MI_SelPatternLines` returns nothing or fails** - say the shift patterns couldn't be read; don't offer the double shift unless the planner names a pattern, and then give Low confidence.
- **Another shift is already running on the first day** - don't offer; "the first day already reads <blocks and shift names>"; ask the planner to check M3.
- **M3 refuses the adjustment** (unknown pattern, overlap, dates) - report its message; nothing was changed; don't try another route.
- **The adjustment saved but the capacity call failed** - report both results separately; the adjustment stands; no retry.
- **The first day cannot be read** - say "current shift not read"; offer with Medium or Low confidence, or not at all if the planner prefers.
- **Span longer than 4 weeks** - show it, say it is long, ask whether to cover the first 4.
- **Several resources are short** - one at a time, each with its own card; the first change doesn't count as room for the next.
- **Removing it later** - step 6. `M3_PDS010MI_DelShiftPatAdj` is used only there, for the adjustment the planner named, and only with the capacity recreation.
- **A tool is missing** - say which (`M3_PDS010MI_AddShiftPatAdj` or `M3_PDS010MI_CrtCapacity`) and that the double shift isn't
  offered; don't use another write tool.
- **Can't see it / not permitted** - report; don't retry.
