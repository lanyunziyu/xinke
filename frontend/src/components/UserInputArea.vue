<template>
  <div class="bg-white rounded-lg shadow-sm p-6 card-shadow">
    <div class="mb-6">
      <h2 class="text-xl font-semibold text-gray-900 mb-2 flex items-center">
        <el-icon class="mr-2 text-primary-600">
          <EditPen />
        </el-icon>
        请描述您的购房需求
      </h2>
      <p class="text-sm text-gray-600">
        您可以用自然语言描述您的需求，我们的AI助手会智能分析并为您生成定制方案
      </p>
    </div>

    <!-- 输入模式切换 -->
    <div class="mb-4">
      <el-radio-group v-model="inputMode" class="mb-4">
        <el-radio-button label="natural">自然语言描述</el-radio-button>
        <el-radio-button label="structured">结构化填写</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 自然语言输入模式 -->
    <div v-if="inputMode === 'natural'" class="space-y-4">
      <!-- 示例提示 -->
      <div class="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-400">
        <h4 class="font-medium text-blue-900 mb-2">输入示例：</h4>
        <div class="text-sm text-blue-800 space-y-1">
          <p>• "我想在北京朝阳区买房，预算800万，是首套房，希望了解需要准备多少钱"</p>
          <p>• "夫妻都是北京户口，想买二套房改善居住，预算1200万，倾向于组合贷"</p>
          <p>• "非京籍，在北京工作5年，想买首套房自住，预算600万左右"</p>
        </div>
      </div>

      <!-- 快速填写建议 -->
      <div class="mb-4">
        <h4 class="text-sm font-medium text-gray-700 mb-2">快速选择常见需求：</h4>
        <div class="flex flex-wrap gap-2">
          <el-tag
            v-for="template in inputTemplates"
            :key="template.id"
            class="cursor-pointer hover:opacity-80"
            type="info"
            effect="plain"
            @click="useTemplate(template)"
          >
            {{ template.label }}
          </el-tag>
        </div>
      </div>

      <!-- 文本输入框 -->
      <el-input
        v-model="naturalInput"
        type="textarea"
        :rows="6"
        placeholder="请详细描述您的购房需求，包括区域偏好、预算范围、购房目的等..."
        show-word-limit
        maxlength="500"
        class="mb-4"
        @input="handleNaturalInputChange"
      />

      <!-- 智能提取预览 -->
      <div v-if="extractedInfo && Object.keys(extractedInfo).length > 0" class="bg-gray-50 rounded-lg p-4">
        <h4 class="text-sm font-medium text-gray-700 mb-2 flex items-center">
          <el-icon class="mr-1"><Search /></el-icon>
          AI智能提取的信息：
        </h4>
        <div class="text-sm text-gray-600 space-y-1">
          <div v-if="extractedInfo.location" class="flex items-center">
            <span class="w-20 text-gray-500">区域：</span>
            <span class="text-gray-900 font-medium">{{ extractedInfo.location }}</span>
          </div>
          <div v-if="extractedInfo.budget" class="flex items-center">
            <span class="w-20 text-gray-500">预算：</span>
            <span class="text-gray-900 font-medium">{{ extractedInfo.budget }}万元</span>
          </div>
          <div v-if="extractedInfo.purpose" class="flex items-center">
            <span class="w-20 text-gray-500">目的：</span>
            <span class="text-gray-900 font-medium">{{ extractedInfo.purpose }}</span>
          </div>
          <div v-if="extractedInfo.is_first_home !== null" class="flex items-center">
            <span class="w-20 text-gray-500">首套房：</span>
            <span class="text-gray-900 font-medium">{{ extractedInfo.is_first_home ? '是' : '否' }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 结构化输入模式 -->
    <div v-else class="space-y-4">
      <el-alert
        title="结构化填写模式"
        type="info"
        description="请按照表单逐项填写您的购房信息，系统会根据您的情况生成专业的购房方案"
        show-icon
        :closable="false"
        class="mb-4"
      />

      <!-- 基本信息表单 -->
      <StructuredForm
        v-model="structuredData"
        @change="handleStructuredChange"
      />
    </div>

    <!-- 提交按钮区域 -->
    <div class="flex justify-center pt-6 border-t border-gray-200">
      <el-button
        type="primary"
        size="large"
        :loading="loading"
        :disabled="!canSubmit"
        @click="handleSubmit"
        class="px-8 py-2 min-w-32"
      >
        <el-icon class="mr-2"><Search /></el-icon>
        {{ loading ? '正在分析...' : '开始分析' }}
      </el-button>
    </div>

    <!-- 提示信息 -->
    <div class="mt-4 text-center">
      <p class="text-xs text-gray-500">
        提交后，AI助手会分析您的需求并可能要求补充详细信息
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { debounce } from '../utils/format'
import StructuredForm from './StructuredForm.vue'

// Props
const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['submit'])

// 响应式数据
const inputMode = ref('natural') // 'natural' | 'structured'
const naturalInput = ref('')
const structuredData = ref({})
const extractedInfo = ref({})

// 输入模板
const inputTemplates = ref([
  {
    id: 1,
    label: '北京首套房自住',
    content: '我想在北京买首套房自住，预算800万左右，希望了解购房政策和需要准备多少资金'
  },
  {
    id: 2,
    label: '改善型二套房',
    content: '夫妻都是北京户口，现有一套房，想买二套房改善居住条件，预算1200万，考虑组合贷'
  },
  {
    id: 3,
    label: '非京籍首购',
    content: '外地户口在北京工作满5年，想购买首套房，预算600万，需要了解购房资格和贷款政策'
  },
  {
    id: 4,
    label: '投资性购房',
    content: '有一定资金想在北京投资房产，预算1000万左右，希望了解投资建议和税费成本'
  }
])

// 计算属性
const canSubmit = computed(() => {
  if (inputMode.value === 'natural') {
    return naturalInput.value.trim().length >= 10
  } else {
    // 结构化表单的基本验证
    const required = ['location', 'budget', 'purpose']
    return required.every(field => structuredData.value[field])
  }
})

// 防抖的自然语言分析函数
const debouncedAnalyze = debounce((input) => {
  if (input.length >= 20) {
    analyzeNaturalInput(input)
  }
}, 1000)

// 事件处理函数
const handleNaturalInputChange = () => {
  if (naturalInput.value.length >= 20) {
    debouncedAnalyze(naturalInput.value)
  } else {
    extractedInfo.value = {}
  }
}

const handleStructuredChange = (data) => {
  structuredData.value = { ...data }
}

const handleSubmit = () => {
  if (!canSubmit.value) return

  let message = ''
  if (inputMode.value === 'natural') {
    message = naturalInput.value.trim()
  } else {
    // 转换结构化数据为自然语言描述
    message = generateDescription(structuredData.value)
  }

  emit('submit', message)

  // 清空输入
  if (inputMode.value === 'natural') {
    naturalInput.value = ''
    extractedInfo.value = {}
  } else {
    structuredData.value = {}
  }
}

const useTemplate = (template) => {
  naturalInput.value = template.content
  analyzeNaturalInput(template.content)
}

// 辅助函数
const analyzeNaturalInput = async (input) => {
  try {
    // 简单的关键词提取逻辑（实际应用中可能需要调用AI接口）
    const extracted = {}

    // 提取区域信息
    const locations = ['朝阳', '海淀', '西城', '东城', '丰台', '石景山', '通州', '昌平', '大兴', '房山', '门头沟', '怀柔', '密云', '延庆', '顺义', '平谷']
    for (const location of locations) {
      if (input.includes(location)) {
        extracted.location = location + '区'
        break
      }
    }

    // 提取预算信息
    const budgetMatch = input.match(/(\d+)万/)
    if (budgetMatch) {
      extracted.budget = parseInt(budgetMatch[1])
    }

    // 提取购房目的
    if (input.includes('自住')) extracted.purpose = '自住'
    else if (input.includes('投资')) extracted.purpose = '投资'
    else if (input.includes('改善')) extracted.purpose = '改善居住'

    // 提取首套房信息
    if (input.includes('首套') || input.includes('第一套')) extracted.is_first_home = true
    else if (input.includes('二套') || input.includes('第二套')) extracted.is_first_home = false

    extractedInfo.value = extracted
  } catch (error) {
    console.error('分析自然语言输入失败:', error)
  }
}

const generateDescription = (data) => {
  const parts = []

  if (data.location) parts.push(`想在${data.location}买房`)
  if (data.budget) parts.push(`预算${data.budget}万元`)
  if (data.purpose) parts.push(`用于${data.purpose}`)
  if (data.is_first_home !== undefined) {
    parts.push(data.is_first_home ? '是首套房' : '不是首套房')
  }
  if (data.loan_preference) parts.push(`倾向于${data.loan_preference}`)

  let description = parts.join('，')
  if (!description.endsWith('。')) description += '。'
  description += '希望了解购房政策和资金准备建议。'

  return description
}

// 监听输入模式变化
watch(inputMode, () => {
  // 清空之前的数据
  naturalInput.value = ''
  structuredData.value = {}
  extractedInfo.value = {}
})
</script>

<style scoped>
.card-shadow {
  transition: box-shadow 0.3s ease;
}

.card-shadow:hover {
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

/* 自定义标签样式 */
.el-tag {
  transition: all 0.2s ease;
}

.el-tag:hover {
  transform: translateY(-1px);
}

/* 输入框焦点样式 */
:deep(.el-textarea__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* 按钮加载状态样式 */
.el-button.is-loading {
  pointer-events: none;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .el-radio-group .el-radio-button {
    display: block;
    margin-bottom: 8px;
  }

  .flex.flex-wrap {
    gap: 8px;
  }
}
</style>