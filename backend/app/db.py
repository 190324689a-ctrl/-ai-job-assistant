"""数据库：SQLite + SQLAlchemy，持久化对话历史 / 简历 / 面试 / 知识库文档。"""
import os

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String,
                        Text, create_engine)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

from .config import settings

os.makedirs(settings.data_dir, exist_ok=True)
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), default="新的对话")
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String(20))  # user / assistant
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class ResumeRecord(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    filename = Column(String(200))
    raw_text = Column(Text)
    score = Column(Float, nullable=True)
    report_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class InterviewSession(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True)
    direction = Column(String(50))
    round_no = Column(Integer, default=0)
    transcript_json = Column(Text, default="[]")
    report_json = Column(Text, nullable=True)
    status = Column(String(20), default="ongoing")  # ongoing / finished
    created_at = Column(DateTime, default=datetime.utcnow)


class KbDocument(Base):
    __tablename__ = "kb_documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String(200))
    chunks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
