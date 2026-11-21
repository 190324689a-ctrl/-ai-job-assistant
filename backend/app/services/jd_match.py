"""JD 解析与匹配服务：技能词典提取 + 关键词重叠度打分。"""
import re

# 深圳 AI 应用开发岗高频技能词典（可扩展）
SKILL_KEYWORDS = [
    "Python", "Java", "LangChain", "LangGraph", "Dify", "RAG", "Agent",
    "向量数据库", "Milvus", "FAISS", "Elasticsearch", "Prompt 工程",
    "FastAPI", "Spring Boot", "Vue", "Docker", "MySQL", "Redis",
    "微调", "Fine-tuning", "Embedding", "重排序", "Rerank", "流式输出",
    "SSE", "大模型", "LLM", "知识库", "多模态", "Kubernetes", "Git",
]
# 同义词归一：JD/简历里不同写法映射到同一技能
ALIASES = {
    "springboot": "Spring Boot", "spring boot": "Spring Boot",
    "vue3": "Vue", "vue.js": "Vue", "elasticsearch": "Elasticsearch",
    "es": "Elasticsearch", "fine-tuning": "微调", "finetuning": "微调",
    "rerank": "重排序", "large language model": "LLM",
}


def extract_skills(text: str) -> list[str]:
    """从文本中提取技能词（大小写不敏感 + 同义词归一）。"""
    low = text.lower()
    found: list[str] = []
    for skill in SKILL_KEYWORDS:
        if skill.lower() in low:
            found.append(skill)
    for alias, canonical in ALIASES.items():
        if alias in low and canonical not in found:
            found.append(canonical)
    return found


def match_jd(jd_text: str, resume_text: str) -> dict:
    jd_skills = extract_skills(jd_text)
    resume_skills = set(extract_skills(resume_text))
    matched = [s for s in jd_skills if s in resume_skills]
    missing = [s for s in jd_skills if s not in resume_skills]
    score = round(len(matched) / len(jd_skills) * 100) if jd_skills else 0
    suggestions = []
    for s in missing:
        suggestions.append(f"补强「{s}」：做一个相关小项目并写入简历，或在现有项目描述中体现该能力")
    summary = (f"JD 共提取 {len(jd_skills)} 个关键技能，简历已覆盖 {len(matched)} 个，"
               f"匹配度 {score} 分。" + ("缺口主要在：" + "、".join(missing[:5]) + "。"
               if missing else "已基本覆盖 JD 要求。"))
    return {"match_score": score, "jd_skills": jd_skills,
            "matched": matched, "missing": missing,
            "suggestions": suggestions, "summary": summary}
