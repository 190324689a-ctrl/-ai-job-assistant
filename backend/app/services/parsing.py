"""文件解析：PDF / DOCX / TXT / MD 文本提取。"""
import io

from fastapi import UploadFile


def extract_text(filename: str, data: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages)
    if name.endswith(".docx"):
        from docx import Document
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs)
    # txt / md 默认 utf-8，失败时忽略非法字符
    return data.decode("utf-8", errors="ignore")


async def read_upload(file: UploadFile) -> str:
    data = await file.read()
    return extract_text(file.filename or "file.txt", data)
