import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import './styles/global.css'
import {
  getUsers,
  findUserByName,
  addUser,
  removeUserById,
  resetMockUsers
} from './mock/user'

const app = createApp(App)

// 全局注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(ElementPlus)
app.use(router)

app.mount('#app')

// 开发环境暴露 mock 数据管理接口，便于在控制台查看 / 修改模拟数据
// 用法示例：
//   $mock.list()          列出全部模拟用户
//   $mock.find('admin')   按用户名查询
//   $mock.add({...})      追加用户
//   $mock.remove(2)       按 id 删除
//   $mock.reset()         恢复种子数据
if (import.meta.env.DEV) {
  window.$mock = {
    list: getUsers,
    find: findUserByName,
    add: addUser,
    remove: removeUserById,
    reset: resetMockUsers
  }
  // 开发友好提示
  console.info(
    '%c[mock] 用户模拟数据已加载。控制台可用 $mock.list() / $mock.find(name) / $mock.add({...}) / $mock.remove(id) / $mock.reset()',
    'color:#67c23a'
  )
}
