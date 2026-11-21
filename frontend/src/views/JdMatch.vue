<template>
  <div class="page">
    <h2>JD 匹配</h2>
    <p class="desc">粘贴岗位 JD 与你的简历，算匹配度，看看缺哪些技能、怎么补。</p>
    <el-card class="card">
      <el-input v-model="jd" type="textarea" :rows="6" placeholder="粘贴 JD 文本（至少 20 字）…" />
      <el-input v-model="resume" type="textarea" :rows="6" placeholder="粘贴简历文本（至少 20 字）…" style="margin-top:12px" />
      <div style="margin-top:12px">
        <el-button type="primary" :loading="loading" @click="run">计算匹配度</el-button>
        <el-button @click="fillSample">填入示例</el-button>
      </div>
    </el-card>
    <el-card v-if="result" class="card">
      <div class="row" style="align-items:center">
        <div><div class="muted">匹配度</div><div class="score">{{ result.match_score }}<span style="font-size:16px"> / 100</span></div></div>
        <el-progress :percentage="result.match_score" :status="result.match_score >= 70 ? 'success' : 'warning'" style="flex:1" />
      </div>
      <p><b>总结：</b>{{ result.summary }}</p>
      <h4>JD 要求技能</h4><el-tag v-for="x in result.jd_skills" :key="x" style="margin:0 6px 6px 0">{{ x }}</el-tag>
      <h4>已匹配</h4><el-tag v-for="x in result.matched" :key="x" type="success" style="margin:0 6px 6px 0">{{ x }}</el-tag>
      <h4>缺失</h4><el-tag v-for="x in result.missing" :key="x" type="danger" style="margin:0 6px 6px 0">{{ x }}</el-tag>
      <h4>建议</h4><ul><li v-for="x in result.suggestions" :key="x">{{ x }}</li></ul>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { matchJd, errMsg, SAMPLE_RESUME, SAMPLE_JD } from '../api/client'
const jd = ref('')
const resume = ref('')
const result = ref(null)
const loading = ref(false)
function fillSample() { jd.value = SAMPLE_JD; resume.value = SAMPLE_RESUME }
async function run() {
  if (jd.value.trim().length < 20 || resume.value.trim().length < 20) return ElMessage.warning('JD 和简历各至少 20 字')
  loading.value = true
  try { result.value = await matchJd(jd.value, resume.value) }
  catch (e) { ElMessage.error(errMsg(e)) } finally { loading.value = false }
}
</script>
