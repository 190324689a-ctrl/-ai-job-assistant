import axios from 'axios'

// VITE_API_BASE_URL 留空时走 Vite 代理（/api -> localhost:8000）。
// 直连后端时可设为 http://localhost:8000
const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
  timeout: 120000,
})

export const health = () => api.get('/health').then((r) => r.data)
export const chat = (message, conversation_id) =>
  api.post('/api/chat', { message, conversation_id }).then((r) => r.data)
export const analyzeResume = (text, target_jd = '') =>
  api.post('/api/resume/analyze', { text, target_jd }).then((r) => r.data)
export const uploadResume = (file, target_jd = '') => {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('target_jd', target_jd)
  return api.post('/api/resume/upload', fd).then((r) => r.data)
}
export const resumeHistory = () => api.get('/api/resume/history').then((r) => r.data)
export const matchJd = (jd_text, resume_text) =>
  api.post('/api/jd/match', { jd_text, resume_text }).then((r) => r.data)
export const ragUpload = (file) => {
  const fd = new FormData()
  fd.append('file', file)
  return api.post('/api/rag/upload', fd).then((r) => r.data)
}
export const ragQuery = (question, top_k = 4) =>
  api.post('/api/rag/query', { question, top_k }).then((r) => r.data)
export const ragStats = () => api.get('/api/rag/stats').then((r) => r.data)
export const ragClear = () => api.delete('/api/rag/clear').then((r) => r.data)
export const interviewStart = (direction) =>
  api.post('/api/interview/start', { direction }).then((r) => r.data)
export const interviewAnswer = (session_id, answer) =>
  api.post('/api/interview/answer', { session_id, answer }).then((r) => r.data)
export const interviewFinish = (session_id) =>
  api.post(`/api/interview/${session_id}/finish`).then((r) => r.data)

export function errMsg(e) {
  return e?.response?.data?.detail || e?.message || '请求失败，请确认后端已启动（http://localhost:8000）'
}

export const SAMPLE_RESUME = `张三 计算机科学与技术本科 2025 届毕业生
技术栈：Python、Java、Spring Boot、Vue 3、MySQL、Redis
项目经历：
- 医院医务管理系统（独立开发并上线）：负责挂号、排班、药品管理模块，用户量 500+，上线后挂号效率提升 40%。
- 企业工资核算系统：负责工资计算、人事档案模块，支持 200 人规模企业月度核算。
求职意向：AI 应用开发工程师`

export const SAMPLE_JD = `AI 应用开发工程师：熟悉 Python、LangChain、RAG、向量数据库（Milvus/FAISS）、FastAPI、Docker，有 Agent 工具调用与 Prompt 工程经验者优先。`
