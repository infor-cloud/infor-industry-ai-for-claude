# Infor Industry AI for Claude

This repository holds the Infor Industry AI plugin for Claude and what an Infor M3 tenant needs to run it: the setup guide for the M3 connector and the M3 GenAI Gateway tool configuration.

The plugin gives buyers, production planners and customer service reps skills that work on live M3 data. Buyers get a morning view and the impact of a delayed purchase order. Planners see which manufacturing orders are at risk and what can fix them. Reps can take a rush order from the customer's call to the customer update. Claude changes M3 only after an explicit yes for that exact change.

## How it works

```mermaid
flowchart LR
    plugin[Infor Industry AI plugin] --> claude[Claude]
    claude -- "M3 connector<br/>with the user's token" --> ionapi[Infor ION API Gateway]
    ionapi --> gateway[M3 GenAI Gateway]
    gateway -- "MI transaction<br/>as the signed-in user" --> m3[(M3 Business Engine)]
```

M3 GenAI Gateway exposes M3 MI transactions as MCP tools. Claude calls them through Infor ION API Gateway as the signed-in M3 user, so M3 security applies exactly as it does in M3. The plugin adds the skills: instructions, reference material and dashboards that tell Claude how each role works with those tools. The plugin has no server of its own.

## What's in this repository

| Path | What it is |
|---|---|
| [`plugins/infor-industry-ai`](plugins/infor-industry-ai) | The plugin: the skills `m3-foundation`, `m3-buyer`, `m3-production-planner` and `m3-customer-service-rep`, and the buyer, planner and rep dashboards. Its [README](plugins/infor-industry-ai/README.md) describes each skill, the data the plugin sends and the write tools each skill may call. |
| [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | Makes this repository a plugin marketplace, so Claude Code can install the plugin from it. |
| [`docs/setup.md`](docs/setup.md) | Setup and reference guide for the M3 connector: prerequisites, the four setup parts and who does each, the tool set, M3 roles and permissions, data safeguards and troubleshooting. |
| [`scripts/genai-gateway`](scripts/genai-gateway) | `gg.py`, which lists, checks and sets up the M3 GenAI Gateway tools in a tenant, and [`tools/`](scripts/genai-gateway/tools), the customized tool definitions the skills need. |

## Get started

1. **Set up the M3 connector** with the [setup guide](docs/setup.md). Each part names who does it:
   - A user with the IFS role `M3GENAI-BE-Administrator` reviews the tools. To create the customized tools in a tenant, or check a tenant against the tool set, they use the [GenAI Gateway tool scripts](scripts/genai-gateway/README.md).
   - A user with the `IONAPI-Administrator` role registers Claude in ION API.
   - A Claude Owner or Primary Owner adds the connector for the organization.
   - Each user connects Claude to M3 by signing in with their Infor OS account.
2. **Install the plugin.**
   - Claude apps: Customize, Plugins, Add, Upload plugin, and choose a zip of [`plugins/infor-industry-ai`](plugins/infor-industry-ai).
   - Claude Code:

     ```bash
     claude plugin marketplace add infor-cloud/infor-industry-ai-for-claude
     claude plugin install infor-industry-ai@infor-claude-plugins
     ```

3. **Say "get started"** in Claude.

Test on a non-production M3 environment first.

## Requirements

- An Infor M3 tenant with Velocity Suite, which includes M3 GenAI Gateway.
- The M3 connector, set up as the [setup guide](docs/setup.md) describes.
- Optional: the Microsoft 365 connector, to e-mail colleagues and create Outlook drafts.

## Data and privacy

The plugin has no server, hooks, scripts or telemetry. It reads and changes M3 data through the M3 connector as the signed-in user. When the Microsoft 365 connector is added, it can also e-mail colleagues and create Outlook drafts. The dashboards load their fonts from Google Fonts. The [plugin README](plugins/infor-industry-ai/README.md#data-and-privacy) describes each of these in full.

Infor's privacy policy: https://www.infor.com/about/privacy

## Checks

Each pull request and each push to `main` runs the [CI workflow](.github/workflows/ci.yml):

- `claude plugin validate --strict` on the marketplace and the plugin.
- The other rules of the [plugin directory's checklist](https://claude.com/docs/plugins/pre-submission-checklist): repository layout and file names, the plugin's file types and sizes, its README and license, that its README describes every host the plugin names, and that no ION API credentials are committed. Run them locally with `python3 scripts/ci/check-plugin.py`.
- A version check: any change to the plugin must raise `version` in [`plugin.json`](plugins/infor-industry-ai/.claude-plugin/plugin.json), so installed copies update.
- A [gitleaks](https://github.com/gitleaks/gitleaks) secret scan of the full history.

## Support

For help with setup or tool behavior, contact Infor Support through [Infor Concierge](https://concierge.infor.com).

## License

Proprietary to Infor. You may use this repository only under a valid agreement with Infor for the Infor products it works with. See [LICENSE](LICENSE).
