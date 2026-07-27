<script setup lang="ts">
import type { ProgressStep } from "@/types";
import { Check, Close, Loading } from "@element-plus/icons-vue";

/**
 * 执行流程时间线组件
 * 用于展示 LangGraph 各节点的执行状态
 */
defineProps<{
  steps: ProgressStep[];
}>();

/**
 * 获取已完成步骤数量
 * @param steps - 步骤列表
 * @returns 已完成数量
 */
function getCompletedCount(steps: ProgressStep[]): number {
  return steps.filter((s) => s.status === "success").length;
}

/**
 * 获取步骤状态描述
 * @param status - 步骤状态
 * @returns 状态描述文本
 */
function getStatusDesc(status: string): string {
  switch (status) {
    case "success":
      return "已完成";
    case "running":
      return "执行中...";
    case "error":
      return "执行失败";
    default:
      return "等待执行";
  }
}
</script>

<template>
  <div class="timeline-wrapper">
    <div class="section-header">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="15"
        height="15"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <polyline points="23 4 23 10 17 10"></polyline>
        <polyline points="1 20 1 14 7 14"></polyline>
        <path
          d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"
        ></path>
      </svg>
      <span class="section-title-text">执行流程</span>
      <span class="progress-count">
        {{ getCompletedCount(steps) }} / {{ steps.length }} 步
      </span>
    </div>

    <div class="timeline">
      <div
        v-for="(step, index) in steps"
        :key="index"
        class="timeline-item"
        :class="`status-${step.status}`"
      >
        <div class="timeline-rail">
          <div class="timeline-dot">
            <Check v-if="step.status === 'success'" :size="13" />
            <Close v-else-if="step.status === 'error'" :size="13" />
            <Loading
              v-else-if="step.status === 'running'"
              :size="13"
              class="spin"
            />
            <span v-else class="dot-index">{{ index + 1 }}</span>
          </div>
          <div
            v-if="index < steps.length - 1"
            class="timeline-line"
            :class="{ filled: step.status === 'success' }"
          ></div>
        </div>
        <div class="timeline-content">
          <div class="timeline-title">{{ step.step }}</div>
          <div class="timeline-desc">{{ getStatusDesc(step.status) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.timeline-wrapper {
  margin-bottom: 20px;
  padding: 18px;
  background: var(--bg-page);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  color: var(--text-primary);
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border);
}

.section-header svg {
  color: var(--primary);
  font-size: 18px;
}

.section-title-text {
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 0.3px;
}

.progress-count {
  margin-left: auto;
  padding: 4px 12px;
  background: var(--bg-card);
  color: var(--primary);
  border-radius: var(--radius-full);
  font-size: 12px;
  font-weight: 600;
  border: 1px solid rgb(99 102 241 / 0.2);
}

.timeline-item {
  display: flex;
  gap: 14px;
  min-height: 40px;
  padding: 6px 0;
}

.timeline-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex-shrink: 0;
  width: 26px;
}

.timeline-dot {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  border: 2.5px solid var(--border);
  background: var(--bg-card);
  color: var(--text-tertiary);
  transition: all var(--transition-normal);
  z-index: 1;
  flex-shrink: 0;
}

.status-success .timeline-dot {
  background: var(--success);
  border-color: var(--success);
  color: #fff;
  box-shadow: 0 0 0 5px rgb(16 185 129 / 0.15);
}

.status-running .timeline-dot {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
  box-shadow: 0 0 0 5px rgb(99 102 241 / 0.15);
  animation: pulse-dot 2s ease-in-out infinite;
}

.status-error .timeline-dot {
  background: var(--error);
  border-color: var(--error);
  color: #fff;
  box-shadow: 0 0 0 5px rgb(239 68 68 / 0.15);
}

@keyframes pulse-dot {
  0%,
  100% {
    box-shadow: 0 0 0 5px rgb(99 102 241 / 0.15);
  }
  50% {
    box-shadow: 0 0 0 10px rgb(99 102 241 / 0.05);
  }
}

.timeline-line {
  width: 3px;
  flex: 1;
  background: var(--border-light);
  margin: 4px 0;
  transition: all var(--transition-normal);
  border-radius: var(--radius-full);
}

.timeline-line.filled {
  background: var(--success);
  box-shadow: 0 0 4px rgb(16 185 129 / 0.3);
}

.timeline-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding-bottom: 12px;
  flex: 1;
}

.timeline-title {
  font-size: 13px;
  font-weight: 600;
  transition: color var(--transition-fast);
}

.status-success .timeline-title {
  color: var(--success);
}

.status-running .timeline-title {
  color: var(--primary);
}

.status-error .timeline-title {
  color: var(--error);
}

.timeline-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 3px;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
