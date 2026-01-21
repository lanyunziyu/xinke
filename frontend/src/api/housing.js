import axios from 'axios'

// 创建axios实例
const apiClient = axios.create({
  baseURL: 'http://localhost:8000',  // 直接连接到后端服务
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加时间戳
    config.headers['X-Timestamp'] = Date.now()

    // 添加请求ID（用于调试）
    if (!config.headers['X-Request-ID']) {
      config.headers['X-Request-ID'] = generateRequestId()
    }

    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('API Response:', response.status, response.data)
    return response.data
  },
  (error) => {
    console.error('API Error:', error.response?.status, error.response?.data || error.message)

    // 统一错误处理
    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response

      switch (status) {
        case 400:
          throw new Error(data.detail || '请求参数错误')
        case 500:
          throw new Error(data.detail || '服务器内部错误')
        case 503:
          throw new Error('Agent服务暂时不可用，请稍后重试或联系管理员')
        default:
          throw new Error(data.detail || `请求失败 (${status})`)
      }
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('请求超时，请检查网络连接')
    } else {
      throw new Error('网络错误，请检查连接')
    }
  }
)

// 购房助手API类
export class HousingAPI {
  /**
   * 分析自然语言输入
   * @deprecated 使用统一的 sendChatMessage 方法替代
   * @param {string} input - 用户输入的自然语言
   * @param {object} options - 附加选项
   * @returns {Promise<object>} 分析结果
   */
  static async analyzeNaturalInput(input, options = {}) {
    console.warn('🚨 analyzeNaturalInput 已废弃，请使用 sendChatMessage 方法')
    // 注意：这个接口需要后端实现，目前使用模拟数据

    // 模拟分析结果
    const mockResponse = {
      extractedInfo: {
        location: extractLocation(input),
        budget: extractBudget(input),
        purchase_needs: {
          purpose: extractPurpose(input),
          is_first_home: extractFirstHome(input)
        }
      },
      feedback: '我已经分析了您的需求。请补充一些详细信息以便为您生成更精准的方案。',
      missingFields: [
        'identity_info.male_beijing_hukou',
        'identity_info.female_beijing_hukou',
        'identity_info.marital_status',
        'residence_status.properties_in_beijing'
      ]
    }

    // 延迟模拟网络请求
    await new Promise(resolve => setTimeout(resolve, 1000))

    return mockResponse

    // 实际API调用（待后端实现）
    // return await apiClient.post('/v1/analyze-input', {
    //   input,
    //   timestamp: Date.now(),
    //   ...options
    // })
  }

  /**
   * 验证和补充用户画像信息
   * @deprecated 使用统一的 sendChatMessage 方法替代
   * @param {object} userProfile - 用户画像数据
   * @param {object} options - 附加选项
   * @returns {Promise<object>} 验证结果
   */
  static async validateAndSupplement(userProfile, options = {}) {
    console.warn('🚨 validateAndSupplement 已废弃，请使用 sendChatMessage 方法')
    // 注意：这个接口需要后端实现，目前使用模拟验证

    const missingFields = []

    // 检查必填字段
    if (userProfile.identity_info?.male_beijing_hukou === null) missingFields.push('identity_info.male_beijing_hukou')
    if (userProfile.identity_info?.female_beijing_hukou === null) missingFields.push('identity_info.female_beijing_hukou')
    if (!userProfile.identity_info?.marital_status) missingFields.push('identity_info.marital_status')
    if (userProfile.residence_status?.properties_in_beijing === null) missingFields.push('residence_status.properties_in_beijing')
    if (!userProfile.core_requirements?.loan_preference) missingFields.push('core_requirements.loan_preference')

    await new Promise(resolve => setTimeout(resolve, 800))

    return {
      stillMissing: missingFields,
      feedback: missingFields.length > 0
        ? '还需要补充一些关键信息。'
        : '信息已完整，正在生成方案...'
    }
  }

  /**
   * 生成购房方案
   * @deprecated 使用统一的 sendChatMessage 方法替代
   * @param {object} userProfile - 完整的用户画像
   * @param {object} options - 扩展选项
   * @returns {Promise<object>} 方案结果
   */
  static async generateSolution(userProfile, options = {}) {
    console.warn('🚨 generateSolution 已废弃，请使用 sendChatMessage 方法')
    return await apiClient.post('/v1/generate-solution', {
      ...userProfile,
      // 预留扩展参数
      options: {
        reportFormat: 'json',
        includeImages: true,
        detailLevel: 'full',
        ...options.options
      },
      sessionId: options.sessionId,
      requestId: options.requestId,
      timestamp: Date.now()
    })
  }

  /**
   * 查询购房政策
   * @deprecated 使用统一的 sendChatMessage 方法替代
   * @param {string} location - 购房区域
   * @param {string} buyerType - 购房者类型
   * @param {object} options - 附加选项
   * @returns {Promise<object>} 政策信息
   */
  static async lookupPolicy(location, buyerType, options = {}) {
    console.warn('🚨 lookupPolicy 已废弃，请使用 sendChatMessage 方法')
    return await apiClient.post('/v1/lookup-policy', {
      location,
      buyer_type: buyerType,
      ...options
    })
  }

  /**
   * 计算购房成本
   * @deprecated 使用统一的 sendChatMessage 方法替代
   * @param {number} totalPrice - 房屋总价
   * @param {boolean} isFirstHome - 是否首套房
   * @param {string} loanType - 贷款类型
   * @param {object} options - 附加选项
   * @returns {Promise<object>} 成本计算结果
   */
  static async calculateCost(totalPrice, isFirstHome, loanType = 'combination', options = {}) {
    console.warn('🚨 calculateCost 已废弃，请使用 sendChatMessage 方法')
    return await apiClient.post('/v1/calculate-cost', {
      total_price: totalPrice,
      is_first_home: isFirstHome,
      loan_type: loanType,
      ...options
    })
  }

  /**
   * 生成分享链接
   * @param {object} sessionData - 会话数据
   * @param {object} options - 附加选项
   * @returns {Promise<object>} 分享链接信息
   */
  static async generateShareLink(sessionData, options = {}) {
    // 注意：这个接口需要后端实现
    console.warn('generateShareLink API needs backend implementation')

    // 模拟生成分享链接
    await new Promise(resolve => setTimeout(resolve, 500))

    const shareCode = generateShareCode()
    const shareUrl = `${window.location.origin}/share/${shareCode}`

    return {
      shareUrl,
      shareCode,
      expiresAt: new Date(Date.now() + 72 * 60 * 60 * 1000), // 72小时后过期
      ...options
    }
  }

  /**
   * 下载报告
   * @param {string} sessionId - 会话ID
   * @param {object} options - 下载选项
   * @returns {Promise<void>}
   */
  static async downloadReport(sessionId, options = {}) {
    // 注意：这个接口需要后端实现
    console.warn('downloadReport API needs backend implementation')

    // 模拟下载
    await new Promise(resolve => setTimeout(resolve, 1000))

    // 创建模拟PDF下载
    const filename = `购房方案报告_${sessionId}_${formatDate(new Date())}.pdf`
    const mockPdfContent = generateMockPdfBlob()

    const url = window.URL.createObjectURL(mockPdfContent)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  }

  /**
   * 健康检查
   * @returns {Promise<object>} 服务状态
   */
  static async healthCheck() {
    return await apiClient.get('/health')
  }

  /**
   * 检查Agent状态
   * @returns {Promise<boolean>} Agent是否可用
   */
  static async checkAgentStatus() {
    try {
      const health = await this.healthCheck()
      return health.status === 'healthy' && health.agent_initialized
    } catch (error) {
      console.error('Agent状态检查失败:', error)
      return false
    }
  }

  /**
   * 发送聊天消息到Agent（非流式）
   * @param {string} message - 用户消息
   * @param {string} conversationId - 会话ID（可选）
   * @param {number} maxIterations - 最大迭代次数（默认15）
   * @returns {Promise<object>} 聊天响应
   */
  static async sendChatMessage(message, conversationId = null, maxIterations = 15) {
    return await apiClient.post('/chat', {
      message,
      stream: false,
      conversation_id: conversationId,
      max_iterations: maxIterations
    })
  }

  /**
   * 发送聊天消息到Agent（流式）
   * @param {string} message - 用户消息
   * @param {function} onEvent - 接收事件的回调函数 (eventType, data) => void
   * @param {string} conversationId - 会话ID（可选）
   * @param {number} maxIterations - 最大迭代次数（默认15）
   * @returns {Promise<void>} 流式响应处理
   */
  static async sendChatMessageStream(message, onEvent, conversationId = null, maxIterations = 15) {
    try {
      const response = await fetch(`${apiClient.defaults.baseURL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          stream: true,
          conversation_id: conversationId,
          max_iterations: maxIterations
        })
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      let buffer = ''
      let currentEvent = null

      while (true) {
        const { value, done } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')

        // 保留最后一行（可能不完整）
        buffer = lines.pop()

        for (const line of lines) {
          const trimmedLine = line.trim()

          if (trimmedLine.startsWith('event: ')) {
            // 新事件类型
            currentEvent = trimmedLine.slice(7)
          } else if (trimmedLine.startsWith('data: ')) {
            // 事件数据
            if (currentEvent) {
              try {
                const data = JSON.parse(trimmedLine.slice(6))
                onEvent(currentEvent, data)
              } catch (e) {
                console.warn('解析SSE数据失败:', e, trimmedLine)
              }
            }
          } else if (trimmedLine === '') {
            // 空行表示事件结束
            currentEvent = null
          }
        }
      }
    } catch (error) {
      console.error('流式请求失败:', error)
      throw error
    }
  }

  /**
   * 获取所有会话列表
   * @returns {Promise<object>} 会话列表
   */
  static async getSessions() {
    return await apiClient.get('/sessions')
  }

  /**
   * 获取特定会话信息
   * @param {string} conversationId - 会话ID
   * @returns {Promise<object>} 会话详情
   */
  static async getSession(conversationId) {
    return await apiClient.get(`/sessions/${conversationId}`)
  }

  /**
   * 重置特定会话
   * @param {string} conversationId - 会话ID
   * @returns {Promise<object>} 重置结果
   */
  static async resetSession(conversationId) {
    return await apiClient.post('/reset', {
      conversation_id: conversationId
    })
  }

  /**
   * 重置所有会话
   * @returns {Promise<object>} 重置结果
   */
  static async resetAllSessions() {
    return await apiClient.post('/reset')
  }

  /**
   * 生成购房方案（直接调用Agent）
   * @param {string} userInput - 用户的自然语言输入
   * @param {object} options - 扩展选项
   * @returns {Promise<object>} 方案结果
   */
  static async generateHousingSolution(userInput, options = {}) {
    return await this.sendChatMessage(userInput, options.conversationId, options.maxIterations)
  }
}

// 辅助函数

/**
 * 生成请求ID
 * @returns {string} 唯一请求ID
 */
export function generateRequestId() {
  return 'req_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
}

/**
 * 生成分享码
 * @returns {string} 分享码
 */
function generateShareCode() {
  return Math.random().toString(36).substr(2, 8).toUpperCase()
}

/**
 * 格式化日期
 * @param {Date} date - 日期对象
 * @returns {string} 格式化的日期字符串
 */
function formatDate(date) {
  return date.toISOString().split('T')[0].replace(/-/g, '')
}

/**
 * 生成模拟PDF Blob
 * @returns {Blob} PDF文件的Blob对象
 */
function generateMockPdfBlob() {
  const content = '%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\n\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n207\n%%EOF'
  return new Blob([content], { type: 'application/pdf' })
}

// 自然语言解析辅助函数（简单实现）

/**
 * 从输入中提取位置信息
 * @param {string} input - 用户输入
 * @returns {string} 提取的位置
 */
function extractLocation(input) {
  const locations = ['朝阳', '海淀', '西城', '东城', '丰台', '石景山', '通州', '昌平', '大兴', '房山', '门头沟', '怀柔', '密云', '延庆', '顺义', '平谷']
  for (const location of locations) {
    if (input.includes(location)) {
      return location
    }
  }
  if (input.includes('北京')) {
    return '北京'
  }
  return ''
}

/**
 * 从输入中提取预算信息
 * @param {string} input - 用户输入
 * @returns {number|null} 提取的预算
 */
function extractBudget(input) {
  const budgetMatch = input.match(/(\d+)万/);
  if (budgetMatch) {
    return parseInt(budgetMatch[1])
  }
  return null
}

/**
 * 从输入中提取购房目的
 * @param {string} input - 用户输入
 * @returns {string} 购房目的
 */
function extractPurpose(input) {
  if (input.includes('自住')) return '自住'
  if (input.includes('投资')) return '投资'
  if (input.includes('改善')) return '改善居住'
  return '自住' // 默认值
}

/**
 * 从输入中判断是否首套房
 * @param {string} input - 用户输入
 * @returns {boolean|null} 是否首套房
 */
function extractFirstHome(input) {
  if (input.includes('首套') || input.includes('第一套') || input.includes('首次')) return true
  if (input.includes('二套') || input.includes('第二套') || input.includes('再次')) return false
  return null
}

export default HousingAPI