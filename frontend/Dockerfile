# AI 求职助手 · 前端镜像（Vue 3 + Vite）
# 先构建，再用 vite preview 对外提供页面，并把 /api 代理到后端服务。
FROM node:24-alpine

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

EXPOSE 4173
# BACKEND_URL 由 docker-compose 传入，如 http://backend:8000
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "4173"]
