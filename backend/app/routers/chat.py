"""路由：通用对话（含 SSE 流式）与健康检查。"""
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db import Conversation, Message, get_db
from ..llm.client import llm
from ..schemas import ChatRequest, ChatResponse

router = APIRouter()


def _get_or_create_conversation(db: Session, conversation_id: int | None) -> Conversation:
    if conversation_id:
        conv = db.query(Conversation).filter_by(id=conversation_id).first()
        if conv:
            return conv
    conv = Conversation(title="新的对话")
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    conv = _get_or_create_conversation(db, req.conversation_id)
    history = db.query(Message).filter_by(conversation_id=conv.id).order_by(Message.id).all()
    messages = [{"role": m.role, "content": m.content} for m in history[-10:]]
    messages.append({"role": "user", "content": req.message})
    reply = await llm.chat(messages)
    db.add_all([Message(conversation_id=conv.id, role="user", content=req.message),
                Message(conversation_id=conv.id, role="assistant", content=reply)])
    if len(history) == 0:
        conv.title = req.message[:30]
    db.commit()
    return ChatResponse(reply=reply, conversation_id=conv.id, mock_mode=llm.mock_mode)


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest, db: Session = Depends(get_db)):
    conv = _get_or_create_conversation(db, req.conversation_id)
    history = db.query(Message).filter_by(conversation_id=conv.id).order_by(Message.id).all()
    messages = [{"role": m.role, "content": m.content} for m in history[-10:]]
    messages.append({"role": "user", "content": req.message})

    async def gen():
        full = ""
        async for piece in llm.chat_stream(messages):
            full += piece
            yield f"data: {json.dumps({'delta': piece}, ensure_ascii=False)}\n\n"
        db.add_all([Message(conversation_id=conv.id, role="user", content=req.message),
                    Message(conversation_id=conv.id, role="assistant", content=full)])
        db.commit()
        yield f"data: {json.dumps({'done': True, 'conversation_id': conv.id}, ensure_ascii=False)}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.get("/conversations")
def list_conversations(db: Session = Depends(get_db)):
    convs = db.query(Conversation).order_by(Conversation.id.desc()).limit(50).all()
    return [{"id": c.id, "title": c.title, "created_at": str(c.created_at)} for c in convs]


@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: int, db: Session = Depends(get_db)):
    msgs = (db.query(Message).filter_by(conversation_id=conversation_id)
            .order_by(Message.id).all())
    return [{"role": m.role, "content": m.content} for m in msgs]
