import { fetchEventSource } from '@microsoft/fetch-event-source';
import type { SSEMessage, QueryRequest } from '@/types';

/**
 * 发送查询请求（SSE 流式响应）
 * @param data - 查询参数
 * @param onMessage - 消息回调
 * @param onError - 错误回调
 * @param onClose - 关闭回调
 */
export async function queryStream(
  data: QueryRequest,
  onMessage: (message: SSEMessage) => void,
  onError?: (error: Error) => void,
  onClose?: () => void
): Promise<void> {
  try {
    await fetchEventSource('/api/query', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      async onmessage(event) {
        if (!event.data) return;
        try {
          const message: SSEMessage = JSON.parse(event.data);
          onMessage(message);
        } catch (e) {
          console.error('解析 SSE 消息失败:', e);
        }
      },
      onclose() {
        onClose?.();
      },
      onerror(error) {
        onError?.(error);
        throw error;
      },
    });
  } catch (err) {
    onError?.(err instanceof Error ? err : new Error(String(err)));
  }
}
