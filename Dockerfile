# AI 求职助手 · 后端镜像（FastAPI + Python 3.12）
FROM python:3.12-slim

WORKDIR /app/backend
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 保持与本地一致的目录结构：/app/backend + /app/data，
# 这样 backend/app/config.py 里 parents[2] 仍指向项目根目录 /app。
WORKDIR /app
COPY backend/ ./backend/
RUN mkdir -p /app/data

WORKDIR /app/backend
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
