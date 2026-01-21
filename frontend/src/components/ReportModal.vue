<template>
  <el-dialog
    v-model="isVisible"
    title="完整购房方案报告"
    :width="dialogWidth"
    :fullscreen="isFullscreen"
    :close-on-click-modal="false"
    :close-on-press-escape="true"
    destroy-on-close
    class="report-modal"
  >
    <!-- 头部工具栏 -->
    <template #header>
      <div class="dialog-header flex items-center justify-between">
        <div class="header-left flex items-center">
          <el-icon class="mr-2 text-primary-600"><Document /></el-icon>
          <span class="text-lg font-semibold">完整购房方案报告</span>
          <el-tag type="success" size="small" class="ml-2">已生成</el-tag>
        </div>

        <div class="header-actions flex items-center space-x-2">
          <!-- 工具按钮 -->
          <el-tooltip content="全屏显示">
            <el-button
              circle
              size="small"
              @click="toggleFullscreen"
            >
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </el-tooltip>

          <el-tooltip content="打印报告">
            <el-button
              circle
              size="small"
              @click="handlePrint"
            >
              <el-icon><Printer /></el-icon>
            </el-button>
          </el-tooltip>

          <el-tooltip content="下载PDF">
            <el-button
              type="primary"
              circle
              size="small"
              @click="handleDownload"
            >
              <el-icon><Download /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
      </div>
    </template>

    <!-- 报告内容 -->
    <div class="report-content" ref="reportContentRef">
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state flex items-center justify-center py-20">
        <el-icon class="animate-spin mr-2 text-2xl text-primary-600"><Loading /></el-icon>
        <span class="text-gray-600">正在加载完整报告...</span>
      </div>

      <!-- 报告主体 -->
      <div v-else class="report-body">
        <!-- 报告标题页 -->
        <div class="report-title-page mb-8 text-center">
          <h1 class="text-3xl font-bold text-gray-900 mb-4">购房资金方案报告</h1>
          <div class="text-lg text-gray-600 mb-2">{{ userInfo }}</div>
          <div class="text-sm text-gray-500">报告生成时间：{{ generateTime }}</div>
          <div class="w-24 h-1 bg-primary-600 mx-auto mt-4 rounded"></div>
        </div>

        <!-- 执行摘要 -->
        <section class="report-section mb-8">
          <h2 class="section-title">执行摘要</h2>
          <div class="section-content bg-gradient-to-r from-blue-50 to-indigo-50 p-6 rounded-lg">
            <div class="summary-grid grid grid-cols-1 md:grid-cols-3 gap-6 mb-4">
              <div class="summary-item text-center">
                <div class="text-2xl font-bold text-blue-600">{{ formatMoney(summary.downPayment) }}</div>
                <div class="text-sm text-gray-600">需准备首付</div>
              </div>
              <div class="summary-item text-center">
                <div class="text-2xl font-bold text-green-600">{{ formatMoney(summary.monthlyPayment) }}</div>
                <div class="text-sm text-gray-600">月供金额</div>
              </div>
              <div class="summary-item text-center">
                <div class="text-2xl font-bold text-orange-600">{{ summary.qualification ? '符合' : '受限' }}</div>
                <div class="text-sm text-gray-600">购房资格</div>
              </div>
            </div>
            <p class="text-gray-700 leading-relaxed">{{ summary.description }}</p>
          </div>
        </section>

        <!-- 详细分析 -->
        <section class="report-section mb-8">
          <h2 class="section-title">详细分析</h2>

          <!-- 成本构成 -->
          <div class="subsection mb-6">
            <h3 class="subsection-title">资金构成</h3>
            <div class="cost-table">
              <table class="w-full border-collapse">
                <thead>
                  <tr class="bg-gray-50">
                    <th class="table-header">费用项目</th>
                    <th class="table-header">金额</th>
                    <th class="table-header">占比</th>
                    <th class="table-header">说明</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in costBreakdown" :key="item.name" class="border-b">
                    <td class="table-cell font-medium">{{ item.name }}</td>
                    <td class="table-cell text-right">{{ formatMoney(item.amount) }}</td>
                    <td class="table-cell text-right">{{ item.percentage }}%</td>
                    <td class="table-cell text-gray-600">{{ item.description }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 贷款方案 -->
          <div class="subsection mb-6">
            <h3 class="subsection-title">贷款方案</h3>
            <div class="loan-details grid grid-cols-1 md:grid-cols-2 gap-6">
              <div class="loan-card p-4 bg-green-50 rounded-lg">
                <h4 class="font-semibold text-green-900 mb-3">推荐方案：组合贷款</h4>
                <ul class="space-y-2 text-sm text-green-800">
                  <li>• 公积金贷款：120万元（利率3.25%）</li>
                  <li>• 商业贷款：680万元（利率4.3%）</li>
                  <li>• 贷款期限：30年</li>
                  <li>• 月供总额：{{ formatMoney(summary.monthlyPayment) }}</li>
                </ul>
              </div>
              <div class="alternative-card p-4 bg-blue-50 rounded-lg">
                <h4 class="font-semibold text-blue-900 mb-3">备选方案：商业贷款</h4>
                <ul class="space-y-2 text-sm text-blue-800">
                  <li>• 商业贷款：800万元（利率4.5%）</li>
                  <li>• 贷款期限：30年</li>
                  <li>• 月供总额：4.05万元</li>
                  <li>• 总利息更高，但审批更快</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 政策解读 -->
          <div class="subsection mb-6">
            <h3 class="subsection-title">政策解读</h3>
            <div class="policy-content space-y-4">
              <div class="policy-item">
                <h4 class="font-medium text-gray-800 mb-2">购房资格</h4>
                <p class="text-gray-600 text-sm leading-relaxed">
                  根据北京市现行政策，您{{ summary.qualification ? '符合' : '暂不符合' }}购房资格条件。
                  {{ summary.qualification
                    ? '可以正常购买住房，享受首套房相关优惠政策。'
                    : '需要满足社保或个税连续缴纳60个月的要求。'
                  }}
                </p>
              </div>
              <div class="policy-item">
                <h4 class="font-medium text-gray-800 mb-2">税费政策</h4>
                <p class="text-gray-600 text-sm leading-relaxed">
                  契税：首套房90平米以下1%，90-144平米1.5%，144平米以上3%；
                  增值税：满2年免征；个人所得税：满5年且唯一住房免征。
                </p>
              </div>
            </div>
          </div>
        </section>

        <!-- 风险提示 -->
        <section class="report-section mb-8">
          <h2 class="section-title">风险提示</h2>
          <div class="risk-content bg-yellow-50 p-6 rounded-lg border border-yellow-200">
            <ul class="space-y-2 text-sm text-yellow-800">
              <li>• 房价波动风险：房地产市场价格存在波动，购房时机需谨慎选择</li>
              <li>• 政策变化风险：购房政策可能调整，建议及时关注最新政策变化</li>
              <li>• 利率风险：贷款利率可能上调，影响月供负担</li>
              <li>• 流动性风险：房产变现周期较长，需确保有足够资金缓冲</li>
            </ul>
          </div>
        </section>

        <!-- 专家建议 -->
        <section class="report-section">
          <h2 class="section-title">专家建议</h2>
          <div class="advice-content space-y-4">
            <div v-for="advice in expertAdvice" :key="advice.id" class="advice-item p-4 bg-gray-50 rounded-lg">
              <div class="flex items-start">
                <el-icon class="mr-3 mt-1 text-primary-600"><Star /></el-icon>
                <div>
                  <h4 class="font-medium text-gray-800 mb-1">{{ advice.title }}</h4>
                  <p class="text-sm text-gray-600 leading-relaxed">{{ advice.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- 报告页脚 -->
        <div class="report-footer mt-12 pt-6 border-t border-gray-200 text-center">
          <div class="text-sm text-gray-500 mb-2">
            本报告由购房资金方案助手AI生成，仅供参考，具体以相关部门最新政策为准
          </div>
          <div class="text-xs text-gray-400">
            报告编号：{{ reportId }} | 生成时间：{{ generateTime }}
          </div>
        </div>
      </div>
    </div>

    <!-- 底部操作栏 -->
    <template #footer>
      <div class="dialog-footer flex justify-center space-x-4">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="info" @click="handlePrint">
          <el-icon class="mr-2"><Printer /></el-icon>
          打印报告
        </el-button>
        <el-button type="primary" @click="handleDownload">
          <el-icon class="mr-2"><Download /></el-icon>
          下载PDF
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { formatMoney, formatDate } from '../utils/format'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  reportData: {
    type: Object,
    default: () => ({})
  },
  reportUrl: {
    type: String,
    default: ''
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'download', 'print'])

// 响应式数据
const loading = ref(false)
const isFullscreen = ref(false)
const reportContentRef = ref()

// 计算属性
const isVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const dialogWidth = computed(() => {
  return isFullscreen.value ? '100%' : '90%'
})

const userInfo = computed(() => {
  const profile = props.reportData?.user_profile
  if (!profile) return '购房方案报告'

  return `${profile.location || '北京'}购房方案 | 预算${formatMoney(profile.budget || 0)}`
})

const generateTime = computed(() => {
  return formatDate(new Date(), 'YYYY-MM-DD HH:mm:ss')
})

const reportId = computed(() => {
  return 'RPT' + Date.now().toString().slice(-8)
})

const summary = computed(() => {
  const solution = props.reportData?.solution
  return {
    downPayment: solution?.down_payment || 300,
    monthlyPayment: solution?.monthly_payment || 3.5,
    qualification: solution?.qualification_status !== false,
    description: solution?.summary || '基于您的购房需求和当前政策，我们为您制定了这套资金方案。该方案充分考虑了您的经济状况和政策环境，旨在帮助您以最优的方式实现购房目标。'
  }
})

const costBreakdown = computed(() => [
  { name: '首付款', amount: 300, percentage: 30, description: '房屋总价的30%' },
  { name: '贷款金额', amount: 700, percentage: 70, description: '银行贷款部分' },
  { name: '契税', amount: 30, percentage: 3, description: '根据房价和面积计算' },
  { name: '公维基金', amount: 5, percentage: 0.5, description: '按房价2%计算' },
  { name: '其他费用', amount: 15, percentage: 1.5, description: '包括评估费、担保费等' }
])

const expertAdvice = computed(() => [
  {
    id: 1,
    title: '资金准备建议',
    content: '建议准备充足的资金缓冲，首付资金基础上额外准备10-15%的备用资金，用于应对突发情况和装修等费用。'
  },
  {
    id: 2,
    title: '贷款选择建议',
    content: '组合贷款虽然手续相对复杂，但能有效降低利息成本。建议优先申请公积金贷款额度，不足部分使用商业贷款。'
  },
  {
    id: 3,
    title: '购房时机建议',
    content: '当前市场相对平稳，建议在资金准备充足的前提下择机入市。重点关注地段、配套和物业品质。'
  },
  {
    id: 4,
    title: '风险管控建议',
    content: '购房前务必核实开发商资质、房屋产权状况。签约时仔细审查合同条款，必要时可寻求专业律师协助。'
  }
])

// 事件处理函数
const handleClose = () => {
  isVisible.value = false
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const handlePrint = () => {
  if (typeof window !== 'undefined') {
    // 创建打印样式
    const printStyles = `
      <style>
        @media print {
          body { font-size: 12px; line-height: 1.4; }
          .report-section { break-inside: avoid; margin-bottom: 20px; }
          .section-title { color: #000 !important; border-bottom: 2px solid #000; }
          table { border-collapse: collapse; width: 100%; }
          th, td { border: 1px solid #000; padding: 8px; }
          .no-print { display: none !important; }
        }
      </style>
    `

    const printWindow = window.open('', '_blank')
    printWindow.document.write(`
      <html>
        <head>
          <title>购房方案报告</title>
          ${printStyles}
        </head>
        <body>
          ${reportContentRef.value.innerHTML}
        </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }

  emit('print')
}

const handleDownload = () => {
  emit('download')
  ElMessage.success('PDF下载已开始')
}

// 监听弹窗打开，模拟加载过程
watch(isVisible, (visible) => {
  if (visible) {
    loading.value = true
    setTimeout(() => {
      loading.value = false
    }, 1500) // 模拟加载时间
  }
})
</script>

<style scoped>
.report-modal {
  --el-dialog-padding-primary: 20px;
}

.dialog-header {
  padding: 0;
}

.report-content {
  max-height: 70vh;
  overflow-y: auto;
  padding: 20px 0;
}

.report-body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.6;
  color: #333;
}

.section-title {
  @apply text-xl font-semibold text-gray-900 mb-4 pb-2 border-b-2 border-primary-600;
}

.subsection-title {
  @apply text-lg font-medium text-gray-800 mb-3;
}

.report-section {
  margin-bottom: 32px;
}

.subsection {
  margin-bottom: 24px;
}

.table-header {
  @apply px-4 py-3 text-left font-medium text-gray-700 border-b border-gray-200;
}

.table-cell {
  @apply px-4 py-3 text-sm border-b border-gray-100;
}

.cost-table table {
  @apply bg-white rounded-lg overflow-hidden shadow-sm border border-gray-200;
}

.loading-state {
  height: 300px;
}

/* 打印样式 */
@media print {
  .report-content {
    max-height: none !important;
    overflow: visible !important;
  }

  .dialog-header,
  .dialog-footer {
    display: none !important;
  }

  .section-title {
    color: #000 !important;
    border-bottom: 2px solid #000 !important;
  }

  .report-section {
    break-inside: avoid;
    margin-bottom: 20px;
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 95% !important;
    margin: 5vh auto !important;
  }

  .summary-grid {
    grid-template-columns: 1fr !important;
    gap: 16px;
  }

  .loan-details {
    grid-template-columns: 1fr !important;
    gap: 16px;
  }

  .dialog-footer .flex {
    flex-direction: column;
    gap: 8px;
  }

  .dialog-footer .el-button {
    width: 100%;
  }
}

/* 滚动条样式 */
.report-content::-webkit-scrollbar {
  width: 8px;
}

.report-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.report-content::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.report-content::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>