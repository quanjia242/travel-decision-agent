# 出行决策 Agent

基于 [TencentEdgeOne/openai-agent-starter-python](https://github.com/TencentEdgeOne/openai-agent-starter-python) 改造的课程项目：用户输入**当前位置**和**品牌 / 门店偏好**，Agent 通过高德地图 Web 服务检索附近商场、核对门店匹配情况、比较距离，给出带数据依据的推荐。

> 完整手动操作流程见 **[MANUAL_STEPS.md](./MANUAL_STEPS.md)**（Fork、Makers 绑定、Key、Secret、部署上线、课后提交）。

## 功能与调用链

```
用户输入位置和品牌
  → geocode_location        位置描述 → 经纬度
  → search_nearby_malls     检索附近商场（名称/地址/经纬度/直线距离）
  → search_brands_in_mall   逐个核对品牌门店是否匹配
  → get_distance            需要时精确比较距离
  → 按「品牌匹配 + 距离」排序 → 返回推荐与依据
```

核心约束：地点、门店、距离**一律以工具返回为准**，不由模型自行生成；工具失败返回 `ok=false` + `error` + `hint`，Agent 必须转述原因；所有密钥只从环境变量读取。

## 工具清单

| 工具 | 高德接口 | 说明 |
|---|---|---|
| `geocode_location` | `/v3/geocode/geo` | 把「红莲南路地铁站」解析成 `lng,lat` |
| `search_nearby_malls` | `/v3/place/around` | 按半径检索商场，按距离由近到远排序 |
| `search_brands_in_mall` | `/v3/place/around` | 在商场周边逐个核对品牌，返回 `all_matched` |
| `get_distance` | `/v3/distance` | 直线 / 驾车 / 步行距离，用于排序比较 |

接口描述另见 [api-schema.json](./api-schema.json)。

## 环境变量

| 变量 | 必填 | 说明 |
|---|---|---|
| `AI_GATEWAY_API_KEY` | 是 | Makers Models 的 API Key，或任意 OpenAI 兼容服务商 Key |
| `AI_GATEWAY_BASE_URL` | 是 | Makers Models 用 `https://ai-gateway.edgeone.link/v1` |
| `AI_GATEWAY_MODEL` | 否 | 默认 `@makers/deepseek-v4-flash`（内置免费模型，有用量上限） |
| `AMAP_API_KEY` | 是 | 高德开放平台 **Web 服务** Key（不是 Web 端 JS API Key） |

`.env.example` 是可提交的模板；`.env` 已被 `.gitignore` 忽略，切勿提交。

## 本地开发

前置：Node.js ≥ 18、Python ≥ 3.10、EdgeOne CLI（`npm i -g edgeone`）。

```bash
npm install
pip install -r requirements.txt
cp .env.example .env       # 填入 AI_GATEWAY_API_KEY 与 AMAP_API_KEY
edgeone makers dev
```

本地观测面板：`http://localhost:8080/agent-metrics`。

测试用例：
1. `我在红莲南路地铁站附近，我想要去一个既有倍轻松又有西厅村屋的离得近的商场，帮我推荐。`
2. 同一会话追问：`如果不要求两个品牌同时存在，还有没有距离更近的选择？`

## 项目结构

```
├── agents/                          # 有状态的 Agent Functions（Python）
│   ├── chat/index.py               # POST /chat —— SSE 流式聊天 + Agent 定义
│   ├── chat/stop.py                # POST /chat/stop —— 中断当前 run
│   ├── _logger.py                  # 日志工具
│   └── _tools.py                   # 4 个高德地图 @function_tool
├── cloud-functions/                 # 无状态云函数（/history 等）
├── src/                             # React + Vite + TypeScript 前端
├── api-schema.json                  # 第三方 API 接入描述（课程 9.2）
├── .env.example / .env              # 环境变量模板 / 本地配置（本地配置不提交）
├── requirements.txt                 # Python 依赖
├── edgeone.json                     # framework=openai-agents-sdk
├── MANUAL_STEPS.md                  # 手动操作步骤
└── README_zh-CN.md / README.md
```

> `edgeone.json` 沿用模板原值，不要直接覆盖；改动前先核对构建命令、输出目录与 workflow。

## 部署

代码 push 到自己的 Fork 后由 EdgeOne Makers 自动部署；修改环境变量或部署配置后，在 Makers **部署管理 → 新建部署 → 确认**。上线完成标准：临时预览地址可访问。自定义域名为选做项。

## License

MIT（沿用上游 starter）。
