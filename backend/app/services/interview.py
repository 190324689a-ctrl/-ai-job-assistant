"""模拟面试服务：多轮追问（难度递进）+ 结束评估报告。"""
import json

from ..llm.client import llm

MAX_ROUNDS = 5

DIRECTION_FOCUS = {
    "AI 应用开发": "Python、LangChain、RAG、向量检索、Agent 工具调用、Prompt 工程、FastAPI、流式输出",
    "Java 后端": "Spring Boot、MySQL、Redis、微服务、JVM、并发、高并发设计",
    "前端": "Vue 3、TypeScript、Element Plus、性能优化、工程化",
}


def interview_system_prompt(direction: str, round_no: int) -> str:
    focus = DIRECTION_FOCUS.get(direction, "通用软件开发")
    difficulty = ["基础", "进阶", "深入", "综合设计", "复盘"][min(round_no - 1, 4)]
    return (f"你是一名资深面试官，正在进行「模拟面试」，岗位方向：{direction}，"
            f"考察重点：{focus}。现在是第{round_no}轮，难度：{difficulty}。"
            "只输出一道面试题，不要输出其他内容。题目要结合真实项目场景，"
            "难度随轮次递进；第 5 轮请让候选人复盘自己的表现。")


async def next_question(direction: str, round_no: int,
                        history: list[dict]) -> str:
    messages = [{"role": "system",
                 "content": interview_system_prompt(direction, round_no)}]
    for turn in history[-6:]:
        messages.append({"role": "user", "content": f"候选人回答：{turn['answer']}"})
        messages.append({"role": "assistant", "content": turn["question"]})
    return await llm.chat(messages, temperature=0.7)


REPORT_SYSTEM_PROMPT = """你是一名资深面试官，任务是「面试评估」。
请只输出 JSON，不要输出任何其他文字，字段如下：
{
  "scores": {"表达清晰度": 0-100, "技术深度": 0-100, "STAR结构": 0-100,
             "知识点覆盖": 0-100, "综合": 0-100},
  "strengths": ["优点1", "优点2"],
  "weaknesses": ["不足1", "不足2"],
  "suggestions": ["可执行的改进建议1", "建议2", "建议3"],
  "summary": "一句话总体评价"
}
"""


async def evaluate(transcript: list[dict]) -> dict:
    text = "\n".join(f"Q: {t['question']}\nA: {t['answer']}"
                     for t in transcript)
    try:
        raw = await llm.chat(
            [{"role": "system", "content": REPORT_SYSTEM_PROMPT},
             {"role": "user", "content": f"面试全程记录：\n{text[:6000]}"}],
            temperature=0.3)
        return json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
    except Exception:
        # 规则降级：按回答长度与关键词覆盖启发式打分
        total_len = sum(len(t["answer"]) for t in transcript)
        base = 65 + min(total_len // 100, 20)
        return {
            "scores": {"表达清晰度": base, "技术深度": base - 3,
                       "STAR结构": base - 5, "知识点覆盖": base - 2, "综合": base},
            "strengths": ["能结合实际项目回答"],
            "weaknesses": ["部分回答偏简短，可再展开细节"],
            "suggestions": ["回答先给结论再展开", "每个项目准备 STAR 完整版故事"],
            "summary": "规则版评估（LLM 未返回有效结果），建议配置 LLM API Key 获得深度评估。",
        }
