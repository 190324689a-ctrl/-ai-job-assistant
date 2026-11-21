<template>
  <el-container class="layout">
    <el-header class="header">
      <router-link to="/" class="brand">🤖 AI 求职助手</router-link>
      <el-menu mode="horizontal" :default-active="$route.path" router class="nav">
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/chat">AI 对话</el-menu-item>
        <el-menu-item index="/resume">简历诊断</el-menu-item>
        <el-menu-item index="/jd">JD 匹配</el-menu-item>
        <el-menu-item index="/rag">知识库问答</el-menu-item>
        <el-menu-item index="/interview">模拟面试</el-menu-item>
      </el-menu>
      <el-tag :type="health?.mock_mode ? 'warning' : 'success'" class="health">
        {{ health ? (health.mock_mode ? 'Mock 模式' : `已接模型 ${health.model}`) : '后端未连接' }}
      </el-tag>
    </el-header>
    <el-main>
      <router-view />
    </el-main>
    <el-footer class="footer">
      面向深圳 AI 应用开发工程师求职 · 后端默认 Mock 模式，无 Key 也能跑；配置 LLM_API_KEY 后走真实模型。
    </el-footer>
  </el-container>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { health as healthApi } from './api/client'

const health = ref(null)
onMounted(async () => {
  try { health.value = await healthApi() } catch { health.value = null }
})
</script>

<style scoped>
.layout { min-height: 100vh; }
.header { display: flex; align-items: center; gap: 16px; border-bottom: 1px solid #e5e7eb; background: #fff; }
.brand { font-size: 20px; font-weight: 700; color: #111; text-decoration: none; white-space: nowrap; }
.nav { flex: 1; border-bottom: none; }
.health { white-space: nowrap; }
.footer { text-align: center; color: #909399; font-size: 13px; }
</style>
