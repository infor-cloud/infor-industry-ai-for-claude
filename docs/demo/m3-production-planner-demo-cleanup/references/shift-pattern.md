# Delete the shift pattern adjustments of a work center

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_PDS010MI_Get`, `M3_CPS100MI_SelTotalLoad`, `M3_PDS016MI_GetDailyCap`, `M3_PDS010MI_DelShiftPatAdj`, `M3_PDS010MI_CrtCapacity`

Command: "Delete shift pattern for <work center>". The rules in `SKILL.md` apply (typed work center, one card, one yes,
re-read before writing, facility, refusals, read back).

This file is also used by `production-demo-reset.md`, which calls for steps 2 and 3 with a wider window and does its own card
and delete.

The normal (original) shift pattern, usually 001, is **never deleted**: only deviating weeks and days are adjustments.

The connector can't list shift pattern adjustments, and `M3_PDS010MI_DelShiftPatAdj` needs the work center and the exact
from date, so find them from the capacity first.

## Steps

1. **The work center.** Use the code in the command (`M3_PDS010MI_Get { Facility, WorkCenter }` to confirm it and read
   its description). If the user gave a description and you don't know the code from this conversation, ask for the code
   once.
2. **The weeks.** `M3_CPS100MI_SelTotalLoad { Facility, WorkCenter, FromDate: <Monday two weeks ago>, ToDate: <today + 14 weeks> }`.
   The rating per week is `CapacityPerUnitAndShift`; the **normal rating is the most common value**. Weeks with another
   value are candidates. If there are none: say "No shift pattern adjustment found on <work center name (code)> from
   <from> to <to>." and stop.
3. **The days.** For each run of consecutive candidate weeks read each weekday, Monday to Friday, with
   `M3_PDS016MI_GetDailyCap { Date, Facility, WorkCenter, StartTime: 700 }`. A normal day reads the normal shift (`001`,
   07:00 to 11:00, 4 h); a day with an adjustment reads another shift, other hours or no block at 07:00. The **first and
   last such day** of a run are its from date and to date. If an adjustment started on a weekend, the first weekday found
   is not its from date: if M3 answers "does not exist" to the delete in step 5, try the Sunday and then the Saturday
   before it (a failed delete changes nothing).
4. **Card** (one line per adjustment found; nothing else is listed):

   > **Delete the shift pattern on <work center name> (<code>)**
   > <from date> to <to date>: shift <shift read on those days>, <h> h a week instead of <normal> h.
   > The work center goes back to the normal shift <normal> for those days.
   > Reply **yes** to delete.

5. **After the yes**, per adjustment: `M3_PDS010MI_DelShiftPatAdj { Facility, WorkCenter, FromDate }`. Only when M3
   accepts it, `M3_PDS010MI_CrtCapacity { Facility, WorkCenter, FromDate, ToDate }` for the same span (the to date is the
   last day found). If the delete is refused, change nothing else and say what M3 said.
6. **Read back.** `M3_PDS016MI_GetDailyCap` for the from date at 07:00 (and the to date): the normal shift again. If it
   still reads the old shift, read again every 20 seconds, up to 4 times, then say that M3 still shows the old shift and
   to read it again later. Report per adjustment: "<work center>: back to the normal shift from <from> to <to>." If the
   delete worked but the capacity call failed, say that and nothing more (no retry).
7. **MOs that were planned on the extra capacity are not rescheduled** by this command.
