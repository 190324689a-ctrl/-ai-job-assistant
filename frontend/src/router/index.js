import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Chat from '../views/Chat.vue'
import Resume from '../views/Resume.vue'
import Rag from '../views/Rag.vue'
import Interview from '../views/Interview.vue'
import JdMatch from '../views/JdMatch.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: Home },
    { path: '/chat', name: 'chat', component: Chat },
    { path: '/resume', name: 'resume', component: Resume },
    { path: '/rag', name: 'rag', component: Rag },
    { path: '/interview', name: 'interview', component: Interview },
    { path: '/jd', name: 'jd', component: JdMatch },
  ],
})
