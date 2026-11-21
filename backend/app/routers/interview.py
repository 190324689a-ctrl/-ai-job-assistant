"""路由：AI 模拟面试（开始 / 回答追问 / 结束评估）。"""
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import InterviewSession, get_db
from ..schemas import (InterviewAnswerRequest, InterviewReport,
                       InterviewStartRequest)
from ..services.interview import MAX_ROUNDS, evaluate, next_question

router = APIRouter()


@router.post("/interview/start")
async def start_interview(req: InterviewStartRequest,
                          db: Session = Depends(get_db)):
    session = InterviewSession(direction=req.direction, round_no=1)
    db.add(session)
    db.commit()
    db.refresh(session)
    q = await next_question(req.direction, 1, [])
    transcript = [{"round": 1, "question": q, "answer": ""}]
    session.transcript_json = json.dumps(transcript, ensure_ascii=False)
    db.commit()
    return {"session_id": session.id, "direction": req.direction,
            "round": 1, "total_rounds": MAX_ROUNDS, "question": q}


@router.post("/interview/answer")
async def answer_interview(req: InterviewAnswerRequest,
                           db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter_by(id=req.session_id).first()
    if not session:
        raise HTTPException(404, "面试会话不存在")
    if session.status != "ongoing":
        raise HTTPException(400, "该面试已结束")
    transcript = json.loads(session.transcript_json)
    transcript[-1]["answer"] = req.answer
    if session.round_no >= MAX_ROUNDS:
        report = await evaluate(transcript)
        session.transcript_json = json.dumps(transcript, ensure_ascii=False)
        session.report_json = json.dumps(report, ensure_ascii=False)
        session.status = "finished"
        db.commit()
        return {"finished": True, "round": session.round_no,
                "report": report}
    session.round_no += 1
    q = await next_question(session.direction, session.round_no, transcript)
    transcript.append({"round": session.round_no, "question": q, "answer": ""})
    session.transcript_json = json.dumps(transcript, ensure_ascii=False)
    db.commit()
    return {"finished": False, "round": session.round_no,
            "total_rounds": MAX_ROUNDS, "question": q}


@router.post("/interview/{session_id}/finish")
async def finish_interview(session_id: int, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(404, "面试会话不存在")
    if session.status == "finished":
        return {"finished": True, "report": json.loads(session.report_json)}
    transcript = json.loads(session.transcript_json)
    answered = [t for t in transcript if t.get("answer")]
    report = await evaluate(answered)
    session.report_json = json.dumps(report, ensure_ascii=False)
    session.status = "finished"
    db.commit()
    return {"finished": True, "report": report}


@router.get("/interview/{session_id}")
def get_interview(session_id: int, db: Session = Depends(get_db)):
    session = db.query(InterviewSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(404, "面试会话不存在")
    return {"session_id": session.id, "direction": session.direction,
            "round": session.round_no, "status": session.status,
            "transcript": json.loads(session.transcript_json),
            "report": json.loads(session.report_json) if session.report_json else None}
