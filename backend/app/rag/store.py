"""向量库：FAISS（IndexFlatIP，余弦相似度）为主，faiss 不可用时自动
降级为 NumPy 暴力检索。索引与元数据持久化到 data/ 目录。
"""
import json
import os

import numpy as np

from ..config import settings
from .embeddings import DIM, embed_batch

try:
    import faiss  # type: ignore
    _HAS_FAISS = True
except ImportError:
    _HAS_FAISS = False

INDEX_PATH = os.path.join(settings.data_dir, "faiss.index")
META_PATH = os.path.join(settings.data_dir, "faiss_meta.json")


class VectorStore:
    """内存索引 + 磁盘持久化；元数据为 {text, source} 列表。"""

    def __init__(self):
        self.metas: list[dict] = []
        self.vectors: np.ndarray = np.zeros((0, DIM), dtype=np.float32)
        self.index = None
        self._load()

    # ---------- 持久化 ----------
    def _load(self):
        if os.path.exists(META_PATH):
            with open(META_PATH, encoding="utf-8") as f:
                self.metas = json.load(f)
        if _HAS_FAISS and os.path.exists(INDEX_PATH) and self.metas:
            self.index = faiss.read_index(INDEX_PATH)
        elif self.metas:
            # 无 faiss 时从元数据重建向量（确定性 embedding，可复算）
            self.vectors = embed_batch([m["text"] for m in self.metas])

    def _save(self):
        os.makedirs(settings.data_dir, exist_ok=True)
        with open(META_PATH, "w", encoding="utf-8") as f:
            json.dump(self.metas, f, ensure_ascii=False)
        if _HAS_FAISS and self.index is not None:
            faiss.write_index(self.index, INDEX_PATH)

    def _rebuild_faiss(self):
        if not _HAS_FAISS:
            return
        self.index = faiss.IndexFlatIP(DIM)
        if len(self.vectors):
            self.index.add(self.vectors.astype(np.float32))

    # ---------- 写入 / 检索 ----------
    def add(self, chunks: list[str], source: str) -> int:
        if not chunks:
            return 0
        vecs = embed_batch(chunks)
        self.metas.extend({"text": c, "source": source} for c in chunks)
        self.vectors = np.vstack([self.vectors, vecs]) if len(self.vectors) else vecs
        self._rebuild_faiss()
        self._save()
        return len(chunks)

    def search(self, query: str, top_k: int = 4) -> list[dict]:
        if not self.metas:
            return []
        from .embeddings import embed
        q = embed(query).reshape(1, -1).astype(np.float32)
        k = min(top_k, len(self.metas))
        if _HAS_FAISS and self.index is not None:
            scores, idxs = self.index.search(q, k)
            return [{"text": self.metas[i]["text"], "source": self.metas[i]["source"],
                     "score": float(scores[0][j])}
                    for j, i in enumerate(idxs[0]) if i >= 0]
        sims = self.vectors @ q[0]
        order = np.argsort(-sims)[:k]
        return [{"text": self.metas[i]["text"], "source": self.metas[i]["source"],
                 "score": float(sims[i])} for i in order]

    def count(self) -> int:
        return len(self.metas)

    def clear(self):
        self.metas, self.vectors, self.index = [], np.zeros((0, DIM), dtype=np.float32), None
        for p in (INDEX_PATH, META_PATH):
            if os.path.exists(p):
                os.remove(p)


store = VectorStore()
