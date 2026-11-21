"""简历诊断服务：LLM 结构化诊断 + JD 匹配打分。"""
import json

from ..llm.client import llm
from ..schemas import ResumeReport
from .jd_match import extract_skills, match_jd

RESUME_SYSTEM_PROMPT = """你是一名资深的 AI 岗位求职顾问，任务是「简历诊断」。
请只输出 JSON，不要输出任何其他文字，字段如下：
{
  "score": 0-100 的整数（与目标岗位的匹配度）,
  "highlights": ["亮点1", "亮点2", "亮点3"],
  "issues": ["问题1", "问题2", "问题3"],
  "suggestions": ["可执行的改进建议1", "建议2", "建议3"],
  "missing_skills": ["缺失技能1", "缺失技能2"],
  "summary": "一句话总体评价"
}
诊断要点：量化成果、STAR 结构、技能关键词密度、项目与目标岗位的相关性、篇幅结构。
"""


async def diagnose_resume(text: str, target_jd: str = "") -> ResumeReport:
    """调用 LLM 诊断；失败或解析失败时降级为规则版报告（接口不中断）。"""
    user_prompt = f"简历文本：\n{text[:6000]}"
    if target_jd:
        user_prompt += f"\n\n目标岗位 JD：\n{target_jd[:3000]}"
    try:
        raw = await llm.chat(
            [{"role": "system", "content": RESUME_SYSTEM_PROMPT},
             {"role": "user", "content": user_prompt}],
            temperature=0.3)
        data = json.loads(raw[raw.find("{"):raw.rfind("}") + 1])
        report = ResumeReport(**data)
    except Exception:
        report = _rule_based_report(text, target_jd)
    # 用 JD 匹配校准缺口技能
    if target_jd:
        m = match_jd(target_jd, text)
        report.missing_skills = m["missing"] or report.missing_skills
        report.score = round(report.score * 0.6 + m["match_score"] * 0.4)
    return report


def _rule_based_report(text: str, target_jd: str) -> ResumeReport:
    """LLM 不可用时的规则降级：基于关键词与量化指标启发式打分。"""
    skills = extract_skills(text)
    has_number = any(ch.isdigit() for ch in text)
    score = 60 + min(len(skills) * 2, 20) + (5 if has_number else 0)
    missing = [s for s in extract_skills(target_jd) if s not in skills] if target_jd else []
    return ResumeReport(
        score=min(score, 95),
        highlights=[f"已覆盖 {len(skills)} 个岗位相关技能关键词",
                    "项目经历描述具体" if "项目" in text else "经历描述完整"],
        issues=([] if has_number else ["缺少量化成果数据"])
               + (["缺少 AI / 大模型方向关键词"] if "RAG" not in skills and "LangChain" not in skills else []),
        suggestions=["为每个项目补充量化指标", "对照 JD 补充缺失技能关键词"],
        missing_skills=missing,
        summary="规则版诊断（LLM 未返回有效结果），建议配置 LLM API Key 获得深度诊断。",
    )
