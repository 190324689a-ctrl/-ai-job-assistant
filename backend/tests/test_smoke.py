"""Smoke 测试：Mock 模式下核心接口全流程（无需真实 API Key）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.db import init_db  # noqa: E402

init_db()  # 测试客户端不触发 startup 事件，这里显式建表

client = TestClient(app)

SAMPLE_RESUME = """张三 计算机科学与技术本科 2025 届毕业生
技术栈：Python、Java、Spring Boot、Vue 3、MySQL、Redis
项目经历：
- 医院医务管理系统（独立开发并上线）：负责挂号、排班、药品管理模块，用户量 500+，上线后挂号效率提升 40%。
- 企业工资核算系统：负责工资计算、人事档案模块，支持 200 人规模企业月度核算。
求职意向：AI 应用开发工程师
"""

SAMPLE_JD = """AI 应用开发工程师：熟悉 Python、LangChain、RAG、向量数据库（Milvus/FAISS）、
FastAPI、Docker，有 Agent 工具调用与 Prompt 工程经验者优先。"""


def test_health():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_chat():
    r = client.post("/api/chat", json={"message": "你好，介绍一下你自己"})
    assert r.status_code == 200
    assert r.json()["reply"]


def test_chat_stream():
    with client.stream("POST", "/api/chat/stream",
                       json={"message": "你好"}) as r:
        assert r.status_code == 200
        body = "".join(r.iter_text())
        assert "data:" in body and "done" in body


def test_resume_analyze():
    r = client.post("/api/resume/analyze",
                    json={"text": SAMPLE_RESUME, "target_jd": SAMPLE_JD})
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["score"] <= 100
    assert body["highlights"] and body["suggestions"]


def test_jd_match():
    r = client.post("/api/jd/match",
                    json={"jd_text": SAMPLE_JD, "resume_text": SAMPLE_RESUME})
    assert r.status_code == 200
    assert "match_score" in r.json()


def test_rag_flow():
    # 先上传知识库文档
    r = client.post("/api/rag/upload",
                    files={"file": ("notes.txt",
                                    "RAG 是检索增强生成：先检索知识库片段，再交给大模型作答。\n"
                                    "向量数据库 Milvus 可存储 Embedding 用于相似度检索。".encode(),
                                    "text/plain")})
    assert r.status_code == 200 and r.json()["chunks"] > 0
    # 再提问
    r = client.post("/api/rag/query", json={"question": "什么是 RAG？"})
    assert r.status_code == 200
    assert r.json()["sources"], "应返回引用来源"


def test_interview_flow():
    r = client.post("/api/interview/start", json={"direction": "AI 应用开发"})
    assert r.status_code == 200
    sid = r.json()["session_id"]
    assert r.json()["question"]
    r = client.post("/api/interview/answer",
                    json={"session_id": sid, "answer": "我叫张三，做过医院管理系统，负责挂号与排班模块。"})
    assert r.status_code == 200
    assert "question" in r.json() or r.json().get("finished")
    r = client.post(f"/api/interview/{sid}/finish")
    assert r.status_code == 200
    assert "scores" in r.json()["report"]
