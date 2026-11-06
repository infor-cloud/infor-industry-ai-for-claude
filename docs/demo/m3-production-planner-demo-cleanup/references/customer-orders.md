# Delete the customer orders for an item

**Tools for this file** (load the ones the next step needs, together in one tool search): `M3_MNS150MI_GetUserData_CurrentUser`, `M3_OIS100MI_SearchLine_LimitedOutput`, `M3_OIS100MI_GetOrderHead`, `M3_OIS100MI_DelHead`, `M3_OIS100MI_DelLine`

Command: "Delete all COs for item <item>". The rules in `SKILL.md` apply (typed item, one card, one yes, re-read before
writing, facility, refusals, read back). `production-demo-reset.md` reuses steps 1, 2 and 4 as part of the full reset.

## Steps

1. **Read the lines.** `M3_OIS100MI_SearchLine_LimitedOutput { ItemNumber_ExactSearch: <item> }`. Searched on the item
   alone this returns the item's whole history (invoiced and completed lines too), so filter the result yourself. Group
   the lines by `OrderNumber`. Ignore lines already deleted (status 90). For each order read all its lines
   (`{ OrderNumber_ExactSearch: <order> }`): the other items and every line status. Lines in a facility other than the
   user's are not deleted: count them and say so.
2. **Sort the orders:**
   - **Delete the whole order** (`M3_OIS100MI_DelHead { OrderNumber }`; M3 sets the status to 90): every line of the
     order is for the item and every line status is **below 66**.
   - **Delete only the lines for the item** (`M3_OIS100MI_DelLine { OrderNumber, LineNumber, LineSuffix }`): the order
     also has other items. The order stays with its other lines.
   - **Not deleted**: a line with status 66 or higher (delivered, invoiced), which M3 doesn't allow. List the order and
     line.
3. **Card:**

   > **Delete customer orders for <item name> (<item>)**
   > Whole orders (<n>): <order numbers>.
   > Only the lines for this item (<n>): <order/line, order/line>; the other lines stay.
   > Left alone (<n>): <order/line> (delivered or invoiced).
   > This can't be undone. Reply **yes** to delete.

4. **After the yes**, one call per order (or per line), re-reading each just before its call.
5. **Read back.** `M3_OIS100MI_GetOrderHead` shows status 90 for each whole order; read the item's lines again and check
   that the deleted ones are gone or at status 90. Report: deleted, refused (with M3's message), left.
