# AI 求职助手

面向深圳 **AI 应用开发工程师**求职的练手 / 作品项目：简历诊断、JD 匹配、知识库问答（RAG）、AI 模拟面试、AI 对话，全部跑通。

- 后端：FastAPI（Python 3.12）+ SQLite + FAISS（可用时）+ OpenAI 兼容 LLM 客户端
- 前端：Vue 3 + Vite + Element Plus + Vue Router
- **无 Key 也能跑**：不配置 `LLM_API_KEY` 时后端自动走 Mock 模式，演示全流程；配置后走真实模型。

## 功能

| 页面 | 路由 | 对应后端接口 |
| --- | --- | --- |
| 首页 | `/` | — |
| AI 对话 | `/chat` | `POST /api/chat` |
| 简历诊断 | `/resume` | `POST /api/resume/analyze`、`POST /api/resume/upload`、`GET /api/resume/history` |
| JD 匹配 | `/jd` | `POST /api/jd/match` |
| 知识库问答 | `/rag` | `POST /api/rag/upload`、`POST /api/rag/query`、`GET /api/rag/stats`、`DELETE /api/rag/clear` |
| 模拟面试 | `/interview` | `POST /api/interview/start`、`POST /api/interview/answer`、`POST /api/interview/{id}/finish` |

后端接口文档（启动后端后打开）：http://localhost:8000/docs

## 本地运行（不走 Docker）

```bash
# 1. 后端（新终端）
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --port 8000
# 健康检查：curl http://localhost:8000/health
# 应返回 {"status":"ok","mock_mode":true,...}

# 2. 前端（另一个新终端）
cd frontend
npm install
npm run dev
# 打开 http://localhost:5173
# 前端通过 Vite 代理访问后端（/api、/health -> localhost:8000）
```

## 配置真实模型（DeepSeek / OpenAI 兼容）

```bash
cp .env.example backend/.env
# 编辑 backend/.env，填入：
#   LLM_API_KEY=你的 key
#   LLM_BASE_URL=https://api.deepseek.com/v1   # DeepSeek 默认；OpenAI 用 https://api.openai.com/v1
#   LLM_MODEL=deepseek-chat                    # OpenAI 用 gpt-4o-mini 等
```

也可以不写文件，直接在启动后端前导出环境变量：

```bash
LLM_API_KEY=你的key LLM_BASE_URL=https://api.deepseek.com/v1 LLM_MODEL=deepseek-chat \
  .venv/bin/python -m uvicorn app.main:app --port 8000
```

> ⚠️ 永远不要把真实 Key 提交到 Git。`.env` 已在 `.gitignore` 里。

## 用 Docker 运行

```bash
docker compose up --build
# 前端：http://localhost:4173
# 后端：http://localhost:8000
```

用真实模型时，先在项目根目录建 `.env`（或启动时传环境变量）：

```bash
LLM_API_KEY=你的key docker compose up --build
```

停止：`docker compose down`（数据保留在本地 `data/` 目录）。

## 测试与构建

```bash
# 后端冒烟测试（7 个，Mock 模式，无需 Key）
cd backend && .venv/bin/python -m pytest tests/test_smoke.py -q

# 前端构建
cd frontend && npm run build
```

## 项目结构

```
ai-job-assistant/
├── backend/            # FastAPI 后端
│   ├── app/            # main / routers / services / llm / rag
│   ├── tests/          # 冒烟测试 test_smoke.py（7 个）
│   └── requirements.txt
├── frontend/           # Vue 3 + Vite + Element Plus
│   └── src/
│       ├── api/client.js    # 所有后端接口封装
│       ├── router/index.js  # 6 个页面路由
│       └── views/           # Home / Chat / Resume / JdMatch / Rag / Interview
├── data/               # SQLite + FAISS 数据（本地运行产生，不提交）
├── Dockerfile          # 后端镜像
├── frontend/Dockerfile # 前端镜像
├── docker-compose.yml  # 后端 + 前端一键启动
└── .env.example        # 模型配置模板（无真实 Key）
```

## 推送到 GitHub（仓库尚未创建）

```bash
# 1. 在 https://github.com/190324689a-ctrl 新建一个空仓库，名字建议 ai-job-assistant
#    （不要勾选 README / .gitignore / License，避免与本地冲突）
# 2. 本地关联并推送（在项目根目录执行）：
git remote add origin https://github.com/190324689a-ctrl/ai-job-assistant.git
git branch -M main
git push -u origin main
```
