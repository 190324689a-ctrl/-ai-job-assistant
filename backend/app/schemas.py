"""Pydantic Schemas：请求 / 响应模型。"""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    mock_mode: bool


class ResumeAnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=20, description="简历纯文本")
    target_jd: str = ""


class ResumeReport(BaseModel):
    score: int
    highlights: list[str]
    issues: list[str]
    suggestions: list[str]
    missing_skills: list[str]
    summary: str


class RagUploadResponse(BaseModel):
    filename: str
    chunks: int
    total_chunks: int


class RagQueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = 4


class RagSource(BaseModel):
    text: str
    source: str
    score: float


class RagQueryResponse(BaseModel):
    answer: str
    sources: list[RagSource]
    mock_mode: bool


class InterviewStartRequest(BaseModel):
    direction: str = "AI 应用开发"


class InterviewAnswerRequest(BaseModel):
    session_id: int
    answer: str = Field(..., min_length=1)


class InterviewReport(BaseModel):
    scores: dict[str, int]
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    summary: str


class JdMatchRequest(BaseModel):
    jd_text: str = Field(..., min_length=20)
    resume_text: str = Field(..., min_length=20)


class JdMatchResponse(BaseModel):
    match_score: int
    jd_skills: list[str]
    matched: list[str]
    missing: list[str]
    suggestions: list[str]
    summary: str
