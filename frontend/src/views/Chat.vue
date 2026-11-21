<template>
  <div class="page">
    <h2>AI 对话</h2>
    <p class="desc">问求职相关问题：改简历、写自我介绍、准备面试回答、分析 JD 都可以。</p>
    <el-card class="card">
      <div v-if="!messages.length" class="muted">还没有对话，试试：“帮我写一段 AI 应用开发工程师的自我介绍”。</div>
      <div v-for="(m, i) in messages" :key="i" style="margin-bottom:12px">
        <el-tag :type="m.role === 'user' ? 'primary' : 'success'">{{ m.role === 'user' ? '我' : 'AI' }}</el-tag>
        <pre class="answer" style="margin-top:6px">{{ m.content }}</pre>
      </div>
      <el-input v-model="input" type="textarea" :rows="3" placeholder="输入你的问题…" @keyup.enter.ctrl="send" />
      <div style="margin-top:12px">
        <el-button type="primary" :loading="loading" @click="send">发送</el-button>
        <el-button @click="messages = []; conversationId = null">新对话</el-button>
        <span class="muted">Ctrl+Enter 发送</span>
      </div>
    </el-card>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { chat as chatApi, errMsg } from '../api/client'
const input = ref('')
const messages = ref([])
const conversationId = ref(null)
const loading = ref(false)
async function send() {
  const q = input.value.trim()
  if (!q || loading.value) return
  messages.value.push({ role: 'user', content: q })
  input.value = ''
  loading.value = true
  try {
    const r = await chatApi(q, conversationId.value)
    conversationId.value = r.conversation_id
    messages.value.push({ role: 'assistant', content: r.reply })
  } catch (e) { ElMessage.error(errMsg(e)) } finally { loading.value = false }
}
</script>
