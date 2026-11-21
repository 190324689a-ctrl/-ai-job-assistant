<template>
  <div class="page">
    <h2>简历诊断</h2>
    <p class="desc">粘贴简历文本（至少 20 字），可同时粘贴目标 JD；也可以直接上传 PDF / DOCX / TXT 简历文件。</p>
    <el-card class="card">
      <el-input v-model="text" type="textarea" :rows="8" placeholder="粘贴简历纯文本…" />
      <el-input v-model="jd" type="textarea" :rows="3" placeholder="目标 JD（可选）" style="margin-top:12px" />
      <div style="margin-top:12px">
        <el-button type="primary" :loading="loading" @click="analyze">开始诊断</el-button>
        <el-button @click="fillSample">填入示例</el-button>
        <el-upload :show-file-list="false" :before-upload="onFile" accept=".pdf,.docx,.txt,.md" style="display:inline-block;margin-left:8px">
          <el-button>上传简历文件诊断</el-button>
        </el-upload>
      </div>
    </el-card>
    <el-card v-if="report" class="card">
      <div class="row" style="align-items:center">
        <div><div class="muted">综合评分</div><div class="score">{{ report.score }}<span style="font-size:16px"> / 100</span></div></div>
        <el-progress :percentage="report.score" style="flex:1" />
      </div>
      <p><b>总结：</b>{{ report.summary }}</p>
      <h4>亮点</h4><ul><li v-for="x in report.highlights" :key="x">{{ x }}</li></ul>
      <h4>问题</h4><ul><li v-for="x in report.issues" :key="x">{{ x }}</li></ul>
      <h4>改进建议</h4><ul><li v-for="x in report.suggestions" :key="x">{{ x }}</li></ul>
      <div v-if="report.missing_skills?.length"><h4>缺失技能</h4><el-tag v-for="x in report.missing_skills" :key="x" type="warning" style="margin:0 6px 6px 0">{{ x }}</el-tag></div>
    </el-card>
    <el-card v-if="history.length" class="card">
      <h4>最近诊断记录</h4>
      <el-table :data="history" style="width:100%">
        <el-table-column prop="filename" label="来源" />
        <el-table-column prop="score" label="评分" width="80" />
        <el-table-column prop="created_at" label="时间" />
      </el-table>
    </el-card>
  </div>
</template>
<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { analyzeResume, uploadResume, resumeHistory, errMsg, SAMPLE_RESUME, SAMPLE_JD } from '../api/client'
const text = ref('')
const jd = ref('')
const report = ref(null)
const history = ref([])
const loading = ref(false)
async function loadHistory() { try { history.value = await resumeHistory() } catch { /* ignore */ } }
onMounted(loadHistory)
function fillSample() { text.value = SAMPLE_RESUME; jd.value = SAMPLE_JD }
async function analyze() {
  if (text.value.trim().length < 20) return ElMessage.warning('简历至少 20 字')
  loading.value = true
  try { report.value = await analyzeResume(text.value, jd.value); loadHistory() }
  catch (e) { ElMessage.error(errMsg(e)) } finally { loading.value = false }
}
async function onFile(file) {
  loading.value = true
  try { report.value = await uploadResume(file, jd.value); ElMessage.success('文件诊断完成'); loadHistory() }
  catch (e) { ElMessage.error(errMsg(e)) } finally { loading.value = false }
  return false
}
</script>
