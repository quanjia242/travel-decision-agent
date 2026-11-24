# 出行决策 Agent — 手动操作步骤（按课程手册七步）

> 目标：部署一个「可查询附近商场、结合品牌偏好生成推荐」的在线 Agent。
> 本文件只写**需要你在网页/控制台上手动操作**的部分；代码改造已由我在工作区完成，见文末「我已经帮你做完的部分」。
> 环境：Windows + Git Bash。所有命令在 `C:/Users/Administrator/Desktop/agent` 下执行。

---

## 进度核对表（2026-11-24 复查结果）

| 步骤 | 状态 | 说明 |
|---|---|---|
| 准备：四账号 | ⚠️ 待你确认 | 腾讯云/Makers、GitHub、WorkBuddy、高德 是否都已登录 |
| 准备：环境检查 | ✅ 已完成 | Git 2.55.0 / Python 3.13.14 / Node 22.22.2 / npm 10.9.7 |
| 一：Fork Starter | ✅ 已完成 | `https://github.com/quanjia242/travel-decision-agent`（已核实为真实 Fork，默认分支 `main`） |
| 一：Makers 授权 + 绑定 Fork | ❌ 未做 | 网页操作，必须先完成 Fork |
| 二：代码到本地 | ✅ 已完成 | 代码已就位（从上游模板展开），改造后可直接用 |
| 二：高德 Web 服务 Key | ✅ 已完成 | Web 服务类型 Key 已配好，实测地理编码返回 `status=1 OK` |
| 三：`.env` / `.env.example` / `.gitignore` | ✅ 已完成 | 两个 Key 均已填入；`.env` 被 git 忽略，提交物扫描无泄漏 |
| 三：GitHub Actions Secret | ⏭️ 本模板不适用 | 仓库内没有 `.github/workflows`，自动部署走 Makers 侧 Git 集成 |
| 四：Agent 改造 | ✅ 已完成 | 4 个高德工具 + 前端文案全部改完，构建通过 |
| 五：依赖安装 | ✅ 已完成 | `npm install`、`pip install -r requirements.txt`、`npm i -g edgeone` |
| 五：两个测试场景的逻辑验证 | ✅ 已完成 | 用真实 Key 端到端跑通 `python output/e2e_test.py 2`，场景一/二均通过 |
| 五：`edgeone makers dev` 本地服务 | ❌ 被阻塞 | 仍需你在自己终端 `edgeone login`（本机弹不出浏览器） |
| 六：commit / push | ✅ 已完成 | `eb4deee` 已推到 `main`（`91445b3..eb4deee`），远端指针已核对一致；提交物无 `.env`、无真实 Key |
| 七：Makers 新建部署上线 | ❌ 未做 | 网页操作 |
| 课后：`submission/` 证据 | 🟡 目录已建 | 5 张截图 + 公开地址待补 |

> 本轮实测修掉两个问题：① SDK 默认 10 轮不够用（真实场景需要 20+ 次工具调用），已在 `agents/chat/index.py` 改为 30 轮，并在指令里限制「只核对最近 5 个商场」；② 高德个人 Key 触发 `CUQPS_HAS_EXCEEDED_THE_LIMIT` 限流，已在 `agents/_tools.py` 加退避重试 + 品牌间节流。工具调用从 25 次降到 8 次，两个测试场景都通过。

---

## 0. 全局地图：七步里哪些归你、哪些归我

| 步骤 | 内容 | 谁做 |
|---|---|---|
| 准备 | 四个账号、Git 环境 | 你（环境我已检查，见 §1.3） |
| 一 | Fork starter、Makers 授权 GitHub 并绑定 Fork | **你（纯网页操作）** |
| 二 | 拉代码到本地、申请高德 Web 服务 Key | 代码我已就位；Key **你** |
| 三 | 填 `.env`、配 GitHub Secret、取 AI Gateway Key | **你**（模板我已生成） |
| 四 | 用自然语言改造 Agent | **我（已完成）** |
| 五 | 本地启动 + 两个场景验证 | 我执行，你提供已配好 Key 的确认 |
| 六 | commit / push、看 GitHub Actions | 我执行，**你给 Fork 地址** |
| 七 | Makers 新建部署、上线验证 | **你（纯网页操作）** |

**关键原则（手册反复强调）**：代码必须提交到**你自己 Fork 的仓库**，不是上游 `TencentEdgeOne/openai-agent-starter-python`；所有 Key/Token 不要发到聊天窗口、不要写进代码或提交物。

---

## 1. 开始前准备

### 1.1 四个账号（都要先登录好，建议同一浏览器）

1. **腾讯云 / EdgeOne Makers 账号** — 控制台：<https://console.cloud.tencent.com/edgeone/makers>（旧版地址若跳转，以跳转后的当前控制台为准）
2. **GitHub 账号** — <https://github.com/>
3. **WorkBuddy 账号** — 当前已登录
4. **高德开放平台账号** — 注册：<https://console.amap.com/dev/id/>，控制台：<https://console.amap.com/>

> 高德注册后**必须先完成实名认证**，否则创建不出可用的 Web 服务 Key。

### 1.2 平台地址速查

| 用途 | 地址 |
|---|---|
| 腾讯云登录 / 注册 | <https://cloud.tencent.com/login> |
| EdgeOne Makers 控制台 | <https://console.cloud.tencent.com/edgeone/makers> |
| 上游 Starter 仓库 | <https://github.com/TencentEdgeOne/openai-agent-starter-python> |
| GitHub 登录 | <https://github.com/login> |
| 高德开发者注册 | <https://console.amap.com/dev/id/> |
| 高德开放平台控制台 | <https://console.amap.com/> |

### 1.3 环境检查（已完成，结果如下）

```
git version 2.55.0.windows.3
Python 3.13.14
Node.js v22.22.2 / npm 10.9.7
```
满足手册要求（Node ≥ 18、Python ≥ 3.10）。若你换电脑重做，检查命令：
```bash
git --version && python3 --version && node --version
```
Git 缺失时按 <https://git-scm.com/install/windows> 安装。

---

## 2. 第一步：Fork Starter 并绑定 Makers（**你手动**）

### 2.0 先理解仓库关系（重要，别搞错）

| 角色 | 作用 |
|---|---|
| 上游 Starter `TencentEdgeOne/openai-agent-starter-python` | 提供初始示例代码，**只读** |
| 你的 Fork `travel-decision-agent` | 本课程**实际修改、Commit、Push** 的仓库 |
| EdgeOne Makers | 绑定这个 Fork，提供运行、预览、部署 |
| WorkBuddy（我） | 把 Fork 拉到本地，按自然语言改代码 |

> 所以：Makers 里选仓库、以及后面给我的 Git 地址，**都必须是你的 Fork**。

### 2.0.1 Fork 上游仓库

1. 打开 <https://github.com/TencentEdgeOne/openai-agent-starter-python>
2. 点右上角 **Fork**
3. 在表单里：
   - **Owner**：选你自己的 GitHub 账号（不要选组织）
   - **Repository name**：填 `travel-decision-agent`
   - 点 **Create fork**
4. 完成后浏览器应停在 `https://github.com/<你的账号>/travel-decision-agent`，页面上有 `forked from TencentEdgeOne/openai-agent-starter-python` 标识。
5. **把这个地址复制下来**，后面 Makers 绑定和给我设置 remote 都要用。

### 2.1 在 Makers 授权 GitHub 并绑定 Fork

1. 登录腾讯云 → 打开 [EdgeOne Makers 控制台](https://console.cloud.tencent.com/edgeone/makers)
2. 路径：**服务总览 → 授权 Git 平台 → GitHub**，完成 OAuth 授权（注意登录的是拥有上面 Fork 的那个 GitHub 账号）
3. 返回 Makers，进入 **立即创建 / 创建项目**
4. 在「仓库 / 代码来源」处选择刚才 Fork 出来的 **`travel-decision-agent`**
   - 若界面写成「绑定已有仓库 / 从 GitHub 导入」，同样选这个 Fork
   - **不要**选其他 Starter，也**不要**重复创建仓库
5. 确认创建，等待初始化部署完成。

### 2.2 检查项目概览（完成判定）

在概览页确认四项都出现：
- [ ] 项目创建成功
- [ ] 显示已绑定的 GitHub 仓库（你的 Fork）
- [ ] 有预览地址
- [ ] 有部署状态

> 本阶段**不改业务代码**，只确认项目能正常初始化。

**常见问题排查**

| 现象 | 处理 |
|---|---|
| 授权后仍显示未连接 | 刷新 Makers，确认 GitHub 登录的是正确账号 |
| 看不到组织仓库 | 找组织管理员批准 GitHub App |
| Fork 仓库不出现 | 刷新 GitHub 授权范围，确认授权的是拥有该 Fork 的账号 |
| 创建按钮一直转圈 | 先回项目列表确认是否已绑定，避免重复创建 |
| 初始部署失败 | 打开构建日志，定位是拉取 / 安装 / 构建 / 启动哪一步失败 |

---

## 3. 第二步：代码交接 + 申请高德 Key（**Key 归你**）

### 3.1 代码交接（我已做了等价动作，你只需补一个地址）

手册原本要求把 Fork 的 HTTPS 地址发给 WorkBuddy 拉取。我因为还没有你的 Fork 地址，先从上游 starter 的公开模板把完整代码展开到了工作区，并按第四步需求完成了改造。

**你只需要告诉我 Fork 地址**（形如 `https://github.com/<你的账号>/travel-decision-agent.git`），我会执行：
```bash
git remote add origin <你的 Fork 地址>
```
> 注意：本地仓库是我用 `git init` 新建的，没有上游提交历史，直接 push 会被 GitHub 拒绝。我会用「合并无关历史 / 或重新 clone 后覆盖改动」的方式处理，**这一步不用你操心**，我不会用 `--force` 覆盖你 Fork 里的东西。

如果你更想严格照手册走，也可以自己执行：
```bash
git clone https://github.com/<你的账号>/travel-decision-agent.git
```
然后告诉我新目录，我把改造后的文件搬过去。

> 小提醒：前端右下角的 GitHub 图标目前仍指向上游 starter 仓库（`src/components/GitHubLink.tsx` 已标注 TODO）。你给出 Fork 地址后，我会把它改成你自己的仓库地址，再一起提交。

### 3.2 申请高德 Web 服务 Key（**你手动**）

1. 打开 <https://console.amap.com/dev/id/> 注册并完成**实名认证**；已有账号直接登录 <https://console.amap.com/>
2. 进入控制台 → **应用管理 → 我的应用 → 创建新应用**（名字随意，如 `travel-agent-course`）
3. 在该应用下点 **添加 Key**：
   - Key 名称：如 `amap-web-service`
   - **服务平台务必选「Web 服务」**（不是「Web 端(JS API)」、不是 Android/iOS）
   - 提交后得到一串 Key
4. 保存这串 Key 备用（**不要发给我，直接填进 `.env`**，见 §4.1）

> 选错服务平台是最常见的鉴权失败原因：Web 端(JS API) 的 Key 调不了 `/v3/place/around`、`/v3/distance` 等 Web 服务接口。

---

## 4. 第三步：配置环境变量与 GitHub Secret（**你手动**）

### 4.1 填本地 `.env`（文件我已生成模板，只需填值）

工作区根目录已有 `.env`（已被 `.gitignore` 忽略）和 `.env.example`（可提交的示例）：

```ini
# ========== Makers AI 网关 ==========
AI_GATEWAY_API_KEY=         # ← 填 Makers 控制台生成的 API Key
AI_GATEWAY_BASE_URL=https://ai-gateway.edgeone.link/v1
AI_GATEWAY_MODEL=@makers/deepseek-v4-flash

# ========== 高德 Web 服务 ==========
AMAP_API_KEY=               # ← 填 §3.2 申请的 Key
```

**`AI_GATEWAY_API_KEY` 获取路径**：EdgeOne Makers 控制台 → **模型与密钥 / Models → API Key** → 新建 Key → 复制。
`@makers/deepseek-v4-flash` 是内置免费模型（有用量上限），做原型够用；生产建议绑定自己的付费厂商（BYOK）。

同时确认线上（Makers 项目环境变量）也填了同名变量，否则部署后 Agent 会报鉴权错误。

**验证 `.env` 确实被忽略**（我已跑过，输出如下）：
```bash
git check-ignore -v .env
# .gitignore:13:.env   .env
```
若无输出，先检查 `.gitignore` 再 push。

### 4.2 配置 GitHub Actions Secret（**你手动**）

1. 打开你的 Fork 仓库 → **Settings → Secrets and variables → Actions → New repository secret**
2. Name：`EDGEONE_API_TOKEN`（若 workflow 里引用了别的名字，以 workflow 为准）
3. Value：粘贴 Makers 控制台生成的部署 Token
4. 保存（列表只显示名称，不显示值）

**安全清单（手册原文要求）**
- [ ] 不把 `.env` 提交到 GitHub
- [ ] 不把 API Key 写进 Python / JSON / 提示词
- [ ] 不把 Token 拼接进 Git URL
- [ ] 不把原文邀请码、活动额度复制到课程材料
- [ ] 不在聊天窗口发送任何真实 Key / Token 给我

---

## 5. 第四步：用自然语言改造 Agent（**我已完成**）

手册里这一步是向 WorkBuddy 发送需求（含场景、输入示例、预期结果）。需求是：

> 做一个出行决策 Agent：用户输入所处位置 → 通过地图检索附近商场 → 获取距离、店铺等信息 → 结合品牌偏好推荐。
> 场景：我在红莲南路地铁站附近，想要一个既有「倍轻松」又有「西厅村屋」的、离得近的商场。

我按此完成了改造，**改动文件**：

| 文件 | 改动 |
|---|---|
| `agents/_tools.py` | 删掉 4 个 demo 工具，重写为 4 个高德地图工具 |
| `agents/chat/index.py` | Agent 名称 / instructions / 工具注册改为出行决策流程 |
| `.env.example`、`.env` | 加入 `AMAP_API_KEY`，网关地址改为 Makers 实值 |
| `api-schema.json` | 新增：第三方 API 三步接入范式的工具描述清单 |
| `src/App.tsx` | 工具指示灯映射到新工具 |
| `src/i18n/zh.ts` / `en.ts` | 标题、提示语、预设问题、工具名改为出行决策场景 |
| `src/components/CodeViewer.tsx` | 展示的示例代码同步为新工具 |

**Agent 调用链**（对应手册 9.1）：
```
用户输入位置和品牌
  → geocode_location        位置 → 经纬度
  → search_nearby_malls     检索附近商场（含直线距离）
  → search_brands_in_mall   逐个核对品牌/门店匹配
  → get_distance            需要时精确比较距离
  → 按「品牌匹配 + 距离」排序 → 返回推荐与依据
```
工具返回统一 `{"ok": true/false, "error", "hint"}`，失败时 Agent 必须转述原因；地点、门店、距离一律以工具返回为准，禁止模型编造。所有密钥只从环境变量读取。

**已验证的检查项**（我已在本地跑过）：
- Python 语法编译通过；`api-schema.json` JSON 合法
- `git check-ignore -v .env` 命中 `.gitignore:13:.env`，`git status` 里不含 `.env`
- 前端 `npm install` + `npm run build` 通过（308 modules，产出 `dist/`）
- `pip install -r requirements.txt` 通过；4 个 `@function_tool` 全部成功注册，参数 schema 正常
- 工具逻辑离线自测通过：无 Key 时四个工具都返回 `ok=false` + `hint` 且不抛异常；模拟高德数据下完整链路（位置解析 → 商场候选 850m / 2600m → 双品牌匹配 → 距离 850m）断言通过

---

## 6. 第五步：启动本地服务并验证（我执行，你确认 Key 已填好）

前置（首次）：
```bash
npm install                      # 前端依赖（已执行完成）
pip install -r requirements.txt  # Python 依赖（已执行完成）
npm i -g edgeone                 # EdgeOne CLI，若提示需登录则按提示登录腾讯云
# .env 已生成并填好模板，你只需补两个值
```
启动：
```bash
edgeone makers dev
```
- 实际访问地址以终端输出为准（通常是 `http://localhost:8080`）
- 本地观测面板：`http://localhost:8080/agent-metrics`
- 首次安装依赖期间不要重复启动

**测试场景一（信息完整）** — 直接点预设问题或输入：
```
我在红莲南路地铁站附近，我想要去一个既有倍轻松又有西厅村屋的离得近的商场，帮我推荐。
```
预期：返回候选商场、品牌/店铺信息、距离依据、推荐说明。

**测试场景二（连续追问，同一会话）**：
```
如果不要求两个品牌同时存在，还有没有距离更近的选择？
```
预期：保留上一轮地点条件，按新约束重新比较候选结果。

**本地运行排查表**

| 现象 | 先查什么 |
|---|---|
| 依赖安装失败 | 运行时版本、锁文件、网络 |
| 页面打不开 | 终端给出的实际端口、启动日志 |
| 回答有地点但没有工具过程 | `AMAP_API_KEY`、工具描述、项目日志 |
| 追问忘记前文 | 是否误开新会话、会话是否连续 |
| 返回鉴权错误 | 高德 Key 类型（必须 Web 服务）、Key 状态、接口权限 |

---

## 7. 第六步：提交并推送（我执行，你给 Fork 地址）

你只需在 §2.0.1 拿到 Fork 地址后发给我。我会按顺序做完：
1. `git status` / `git diff`，确认 `.env` 不在待提交列表、代码和日志里没有真实 Key、没有无关改动
2. 设置 `origin` 为你的 Fork（并处理本地与 Fork 的提交历史衔接）
3. `git add .` → `git commit -m "feat: add travel decision agent with amap"` → `git push`
4. 回报 Commit ID、推送分支、Push 结果

**Push 后你手动回到 Makers 控制台**看自动更新状态。若自动部署没触发，依次检查：
- Push 的分支是否是项目部署分支（通常 `main`）
- GitHub → **Actions** 看 workflow 是否触发，失败在 Checkout / Install / Build / Deploy 哪一步
- `EDGEONE_API_TOKEN` 名称与 workflow 引用是否一致

> 手册特别提醒：若模板已自带 `edgeone.json`，**不要直接覆盖**。本项目 `edgeone.json` 保持原样（framework=openai-agents-sdk，buildCommand=npm run build，outputDirectory=dist），改动前先核对构建命令、输出目录和 workflow。

---

## 8. 第七步：新建部署并正式上线（**你手动**）

修改环境变量 / 界面 / 部署配置后：

1. Makers 控制台 → **部署管理 → 新建部署 → 确认**
2. 等待部署完成，先用**临时预览地址**验证页面和 Agent 对话
3. 在项目概览页查看部署状态与预览入口

**上线验证清单**
- [ ] 公开预览地址可访问（这就是课程的完成标准）
- [ ] 输入一次出行决策问题，能正常返回推荐
- [ ] 页面不依赖本地开发服务
- [ ] 回答里没有暴露 Key 或调试信息

**自定义域名（选做）**：
`项目概览 / 自定义域名 → 添加域名 → 按提示配置 DNS → 等待验证和 HTTPS 生效`

---

## 9. 课后提交证据（**你手动截图**）

按手册要求建 `submission/` 目录：

```
submission/
├── local-running.png       # 本地调试页面
├── normal-result.png       # 正常请求结果
├── follow-up-result.png    # 连续追问结果
├── actions-success.png     # GitHub Actions 成功
├── deploy-success.png      # Makers 部署成功
└── public-entry.txt        # 公开预览地址
```

---

## 10. 现在剩下的（全部是网页/控制台手动操作）

代码已经推到你 Fork 的 `main` 分支了，我这边能做的都做完了。剩下三步：

1. **Makers 绑定这个 Fork 仓库**：控制台 → 项目 → 导入 Git 仓库（或新建项目）→ 选 GitHub → 授权 → 选 `travel-decision-agent` → 构建命令 `npm run build`、输出目录 `dist`、部署分支 `main` → 开始部署。
   > 线上**环境变量**也要填同名变量：`AI_GATEWAY_API_KEY`、`AI_GATEWAY_BASE_URL`、`AI_GATEWAY_MODEL`、`AMAP_API_KEY`（值不要发给任何人）。
2. **新建部署并上线验证**：部署管理 → 新建部署 → 等构建完成 → 打开临时预览地址，输入一次出行决策问题，确认回答不暴露 Key。
3. **补 `submission/` 证据**：`local-running.png`、`normal-result.png`、`follow-up-result.png`、`actions-success.png`、`deploy-success.png`、`public-entry.txt`（填公开预览地址）。

> 本地服务截图：在你自己终端跑 `edgeone login` 后 `edgeone makers dev`（访问地址以终端输出为准）。Agent 逻辑我已用真实 Key 端到端验证过两个场景，这一步主要是为了拿截图证据。

---

## 11. 已完成事项与剩余命令

依赖、两个 Key、`git` 身份、`origin`、commit 和 push 都已完成（详见顶部进度表）。本机现在只剩「本地服务登录」这一件事：

```bash
cd C:/Users/Administrator/Desktop/agent

# ① 登录 EdgeOne（必须在你自己能弹出浏览器的终端里跑，我这边是非交互环境，登录窗口弹不出来）
edgeone login

# ② 启动本地服务（Key 已填好，登录后直接跑）
edgeone makers dev
# 访问地址以终端输出为准，官方默认是 http://localhost:8088
# 本地观测面板：http://localhost:8088/agent-metrics
```

推送结果备查：

- Commit ID：`eb4deee`（merge commit，含 `02776b6`、`8daf60d`）
- 推送分支：`main`
- Push 结果：`91445b3..eb4deee  main -> main`，远端指针已核对一致
- 走的是 SSH（`git@github.com:quanjia242/travel-decision-agent.git`），因为本机 `github.com` HTTPS 不通

> 提醒：两个 Key 曾出现在聊天窗口，课程结束后建议到 Makers 控制台和高德控制台各删掉重建一次。

