/**
 * 执行流程步骤状态
 */
export type StepStatus = 'pending' | 'running' | 'success' | 'error';

/**
 * 执行流程步骤
 */
export interface ProgressStep {
  step: string;
  status: StepStatus;
}

/**
 * SSE 消息类型
 */
export type SSEMessageType = 'progress' | 'result' | 'error';

/**
 * SSE 消息
 */
export interface SSEMessage {
  type: SSEMessageType;
  step?: string;
  status?: 'running' | 'success' | 'error';
  data?: any[];
  message?: string;
}

/**
 * 消息角色
 */
export type MessageRole = 'user' | 'assistant';

/**
 * 消息状态
 */
export type MessageStatus = 'loading' | 'success' | 'error';

/**
 * 聊天消息
 */
export interface ChatMessage {
  id: string;
  role: MessageRole;
  query: string;
  progressSteps: ProgressStep[];
  finalResult: any[];
  errorMessage: string;
  status: MessageStatus;
  createdAt: number;
}

/**
 * 会话状态
 */
export type ConversationStatus = 'loading' | 'success' | 'error';

/**
 * 会话
 */
export interface Conversation {
  id: string;
  messages: ChatMessage[];
  title: string;
  status: ConversationStatus;
  createdAt: number;
}

/**
 * 查询请求参数
 */
export interface QueryRequest {
  query: string;
}

/**
 * 查询结果列
 */
export interface ResultColumn {
  prop: string;
  label: string;
}

/**
 * 示例问题
 */
export interface SampleQuestion {
  id: string;
  text: string;
}
