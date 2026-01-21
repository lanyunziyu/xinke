<template>
  <div class="bg-white rounded-lg shadow-sm p-6 card-shadow">
    <div class="mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-2 flex items-center">
        <el-icon class="mr-2 text-primary-600">
          <ChatDotRound />
        </el-icon>
        信息补充
      </h2>
      <p class="text-sm text-gray-600">
        AI助手正在与您对话，可以随时提问或补充信息，我会为您生成最适合的购房方案
      </p>
    </div>

    <!-- 对话历史区域 -->
    <div class="conversation-container mb-6">
      <div class="conversation-list scrollbar-thin" ref="conversationRef">
        <div
          v-for="message in messages"
          :key="message.id"
          class="message-item mb-4"
          :class="`message-${message.role}`"
        >
          <!-- 用户消息 -->
          <div v-if="message.role === 'user'" class="user-message">
            <div class="message-header">
              <el-icon class="mr-2"><User /></el-icon>
              <span class="font-medium">您</span>
              <span class="message-time">{{ formatMessageTime(message.timestamp) }}</span>
            </div>
            <div class="message-content user-content">
              {{ message.content }}
            </div>
          </div>

          <!-- AI助手消息 -->
          <div v-else class="assistant-message">
            <div class="message-header">
              <el-icon class="mr-2"><Robot /></el-icon>
              <span class="font-medium">智能助手</span>
              <span class="message-time">{{ formatMessageTime(message.timestamp) }}</span>
            </div>
            <div class="message-content assistant-content">
              <div v-html="formatMessageContent(message.content)"></div>
            </div>
          </div>
        </div>

        <!-- 工具调用进度显示 -->
        <div v-if="isStreaming && currentToolCalls.length > 0" class="message-item message-assistant">
          <div class="assistant-message">
            <div class="message-header">
              <el-icon class="mr-2"><Robot /></el-icon>
              <span class="font-medium">智能助手</span>
            </div>
            <div class="message-content assistant-content">
              <div class="tool-calls-progress">
                <div v-for="toolCall in currentToolCalls" :key="toolCall.id" class="tool-call-item mb-2">
                  <div class="flex items-center">
                    <el-icon
                      class="mr-2"
                      :class="toolCall.status === 'running' ? 'text-blue-500 animate-spin' : 'text-green-500'"
                      size="16"
                    >
                      <Loading v-if="toolCall.status === 'running'" />
                      <Check v-else />
                    </el-icon>
                    <span class="text-sm" :class="toolCall.status === 'completed' ? 'text-green-600' : 'text-blue-600'">
                      {{ toolCall.message }}
                    </span>
                  </div>
                </div>
                <div v-if="streamingProgress" class="mt-2 text-sm text-gray-600">
                  {{ streamingProgress }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 流式消息显示 -->
        <div v-if="isStreaming && streamingMessage" class="message-item message-assistant">
          <div class="assistant-message">
            <div class="message-header">
              <el-icon class="mr-2"><Robot /></el-icon>
              <span class="font-medium">智能助手</span>
            </div>
            <div class="message-content assistant-content">
              <div v-html="formatMessageContent(streamingMessage)"></div>
              <div class="typing-indicator mt-2">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        </div>

        <!-- 加载指示器 -->
        <div v-else-if="loading" class="message-item message-assistant">
          <div class="assistant-message">
            <div class="message-header">
              <el-icon class="mr-2"><Robot /></el-icon>
              <span class="font-medium">智能助手</span>
            </div>
            <div class="message-content assistant-content">
              <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span class="ml-2 text-gray-500">正在分析...</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 继续对话输入框 -->
    <div class="chat-input-container mb-6">
      <div class="flex items-center space-x-3">
        <el-input
          v-model="currentInput"
          placeholder="继续对话或提供更多信息..."
          :disabled="loading || isStreaming"
          @keyup.enter="handleSendMessage"
          class="flex-1"
        />
        <el-button
          type="primary"
          :disabled="!currentInput.trim() || loading || isStreaming"
          :loading="loading || isStreaming"
          @click="handleSendMessage"
        >
          <el-icon><Position /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 快速操作按钮 -->
    <div class="quick-actions flex justify-center space-x-4 pt-6 border-t border-gray-200">
      <el-button
        v-if="messages.length > 1"
        plain
        @click="handleRestart"
      >
        <el-icon class="mr-2"><RefreshLeft /></el-icon>
        重新开始
      </el-button>

      <el-button
        plain
        @click="handleClearConversation"
      >
        <el-icon class="mr-2"><Delete /></el-icon>
        清空对话
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Loading, Check } from '@element-plus/icons-vue'
import { formatRelativeTime } from '../utils/format'

// Props
const props = defineProps({
  messages: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  streamingMessage: {
    type: String,
    default: ''
  },
  streamingProgress: {
    type: String,
    default: ''
  },
  currentToolCalls: {
    type: Array,
    default: () => []
  }
})

// Emits
const emit = defineEmits(['send-message', 'restart', 'clear-conversation'])

// 响应式引用
const conversationRef = ref()
const currentInput = ref('')

// 事件处理函数
const handleSendMessage = () => {
  if (!currentInput.value.trim()) return

  const message = currentInput.value.trim()
  currentInput.value = ''
  emit('send-message', message)
}

const handleRestart = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重新开始吗？当前的对话记录和已填写的信息将会清空。',
      '重新开始',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    emit('restart')
  } catch {
    // 用户取消
  }
}

const handleClearConversation = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空对话记录吗？已填写的信息不会丢失。',
      '清空对话',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )
    emit('clear-conversation')
  } catch {
    // 用户取消
  }
}

// 辅助函数
const formatMessageTime = (timestamp) => {
  return formatRelativeTime(timestamp)
}

const formatMessageContent = (content) => {
  // 简单的Markdown风格格式化
  if (!content) return ''

  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
    .replace(/\n/g, '<br>')
}

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (conversationRef.value) {
      const container = conversationRef.value
      container.scrollTop = container.scrollHeight
    }
  })
}

// 监听消息变化，自动滚动到底部
watch(
  () => props.messages,
  () => {
    scrollToBottom()
  },
  { deep: true }
)

watch(
  () => props.loading,
  (isLoading) => {
    if (isLoading) {
      scrollToBottom()
    }
  }
)

watch(
  () => props.streamingMessage,
  () => {
    scrollToBottom()
  }
)

// 组件挂载后滚动到底部
onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.conversation-container {
  max-height: 500px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.conversation-list {
  height: 400px;
  overflow-y: auto;
  padding: 16px;
}

.message-item {
  animation: fadeInUp 0.3s ease-out;
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  color: #6b7280;
}

.message-time {
  margin-left: auto;
  font-size: 12px;
  color: #9ca3af;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.5;
  word-wrap: break-word;
  max-width: 85%;
}

.user-message {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin-left: 15%;
}

.user-content {
  background-color: #3b82f6;
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant-message {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-right: 15%;
}

.assistant-content {
  background-color: white;
  color: #374151;
  border: 1px solid #e5e7eb;
  border-bottom-left-radius: 4px;
}

.supplement-form {
  background-color: #fef3c7;
  border: 1px solid #fbbf24;
  border-radius: 8px;
  padding: 20px;
}

.quick-actions {
  margin-top: 16px;
}

/* 打字指示器动画 */
.typing-indicator {
  display: inline-flex;
  align-items: center;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  border-radius: 50%;
  background-color: #9ca3af;
  display: inline-block;
  margin-right: 4px;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 滚动条样式 */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .conversation-container {
    max-height: 400px;
  }

  .conversation-list {
    height: 350px;
    padding: 12px;
  }

  .user-message,
  .assistant-message {
    margin-left: 0;
    margin-right: 0;
  }

  .message-content {
    max-width: 100%;
  }

  .quick-actions {
    flex-direction: column;
    space-x: 0;
    gap: 8px;
  }

  .supplement-form {
    padding: 16px;
  }
}

/* 代码块样式 */
:deep(code) {
  background-color: #f3f4f6;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 0.9em;
}

/* 链接样式 */
:deep(a) {
  color: #3b82f6;
  text-decoration: underline;
}

:deep(a:hover) {
  color: #2563eb;
}
</style>