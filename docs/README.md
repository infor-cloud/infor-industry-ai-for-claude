# Infor Industry AI documentation

| Guide | Who it's for | What it covers |
|---|---|---|
| [Setup and reference guide](setup.md) | A user with the IFS role `M3GENAI-BE-Administrator`, a user with the `IONAPI-Administrator` role, a Claude Owner or Primary Owner, and each user | Setting up the M3 connector, the tool set, M3 roles and permissions, data safeguards and troubleshooting |
| [GenAI Gateway tool scripts](../scripts/genai-gateway/README.md) | A user with the IFS role `M3GENAI-BE-Administrator` | Checking a tenant against the tool set, and creating or updating the customized tools |
| [Infor Industry AI plugin](../plugins/infor-industry-ai/README.md) | Everyone who installs the plugin | The skills, the data the plugin sends, and the write tools each skill may call |
| [Production planner demo data](demo-data.md) | People who prepare and run demos on a demo or test tenant | Setting up and cleaning up the production planner's demo data with the demo data skill, which is installed separately from the plugin |

## Where to start

1. Set up the M3 connector with the [setup guide](setup.md).
2. Check the tenant's tools, and create the customized ones, with the [GenAI Gateway tool scripts](../scripts/genai-gateway/README.md).
3. Install the plugin as its [README](../plugins/infor-industry-ai/README.md#install) describes, and say "get started".
4. To run production planner demos on a demo or test tenant, install the demo data skill as [Production planner demo data](demo-data.md#install) describes.
