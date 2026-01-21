<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 头部导航 -->
    <header class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto container-spacing py-4">
        <div class="flex items-center justify-between">
          <h1 class="text-2xl font-bold text-gray-900 flex items-center">
            <el-icon class="mr-2 text-primary-600" size="28">
              <House />
            </el-icon>
            购房资金方案助手
          </h1>
          <div class="text-sm text-gray-600">
            智能分析 · 精准方案 · 一站服务
          </div>
        </div>
      </div>
    </header>

    <!-- 主内容区域 -->
    <main class="max-w-6xl mx-auto container-spacing py-8">
      <!-- 进度指示器 -->
      <div class="step-indicator mb-8">
        <div
          class="step-item"
          :class="{
            'active': currentStep === 'input',
            'completed': ['chat', 'result'].includes(currentStep)
          }"
        >
          <div class="flex flex-col items-center">
            <div class="w-8 h-8 rounded-full border-2 flex items-center justify-center mb-2"
                 :class="{
                   'border-primary-600 bg-primary-600 text-white': currentStep === 'input' || ['chat', 'result'].includes(currentStep),
                   'border-gray-300 text-gray-300': currentStep !== 'input' && !['chat', 'result'].includes(currentStep)
                 }">
              <el-icon><Edit /></el-icon>
            </div>
            <span class="text-xs">需求输入</span>
          </div>
        </div>

        <div class="step-item"
             :class="{
               'active': currentStep === 'chat',
               'completed': currentStep === 'result'
             }">
          <div class="flex flex-col items-center">
            <div class="w-8 h-8 rounded-full border-2 flex items-center justify-center mb-2"
                 :class="{
                   'border-primary-600 bg-primary-600 text-white': currentStep === 'chat' || currentStep === 'result',
                   'border-gray-300 text-gray-300': !['chat', 'result'].includes(currentStep)
                 }">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <span class="text-xs">信息补充</span>
          </div>
        </div>

        <div class="step-item"
             :class="{ 'active': currentStep === 'result' }">
          <div class="flex flex-col items-center">
            <div class="w-8 h-8 rounded-full border-2 flex items-center justify-center mb-2"
                 :class="{
                   'border-primary-600 bg-primary-600 text-white': currentStep === 'result',
                   'border-gray-300 text-gray-300': currentStep !== 'result'
                 }">
              <el-icon><Document /></el-icon>
            </div>
            <span class="text-xs">方案报告</span>
          </div>
        </div>
      </div>

      <!-- 内容区域 -->
      <div class="space-y-6">
        <!-- 1. 用户输入区域 -->
        <UserInputArea
          v-if="currentStep === 'input'"
          :loading="loading"
          @submit="handleUserSubmit"
          class="fade-in"
        />

        <!-- 2. 聊天对话区域 -->
        <ModelFeedback
          v-if="currentStep === 'chat'"
          :messages="conversation"
          :loading="loading"
          :is-streaming="isStreaming"
          :streaming-message="streamingMessage"
          :streaming-progress="streamingProgress"
          :current-tool-calls="currentToolCalls"
          @send-message="handleSendMessage"
          @restart="handleRestart"
          @clear-conversation="handleClearConversation"
          class="fade-in"
        />

        <!-- 3. 结果展示区域 -->
        <ReportView
          v-if="currentStep === 'result'"
          :report-data="reportData"
          :loading="loading"
          @view-detail="showReportModal"
          @share="handleShare"
          @download="handleDownload"
          @restart="handleRestart"
          @continue-chat="handleContinueChat"
          class="fade-in"
        />
      </div>
    </main>

    <!-- 报告详情弹窗 -->
    <ReportModal
      v-model="reportModalVisible"
      :report-data="reportData"
      :report-url="reportUrl"
    />

    <!-- 全局加载遮罩 -->
    <el-loading
      v-loading="globalLoading"
      element-loading-text="正在生成方案..."
      element-loading-background="rgba(0, 0, 0, 0.8)"
      body-style="{ 'background': 'rgba(0, 0, 0, 0.8)' }"
    />

    <!-- 错误提示 -->
    <el-alert
      v-if="error"
      :title="error"
      type="error"
      show-icon
      closable
      @close="clearError"
      class="fixed top-4 right-4 z-50 max-w-md"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useHousingStore } from './stores/housing'

// 组件导入
import UserInputArea from './components/UserInputArea.vue'
import ModelFeedback from './components/ModelFeedback.vue'
import ReportView from './components/ReportView.vue'
import ReportModal from './components/ReportModal.vue'

// 状态管理
const housingStore = useHousingStore()

// 响应式数据
const reportModalVisible = ref(false)
const globalLoading = ref(false)

// 计算属性
const currentStep = computed(() => housingStore.currentStep)
const loading = computed(() => housingStore.loading)
const isStreaming = computed(() => housingStore.isStreaming)
const streamingMessage = computed(() => housingStore.streamingMessage)
const streamingProgress = computed(() => housingStore.streamingProgress)
const currentToolCalls = computed(() => housingStore.currentToolCalls)
const conversation = computed(() => housingStore.conversationHistory)
const reportData = computed(() => housingStore.reportData)
const reportUrl = computed(() => housingStore.reportUrl)
const error = computed(() => housingStore.error)

// 事件处理函数
const handleUserSubmit = async (input) => {
  try {
    // 使用流式聊天发送初始消息
    await housingStore.sendMessageStream(input)
  } catch (error) {
    ElMessage.error('发送消息失败，请重试')
  }
}

const handleSendMessage = async (message) => {
  try {
    // 发送聊天消息（可以选择流式或非流式）
    await housingStore.sendMessageStream(message)
  } catch (error) {
    ElMessage.error('发送消息失败，请重试')
  }
}

const handleClearConversation = () => {
  housingStore.conversationHistory = []
  ElMessage.info('对话记录已清空')
}

const showReportModal = () => {
  reportModalVisible.value = true
}

const handleShare = async () => {
  try {
    const shareUrl = await housingStore.generateShareLink()

    // 复制到剪贴板
    await navigator.clipboard.writeText(shareUrl)
    ElMessage.success('分享链接已复制到剪贴板')
  } catch (error) {
    ElMessage.error('生成分享链接失败')
  }
}

const handleDownload = async () => {
  try {
    await housingStore.downloadReport()
    ElMessage.success('报告下载已开始')
  } catch (error) {
    ElMessage.error('下载失败，请重试')
  }
}

const handleRestart = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要重新开始吗？当前的分析结果将会丢失。',
      '重新开始',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )

    housingStore.resetState()
    ElMessage.info('已重新开始')
  } catch {
    // 用户取消操作
  }
}

const clearError = () => {
  housingStore.clearError()
}

const handleContinueChat = () => {
  // 返回到聊天阶段，允许用户继续提问
  housingStore.currentStep = 'chat'
}

// 生命周期
onMounted(() => {
  // 初始化应用
  console.log('购房资金方案助手已启动')
})
</script>

<style scoped>
/* 步骤指示器连接线 */
.step-indicator::before {
  content: '';
  position: absolute;
  top: 16px;
  left: 25%;
  right: 25%;
  height: 2px;
  background: linear-gradient(to right, #e5e7eb, #e5e7eb);
  z-index: 0;
}

.step-item {
  position: relative;
  z-index: 1;
}

/* 动画效果 */
.fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>