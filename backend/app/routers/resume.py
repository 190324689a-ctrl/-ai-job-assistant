"""路由：简历诊断（上传解析 / 文本诊断）与 JD 匹配。"""
import json

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from ..db import ResumeRecord, get_db
from ..schemas import JdMatchRequest, JdMatchResponse, ResumeAnalyzeRequest, ResumeReport
from ..services.jd_match import match_jd
from ..services.parsing import extract_text, read_upload
from ..services.resume import diagnose_resume

router = APIRouter()


@router.post("/resume/analyze", response_model=ResumeReport)
async def analyze_resume(req: ResumeAnalyzeRequest, db: Session = Depends(get_db)):
    report = await diagnose_resume(req.text, req.target_jd)
    db.add(ResumeRecord(filename="text-input", raw_text=req.text[:20000],
                        score=report.score,
                        report_json=report.model_dump_json()))
    db.commit()
    return report


@router.post("/resume/upload", response_model=ResumeReport)
async def upload_resume(file: UploadFile = File(...),
                        target_jd: str = Form(""),
                        db: Session = Depends(get_db)):
    text = await read_upload(file)
    if len(text.strip()) < 20:
        from fastapi import HTTPException
        raise HTTPException(400, "未能从文件中解析出有效文本，请确认是 PDF/DOCX/TXT 简历")
    report = await diagnose_resume(text, target_jd)
    db.add(ResumeRecord(filename=file.filename, raw_text=text[:20000],
                        score=report.score,
                        report_json=report.model_dump_json()))
    db.commit()
    return report


@router.post("/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    """只解析不诊断：返回提取的纯文本，供前端预览确认。"""
    text = await read_upload(file)
    return {"filename": file.filename, "length": len(text),
            "text": text[:8000]}


@router.get("/resume/history")
def resume_history(db: Session = Depends(get_db)):
    rows = db.query(ResumeRecord).order_by(ResumeRecord.id.desc()).limit(20).all()
    return [{"id": r.id, "filename": r.filename, "score": r.score,
             "created_at": str(r.created_at),
             "report": json.loads(r.report_json) if r.report_json else None}
            for r in rows]


@router.post("/jd/match", response_model=JdMatchResponse)
async def jd_match(req: JdMatchRequest):
    return match_jd(req.jd_text, req.resume_text)
