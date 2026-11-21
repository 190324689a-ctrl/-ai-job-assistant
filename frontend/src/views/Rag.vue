<template>
  <div class="page">
    <h2>知识库问答（RAG）</h2>
    <p class="desc">上传面试笔记、面经、岗位资料等文档（txt / md / pdf / docx），再提问，答案只基于知识库片段，并给出引用来源。</p>
    <el-card class="card">
      <div class="row" style="align-items:center">
        <span>知识库：{{ stats.total_chunks }} 个片段 · {{ stats.engine || '—' }}</span>
        <el-button @click="loadStats">刷新</el-button>
        <el-button type="danger" plain @click="clearKb">清空知识库</el-button>
      </div>
      <div style="margin-top:12px">
        <el-upload :show-file-list="false" :before-upload="onFile" accept=".txt,.md,.pdf,.docx">
          <el-button type="primary">上传文档建库</el-button>
        </el-upload>
        <span class="muted" style="margin-left:8px">上传后会切分并入库，可多次上传。</span>
      </div>
    </el-card>
    <el-card class="card">
      <el-input v-model="q" placeholder="比如：什么是 RAG？" @keyup.enter="ask" />
      <div style="margin-top:12px"><el-button type="primary" :loading="loading" @click="ask">提问</el-button></div>
      <div v-if="answer" style="margin-top:16px">
        <h4>回答 <el-tag v-if="answer.mock_mode" type="warning">Mock 模式</el-tag></h4>
        <pre class="answer">{{ answer.answer }}</pre>
        <h4>引用来源</h4>
        <div v-if="!answer.sources.length" class="muted">暂无来源，请先上传文档。</div>
        <el-card v-for="(s, i) in answer.sources" :key="i" shadow="never" style="margin-bottom:8px">
          <div class="muted">[来源 {{ i + 1 }}] {{ s.source }} · 相似度 {{ s.score }}</div>
          <div>{{ s.text }}</div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ragUpload, ragQuery, ragStats, ragClear, errMsg } from '../api/client'
const q = ref('')
const answer = ref(null)
const stats = ref({ total_chunks: 0 })
const loading = ref(false)
async function loadStats() { try { stats.value = await ragStats() } catch { /* ignore */ } }
onMounted(loadStats)
async function onFile(file) {
  try { const r = await ragUpload(file); ElMessage.success(`已入库 ${r.chunks} 个片段，共 ${r.total_chunks} 个`); loadStats() }
  catch (e) { ElMessage.error(errMsg(e)) }
  return false
}
async function ask() {
  if (!q.value.trim()) return ElMessage.warning('先输入问题')
  loading.value = true
  try { answer.value = await ragQuery(q.value) }
  catch (e) { ElMessage.error(errMsg(e)) } finally { loading.value = false }
}
async function clearKb() {
  try { await ElMessageBox.confirm('确定清空知识库吗？', '提示', { type: 'warning' }) }
  catch { return }
  await ragClear(); answer.value = null; loadStats(); ElMessage.success('已清空')
}
</script>
