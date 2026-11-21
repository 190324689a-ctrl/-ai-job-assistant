"""文本切分：按段落优先、定长滑动窗口切分，保留重叠避免语义断裂。"""
import re


def split_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text.strip())
    if not text:
        return []
    # 先按段落切，再对超长段落做滑动窗口
    chunks: list[str] = []
    for para in text.split("\n\n"):
        para = para.strip()
        if not para:
            continue
        if len(para) <= chunk_size:
            chunks.append(para)
            continue
        step = chunk_size - overlap
        for i in range(0, len(para), step):
            chunks.append(para[i:i + chunk_size])
            if i + chunk_size >= len(para):
                break
    return chunks
