<template>
  <div class="report-view">
    <!-- 报告标题 -->
    <div class="report-header mb-6">
      <el-alert
        title="购房方案已生成！"
        type="success"
        description="您的专属购房资金方案已完成，请查看详细内容。"
        show-icon
        :closable="false"
        class="mb-4"
      />
    </div>

    <!-- 报告内容 -->
    <div class="report-content bg-white rounded-lg shadow-sm p-6">
      <!-- 如果有结构化的报告数据，显示卡片式布局 -->
      <div v-if="hasStructuredData" class="structured-report">
        <!-- 方案概览 -->
        <div class="overview-section mb-8">
          <h2 class="section-title">方案概览</h2>
          <div class="metrics-grid">
            <div class="metric-card" v-for="metric in keyMetrics" :key="metric.key">
              <div class="metric-value">{{ metric.value }}</div>
              <div class="metric-label">{{ metric.label }}</div>
              <div class="metric-desc">{{ metric.description }}</div>
            </div>
          </div>
        </div>

        <!-- 快速摘要 -->
        <div class="summary-section mb-6">
          <div class="quick-facts">
            <div class="fact-item" v-for="fact in quickFacts" :key="fact.key">
              <el-icon class="fact-icon"><component :is="fact.icon" /></el-icon>
              <span class="fact-text">{{ fact.text }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 原始Markdown内容显示 -->
      <div class="markdown-content">
        <div
          class="prose prose-lg max-w-none"
          v-html="renderedContent"
        ></div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="action-section mt-6">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex flex-wrap justify-center gap-4">
          <el-button
            type="primary"
            size="large"
            @click="handleViewFullReport"
            :loading="loading"
          >
            <el-icon class="mr-2"><Document /></el-icon>
            查看完整报告
          </el-button>

          <el-button
            type="success"
            size="large"
            @click="handleShare"
            :loading="loading"
          >
            <el-icon class="mr-2"><Share /></el-icon>
            分享方案
          </el-button>

          <el-button
            size="large"
            @click="handleDownload"
            :loading="loading"
          >
            <el-icon class="mr-2"><Download /></el-icon>
            下载PDF
          </el-button>

          <el-button
            plain
            size="large"
            @click="handleRestart"
          >
            <el-icon class="mr-2"><RefreshRight /></el-icon>
            重新开始
          </el-button>
        </div>

        <!-- 继续咨询 -->
        <div class="mt-4 text-center">
          <p class="text-sm text-gray-600 mb-2">
            还有疑问？继续与AI助手对话
          </p>
          <el-button type="primary" text @click="handleContinueChat">
            继续咨询
          </el-button>
        </div>
      </div>
    </div>

    <!-- 专家提醒 -->
    <div class="expert-tips mt-6" v-if="expertTips.length > 0">
      <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 class="text-lg font-medium text-blue-900 mb-3 flex items-center">
          <el-icon class="mr-2"><Warning /></el-icon>
          重要提醒
        </h3>
        <div class="space-y-2">
          <div v-for="tip in expertTips" :key="tip.id" class="text-blue-800 text-sm">
            • {{ tip }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { marked } from 'marked'

// Props
const props = defineProps({
  reportData: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['view-detail', 'share', 'download', 'restart', 'continue-chat'])

// 响应式数据
const rawContent = ref('')

// 计算属性
const renderedContent = computed(() => {
  const content = props.reportData?.content || rawContent.value || ''
  if (!content) return '<p class="text-gray-500">暂无报告内容</p>'

  // 使用marked渲染Markdown
  try {
    return marked(content, {
      breaks: true,
      gfm: true
    })
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return `<pre class="whitespace-pre-wrap text-sm">${content}</pre>`
  }
})

const hasStructuredData = computed(() => {
  // 检查是否包含结构化数据
  const content = props.reportData?.content || ''
  return content.includes('总成本概览') || content.includes('月供压力分析')
})

const keyMetrics = computed(() => {
  const content = props.reportData?.content || ''
  const metrics = []

  // 简单的文本解析提取关键数据
  const downPaymentMatch = content.match(/首付.*?(\d+)万元/i)
  const monthlyPaymentMatch = content.match(/月供.*?(\d+,?\d*)元/i)
  const totalCostMatch = content.match(/总支出.*?(\d+)万元/i)

  if (downPaymentMatch) {
    metrics.push({
      key: 'downPayment',
      value: `${downPaymentMatch[1]}万元`,
      label: '首付金额',
      description: '20%，需自有资金'
    })
  }

  if (monthlyPaymentMatch) {
    metrics.push({
      key: 'monthlyPayment',
      value: `${monthlyPaymentMatch[1]}元`,
      label: '月供金额',
      description: '25年等额本息'
    })
  }

  if (totalCostMatch) {
    metrics.push({
      key: 'totalCost',
      value: `${totalCostMatch[1]}万元`,
      label: '总费用',
      description: '含税费和中介费'
    })
  }

  return metrics
})

const quickFacts = computed(() => {
  const content = props.reportData?.content || ''
  const facts = []

  if (content.includes('首套房')) {
    facts.push({
      key: 'firstHome',
      icon: 'House',
      text: '符合首套房认定标准'
    })
  }

  if (content.includes('组合贷')) {
    facts.push({
      key: 'loan',
      icon: 'CreditCard',
      text: '建议使用组合贷款'
    })
  }

  if (content.includes('满五唯一')) {
    facts.push({
      key: 'tax',
      icon: 'Discount',
      text: '选择满五唯一房源可省税费'
    })
  }

  return facts
})

const expertTips = computed(() => {
  const content = props.reportData?.content || ''
  const tips = []

  if (content.includes('社保不能断')) {
    tips.push('女方社保缴费不能中断，否则影响购房资格')
  }

  if (content.includes('中介费可谈')) {
    tips.push('中介费通常可以协商，900万房价约可省3-5万元')
  }

  if (content.includes('审批较慢')) {
    tips.push('组合贷审批时间较长，签约时需预留1-2个月时间')
  }

  if (content.includes('月供压力')) {
    tips.push('月收入建议达到月供的2倍以上，确保还款安全')
  }

  return tips
})

// 事件处理函数
const handleViewFullReport = () => {
  emit('view-detail')
}

const handleShare = () => {
  emit('share')
}

const handleDownload = () => {
  emit('download')
}

const handleRestart = () => {
  emit('restart')
}

const handleContinueChat = () => {
  emit('continue-chat')
}

// 生命周期
onMounted(() => {
  console.log('报告视图已加载:', props.reportData)

  // 如果reportData包含原始内容，设置到rawContent
  if (props.reportData?.content) {
    rawContent.value = props.reportData.content
  }
})
</script>

<style scoped>
.report-view {
  max-width: 100%;
}

.section-title {
  @apply text-xl font-semibold text-gray-900 mb-4 flex items-center;
}

.section-title::before {
  content: '';
  @apply w-1 h-6 bg-primary-600 rounded-full mr-3;
}

.metrics-grid {
  @apply grid grid-cols-1 md:grid-cols-3 gap-6;
}

.metric-card {
  @apply text-center p-6 bg-gray-50 rounded-lg border border-gray-200 hover:shadow-sm transition-all duration-200;
}

.metric-value {
  @apply text-2xl font-bold text-primary-600 mb-2;
  font-variant-numeric: tabular-nums;
}

.metric-label {
  @apply text-sm font-medium text-gray-700 mb-1;
}

.metric-desc {
  @apply text-xs text-gray-500;
}

.quick-facts {
  @apply grid grid-cols-1 md:grid-cols-3 gap-4;
}

.fact-item {
  @apply flex items-center p-4 bg-green-50 rounded-lg border border-green-200;
}

.fact-icon {
  @apply mr-3 text-green-600 text-lg;
}

.fact-text {
  @apply text-sm text-green-800 font-medium;
}

/* Markdown内容样式 */
.markdown-content :deep(h1) {
  @apply text-2xl font-bold text-gray-900 mb-4 pb-2 border-b border-gray-200;
}

.markdown-content :deep(h2) {
  @apply text-xl font-semibold text-gray-800 mb-3 mt-6;
}

.markdown-content :deep(h3) {
  @apply text-lg font-medium text-gray-700 mb-2 mt-4;
}

.markdown-content :deep(p) {
  @apply text-gray-700 leading-relaxed mb-3;
}

.markdown-content :deep(table) {
  @apply w-full border-collapse border border-gray-200 rounded-lg overflow-hidden mb-4;
}

.markdown-content :deep(th) {
  @apply bg-gray-50 border border-gray-200 px-4 py-3 text-left font-medium text-gray-900;
}

.markdown-content :deep(td) {
  @apply border border-gray-200 px-4 py-3 text-gray-700;
}

.markdown-content :deep(ul) {
  @apply list-disc list-inside mb-4 space-y-1;
}

.markdown-content :deep(li) {
  @apply text-gray-700;
}

.markdown-content :deep(blockquote) {
  @apply border-l-4 border-primary-600 pl-4 py-2 bg-gray-50 rounded-r-lg mb-4 text-gray-700 italic;
}

.markdown-content :deep(strong) {
  @apply font-semibold text-gray-900;
}

.markdown-content :deep(code) {
  @apply bg-gray-100 text-gray-800 px-1 py-0.5 rounded text-sm font-mono;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .metrics-grid,
  .quick-facts {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .action-section .flex {
    flex-direction: column;
    gap: 12px;
  }

  .action-section .el-button {
    width: 100%;
  }

  .metric-card {
    padding: 20px;
  }
}

/* 动画效果 */
.metric-card,
.fact-item {
  animation: fadeInUp 0.3s ease-out;
}

.metric-card:nth-child(1) { animation-delay: 0.1s; }
.metric-card:nth-child(2) { animation-delay: 0.2s; }
.metric-card:nth-child(3) { animation-delay: 0.3s; }

@keyframes fadeInUp {
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