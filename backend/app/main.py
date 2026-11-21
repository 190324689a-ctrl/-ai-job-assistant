"""AI 求职助手 · 后端入口。

分层结构：
  routers/   HTTP 路由（chat / resume / rag / interview）
  services/  业务逻辑（简历诊断 / JD 匹配 / 面试）
  llm/       大模型客户端（OpenAI 兼容 + Mock 演示模式）
  rag/       RAG（切分 / 本地向量化 / FAISS 向量库）
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .db import init_db
from .routers import chat, interview, rag, resume

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    init_db()


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    """统一错误处理：不向前端泄露堆栈。"""
    return JSONResponse(status_code=500,
                        content={"detail": f"服务器内部错误：{type(exc).__name__}"})


@app.get("/health")
def health():
    return {"status": "ok", "mock_mode": settings.mock_mode,
            "model": settings.llm_model, "app": settings.app_name}


app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(resume.router, prefix="/api", tags=["resume"])
app.include_router(rag.router, prefix="/api", tags=["rag"])
app.include_router(interview.router, prefix="/api", tags=["interview"])
