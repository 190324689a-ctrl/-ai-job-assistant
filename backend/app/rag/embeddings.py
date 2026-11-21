"""本地轻量向量化：Hashing TF（词哈希 + 归一化），零外部模型依赖。

说明：这是一个可离线运行的确定性向量化方案，用于演示 RAG 全流程；
生产可替换为 OpenAI / BGE 等 Embedding 模型，只需实现同名 embed() 接口。
"""
import hashlib
import re

import numpy as np

from ..config import settings

DIM = settings.embedding_dim


def _tokenize(text: str) -> list[str]:
    # 中英文分词：英文单词 + 连续中文字符按字切分（兼容中文检索）
    tokens = re.findall(r"[a-zA-Z0-9_]+|[\u4e00-\u9fff]", text.lower())
    # 中文按二元组增强语义
    out = list(tokens)
    zh = [t for t in tokens if re.match(r"[\u4e00-\u9fff]", t)]
    out += [zh[i] + zh[i + 1] for i in range(len(zh) - 1)]
    return out


def _hash(token: str) -> int:
    return int(hashlib.md5(token.encode()).hexdigest(), 16) % DIM


def embed(text: str) -> np.ndarray:
    vec = np.zeros(DIM, dtype=np.float32)
    for tok in _tokenize(text):
        vec[_hash(tok)] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec


def embed_batch(texts: list[str]) -> np.ndarray:
    return np.stack([embed(t) for t in texts]) if texts else np.zeros((0, DIM), dtype=np.float32)
