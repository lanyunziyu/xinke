<template>
  <div class="result-display">
    <!-- 成功生成提示 -->
    <div class="success-header mb-6">
      <el-alert
        title="购房方案生成成功！"
        type="success"
        description="基于您的需求和最新政策，我们为您制定了专属的购房资金方案"
        show-icon
        :closable="false"
        class="mb-4"
      />
    </div>

    <!-- 方案概览卡片 -->
    <div class="solution-overview mb-6">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h2 class="text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <el-icon class="mr-2 text-green-600">
            <DocumentChecked />
          </el-icon>
          方案概览
        </h2>

        <!-- 关键数据展示 -->
        <div class="key-metrics grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div class="metric-card">
            <div class="metric-value text-2xl font-bold text-blue-600">
              {{ formatMoney(costSummary.downPayment) }}
            </div>
            <div class="metric-label text-sm text-gray-600 flex items-center">
              <el-icon class="mr-1"><Money /></el-icon>
              首付金额
            </div>
            <div class="metric-detail text-xs text-gray-500 mt-1">
              {{ calculateDownPaymentRatio() }}
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-value text-2xl font-bold text-green-600">
              {{ formatMoney(costSummary.monthlyPayment) }}
            </div>
            <div class="metric-label text-sm text-gray-600 flex items-center">
              <el-icon class="mr-1"><Calendar /></el-icon>
              月供金额
            </div>
            <div class="metric-detail text-xs text-gray-500 mt-1">
              30年期等额本息
            </div>
          </div>

          <div class="metric-card">
            <div class="metric-value text-2xl font-bold text-orange-600">
              {{ formatMoney(costSummary.totalCost) }}
            </div>
            <div class="metric-label text-sm text-gray-600 flex items-center">
              <el-icon class="mr-1"><PieChart /></el-icon>
              总费用
            </div>
            <div class="metric-detail text-xs text-gray-500 mt-1">
              包含税费及相关成本
            </div>
          </div>
        </div>

        <!-- 购房资格状态 -->
        <div class="qualification-status mb-6">
          <div class="flex items-center justify-between p-4 rounded-lg"
               :class="qualificationStatusClass">
            <div class="flex items-center">
              <el-icon class="mr-2 text-lg" :class="qualificationIconClass">
                <component :is="qualificationIcon" />
              </el-icon>
              <div>
                <div class="font-medium">{{ qualificationTitle }}</div>
                <div class="text-sm opacity-90">{{ qualificationDescription }}</div>
              </div>
            </div>
            <el-button v-if="!hasQualification" type="warning" size="small" plain>
              查看解决方案
            </el-button>
          </div>
        </div>

        <!-- 方案摘要 -->
        <div class="solution-summary">
          <h3 class="text-lg font-medium text-gray-800 mb-3 flex items-center">
            <el-icon class="mr-2 text-primary-600"><Reading /></el-icon>
            方案摘要
          </h3>
          <div class="summary-content text-gray-700 leading-relaxed bg-gray-50 p-4 rounded-lg">
            {{ solutionSummary }}
          </div>
        </div>
      </div>
    </div>

    <!-- 详细分析模块 -->
    <div class="detailed-analysis mb-6">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <h3 class="text-lg font-medium text-gray-800 mb-4">详细分析</h3>

        <el-tabs v-model="activeTab" class="analysis-tabs">
          <!-- 成本构成 -->
          <el-tab-pane label="成本构成" name="cost">
            <CostBreakdown :cost-data="costData" />
          </el-tab-pane>

          <!-- 政策解读 -->
          <el-tab-pane label="政策解读" name="policy">
            <PolicyInterpretation :policy-data="policyData" />
          </el-tab-pane>

          <!-- 贷款方案 -->
          <el-tab-pane label="贷款方案" name="loan">
            <LoanPlan :loan-data="loanData" />
          </el-tab-pane>

          <!-- 时间规划 -->
          <el-tab-pane label="时间规划" name="timeline">
            <Timeline :timeline-data="timelineData" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </div>

    <!-- 操作按钮区域 -->
    <div class="action-buttons">
      <div class="bg-white rounded-lg shadow-sm p-6">
        <div class="flex flex-wrap justify-center gap-4">
          <!-- 主要操作 -->
          <el-button
            type="primary"
            size="large"
            @click="handleViewDetail"
            :loading="loading"
          >
            <el-icon class="mr-2"><View /></el-icon>
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

          <!-- 次要操作 -->
          <el-button
            plain
            size="large"
            @click="handleRestart"
          >
            <el-icon class="mr-2"><RefreshRight /></el-icon>
            重新开始
          </el-button>
        </div>

        <!-- 操作提示 -->
        <div class="mt-4 text-center">
          <p class="text-sm text-gray-600">
            报告将保留72小时，建议及时保存。需要调整方案？
            <el-button type="primary" text @click="handleModify">
              点击修改需求
            </el-button>
          </p>
        </div>
      </div>
    </div>

    <!-- 专家建议 -->
    <div class="expert-advice mt-6">
      <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200">
        <h3 class="text-lg font-medium text-blue-900 mb-3 flex items-center">
          <el-icon class="mr-2"><UserFilled /></el-icon>
          专家建议
        </h3>
        <div class="space-y-2">
          <div v-for="advice in expertAdvice" :key="advice.id" class="text-blue-800 text-sm">
            • {{ advice.content }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { formatMoney, formatPercentage } from '../utils/format'
import CostBreakdown from './analysis/CostBreakdown.vue'
import PolicyInterpretation from './analysis/PolicyInterpretation.vue'
import LoanPlan from './analysis/LoanPlan.vue'
import Timeline from './analysis/Timeline.vue'

// Props
const props = defineProps({
  reportData: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['view-detail', 'share', 'download', 'restart', 'modify'])

// 响应式数据
const activeTab = ref('cost')

// 计算属性
const costSummary = computed(() => {
  const solution = props.reportData?.solution
  if (!solution) {
    return {
      downPayment: 0,
      monthlyPayment: 0,
      totalCost: 0
    }
  }

  return {
    downPayment: solution.down_payment || 0,
    monthlyPayment: solution.monthly_payment || 0,
    totalCost: solution.total_cost || 0
  }
})

const solutionSummary = computed(() => {
  return props.reportData?.solution?.summary ||
    '基于您提供的信息，我们为您制定了这套购房资金方案。该方案充分考虑了您的经济状况、购房需求以及当前的政策环境，旨在帮助您以最优的方式实现购房目标。'
})

const hasQualification = computed(() => {
  return props.reportData?.solution?.qualification_status !== false
})

const qualificationStatusClass = computed(() => {
  return hasQualification.value
    ? 'bg-green-100 border border-green-200'
    : 'bg-yellow-100 border border-yellow-200'
})

const qualificationIconClass = computed(() => {
  return hasQualification.value ? 'text-green-600' : 'text-yellow-600'
})

const qualificationIcon = computed(() => {
  return hasQualification.value ? 'CircleCheck' : 'Warning'
})

const qualificationTitle = computed(() => {
  return hasQualification.value ? '符合购房资格' : '购房资格受限'
})

const qualificationDescription = computed(() => {
  return hasQualification.value
    ? '恭喜！您符合在北京的购房资格条件'
    : '根据当前政策，您的购房资格存在一定限制，需要特别注意'
})

// 分析数据
const costData = computed(() => ({
  downPayment: costSummary.value.downPayment,
  loanAmount: 800, // 示例数据
  taxes: 50,
  fees: 30,
  others: 20
}))

const policyData = computed(() => ({
  qualification: hasQualification.value,
  restrictions: ['限购政策', '贷款政策'],
  benefits: ['首套房优惠', '税费减免']
}))

const loanData = computed(() => ({
  loanAmount: 800,
  interestRate: 4.3,
  loanTerm: 30,
  monthlyPayment: costSummary.value.monthlyPayment
}))

const timelineData = computed(() => ([
  { phase: '资金准备', duration: '1-2个月', status: 'pending' },
  { phase: '看房选房', duration: '2-4周', status: 'pending' },
  { phase: '签约付款', duration: '1-2周', status: 'pending' },
  { phase: '贷款审批', duration: '3-4周', status: 'pending' },
  { phase: '过户交房', duration: '2-3周', status: 'pending' }
]))

const expertAdvice = computed(() => [
  {
    id: 1,
    content: '建议提前准备足够的首付资金，留出10-15%的资金缓冲'
  },
  {
    id: 2,
    content: '关注贷款利率变化，适时选择固定利率或浮动利率'
  },
  {
    id: 3,
    content: '购房前务必核实房屋产权状况，避免产生纠纷'
  },
  {
    id: 4,
    content: '考虑房屋的保值增值潜力，选择地段和配套较好的物业'
  }
])

// 事件处理函数
const handleViewDetail = () => {
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

const handleModify = () => {
  emit('modify')
}

// 辅助函数
const calculateDownPaymentRatio = () => {
  const budget = props.reportData?.user_profile?.budget || 1000
  const downPayment = costSummary.value.downPayment || 0
  if (budget === 0) return '0%'

  const ratio = (downPayment / budget) * 100
  return `占总价${formatPercentage(ratio, 0)}`
}

// 组件挂载时的初始化
onMounted(() => {
  console.log('结果展示组件已加载', props.reportData)
})
</script>

<style scoped>
.result-display {
  max-width: 100%;
}

.metric-card {
  @apply text-center p-6 bg-gray-50 rounded-lg border border-gray-200 hover:shadow-sm transition-shadow;
}

.metric-value {
  @apply mb-2;
  font-variant-numeric: tabular-nums;
}

.metric-label {
  @apply font-medium;
}

.qualification-status {
  transition: all 0.2s ease;
}

.analysis-tabs {
  @apply mt-4;
}

:deep(.el-tabs__header) {
  @apply mb-4;
}

:deep(.el-tabs__item) {
  @apply text-gray-600 font-medium;
}

:deep(.el-tabs__item.is-active) {
  @apply text-primary-600 font-semibold;
}

:deep(.el-tabs__active-bar) {
  @apply bg-primary-600;
}

.action-buttons {
  @apply sticky bottom-0 z-10;
  backdrop-filter: blur(10px);
}

.expert-advice {
  animation: slideInUp 0.5s ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .key-metrics {
    grid-template-columns: 1fr;
    gap: 16px;
  }

  .metric-card {
    padding: 20px;
  }

  .action-buttons .flex {
    flex-direction: column;
    gap: 12px;
  }

  .action-buttons .el-button {
    width: 100%;
  }

  .expert-advice {
    margin-top: 20px;
    padding: 16px;
  }
}

/* 渐变动画效果 */
.metric-card {
  animation: fadeInScale 0.3s ease-out;
}

.metric-card:nth-child(1) {
  animation-delay: 0.1s;
}

.metric-card:nth-child(2) {
  animation-delay: 0.2s;
}

.metric-card:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 按钮悬停效果 */
.action-buttons .el-button {
  transition: all 0.2s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-1px);
}
</style>