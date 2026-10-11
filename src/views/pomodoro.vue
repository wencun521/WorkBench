<template>
  <div class="pomodoro-page">
    <el-card class="pomodoro-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span>番茄钟</span>
          <span class="header-tip">专注 25 分钟 · 休息 5 分钟</span>
        </div>
      </template>

      <div class="pomodoro-layout">
        <!-- 左：圆环计时器 -->
        <div class="timer-block">
          <!-- 模式切换 -->
          <div class="mode-switch">
            <button
              class="mode-btn"
              :class="{ active: mode === 'focus' }"
              @click="switchMode('focus')"
            >专注</button>
            <button
              class="mode-btn break"
              :class="{ active: mode === 'break' }"
              @click="switchMode('break')"
            >休息</button>
          </div>

          <!-- SVG 圆环 -->
          <div class="ring-wrap">
            <svg viewBox="0 0 220 220" class="ring-svg">
              <circle class="ring-track" cx="110" cy="110" r="96" />
              <circle
                class="ring-progress"
                :class="mode"
                cx="110"
                cy="110"
                r="96"
                :style="{ strokeDashoffset: ringOffset }"
              />
            </svg>
            <div class="ring-center" :class="mode">
              <div class="time-text">{{ timeText }}</div>
              <div class="mode-text">{{ mode === 'focus' ? '专注中' : '休息中' }}</div>
            </div>
          </div>

          <!-- 控制按钮 -->
          <div class="controls">
            <el-button type="primary" round size="large" @click="toggleRun">
              {{ isRunning ? '暂停' : '开始' }}
            </el-button>
            <el-button round size="large" @click="resetTimer">重置</el-button>
          </div>

          <!-- 关联待办（仅专注模式显示） -->
          <div v-if="mode === 'focus'" class="todo-link">
            <span class="todo-link-label">关联待办：</span>
            <el-select
              v-model="linkedTodoId"
              clearable
              placeholder="不关联"
              size="small"
              style="width: 220px"
            >
              <el-option
                v-for="t in todoOptions"
                :key="t.id"
                :label="t.title"
                :value="t.id"
              />
            </el-select>
          </div>
        </div>

        <!-- 右：统计与记录 -->
        <el-card class="summary-card" shadow="never">
          <template #header>
            <div class="summary-header">
              <span>专注记录</span>
              <span class="today-count">今日 <b>{{ todayCount }}</b> 个</span>
            </div>
          </template>
          <div v-loading="loading" class="record-list">
            <p v-if="!loading && recent.length === 0" class="record-empty">还没有专注记录，开始第一个番茄吧</p>
            <div v-for="s in recent" :key="s.id" class="record-item">
              <el-icon class="record-icon" :size="14"><Timer /></el-icon>
              <span class="record-title">{{ s.todoTitle || '自由专注' }}</span>
              <span class="record-duration">{{ s.durationMinutes }} 分钟</span>
            </div>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { Timer } from '@element-plus/icons-vue'
import { usePomodoro } from '@/composables/usePomodoro'

/* 计时器状态为模块级单例：切换页面/刷新后进度不丢失（见 composables/usePomodoro.js） */
const {
  mode,
  timeText,
  ringOffset,
  isRunning,
  todayCount,
  recent,
  linkedTodoId,
  todoOptions,
  loading,
  toggleRun,
  resetTimer,
  switchMode
} = usePomodoro()
</script>

<style scoped>
.pomodoro-page {
  max-width: 900px;
  margin: 0 auto;
}
.pomodoro-card {
  border-radius: 12px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-header span {
  font-size: 18px;
  font-weight: 600;
  color: #1f2329;
}
.header-tip {
  font-size: 12px;
  font-weight: 400;
  color: #c0c4cc;
}
.pomodoro-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(260px, 1fr);
  gap: 24px;
  align-items: start;
}
@media (max-width: 820px) {
  .pomodoro-layout {
    grid-template-columns: 1fr;
  }
}
/* 计时器 */
.timer-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  padding: 8px 0;
}
.mode-switch {
  display: flex;
  gap: 8px;
  background: #f5f6f8;
  border-radius: 999px;
  padding: 4px;
}
.mode-btn {
  border: none;
  background: transparent;
  padding: 6px 20px;
  border-radius: 999px;
  font-size: 13px;
  color: #909399;
  cursor: pointer;
  transition: all 0.2s;
}
.mode-btn.active {
  background: #409eff;
  color: #fff;
}
.mode-btn.break.active {
  background: #67c23a;
}
.ring-wrap {
  position: relative;
  width: 240px;
  height: 240px;
}
.ring-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}
.ring-track {
  fill: none;
  stroke: #f0f1f4;
  stroke-width: 10;
}
.ring-progress {
  fill: none;
  stroke: #409eff;
  stroke-width: 10;
  stroke-linecap: round;
  stroke-dasharray: 603;
  transition: stroke-dashoffset 1s linear;
}
.ring-progress.break {
  stroke: #67c23a;
}
.ring-center {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.time-text {
  font-size: 40px;
  font-weight: 600;
  color: #1f2329;
  font-variant-numeric: tabular-nums;
}
.mode-text {
  font-size: 13px;
  color: #909399;
}
.ring-center.break .mode-text {
  color: #67c23a;
}
.controls {
  display: flex;
  gap: 12px;
}
.todo-link {
  display: flex;
  align-items: center;
  gap: 8px;
}
.todo-link-label {
  font-size: 13px;
  color: #909399;
}
/* 记录 */
.summary-card {
  border-radius: 12px;
  border: 1px solid #e8e9eb;
}
.summary-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.summary-header span {
  font-size: 15px;
  font-weight: 600;
  color: #1f2329;
}
.today-count b {
  color: #409eff;
  font-size: 18px;
}
.record-list {
  min-height: 120px;
}
.record-empty {
  margin: 8px 0;
  font-size: 13px;
  color: #c0c4cc;
  text-align: center;
}
.record-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 9px 4px;
  border-bottom: 1px solid #f0f0f0;
}
.record-item:last-child {
  border-bottom: none;
}
.record-icon {
  color: #409eff;
  flex-shrink: 0;
}
.record-title {
  flex: 1;
  font-size: 13px;
  color: #303133;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.record-duration {
  font-size: 12px;
  color: #c0c4cc;
  flex-shrink: 0;
}
</style>
