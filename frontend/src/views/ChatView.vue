<script setup lang="ts">
import { ref } from "vue";
import { useChat } from "@/hooks/useChat";
import ChatBubble from "@/components/ChatBubble.vue";
import {
  Plus,
  ChatDotRound,
  Promotion,
  Search,
  Refresh,
  Document,
  MagicStick,
  Check,
  Close,
  Loading,
} from "@element-plus/icons-vue";
import { formatTime } from "@/utils";
import { ElMessage } from "element-plus";

/**
 * 聊天主页面组件
 * 包含侧边栏、消息区、输入区
 */
const {
  isLoading,
  messages,
  conversations,
  currentConversationId,
  messageListRef,
  hasMessages,
  query,
  newConversation,
  selectConversation,
} = useChat();

/**
 * 输入框内容
 */
const inputQuery = ref("");

/**
 * 示例问题列表
 */
const sampleQuestions = [
  "统计 2025 年第一季度各大区的 GMV，并按 GMV 从高到低排序",
  "统计 2025 年 3 月各商品品类的销量和销售额",
  "查询华东地区 2025 年第一季度销售额最高的前 5 个商品",
  "按会员等级统计 2025 年第一季度的订单数和销售额",
];

/**
 * 处理发送
 */
async function handleSubmit(): Promise<void> {
  if (!inputQuery.value.trim()) {
    ElMessage.warning("请输入问题");
    return;
  }
  const q = inputQuery.value.trim();
  inputQuery.value = "";
  await query(q);
}

/**
 * 处理示例问题点击
 * @param question - 示例问题
 */
function handleSampleClick(question: string): void {
  inputQuery.value = question;
  handleSubmit();
}

/**
 * 处理键盘事件
 * @param e - 键盘事件
 */
function handleKeydown(e: KeyboardEvent): void {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    handleSubmit();
  }
}

/**
 * 处理新建会话
 */
function handleNewChat(): void {
  newConversation();
  inputQuery.value = "";
}

/**
 * 处理选择会话
 * @param id - 会话 ID
 */
function handleSelectConv(id: string): void {
  selectConversation(id);
}

/**
 * 获取状态图标组件
 * @param status - 会话状态
 * @returns 图标组件
 */
function getStatusIcon(status: string) {
  switch (status) {
    case "success":
      return Check;
    case "error":
      return Close;
    case "loading":
      return Loading;
    default:
      return ChatDotRound;
  }
}
</script>

<template>
  <div class="app-container">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">
            <ChatDotRound :size="18" />
          </div>
          <span class="logo-text">电商问数</span>
        </div>
        <button class="new-chat-btn" @click="handleNewChat" title="新建会话">
          <Plus :size="12" />
        </button>
      </div>

      <div class="history-list">
        <div class="history-title">
          <span>会话历史</span>
          <span class="history-count">{{ conversations.length }}</span>
        </div>
        <div
          v-for="conv in conversations"
          :key="conv.id"
          class="history-item"
          :class="{ active: conv.id === currentConversationId }"
          @click="handleSelectConv(conv.id)"
        >
          <div class="history-status">
            <component :is="getStatusIcon(conv.status)" :size="14" />
          </div>
          <div class="history-content">
            <div class="history-query">{{ conv.title || "新会话" }}</div>
            <div class="history-meta">
              <span>{{ formatTime(conv.createdAt) }}</span>
              <span class="meta-divider">·</span>
              <span>{{ conv.messages.length }} 条对话</span>
            </div>
          </div>
        </div>
      </div>

      <div class="sidebar-footer">
        <div class="footer-text">
          <span class="footer-label">API</span>
          <span class="footer-value">Vite / api proxy</span>
        </div>
        <div class="footer-text">
          <span class="footer-label">完成</span>
          <span class="footer-value">0</span>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <main class="content-area">
      <!-- 欢迎页面 -->
      <div v-if="!hasMessages" class="welcome-page">
        <div class="welcome-card">
          <div class="welcome-glow"></div>
          <div class="agent-badge">
            <MagicStick :size="14" />
            <span>Shopkeeper Agent</span>
          </div>
          <h1 class="welcome-title">
            <span class="title-gradient">电商数据问数</span>
          </h1>
          <p class="welcome-desc">
            基于 LangGraph 工作流的自然语言转 SQL 智能体，支持语义检索、SQL
            自动生成校验与执行
          </p>

          <div class="feature-cards">
            <div class="feature-card">
              <div class="feature-icon-box blue">
                <Search :size="22" />
              </div>
              <div class="feature-name">混合检索</div>
              <div class="feature-desc">向量 + 全文</div>
            </div>
            <div class="feature-card">
              <div class="feature-icon-box purple">
                <Refresh :size="22" />
              </div>
              <div class="feature-name">SQL 闭环</div>
              <div class="feature-desc">生成校验执行</div>
            </div>
            <div class="feature-card">
              <div class="feature-icon-box green">
                <Document :size="22" />
              </div>
              <div class="feature-name">电商数仓</div>
              <div class="feature-desc">业务指标全</div>
            </div>
          </div>

          <div class="quick-questions">
            <button
              v-for="(question, index) in sampleQuestions"
              :key="index"
              class="quick-question-btn"
              @click="handleSampleClick(question)"
            >
              <Promotion :size="13" />
              <span>{{ question }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 对话容器 -->
      <div v-else class="chat-container" ref="messageListRef">
        <div class="chat-inner">
          <ChatBubble v-for="msg in messages" :key="msg.id" :message="msg" />
        </div>
      </div>

      <!-- 输入区 -->
      <div class="input-area">
        <div class="input-wrapper">
          <textarea
            v-model="inputQuery"
            class="query-input"
            placeholder="问一个电商数据问题..."
            rows="1"
            :disabled="isLoading"
            @keydown="handleKeydown"
          ></textarea>
          <button
            class="send-btn"
            :disabled="!inputQuery.trim() || isLoading"
            @click="handleSubmit"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
        <div class="input-tips">
          <span v-if="isLoading">正在查询中...</span>
          <span v-else>按 Enter 发送</span>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
/* ============ 整体布局 ============ */
.app-container {
  display: flex;
  height: 100vh;
  background: var(--bg-page);
  overflow: hidden;
}

/* ============ 侧边栏 ============ */
.sidebar {
  width: 280px;
  background: var(--bg-sidebar);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
  transition: all var(--transition-normal);
}

.sidebar-header {
  margin-bottom: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding: 8px;
  border-radius: var(--radius-lg);
  transition: background var(--transition-fast);
}

.logo:hover {
  background: var(--bg-hover);
}

.logo-icon {
  width: 34px;
  height: 34px;
  background: var(--primary-gradient);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  box-shadow: var(--shadow-primary);
  transition: transform var(--transition-normal);
}

.logo:hover .logo-icon {
  transform: scale(1.05);
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.5px;
}

.new-chat-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.new-chat-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgb(99 102 241 / 0.06);
}

.history-list {
  flex: 1;
  overflow-y: auto;
}

.history-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 6px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-secondary);
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
}

.history-count {
  padding: 2px 10px;
  background: var(--bg-hover);
  border-radius: var(--radius-full);
  font-size: 11px;
  font-weight: 600;
}

.history-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 11px 13px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-bottom: 3px;
  border: 1px solid transparent;
}

.history-item:hover {
  background: var(--bg-hover);
}

.history-item.active {
  background: linear-gradient(
    135deg,
    rgb(99 102 241 / 0.1),
    rgb(139 92 246 / 0.08)
  );
  border-color: rgb(99 102 241 / 0.25);
}

.history-status {
  margin-top: 2px;
  color: var(--text-tertiary);
  font-size: 10px;
  transition: color var(--transition-fast);
}

.history-item.active .history-status {
  color: var(--primary);
}

.history-content {
  flex: 1;
  min-width: 0;
}

.history-query {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.history-item.active .history-query {
  color: var(--primary);
  font-weight: 600;
}

.history-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
  font-size: 11px;
  color: var(--text-tertiary);
}

.meta-divider {
  color: var(--border);
}

.sidebar-footer {
  padding-top: 14px;
  border-top: 1px solid var(--border);
  margin-top: 12px;
}

.footer-text {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  font-size: 11px;
}

.footer-label {
  color: var(--text-tertiary);
}

.footer-value {
  color: var(--text-secondary);
  font-weight: 600;
}

/* ============ 主内容区 ============ */
.content-area {
  flex: 1;
  padding: 28px 32px;
  overflow: hidden;
  position: relative;
  display: flex;
  flex-direction: column;
}

/* ============ 欢迎页面 ============ */
.welcome-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 500px;
  overflow-y: auto;
}

.welcome-card {
  text-align: center;
  max-width: 680px;
  padding: 56px 48px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-xl);
  position: relative;
  overflow: hidden;
}

.welcome-card::before {
  content: "";
  position: absolute;
  top: -100px;
  left: -100px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgb(99 102 241 / 0.08), transparent);
  border-radius: 50%;
}

.welcome-card::after {
  content: "";
  position: absolute;
  bottom: -100px;
  right: -100px;
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgb(139 92 246 / 0.06), transparent);
  border-radius: 50%;
}

.welcome-glow {
  position: absolute;
  top: -60px;
  left: 50%;
  transform: translateX(-50%);
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, rgb(99 102 241 / 0.12), transparent);
  border-radius: 50%;
  z-index: 0;
}

.agent-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 16px;
  background: rgb(99 102 241 / 0.08);
  border-radius: var(--radius-full);
  font-size: 12px;
  color: var(--primary);
  font-weight: 600;
  margin-bottom: 24px;
  z-index: 1;
  position: relative;
  border: 1px solid rgb(99 102 241 / 0.15);
}

.welcome-title {
  font-size: 40px;
  font-weight: 800;
  margin-bottom: 14px;
  z-index: 1;
  position: relative;
  letter-spacing: -0.5px;
}

.title-gradient {
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-desc {
  font-size: 15px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 36px;
  z-index: 1;
  position: relative;
  max-width: 480px;
  margin-left: auto;
  margin-right: auto;
}

.feature-cards {
  display: flex;
  gap: 18px;
  margin-bottom: 36px;
  z-index: 1;
  position: relative;
}

.feature-card {
  flex: 1;
  padding: 24px 20px;
  background: var(--bg-page);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary-gradient);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.feature-card:hover {
  border-color: rgb(99 102 241 / 0.3);
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-icon-box {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
  color: #fff;
  transition: transform var(--transition-normal);
}

.feature-card:hover .feature-icon-box {
  transform: scale(1.1);
}

.feature-icon-box.blue {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  box-shadow: 0 4px 14px rgb(59 130 246 / 0.3);
}

.feature-icon-box.purple {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  box-shadow: 0 4px 14px rgb(139 92 246 / 0.3);
}

.feature-icon-box.green {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 14px rgb(16 185 129 / 0.3);
}

.feature-name {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.feature-desc {
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.5;
}

.quick-questions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  z-index: 1;
  position: relative;
}

.quick-question-btn {
  padding: 14px 16px;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--text-secondary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all var(--transition-normal);
  text-align: center;
  line-height: 1.5;
}

.quick-question-btn:hover {
  border-color: var(--primary);
  color: var(--primary);
  background: rgb(99 102 241 / 0.05);
  box-shadow: var(--shadow-sm);
}

/* ============ 对话容器 ============ */
.chat-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.chat-inner {
  max-width: 900px;
  margin: 0 auto;
  padding: 8px 4px;
}

/* ============ 输入区 ============ */
.input-area {
  padding-top: 20px;
  padding-bottom: 24px;
  border-top: 1px solid var(--border);
  background: var(--bg-card);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.input-wrapper {
  display: flex;
  gap: 14px;
  max-width: 900px;
  margin: 0 auto;
  align-items: flex-end;
  padding: 0 8px;
}

.query-input {
  flex: 1;
  padding: 14px 18px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-lg);
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  outline: none;
  background: var(--bg-card);
  color: var(--text-primary);
  transition: all var(--transition-normal);
  min-height: 48px;
  max-height: 140px;
  box-shadow: var(--shadow-sm);
}

.query-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 4px rgb(99 102 241 / 0.1), var(--shadow-sm);
}

.query-input::placeholder {
  color: var(--text-tertiary);
}

.query-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.send-btn {
  padding: 14px 16px;
  background: var(--primary-gradient);
  border: none;
  border-radius: var(--radius-lg);
  color: #fff;
  cursor: pointer;
  transition: all var(--transition-normal);
  flex-shrink: 0;
  box-shadow: var(--shadow-primary);
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgb(99 102 241 / 0.4);
}

.send-btn:active:not(:disabled) {
  transform: translateY(-1px);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.input-tips {
  text-align: center;
  margin-top: 10px;
  font-size: 12px;
  color: var(--text-tertiary);
}

/* ============ 滚动条样式 ============ */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--border-light);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--border);
}
</style>
