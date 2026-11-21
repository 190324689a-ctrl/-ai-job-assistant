"""LLM 客户端：OpenAI 兼容 Chat Completions 接口 + Mock 演示模式。

无 API Key 时自动进入 Mock 模式，返回结构合理的模拟回答，
保证全流程（简历诊断 / RAG / 面试 / 流式输出）无需 Key 即可演示。
"""
import json
import re
from typing import AsyncIterator

import httpx

from ..config import settings


class LLMClient:
    def __init__(self):
        self.base_url = settings.llm_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    @property
    def mock_mode(self) -> bool:
        return settings.mock_mode

    # ---------------- 真实调用 ----------------
    async def chat(self, messages: list[dict], temperature: float = 0.7,
                   max_tokens: int = 2000) -> str:
        """一次非流式对话。Mock 模式下按提示词类型返回模拟回答。"""
        if self.mock_mode:
            return self._mock_reply(messages)
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages,
                      "temperature": temperature, "max_tokens": max_tokens},
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    async def chat_stream(self, messages: list[dict], temperature: float = 0.7
                          ) -> AsyncIterator[str]:
        """SSE 流式对话，逐段产出文本增量。"""
        if self.mock_mode:
            full = self._mock_reply(messages)
            for i in range(0, len(full), 20):
                yield full[i:i + 20]
            return
        async with httpx.AsyncClient(timeout=settings.llm_timeout) as client:
            async with client.stream(
                "POST", f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={"model": self.model, "messages": messages,
                      "temperature": temperature, "stream": True},
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    payload = line[5:].strip()
                    if payload == "[DONE]":
                        break
                    try:
                        delta = json.loads(payload)["choices"][0]["delta"]
                        if delta.get("content"):
                            yield delta["content"]
                    except (KeyError, json.JSONDecodeError):
                        continue

    # ---------------- Mock 模式 ----------------
    def _mock_reply(self, messages: list[dict]) -> str:
        """按 system 提示词中的任务标记返回结构化模拟回答。"""
        system = ""
        user = ""
        for m in messages:
            if m.get("role") == "system":
                system += m.get("content", "")
            elif m.get("role") == "user":
                user = m.get("content", "")
        if "简历诊断" in system:
            return self._mock_resume(user)
        if "模拟面试" in system:
            return self._mock_interview(system, user)
        if "面试评估" in system:
            return self._mock_interview_report(user)
        if "知识库问答" in system:
            return self._mock_rag(system, user)
        if "JD解析" in system:
            return self._mock_jd(user)
        return ("【Mock 演示模式】收到你的问题："
                f"{user[:120]}。\n\n这是未配置 LLM API Key 时的模拟回答："
                "建议从简历诊断、RAG 问答或模拟面试开始体验；"
                "配置 LLM_API_KEY 后即可获得真实大模型回答。")

    @staticmethod
    def _mock_resume(user: str) -> str:
        return json.dumps({
            "score": 78,
            "highlights": ["项目经历完整，有真实上线经验", "技术栈与目标岗位匹配度较高",
                           "有独立负责模块的经历"],
            "issues": ["缺少量化成果（如性能提升百分比、用户量）",
                       "技能关键词密度不足，缺少 RAG / Agent 相关表述",
                       "教育背景与实习经历篇幅分配不均"],
            "suggestions": ["为每个项目补充 1-2 个可量化指标",
                            "在项目描述中加入 LangChain / 向量检索等关键词",
                            "把最匹配目标岗位的项目放在简历前部"],
            "missing_skills": ["LangChain", "RAG", "向量数据库", "Prompt 工程"],
            "summary": "简历整体结构清晰，项目经验真实可信；主要短板是缺少 AI / 大模型方向的项目与关键词，补充后与 AI 应用开发岗的匹配度可显著提升。"
        }, ensure_ascii=False, indent=2)

    @staticmethod
    def _mock_interview(system: str, user: str) -> str:
        m = re.search(r"第(\d+)轮", system)
        round_no = int(m.group(1)) if m else 1
        questions = {
            1: "请先做一个 1 分钟自我介绍，重点讲你做过的一个最有挑战的项目，以及你在其中负责的部分。",
            2: "RAG 系统中，检索召回率低通常有哪些原因？如果你负责优化，会从切分策略、Embedding 模型、重排序这三个环节分别怎么入手？",
            3: "请设计一个支持多轮对话的 Agent：需要哪些工具（Tools）？如何处理工具调用失败和幻觉问题？如果让你用 LangGraph 实现，状态图怎么画？",
            4: "生产环境中 LLM 流式输出出现首字延迟过高，你会如何定位和优化？请结合网关、模型推理、SSE 推送三个层面回答。",
            5: "请复盘你刚才的回答：你认为哪一题答得最弱？如果重来一次，你会补充哪些知识点？",
        }
        return questions.get(round_no, questions[1])

    @staticmethod
    def _mock_interview_report(user: str) -> str:
        return json.dumps({
            "scores": {"表达清晰度": 82, "技术深度": 76, "STAR结构": 74,
                       "知识点覆盖": 78, "综合": 78},
            "strengths": ["项目经历描述真实具体", "能结合实际场景回答"],
            "weaknesses": ["RAG 优化细节展开不足", "STAR 结构中 Result 部分常缺失量化结果"],
            "suggestions": ["回答技术问题时先给结论再展开", "每个项目准备 1 个 STAR 完整版故事",
                            "补强向量检索与重排序（Rerank）知识"],
            "summary": "整体表现良好，具备 AI 应用开发岗的基础能力；重点补强 RAG 细节与结构化表达后，面试通过率会明显提升。"
        }, ensure_ascii=False, indent=2)

    @staticmethod
    def _mock_rag(system: str, user: str) -> str:
        sources = re.findall(r"\[来源\d+\] ([^\n]+)", system)
        src_text = "；".join(sources[:3]) if sources else "知识库文档"
        return (f"根据知识库内容回答：{user[:80]}。\n\n"
                f"相关要点已在下方引用来源中列出（来源：{src_text}）。"
                "（Mock 模式：配置 LLM_API_KEY 后由真实模型基于检索片段作答。）")

    @staticmethod
    def _mock_jd(user: str) -> str:
        return json.dumps({
            "skills": ["Python", "LangChain", "RAG", "FastAPI", "Docker",
                       "向量数据库", "Prompt 工程"],
            "must_have": ["Python", "LangChain", "RAG"],
            "nice_to_have": ["Dify", "LangGraph", "Milvus"],
            "summary": "该 JD 核心要求为 Python + LangChain + RAG 方向的 AI 应用开发能力，强调 Agent 与向量检索落地经验。"
        }, ensure_ascii=False, indent=2)


llm = LLMClient()
