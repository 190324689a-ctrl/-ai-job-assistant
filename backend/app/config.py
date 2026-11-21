"""应用配置：通过环境变量切换大模型厂商；无 Key 时自动 Mock 模式。"""
from pathlib import Path

from pydantic_settings import BaseSettings

# 项目根目录（backend/app/config.py 上两级）下的 data/，不依赖启动时的工作目录
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DATA_DIR = _PROJECT_ROOT / "data"


class Settings(BaseSettings):
    app_name: str = "AI 求职助手"
    # LLM：OpenAI 兼容接口。默认 DeepSeek，可切换 Qwen / OpenAI。
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_api_key: str = ""
    llm_model: str = "deepseek-chat"
    llm_timeout: int = 60
    # 向量维度（本地 Hashing TF 向量化）
    embedding_dim: int = 384
    rag_top_k: int = 4
    database_url: str = f"sqlite:///{_DEFAULT_DATA_DIR}/app.db"
    data_dir: str = str(_DEFAULT_DATA_DIR)

    @property
    def mock_mode(self) -> bool:
        return not self.llm_api_key.strip()

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
