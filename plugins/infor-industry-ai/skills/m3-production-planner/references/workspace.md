# Production planner: the workspace (fixed dashboard)

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_LstUserData_ListUserData`, `M3_MNS150MI_GetUserData_CurrentUser`, `M3_OIS100MI_SearchLine_LimitedOutput`, `M3_PPS115MI_LstAltSupplier`, `M3_PMS100MI_LstMaterials`, `M3_MMS200MI_GetItmWhsBal`, `M3_PMS100MI_LstOperations`, `M3_CPS100MI_SelTotalLoad`, `M3_PMS170MI_LstMaterials`, `M3_PMS170MI_LstOperations`, `M3_MMS200MI_LstItmWhsByItm`, `M3_PMS170MI_SetStatus`, `M3_PMS100MI_SplitMO`, `M3_PMS100MI_TriggerJob`, `M3_PMS100MI_Reschedule`, `M3_PPS200MI_SearchLine`, `M3_PPS170MI_SearchPOP`, `M3_MNS150MI_GetUserData`

<!-- contents:start -->
**Contents**

- What this does
- 1. Before anything else
- 2. Find the planner's own copy
- 3. Publish the bundled dashboard if there is none
- 4. Open it
- Edge cases
<!-- contents:end -->

## What this does

The planner's fixed workspace is the artifact **At-Risk Manufacturing Orders — Production Planner** (bundled as
`assets/planner-dashboard.html`; the planner's own link wins; see `m3/page-style.md`). It shows **only real M3 data**,
read live through the planner's own M3 connector each time it opens or is refreshed: no sample data. If M3 cannot be
reached it says so plainly, never shows made-up data. It follows the same rules as the chat answer in
`at-risk-orders.md`.

**Look and feel.** The same as the customer service rep board (`m3-customer-service-rep`, `assets/rep-dashboard.html`): neutral grey
palette in light and dark mode, Source Sans 3, cards, a header card with the as-of time and **Refresh from M3**, filter chips with icons and
counts, sortable column headings (default: finish date, earliest first), a search box (order or product), statuses as bold coloured text with
an icon (At risk red, Tight amber, OK green), finish dates in red (already late) or amber (due today, or after the customer's requested
date), and the rep board's icon set instead of emoji. The page logic does not depend on the look.

**Scope** (controls at the top): all MOs **and MO proposals** in the user's facility and warehouse (**default**), or the MOs and proposals of one **responsible user** (the signed-in user is
always the second option in the **Responsible user** list; another user is found with **Find**, by name or user ID, from the user list read
with `M3_MNS150MI_LstUserData_ListUserData`); the **Window** list sits directly under it: 7, 14 (default) or 28 days, plus overdue ones (90-day lookback, passed to M3 as a lower date bound so old open orders don't fill the 30-row
limit). The user, facility and
warehouse come from `M3_MNS150MI_GetUserData_CurrentUser`; nothing is hardcoded.

**Three tiles:** MOs in window (counts MOs and proposals; overdue and proposal counts, and a note when M3's search returned 30 rows and the list may be cut off),
**At risk** (with the accent), **Earliest failure** (date and MO).
All three tiles are clickable and take the planner to the **Manufacturing orders** list: **MOs in window** with the filter
set to All, **At risk** with the filter set to At risk, and **Earliest failure** to that MO's row (filter set to At risk,
row selected and highlighted, its components and options shown in the Selected MO panel). With no at-risk MO the
Earliest failure tile just scrolls to the list. The tiles are real buttons, work by keyboard and respect reduced motion.

**Actions live on the order, not in a separate list.** The board has no "needs attention" list. Pressing an at-risk MO (or proposal) in the
list opens its components and its numbered options, in the order of the chat (`at-risk-orders.md`, step 5), each with the recommended date,
the buyer draft, the planned PO to release, the swaps, the hold, the double shift and the sales-rep warning that apply to it
(see "The selected MO" below).

**Customer orders exposed (shown in the Selected MO, not as a section of its own):** open lines (status below 66) from `M3_OIS100MI_SearchLine_LimitedOutput` for each product
with an at-risk MO, requested on or before the last at-risk finish date, or confirmed later than requested.

**The board:** one row per MO **or MO proposal** (a proposal shows as "Proposal <n>"), ranked overdue first then by finish date, with status (❌ At risk / ✅ OK / ℹ️ Can't tell),
cause (**Material** or **Capacity**, or both) and the root cause. With the All, At risk and Proposals filters the root cause column lists every cause of the row, one per line ("<component>: <qty> short, needed <date>", a work center over its rating, a passed finish or start date); with a cause filter (Material, Capacity) it shows only the root cause of that cause.
Filters by status and by cause, a Preliminary filter and a Proposals filter. **Preliminary** MOs (📝) aren't read for components: M3
reserves no material for them until they are firmed; an overdue preliminary MO is still
At risk. If the connector can't read an MO's material lines, that MO shows "Can't tell" with the reason instead of
failing the whole board. The first 25 firmed MOs and the first 25 proposals are checked in depth; the rest show "Can't tell".
On load the top at-risk row is selected, so its options show at once. A failed read is listed in the warning at the top with its tool and the item or MO it was for. M3 answering "Record does not exist" to the alternate-supplier read (`M3_PPS115MI_LstAltSupplier`) only means the item has no agreement: it is not a failure.

How it decides: for each MO, its material lines (`M3_PMS100MI_LstMaterials`) give each component's needed quantity and
date; component stock (`M3_MMS200MI_GetItmWhsBal`, allocatable) is netted across the board's MOs in date order, so
competing MOs show up; a component whose running balance goes short is **Short**. Work centers come from the MO's
operations (`M3_PMS100MI_LstOperations`); a week over the rated capacity (`M3_CPS100MI_SelTotalLoad`) in the MO's start
week is a **Capacity** risk. An overdue MO is always At risk. Unconfirmed POs and proposals never count as safe supply.
A short component is **Material** whether it is bought, made or used first by earlier orders (the root cause says "made" or "taken by earlier orders").
An MO proposal is read the same way with `M3_PMS170MI_LstMaterials` and `M3_PMS170MI_LstOperations` (M3 gives no acquisition code
for a proposal's component, so the board reads it from the item-warehouse record, `M3_MMS200MI_LstItmWhsByItm`, to show Purchased or Manufactured; its shortages are Material either way); a proposal whose start date has passed is
At risk, with its root cause "start date passed, proposal not released" and no cause of its own.

**The selected MO** (click a row): the customer order lines it exposes first (matched by product and date, open lines below status 66). A semi-finished MO has none of its own: instead the panel names the **main MO whose demand it serves** (the top of the chain above it: "Demand from MO <no> · <product>, <qty>, finishing <date>"). Then its component lines (needed, by date, allocatable now, Short / Covered / Not checked)
and numbered **options**, in the order and with the conditions of the chat (`at-risk-orders.md`, step 5). A button acts on the
board after its confirmation dialog; a **Copy request** option hands the planner the exact sentence to paste in the chat, where the
flow is checked and confirmed:
- **Release proposal <n>** (a proposal with no short component; `M3_PMS170MI_SetStatus`, Released): button, as `release-mo-proposal.md`
  describes. A proposal with short components gets "Fix the supply before releasing" instead.
- **Split MO <n>: <u> for customer order <c>, <r> as a new MO** (`split-mo.md`): shown **first, above Reschedule**, only when the check says the urgent
  part is estimated to make the requested date (an At risk firm MO, not started, not on hold, not a sub-assembly; the exposed customer
  quantity is below the MO quantity; material and capacity for the urgent part covered). Button **Split…**: the dialog re-reads the MO, its
  operations, materials and the customer lines, shows the two quantities and the estimated finish, lets the planner choose the new MO's finish date
  (suggested: the MO's current finish). The dialog's **Split** button is the yes: the board re-reads, makes the two calls (`M3_PMS100MI_SplitMO`, then
  `M3_PMS100MI_TriggerJob`) and reports what M3 shows.
- **Reschedule this MO**: button, with the recommended start date and its basis (above) in the dialog; one date (start or finish), finite
  capacity pre-ticked when the cause is capacity (`M3_PMS100MI_Reschedule`), as `reschedule-mo.md` describes. Not offered for a proposal.
- **Pull in the PO by <n> days** (a PO that arrives after the component is needed): button "Draft e-mail…", an Outlook draft to the PO's buyer asking to pull it in.
- **Tell the buyer that <component> is short**: the option says what is wrong (the shortage with its quantity and date, and for each order
  why: unconfirmed, arrives N days after it is needed, overdue, or a proposal whose release date has passed). One Outlook draft per buyer, always
  behind the short button "Draft e-mail…"; the buyer's name is shown next to the button only when several buyers are involved. The draft names the
  order type correctly: "manufacturing order <no>" for a firm MO, "planned manufacturing order <no>" only for an MO proposal.
- **The purchase** (`handle-po-or-inform-buyer.md`): when the item has **no PO and no planned PO**, "Handle the purchase yourself: create a planned PO" (button; without a supplier agreement it says the planned PO has to be created in M3). When **planned POs exist**, "Release the existing planned PO(s) to the supplier" (button per proposal, section 4.1) and no new planned PO is offered. When a **PO exists but is late**, "Buy from another supplier" (planned PO, as above) if another supplier has an agreement.
- **Swap the material for an alternative item** (`swap-material.md`), **move an operation to another resource** (`swap-capacity.md`),
  **a temporary double shift** when no resource has room (`shift-pattern.md`) and **hold another MO** (`hold-mo.md`): buttons that run the flow's
  checks in a dialog and then ask for confirmation, shown only for the cause and customer exposure the chat requires.
- **Release the proposal for a short semi-finished component**: button.
- **Free material from a competing order** (cause Material, a component taken by earlier orders): Copy request.
- **Warn the sales rep**: button.
- Splitting an MO is a board action through the Split… dialog (`split-mo.md`); it also runs in chat.
- **Earlier actions never hide an option.** The options follow the state in M3 now. An action done from the board stays in
  the resolution log, but it does not remove the option: an MO you swapped and then swapped back in M3 gets the swap again.
  Every write re-reads the record and stops if it changed, so offering it again is safe.

**Layout of the selected MO.** Header and status line, **Customer orders exposed**, then **Material** (its own heading above the
components table of level 0, so the two are not read as one), then **Capacity**, then the **Full chain** dropdown (closed first; it reads M3 when the MO
is selected and is hidden when there is only level 0: no made component, or every made component covered from stock),
then **Recommended options**, one section for the whole structure: the swap and capacity options of every level first (a lower-level
option says its level and order), every other option from any level in one closed dropdown, **Other options**. The chain
and the options follow `at-risk-orders.md` (step 4 "The full chain", step 5 "One options list for the whole structure").

**Capacity in the selected MO.** One table, a row per work center per week, for every week from the MO's start (today when the start has
passed) to its finish. Columns: work center, **Type** (tag 👷 Labor or ⚙️ Machine; ℹ️ Not read when M3 gives no capacity type, the same tag
style as Source in Material), load (h), rating (h), week, status (✅ within rating / ❌ over rating, with the %). The start week is always shown;
later weeks only for a work center that has load in them. The chain levels use the same weeks when they check capacity.

**Only options that can help are shown.** Swap material, move operation, double shift and hold run their check first
and are left out when it rules them out; the double shift stays with a ⚠️ "Will not solve everything" warning when a week
stays over the rating; reschedule is offered only for an MO that is At risk (`at-risk-orders.md`, step 5).

**Tabs.** Under Key Measures the board has three tabs, in this order: **Manufacturing Orders and Proposals** (the list and the Selected MO
panel; it opens first and the three tiles jump to it), **Late or Unconfirmed Supply** and **Work Center Load**. The Resolution log follows
the tabs. **Work-centre load:** weekly hours against the rating, one small chart per work
centre in a compact grid, over-rating weeks in the danger
colour, in two parts: **Machine capacity** (machine hours) and **Labor capacity** (man hours), by the work center's
capacity type (`capacity-types.md`); a work center whose type M3 does not give is listed as not checked.

**Late or unconfirmed supply — tell the buyer** (its own tab; its note gives the number of orders and buyers): the PO lines (`M3_PPS200MI_SearchLine`) and planned POs
(`M3_PPS170MI_SearchPOP`) behind the short purchased components, each with what is wrong (unconfirmed, arrives after it
is needed, overdue, release date passed), grouped by buyer, shown by name (read with `M3_MNS150MI_GetUserData`; the user ID only when M3 gives no name). One button per buyer drafts the information e-mail of
`inform-buyer-of-late-order.md` (step 4) in the planner's Outlook through their e-mail connector, opens it for review,
and never sends it. The buyer's address comes from `M3_MNS150MI_GetUserData`; when M3 has none, the planner adds it.
Without an e-mail connector the text is offered to copy. The board only creates drafts; to send, use the chat flow
(`inform-buyer-of-late-order.md`), which sends by e-mail after one approval (`m3/mail-delivery.md`). The planner sends no M3 application messages.

**Resolution log:** one line for everything done from the board (reschedules, releases, buyer drafts), with the time,
the result M3 read back and whether it was the user or a colleague, kept in the page's database. It is a record only and never hides an option.

**Writes from the board.** The writes the board runs are: reschedule (one MO at a time), release an MO proposal, create a planned PO and assign its PO
number, release an existing planned PO into a purchase order (`handle-po-or-inform-buyer.md`, 4.1), swap a material (`swap-material.md`), swap an operation's resource (`swap-capacity.md`), hold an MO (`hold-mo.md`) and a temporary double
shift (`shift-pattern.md`), each as its flow in the chat describes: the board runs the same reads and checks first, shows what will change, and writes
only after its own Confirm click. Releasing a held MO is not on the board yet (chat or M3). A split is written from the board only through its own dialog (one Split click, two calls). The board never runs a delete of its own: removing a double shift, deleting orders or proposals is done in chat only. The only delete it runs is a named step of a flow, shown on that flow's card (the MO proposal delete in the material swap). Each write runs only after the planner clicks the button in its own confirmation dialog, which shows exactly what will
change. The board then re-reads the record and stops without writing if it changed since the board loaded (gone,
different dates or quantity, already started), makes **one** call, reads the result back and logs it. An ambiguous
failure (M3 didn't answer) is reported as "outcome unknown: refresh before trying again"; the board never retries a
write by itself. A reschedule is processed by M3 in the background, so the board says the dates can still move.

The board never changes an existing purchase order, never contacts a supplier and
never sends an e-mail (it only creates drafts). It releases a planned PO only through its own confirmation dialog (two steps: set the planned PO to Released, then run the release for that buyer, supplier and facility; printing the PO to the supplier stays the buyer's step). When the planner asks in chat about something done on the board, read the resolution log
(`read_db`, collection `actions`) and the M3 record before answering.

**Scope.** Only the planner's role is built here. The buyer and the customer service rep have their own use cases; the planner only
informs the buyer (and, in chat, warns the sales rep: `warn-sales-rep.md`).


## 1. Before anything else

**Open the existing dashboard first. Never build a new one.** When the planner says things like "show my dashboard",
"show my at-risk MOs in a dashboard", "open my planner board" or "give me all production orders at risk in a dashboard
format", and the user is clearly a production planner working with manufacturing orders (see "Edge cases"
below), follow `m3/page-style.md` and the steps below.

Do this before any M3 call and before any other dashboard skill.

## 2. Find the planner's own copy

Use the link the user gave in this conversation or in the Claude Project's instructions. If there is none, look for
the user's own copy with the Artifact tool's `list` action (a title like "At-Risk Manufacturing Orders", "Production
Planner" or "action board") and open the best match.

## 3. Publish the bundled dashboard if there is none

If the user has no copy (the usual case for a colleague: artifacts are private to their owner and cannot be shared
through the plugin), **publish the bundled dashboard for them**: it ships with this skill as
`assets/planner-dashboard.html`, with its capabilities in `assets/planner-dashboard.capabilities.json`. Copy the file to `/mnt/user-data/outputs/`, load the
`artifact-capabilities` skill and publish it with those capabilities (`db`, `user` and `mcp`). **The page itself stays as
bundled, with one allowed change:** when the user's connector names differ from the bundled ones (`M3 Manufacturing MCP`
and `Microsoft 365`), put their names in the `server` entries of the capabilities and, in the same publish, in the page's
`SERVER` and `MAIL` constants (one edit each, made on the copy before it is published). When the names are the same, change
nothing. If the user has no e-mail connector, drop the `Microsoft 365` entry from the capabilities and leave `MAIL` as it
is: the board then offers the buyer notice as text to copy. Change nothing else in the page. The copy is private to the user; tell them so, and that it is titled
"At-Risk Manufacturing Orders — Production Planner". Reuse it afterwards, never publish a second copy. The page has no
tenant settings to check: user, facility and warehouse come from the signed-in M3 user.

## 4. Open it

Open it with the Artifact tool's `open` action when that is available, otherwise give the link. Add one or two lines
on what it shows ("What this does" above). Say which artifact you opened, so the user can correct you.

Changes to the dashboard go into the **same** artifact, never into a new one, so the link is always the latest version.
Build a new page only if the user explicitly asks for a new dashboard. Do not make something up.

## Edge cases

Offer the planner dashboard only when you are sure the user works with **manufacturing orders**: for example they ask
about MOs at risk, material shortages for production, MO proposals, work-centre capacity or rescheduling. The word
"dashboard" alone is not enough: a buyer (purchase orders, suppliers) needs `m3-buyer` and a customer service rep
(customer orders) needs `m3-customer-service-rep`. If you cannot tell which role the user has, ask one short question
("Do you work with customer orders, purchase orders or manufacturing orders?") before opening anything.
- "Give me all production orders at risk and recommendations" without "dashboard" is the chat answer (`at-risk-orders.md`), not a dashboard request; end it with one line that the same view is in the dashboard.
- If you cannot tell what the user wants, ask once. Do not guess by building something.
