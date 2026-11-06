<!-- Part of references/delayed-po.md (UC3). Read the index first. -->

## Show it

Follow "Answer layout" in `SKILL.md`: status icons (✅ ⚠️ ❌ ℹ️) followed by a word, tables for every section, each in its own table so it has a border (the summary, the overall impact: one per section MO, CO, DO, the mitigation options, one actions table per recommendation, and needs and basis). Name every item in a mitigation option as `<item number> · <item name>` (the substitute in B, the item on the new PO in D). Start each mitigation option's name with its letter ("A. Check if stock balance can be re-allocated"), and label its actions with the same letter. Use a `Mitigation option` table with one row for each of A to E (never "not checked") and columns Mitigation option, Status (✅ possible · ❌ not possible · ⚠️ needs approval), Arrives vs need date, Cost change, Still affected, Risk. An option that works but arrives after the need date gets ⚠️ with the days late.

```
**PO <no>/<line> · <item number> · <item name> · <supplier>**: now <new date> vs. need <need date> (<n> days short)

| Summary | |
|---|---|
| Delay | <what the PO says, what the supplier says, the new gap in days> |
| Coverage | <how much of the short quantity this line covers> |
| Overall impact | <n> MOs, <n> COs (<customer names>), <n> DOs · value <amount> |

**Manufacturing orders (MO)**
| Status | MO · <item number> · <item name> | Need | Short | Priority | Slack |
...

**Customer orders (CO)**
| Status | Order · customer | Need | Short | Value | Slack |
...
<n> more COs possible through MO <no> (matched by product <item number> · <item name> and date; need dates only)

**Distribution orders (DO)**
| Status | DO · from > to | Need | Short | Slack |
...   (or one row: "No distribution orders affected")

**Mitigation options**
| Mitigation option | Status | Arrives | Cost change | Still affected | Risk |
...

**Recommendations with actions**

**Recommendation 1: option <letter>, <name>, because <reason in one sentence>**
| Step | Action | Changes M3 | Who |
|---|---|---|---|
| <letter>1 | <Verb>: <action> | Yes / Draft only / No | <who> |
| <letter>2 | <Verb>: <action> | ... | <who> |

**Recommendation 2 (fallback): option <letter>, <name>, because <reason in one sentence>**
| Step | Action | Changes M3 | Who |
|---|---|---|---|
| <letter>1 | <Verb>: <action> | ... | <who> |

| Note | Detail |
|---|---|
| Needs from you | <supplier quote / approval / decision> |
| Basis | <how dates, costs and impact were derived> |

Reply with an option letter (for example C) to start its steps, or a letter and a step (C2) for one step.

Next: <the next step, or the one question you need answered>
```

## Next step

- **Confirm or re-confirm a PO line** (the buyer called the supplier, or the supplier answered): `po-actions.md`.
- **Replace the item on a PO line** with a substitute (add a new line, delete the old one): `po-actions.md`.
- **Create a PO to an alternate supplier** (D1, with an offer to confirm it at once), then decide what to do with the original line (D2: reconfirm it, delete it or finish mark it): `create-new-po.md`.
- **Draft messages** to suppliers, the customer order responsible and the MO responsible: `messages.md`.
- **Release planned POs:** `planned-pos.md`.
- **Distribution order proposal** from another warehouse, firm (status 20) or released (status 60): `delayed-po/3c-distribution-order.md`.
