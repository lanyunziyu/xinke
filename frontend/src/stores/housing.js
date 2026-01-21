import { defineStore } from 'pinia'
import { HousingAPI } from '../api/housing'
import { generateRequestId } from '../utils/format'

export const useHousingStore = defineStore('housing', {
  state: () => ({
    // 用户输入数据
    userInput: '',
    userProfile: {
      identity_info: {
        male_beijing_hukou: null,
        female_beijing_hukou: null,
        marital_status: '',
        purchase_as_married: null
      },
      residence_status: {
        properties_in_beijing: null,
        properties_nationwide: null
      },
      purchase_needs: {
        purpose: '',
        is_first_home: null
      },
      budget: null,
      core_requirements: {
        loan_preference: '',
        concerns: []
      },
      location: ''
    },

    // 对话和状态
    conversationHistory: [],
    currentStep: 'input', // 'input' | 'chat' | 'result'
    isStreaming: false,
    streamingMessage: '',

    // 流式处理状态
    currentToolCalls: [], // 当前正在执行的工具调用
    streamingProgress: '', // 流式处理进度信息

    // 报告数据
    reportData: null,
    reportUrl: null,
    shareUrl: null,

    // UI状态
    loading: false,
    error: null,

    // 会话信息
    conversationId: null,
    sessions: [],
    currentSessionInfo: null
  }),

  getters: {
    // 是否有活跃的对话
    hasActiveConversation: (state) => {
      return state.conversationHistory.length > 0
    },

    // 获取最新的助手消息
    latestAssistantMessage: (state) => {
      const assistantMessages = state.conversationHistory.filter(msg => msg.role === 'assistant')
      return assistantMessages[assistantMessages.length - 1]?.content || ''
    },

    // 获取成本摘要（从报告数据中提取）
    costSummary: (state) => {
      if (!state.reportData?.content) {
        return {
          downPayment: 0,
          monthlyPayment: 0,
          totalCost: 0
        }
      }

      // 从 Markdown 内容中提取成本信息（简化版本）
      const content = state.reportData.content
      const downPaymentMatch = content.match(/首付[：:]?\s*(\d+\.?\d*)[万元]?/)
      const monthlyPaymentMatch = content.match(/月供[：:]?\s*(\d+\.?\d*)[万元]?/)
      const totalCostMatch = content.match(/总成本[：:]?\s*(\d+\.?\d*)[万元]?/)

      return {
        downPayment: downPaymentMatch ? parseFloat(downPaymentMatch[1]) : 0,
        monthlyPayment: monthlyPaymentMatch ? parseFloat(monthlyPaymentMatch[1]) : 0,
        totalCost: totalCostMatch ? parseFloat(totalCostMatch[1]) : 0
      }
    },

    // 是否正在加载或流式传输
    isBusy: (state) => {
      return state.loading || state.isStreaming
    },

    // 是否有活跃的工具调用
    hasActiveToolCalls: (state) => {
      return state.currentToolCalls.some(tool => tool.status === 'running')
    },

    // 获取活跃的工具调用
    activeToolCalls: (state) => {
      return state.currentToolCalls.filter(tool => tool.status === 'running')
    },

    // 获取已完成的工具调用
    completedToolCalls: (state) => {
      return state.currentToolCalls.filter(tool => tool.status === 'completed')
    }
  },

  actions: {
    // 初始化会话
    initializeSession() {
      this.conversationId = null // 让后端自动生成
      this.conversationHistory = []
      this.currentStep = 'input'
    },

    // 发送聊天消息（统一入口）
    async sendMessage(input) {
      if (!input.trim()) return

      this.loading = true
      this.error = null
      this.userInput = input

      try {
        // 添加用户消息到对话历史
        this.addMessage('user', input)
        this.currentStep = 'chat'

        // 调用Agent聊天接口
        const response = await HousingAPI.sendChatMessage(input, this.conversationId)

        // 更新会话ID（如果是新会话）
        if (response.conversation_id) {
          this.conversationId = response.conversation_id
        }

        // 添加助手回复到对话历史
        this.addMessage('assistant', response.response || response.message)

        // 检查回复中是否包含完整报告
        if (this.isReportResponse(response.response || response.message)) {
          this.reportData = {
            content: response.response || response.message,
            conversationId: response.conversation_id,
            timestamp: new Date().toISOString()
          }
          this.currentStep = 'result'
        }

      } catch (error) {
        this.handleError('发送消息失败', error)
        // 移除可能已添加的用户消息
        if (this.conversationHistory.length > 0 &&
            this.conversationHistory[this.conversationHistory.length - 1].role === 'user') {
          this.conversationHistory.pop()
        }
        this.currentStep = 'input'
      } finally {
        this.loading = false
      }
    },

    // 发送流式聊天消息
    async sendMessageStream(input) {
      if (!input.trim()) return

      this.isStreaming = true
      this.error = null
      this.userInput = input
      this.streamingMessage = ''
      this.streamingProgress = ''
      this.currentToolCalls = []

      try {
        // 添加用户消息到对话历史
        this.addMessage('user', input)
        this.currentStep = 'chat'

        // 调用流式聊天接口
        await HousingAPI.sendChatMessageStream(input, (eventType, data) => {
          this.handleStreamEvent(eventType, data)
        }, this.conversationId)

      } catch (error) {
        this.handleError('发送流式消息失败', error)
        // 移除可能已添加的用户消息
        if (this.conversationHistory.length > 0 &&
            this.conversationHistory[this.conversationHistory.length - 1].role === 'user') {
          this.conversationHistory.pop()
        }
        this.currentStep = 'input'
      } finally {
        this.isStreaming = false
      }
    },

    // 处理流式事件
    handleStreamEvent(eventType, data) {
      switch (eventType) {
        case 'message':
        case 'response_chunk':
          // 累积消息内容
          this.streamingMessage += data.content || data.message || ''
          break

        case 'tool_call':
          // 工具调用事件 - 显示正在调用的工具
          const toolName = data.tool_name || '工具'
          const toolMessage = data.message || `正在调用 ${toolName}...`

          this.currentToolCalls.push({
            id: Date.now() + Math.random(),
            tool_name: toolName,
            status: 'running',
            message: toolMessage,
            timestamp: new Date().toISOString()
          })

          this.streamingProgress = toolMessage
          console.log('工具调用:', data)
          break

        case 'tool_result':
          // 工具执行结果
          const resultToolName = data.tool_name || '工具'
          const resultMessage = data.message || `${resultToolName} 执行完成`

          // 更新工具调用状态
          const runningTool = this.currentToolCalls.find(
            tool => tool.tool_name === resultToolName && tool.status === 'running'
          )
          if (runningTool) {
            runningTool.status = 'completed'
            runningTool.message = resultMessage
          }

          this.streamingProgress = resultMessage
          console.log('工具结果:', data)
          break

        case 'thinking':
          // Agent思考中
          this.streamingProgress = data.message || '正在思考...'
          break

        case 'response_start':
          // 开始生成回复
          this.streamingProgress = '正在生成回复...'
          break

        case 'response_end':
          // 回复结束
          this.streamingProgress = ''
          break

        case 'error':
          // 错误事件
          this.handleError('流式响应错误', new Error(data.error || data.message))
          break

        case 'complete':
        case 'done':
          // 完成事件
          if (data.conversation_id) {
            this.conversationId = data.conversation_id
          }

          // 添加完整的助手回复到对话历史
          const fullMessage = this.streamingMessage || data.response || data.message
          this.addMessage('assistant', fullMessage)

          // 检查是否为完整报告
          if (this.isReportResponse(fullMessage)) {
            this.reportData = {
              content: fullMessage,
              conversationId: data.conversation_id,
              timestamp: new Date().toISOString()
            }
            this.currentStep = 'result'
          }

          // 清理流式状态
          this.streamingMessage = ''
          this.streamingProgress = ''
          this.currentToolCalls = []
          break

        default:
          console.log('未知流式事件:', eventType, data)
      }
    },

    // 检查是否是报告响应
    isReportResponse(message) {
      // 简单检查：如果包含报告的关键标识符，认为是完整报告
      return message.includes('购房资金方案报告') ||
             message.includes('总成本概览') ||
             message.includes('月供压力分析')
    },

    // 会话管理方法
    async loadSessions() {
      try {
        const response = await HousingAPI.getSessions()
        this.sessions = response.sessions || []
        return this.sessions
      } catch (error) {
        this.handleError('加载会话列表失败', error)
        return []
      }
    },

    async loadSession(conversationId) {
      try {
        const session = await HousingAPI.getSession(conversationId)
        this.currentSessionInfo = session
        return session
      } catch (error) {
        this.handleError('加载会话失败', error)
        return null
      }
    },

    async resetCurrentSession() {
      if (!this.conversationId) return

      try {
        await HousingAPI.resetSession(this.conversationId)
        this.initializeSession()
        return true
      } catch (error) {
        this.handleError('重置会话失败', error)
        return false
      }
    },

    async resetAllSessions() {
      try {
        await HousingAPI.resetAllSessions()
        this.initializeSession()
        this.sessions = []
        return true
      } catch (error) {
        this.handleError('重置所有会话失败', error)
        return false
      }
    },

    // 生成分享链接
    async generateShareLink() {
      if (!this.reportData || !this.conversationId) {
        throw new Error('没有可分享的内容')
      }

      try {
        const response = await HousingAPI.generateShareLink({
          conversationId: this.conversationId,
          reportData: this.reportData,
          conversationHistory: this.conversationHistory
        })

        this.shareUrl = response.shareUrl
        return response.shareUrl

      } catch (error) {
        this.handleError('生成分享链接失败', error)
        throw error
      }
    },

    // 下载报告
    async downloadReport() {
      if (!this.reportData || !this.conversationId) {
        throw new Error('没有可下载的报告')
      }

      try {
        await HousingAPI.downloadReport(this.conversationId, {
          format: 'pdf',
          includeCharts: true
        })

      } catch (error) {
        this.handleError('下载报告失败', error)
        throw error
      }
    },

    // 重置状态
    resetState() {
      this.$reset()
      this.initializeSession()
    },

    // 清除错误
    clearError() {
      this.error = null
    },

    // 辅助方法：添加消息到对话历史
    addMessage(role, content) {
      this.conversationHistory.push({
        id: Date.now() + Math.random(), // 避免ID冲突
        role,
        content,
        timestamp: new Date().toISOString()
      })
    },

    // 辅助方法：处理错误
    handleError(message, error) {
      console.error(message, error)
      this.error = message
      if (error.response?.data?.detail) {
        this.error += ': ' + error.response.data.detail
      }
    }
  }
})

// 辅助函数已简化，复杂的用户画像处理逻辑已移除
// 现在使用统一的聊天接口，无需复杂的字段验证和格式化