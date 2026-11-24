# Travel Decision Agent

A course project built on [TencentEdgeOne/openai-agent-starter-python](https://github.com/TencentEdgeOne/openai-agent-starter-python): the user provides a **location** and **brand / store preferences**, and the Agent searches nearby malls via AMap Web Services, verifies which stores are present, compares distances, and recommends with real data.

> Full manual procedure (fork, Makers binding, keys, secrets, deployment): **[MANUAL_STEPS.md](./MANUAL_STEPS.md)** (Chinese) · **[README_zh-CN.md](./README_zh-CN.md)** (Chinese).

**Framework:** OpenAI Agents SDK (Python) · React/Vite frontend · EdgeOne Makers

## How it works

```
user location + brands
  → geocode_location        location → lng,lat
  → search_nearby_malls     nearby malls with straight-line distance
  → search_brands_in_mall   per-brand match evidence
  → get_distance            optional precise comparison
  → rank by brand match + distance → recommendation with evidence
```

Locations, stores and distances come **only from tool results** — the model must never invent them. Every tool returns `{"ok": true|false, "error", "hint"}`; on failure the Agent must explain the reason. All keys are read from environment variables only.

| Tool | AMap endpoint |
|---|---|
| `geocode_location` | `/v3/geocode/geo` |
| `search_nearby_malls` | `/v3/place/around` |
| `search_brands_in_mall` | `/v3/place/around` |
| `get_distance` | `/v3/distance` |

See [api-schema.json](./api-schema.json) for the third-party API integration description.

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `AI_GATEWAY_API_KEY` | Yes | Makers Models API Key, or any OpenAI-compatible provider key. |
| `AI_GATEWAY_BASE_URL` | Yes | For Makers Models use `https://ai-gateway.edgeone.link/v1`. |
| `AI_GATEWAY_MODEL` | No | Defaults to `@makers/deepseek-v4-flash` (free built-in, usage cap). |
| `AMAP_API_KEY` | Yes | AMap **Web Service** Key (not the Web/JS API key). Register at <https://console.amap.com/>. |

`.env.example` is the committable template; `.env` is git-ignored and must never be committed.

## Local Development

Prerequisites: Node.js ≥ 18, Python ≥ 3.10, EdgeOne CLI (`npm i -g edgeone`).

```bash
npm install
pip install -r requirements.txt
cp .env.example .env       # fill in AI_GATEWAY_API_KEY and AMAP_API_KEY
edgeone makers dev
```

Local agent metrics & traces: `http://localhost:8080/agent-metrics`.

Test prompts:
1. `我在红莲南路地铁站附近，我想要去一个既有倍轻松又有西厅村屋的离得近的商场，帮我推荐。`
2. Follow-up in the same conversation: `如果不要求两个品牌同时存在，还有没有距离更近的选择？`

## Project Structure

```text
├── agents/chat/index.py       # POST /chat — SSE streaming + Agent definition
├── agents/chat/stop.py        # POST /chat/stop
├── agents/_tools.py           # 4 AMap @function_tool definitions
├── cloud-functions/           # stateless /history, /conversations, ...
├── src/                       # React + Vite + TypeScript frontend
├── api-schema.json            # third-party API description
├── .env.example / .env        # template / local (ignored)
├── edgeone.json               # framework=openai-agents-sdk (keep template values)
└── MANUAL_STEPS.md            # manual operation steps
```

> Files prefixed with `_` are private modules — not exposed as public routes.

## Deployment

Push to your own fork and EdgeOne Makers deploys automatically. After changing environment variables or deployment config, use **Deployment → New Deployment → Confirm** in Makers. Completion criterion: the temporary preview URL is reachable. Custom domain is optional.

## License

MIT (inherited from the upstream starter).
