"""路由：RAG 知识库（上传建库 / 提问检索作答）。"""
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from ..db import KbDocument, get_db
from ..llm.client import llm
from ..rag.chunker import split_text
from ..rag.store import store
from ..schemas import RagQueryRequest, RagQueryResponse, RagSource, RagUploadResponse
from ..services.parsing import read_upload

router = APIRouter()

RAG_SYSTEM_PROMPT = """你是一名「知识库问答」助手，任务是仅根据下方提供的参考片段回答用户问题。
要求：
1. 答案必须基于参考片段，不要编造片段中没有的信息；片段不足时如实说“知识库中没有相关内容”。
2. 回答末尾注明引用来源编号。
参考片段：
{context}
"""


@router.post("/rag/upload", response_model=RagUploadResponse)
async def upload_document(file: UploadFile = File(...),
                          db: Session = Depends(get_db)):
    text = await read_upload(file)
    chunks = split_text(text)
    n = store.add(chunks, source=file.filename or "未命名文档")
    db.add(KbDocument(filename=file.filename, chunks=n))
    db.commit()
    return RagUploadResponse(filename=file.filename or "", chunks=n,
                             total_chunks=store.count())


@router.post("/rag/query", response_model=RagQueryResponse)
async def query_kb(req: RagQueryRequest):
    hits = store.search(req.question, top_k=req.top_k)
    if not hits:
        return RagQueryResponse(
            answer="知识库目前还是空的，请先上传文档（txt/md/pdf/docx）建立知识库后再提问。",
            sources=[], mock_mode=llm.mock_mode)
    context = "\n\n".join(f"[来源{i + 1}] {h['source']}：{h['text']}"
                          for i, h in enumerate(hits))
    prompt = RAG_SYSTEM_PROMPT.format(context=context)
    answer = await llm.chat([{"role": "system", "content": prompt},
                             {"role": "user", "content": req.question}])
    return RagQueryResponse(
        answer=answer,
        sources=[RagSource(text=h["text"][:500], source=h["source"],
                           score=round(h["score"], 4)) for h in hits],
        mock_mode=llm.mock_mode)


@router.get("/rag/stats")
def rag_stats():
    return {"total_chunks": store.count(),
            "engine": "FAISS" if store.index is not None else "NumPy（FAISS 不可用时降级）"}


@router.delete("/rag/clear")
def rag_clear():
    store.clear()
    return {"ok": True, "total_chunks": 0}
