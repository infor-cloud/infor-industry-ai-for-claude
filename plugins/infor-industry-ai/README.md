# Infor Industry AI for Claude

For buyers, production planners and customer service reps in Infor M3. Claude reads M3 through the M3 connector, applies
each role's rules, and answers with the evidence and the options; it changes M3 only after an explicit yes for that
exact change.

## Skills

| Skill | Who it's for | What it does | Writes? |
|---|---|---|---|
| `m3-foundation` | Everyone | Getting started; what M3 codes and dates mean; stock across warehouses; who is responsible; single questions and actions | Yes, behind an explicit confirmation |
| `m3-buyer` | Buyer | Morning view ranked by the orders that depend on it; delayed POs with impact, options and a recommendation (UC3); planned POs; confirm, add, replace and print PO lines; supplier OTIF; drafted messages | Yes, behind an explicit confirmation |
| `m3-production-planner` | Planner | Overview; MOs at risk and why, with options (UC1); material check; KPIs; MO proposals and release; reschedule; shortage radar; open POs; a purchase from another supplier; notices to the buyer and the sales rep; customers affected | Yes, behind an explicit confirmation |
| `m3-customer-service-rep` | Customer service rep | Rush orders from the call to the customer update (UC2); fixes for short or late lines; the rep's dashboard | Yes, behind an explicit confirmation |

Try: "What needs my attention today?" (buyer) · "Give me all production orders at risk and recommendations to mitigate
the risks." (planner) · "A customer called and needs it by Friday." (customer service) · "Get started."

## Requirements

- The M3 connector (M3 BE MCP), connected and signed in. Each M3 tenant has its own endpoint, so a Claude Owner or
  Primary Owner adds the connector for the organization (Organization settings, Connectors) before people install this
  plugin; the plugin does not ship an endpoint. The
  [setup guide](https://github.com/infor-cloud/infor-industry-ai-for-claude/blob/main/docs/setup.md) covers the
  connector, the M3 GenAI Gateway tools and the M3 roles each step needs.
- Optional: the Microsoft 365 connector, to send messages to colleagues by e-mail and to create Outlook drafts.
- Nothing to configure in the plugin. The user, company, division, facility and warehouse come from the signed-in M3
  user. Values M3 can't give (for example the application message type or the allocation origin for a manual
  allocation) are asked once, when a step needs them, and kept for the conversation. To answer them for everyone, put
  them in a Claude Project's instructions. The M3 administrator knows these codes.
- Test on a non-production M3 environment first.

## Install

- **Claude apps**: Customize, Plugins, Add, Upload plugin, and choose a zip of this folder.
- **Claude Code**: `claude plugin marketplace add infor-cloud/infor-industry-ai-for-claude`, then
  `claude plugin install infor-industry-ai@infor-claude-plugins`.

Then say "get started".

## Data and privacy

The plugin holds instructions, reference material and three dashboard pages. It has no server of its own, no hooks, no
scripts and no telemetry. Data moves only through the connectors your organization has added and the pages you open:

- **Infor M3.** The skills and dashboards read and change M3 data through the M3 connector, which connects to your
  organization's own M3 tenant through Infor ION API. They act as the signed-in M3 user, within that user's M3
  permissions, and change nothing without an explicit yes for that exact change.
- **Microsoft 365, when connected.** The skills can e-mail a message to a colleague after an explicit yes. Mail to
  customers and suppliers is never sent: it stays an Outlook draft for a person to review and send. The planner
  dashboard can also create Outlook drafts.
- **Dashboards.** The buyer, planner and rep dashboards open as Claude artifacts. Each calls the M3 tools listed in its
  `assets/*.capabilities.json` file as the signed-in user, and keeps a log of the actions taken from it in the page's
  own storage. The rep dashboard also stores a daily total of backordered lines and each viewer's settings there, under
  their Claude user ID. Anyone the page is shared with can see that storage. Pages are private until shared, and can
  contain customer and supplier details. The dashboards load nothing from other sites: no fonts, scripts or images.

Infor's privacy policy: https://www.infor.com/about/privacy

## Security notes

- Write tools the skills may propose, each behind its own explicit confirmation and a read-back (from each skill's tools
  line):
  - Foundation (single actions): `M3_CRS420MI_Add`, `M3_CRS420MI_AddFreeText`, `M3_CRS420MI_Delete`, `M3_CRS420MI_Complete`, `M3_PPS170MI_CrtPOP`.
  - Buyer: `M3_PPS200MI_DltLine`, `M3_PPS600MI_PrintPO`, `M3_PPS001MI_ConfirmLine`, `M3_PPS200MI_UpdLine`, `M3_PPS200MI_AddLine`, `M3_PPS001MI_FinishMark`, `M3_PPS370MI_StartEntry`, `M3_PPS370MI_AddHead`, `M3_PPS370MI_AddLine`, `M3_PPS370MI_FinishEntry`, `M3_PPS170MI_CrtPOP`, `M3_PPS170MI_UpdPlannedPO`, `M3_PPS170MI_RelPOP`, `M3_DPS170MI_CrtPlannedDO`, `M3_PMS100MI_Reschedule`, `M3_PMS100MI_UpdMatLine`, `M3_OIS100MI_UpdCOPlanDates`, `M3_CRS420MI_Add`, `M3_CRS420MI_Complete`, `M3_CRS420MI_AddFreeText`, `M3_CRS420MI_Delete`.
  - Planner: `M3_PMS100MI_UpdMatLine`, `M3_PMS100MI_UpdOperation`, `M3_PMS100MI_HoldMO`, `M3_PMS100MI_RelHeldMO`, `M3_PMS100MI_SplitMO`, `M3_PMS100MI_TriggerJob`, `M3_PDS010MI_AddShiftPatAdj`, `M3_PDS010MI_CrtCapacity`, `M3_PDS010MI_DelShiftPatAdj`, `M3_PPS170MI_UpdPlannedPO`, `M3_PPS170MI_RelPOP`, `M3_PPS001MI_ConfirmLine`, `M3_PMS170MI_SetStatus`, `M3_PMS170MI_CrtPlannedMO`, `M3_PMS100MI_CrtMO`, `M3_PMS100MI_Reschedule`, `M3_PMS170MI_DelPlannedMO`, `M3_PPS170MI_CrtPOP`, `M3_PPS370MI_StartEntry`, `M3_PPS370MI_AddHead`, `M3_PPS370MI_AddLine`, `M3_PPS370MI_FinishEntry`, `M3_CRS420MI_Add`, `M3_CRS420MI_AddFreeText`, `M3_CRS420MI_Delete`, `M3_CRS420MI_Complete`.
  - Customer service rep: `M3_OIS100MI_UpdCOPlanDates`, `M3_OIS100MI_AddBatchHead`, `M3_OIS100MI_SndBatchLine`, `M3_OIS100MI_Confirm`, `M3_OIS100MI_AddOrderLine`, `M3_OIS100MI_DelLine`, `M3_MMS120MI_AllocateOrdLine`, `M3_MMS120MI_DeAllocateOrLne`, `M3_DPS170MI_CrtPlannedDO`, `M3_DPS170MI_DelPlannedDO`, `M3_CRS420MI_Add`, `M3_CRS420MI_AddFreeText`, `M3_OIS100MI_DelHead`, `M3_CRS420MI_Delete`, `M3_CRS420MI_Complete`.

  Deletes run only inside the flows that name them (`references/m3/write-protocol.md`). Don't auto-approve these tools;
  the app's permission prompt is the structural backstop behind each skill's confirmation step.
- The dashboards can also call the write tools named in their capabilities files.
- The connector exposes more write and delete tools than the skills use. The skills name the tools they may call; the
  limits are instructions, not enforcement. Access control is enforced by M3 for the signed-in user, and a user with the
  `M3GENAI-BE-Administrator` role can disable any tool in M3 GenAI Gateway.
- Skills treat content returned by M3 as data, not instructions.

## Branding

Answers are in chat. Dashboards will share one look based on the Infor Design System (pending); until then a neutral
interim theme is used, labelled "M3 + Claude", and pages are not official Infor communications.

## License

Proprietary to Infor. You may use the plugin only under a valid agreement with Infor for the Infor products it works
with. See [LICENSE](LICENSE).
