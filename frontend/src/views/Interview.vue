<template>
  <div class="page">
    <h2>AI 模拟面试</h2>
    <p class="desc">选一个方向开始 5 轮面试，认真回答每一题，结束出评分报告。</p>
    <el-card v-if="!started" class="card">
      <el-form label-width="80px">
        <el-form-item label="面试方向">
          <el-select v-model="direction" style="width:280px">
            <el-option label="AI 应用开发" value="AI 应用开发" />
            <el-option label="后端开发" value="后端开发" />
            <el-option label="前端开发" value="前端开发" />
            <el-option label="算法工程师" value="算法工程师" />
          </el-select>
        </el-form-item>
      </el-form>
      <el-button type="primary" :loading="loading" @click="start">开始面试</el-button>
    </el-card>
    <template v-else>
      <el-card class="card">
        <div class="muted">第 {{ round }} / {{ total }} 轮 · 方向：{{ direction }}</div>
        <h3 style="margin-top:8px">Q：{{ question }}</h3>
        <el-input v-model="answer" type="textarea" :rows="5" placeholder="输入你的回答…" />
        <div style="margin-top:12px">
          <el-button type="primary" :loading="loading" @click="submit">提交回答，下一题</el-button>
          <el-button type="success" :loading="loading" @click="finish">结束面试，出报告</el-button>
        </div>
      </el-card>
      <el-card v-if="history.length" class="card">
        <h4>已回答</h4>
        <div v-for="(h, i) in history" :key="i" style="margin-bottom:12px">
          <div><b>Q{{ i + 1 }}：</b>{{ h.q }}</div>
          <div class="muted">A：{{ h.a }}</div>
        </div>
      </el-card>
    </template>
    <el-card v-if="report" class="card">
      <h3>面试报告</h3>
      <p>{{ report.summary }}</p>
      <div class="row">
        <div v-for="(v, k) in report.scores" :key="k" style="min-width:140px">
          <div class="muted">{{ k }}</div>
          <div class="score" style="font-size:28px">{{ v }}</div>
          <el-progress :percentage="v" />
        </div>
      </div>
      <h4>优点</h4><ul><li v-for="x in report.strengths" :key="x">{{ x }}</li></ul>
      <h4>不足</h4><ul><li v-for="x in report.weaknesses" :key="x">{{ x }}</li></ul>
      <h4>建议</h4><ul><li v-for="x in report.suggestions" :key="x">{{ x }}</li></ul>
      <el-button @click="reset">再面一次</el-button>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { interviewStart, interviewAnswer, interviewFinish, errMsg } from '../api/client'
const direction = ref('AI 应用开发')
const started = ref(false)
const sessionId = ref(null)
const round = ref(1)
const total = ref(5)
const question = ref('')
const answer = ref('')
const history = ref([])
const report = ref(null)
const loading = ref(false)
async function start() {
  loading.value = true
  try {
    const r = await interviewStart(direction.value)
    sessionId.value = r.session_id; round.value = r.round; total.value = r.total_rounds || 5
    question.value = r.question; started.value = true; history.value = []; report.value = null
  } catch (e) { ElMessage.error(errMsg(e)) } finally { loading.value = false }
}
async function submit() {
  if (!answer.value.trim()) return ElMessage.warning('先写回答')
  loading.value = true
  try {
    const r = await interviewAnswer(sessionId.value, answer.value)
    history.value.push({ q: question.value, a: answer.value }); answer.value = ''
    if (r.finished) { report.value = r.report; started.value = false }
    else { round.value = r.round; total.value = r.total_rounds || total.value; question.value = r.question }
  } catch (e) { ElMessage.error(errMsg(e)) } finally { loading.value = false }
}
async function finish() {
  loading.value = true
  try { const r = await interviewFinish(sessionId.value); report.value = r.report; started.value = false }
  catch (e) { ElMessage.error(errMsg(e)) } finally { loading.value = false }
}
function reset() { started.value = false; report.value = null; history.value = []; answer.value = '' }
</script>
