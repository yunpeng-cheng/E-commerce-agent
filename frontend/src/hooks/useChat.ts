import { ref, computed, watch, nextTick } from 'vue';
import type { ChatMessage, Conversation, ProgressStep, SSEMessage } from '@/types';
import { queryStream } from '@/api/query';
import { generateId } from '@/utils';

/**
 * 执行流程步骤名称列表
 */
const STEP_NAMES = [
  '抽取关键词',
  '召回字段信息',
  '召回指标信息',
  '召回字段取值',
  '合并召回信息',
  '过滤指标信息',
  '过滤表信息',
  '增加额外上下文',
  '生成SQL',
  '校验SQL',
  '校正SQL',
  '执行SQL',
];

/**
 * 创建初始步骤列表
 * @returns 步骤列表
 */
function createSteps(): ProgressStep[] {
  return STEP_NAMES.map((name) => ({ step: name, status: 'pending' }));
}

/**
 * 聊天状态管理 Hook
 * 处理会话管理、消息发送、SSE 流式响应
 */
export function useChat() {
  /** 是否正在加载 */
  const isLoading = ref(false);

  /** 当前消息列表 */
  const messages = ref<ChatMessage[]>([]);

  /** 会话列表 */
  const conversations = ref<Conversation[]>([]);

  /** 当前会话 ID */
  const currentConversationId = ref<string>('');

  /** 消息列表引用（用于滚动） */
  const messageListRef = ref<HTMLElement | null>(null);

  /**
   * 是否有消息
   */
  const hasMessages = computed(() => messages.value.length > 0);

  /**
   * 同步消息到当前会话
   * @param conv - 会话对象
   */
  function syncMessages(conv: Conversation): void {
    messages.value = conv.messages.map((m) => ({
      ...m,
      progressSteps: [...m.progressSteps],
      finalResult: [...m.finalResult],
    }));
  }

  /**
   * 创建新会话
   */
  function newConversation(): void {
    currentConversationId.value = '';
    messages.value = [];
    isLoading.value = false;
  }

  /**
   * 选择会话
   * @param id - 会话 ID
   */
  function selectConversation(id: string): void {
    const conv = conversations.value.find((c) => c.id === id);
    if (!conv) return;
    currentConversationId.value = conv.id;
    syncMessages(conv);
    isLoading.value = false;
    scrollToBottom();
  }

  /**
   * 确保当前会话存在
   * @returns 当前会话对象
   */
  function ensureConversation(): Conversation {
    if (!currentConversationId.value) {
      const conv: Conversation = {
        id: generateId(),
        messages: [],
        title: '',
        status: 'loading',
        createdAt: Date.now(),
      };
      conversations.value.unshift(conv);
      currentConversationId.value = conv.id;
    }
    return conversations.value.find((c) => c.id === currentConversationId.value)!;
  }

  /**
   * 滚动到底部
   */
  async function scrollToBottom(): Promise<void> {
    await nextTick();
    if (messageListRef.value) {
      messageListRef.value.scrollTop = messageListRef.value.scrollHeight;
    }
  }

  /**
   * 监听消息数量变化，自动滚动
   */
  watch(
    () => messages.value.length,
    () => {
      scrollToBottom();
    }
  );

  /**
   * 发送查询
   * @param queryText - 查询文本
   */
  async function query(queryText: string): Promise<void> {
    const conv = ensureConversation();

    // 设置会话标题（首次查询时）
    if (conv.title === '') {
      conv.title = queryText;
    }

    // 添加用户消息
    const userMsg: ChatMessage = {
      id: generateId(),
      role: 'user',
      query: queryText,
      progressSteps: [],
      finalResult: [],
      errorMessage: '',
      status: 'success',
      createdAt: Date.now(),
    };
    conv.messages.push(userMsg);

    // 添加助手消息（占位）
    const assistantMsg: ChatMessage = {
      id: generateId(),
      role: 'assistant',
      query: queryText,
      progressSteps: createSteps(),
      finalResult: [],
      errorMessage: '',
      status: 'loading',
      createdAt: Date.now(),
    };
    conv.messages.push(assistantMsg);
    syncMessages(conv);

    isLoading.value = true;

    const refresh = () => syncMessages(conv);

    await queryStream(
      { query: queryText },
      (message: SSEMessage) => {
        switch (message.type) {
          case 'progress': {
            const idx = assistantMsg.progressSteps.findIndex((s) => s.step === message.step);
            if (idx !== -1 && message.status) {
              assistantMsg.progressSteps[idx].status = message.status;
            }
            break;
          }
          case 'result': {
            assistantMsg.finalResult = message.data || [];
            break;
          }
          case 'error': {
            assistantMsg.errorMessage = message.message || '未知错误';
            break;
          }
        }
        refresh();
      },
      (error: Error) => {
        isLoading.value = false;
        assistantMsg.errorMessage = error.message || '请求失败';
        assistantMsg.status = 'error';
        conv.status = 'error';
        refresh();
      },
      () => {
        isLoading.value = false;
        assistantMsg.status = assistantMsg.errorMessage ? 'error' : 'success';
        conv.status = assistantMsg.status;
        refresh();
      }
    );
  }

  return {
    isLoading,
    messages,
    conversations,
    currentConversationId,
    messageListRef,
    hasMessages,
    query,
    newConversation,
    selectConversation,
  };
}
