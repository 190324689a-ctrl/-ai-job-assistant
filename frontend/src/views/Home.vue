<template>
  <div class="page">
    <h2>你好，小丁 👋</h2>
    <p class="desc">AI 求职助手：简历诊断、JD 匹配、知识库问答、模拟面试、AI 对话都在这里。先从简历诊断开始，或直接去模拟面试练一轮。</p>
    <div class="row">
      <el-card v-for="c in cards" :key="c.to" class="card" shadow="hover" style="cursor:pointer" @click="$router.push(c.to)">
        <h3>{{ c.icon }} {{ c.title }}</h3>
        <p class="muted">{{ c.desc }}</p>
        <el-button type="primary" text>进入 →</el-button>
      </el-card>
    </div>
    <el-alert title="Mock 模式说明：没有配置 LLM_API_KEY 时，后端用内置 Mock 回答演示全流程；配置 DeepSeek / OpenAI 兼容 Key 后即走真实模型。" type="info" show-icon :closable="false" />
  </div>
</template>
<script setup>
const cards = [
  { to: '/resume', icon: '📄', title: '简历诊断', desc: '粘贴简历 + 目标 JD，打分并给出亮点、问题与改进建议。' },
  { to: '/jd', icon: '🎯', title: 'JD 匹配', desc: '粘贴 JD 与简历，算匹配度，列出已匹配与缺失技能。' },
  { to: '/rag', icon: '📚', title: '知识库问答', desc: '上传面试笔记 / 面经文档，基于知识库回答并给出引用来源。' },
  { to: '/interview', icon: '🎤', title: '模拟面试', desc: '选方向开始 5 轮面试，答完出评分报告与改进建议。' },
  { to: '/chat', icon: '💬', title: 'AI 对话', desc: '自由问答：改简历、写自我介绍、准备面试问题都可以问。' },
]
</script>
