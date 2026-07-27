<script setup lang="ts">
import type { ChatMessage } from "@/types";
import Timeline from "./Timeline.vue";
import ResultTable from "./ResultTable.vue";
import { User, Close } from "@element-plus/icons-vue";

/**
 * 聊天消息气泡组件
 * 展示用户消息和智能体消息
 */
defineProps<{
  message: ChatMessage;
}>();
</script>

<template>
  <!-- 用户消息 -->
  <div v-if="message.role === 'user'" class="message-row role-user">
    <div class="user-row">
      <div class="user-bubble">
        <span>{{ message.query }}</span>
      </div>
      <div class="avatar user-avatar">
        <User :size="18" />
      </div>
    </div>
  </div>

  <!-- 智能体消息 -->
  <div v-else class="message-row role-assistant">
    <div class="assistant-row">
      <div class="avatar assistant-avatar">
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        >
          <path d="M12 20h9"></path>
          <path
            d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"
          ></path>
        </svg>
      </div>
      <div class="assistant-content">
        <!-- 执行流程 -->
        <Timeline :steps="message.progressSteps" />

        <!-- 查询结果 -->
        <ResultTable
          v-if="message.finalResult.length > 0"
          :data="message.finalResult"
        />

        <!-- 错误信息 -->
        <div v-if="message.errorMessage" class="message-error">
          <Close :size="14" />
          <span>{{ message.errorMessage }}</span>
        </div>

        <!-- 状态指示器 -->
        <div v-if="message.status === 'loading'" class="loading-indicator">
          <svg
            class="spin"
            xmlns="http://www.w3.org/2000/svg"
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <circle cx="12" cy="12" r="10" stroke="var(--border)" />
            <path
              d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M6.34 17.66l-2.83-2.83M19.07 4.93l-2.83-2.83"
            />
          </svg>
          <span>正在处理中...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-row {
  margin-bottom: 24px;
}

/* 用户消息 */
.user-row {
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  gap: 12px;
}

.user-bubble {
  max-width: 75%;
  padding: 14px 18px;
  background: var(--primary-gradient);
  color: #fff;
  border-radius: var(--radius-lg) var(--radius-lg) var(--radius-sm)
    var(--radius-lg);
  font-size: 14px;
  line-height: 1.6;
  word-break: break-word;
  box-shadow: 0 6px 16px rgb(99 102 241 / 0.3);
  transition: transform var(--transition-fast);
}

.user-bubble:hover {
  transform: scale(1.01);
}

/* 智能体消息 */
.assistant-row {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  color: #fff;
  transition: transform var(--transition-normal);
}

.avatar:hover {
  transform: scale(1.05);
}

.assistant-avatar {
  background: var(--primary-gradient);
  box-shadow: var(--shadow-primary);
}

.user-avatar {
  background: linear-gradient(135deg, #64748b, #475569);
  box-shadow: 0 4px 12px rgb(100 116 139 / 0.3);
}

.assistant-content {
  flex: 1;
  min-width: 0;
  background: var(--bg-card);
  border: 1.5px solid var(--border);
  border-radius: var(--radius-sm) var(--radius-lg) var(--radius-lg)
    var(--radius-lg);
  padding: 22px 24px;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-normal);
}

.assistant-content:hover {
  box-shadow: var(--shadow-lg);
}

/* 消息内错误 */
.message-error {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
  padding: 12px 16px;
  background: rgb(239 68 68 / 0.06);
  border: 1px solid rgb(239 68 68 / 0.15);
  border-radius: var(--radius-md);
  color: var(--error);
  font-size: 13px;
  font-weight: 500;
}

/* 加载指示器 */
.loading-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 18px;
  padding: 12px 16px;
  background: rgb(99 102 241 / 0.06);
  border: 1px solid rgb(99 102 241 / 0.15);
  border-radius: var(--radius-md);
  color: var(--primary);
  font-size: 13px;
  font-weight: 500;
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
