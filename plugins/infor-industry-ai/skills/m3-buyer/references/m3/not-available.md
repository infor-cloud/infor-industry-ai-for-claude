# Not available in M3 today

Shared reference. State these plainly when asked, and do not approximate them.

**Purchasing**
- Rapid RFQ cycle time and RFQ handling
- Supplier screening against sanctions or restricted-party lists
- Expedite spend vs. penalty avoided
- Transport lead time and cost for alternative delivery methods; a delivery method list
- Supplier-confirmed new dates received only by e-mail (the user must tell you)
- Splitting a PO line (`PPS001MI_ConfirmLine` confirms one line; a partial delivery has to be recorded another way)
- Lead-time variance against the agreement (not built)

**Production**
- Labor: outsourcing options and requests. (Overtime is available as a temporary double shift on a work center resource:
  the planner flow the planner's shift-pattern flow.)
- Moving an MO to another routing, or an operation to a work center outside the same main work center. (The planner can move
  one operation to another resource under the same main work center: the planner's resource swap flow.)
- MO start and finish times and priority as inputs to a reschedule (only one date can be set)
- History for: on-time MO finish rate, on-time in full for customer orders, reschedule churn, supplier on-time delivery,
  days of supply (see the planner's KPI catalogue)

**Customer orders**
- Changing ship-to or price on an existing order line (quantity only by swapping the line)
- Reading which planner a distribution order proposal belongs to

**Everywhere**
- A log of what automated agents did, and an escalation queue
- Workflow items waiting on the user in other systems (for example engineering approval)
