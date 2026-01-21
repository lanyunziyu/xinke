<template>
  <div class="timeline">
    <div class="mb-4">
      <h4 class="font-medium text-gray-800 mb-2">购房时间规划</h4>
      <p class="text-sm text-gray-600">建议的购房流程和时间安排</p>
    </div>

    <div class="timeline-list">
      <div
        v-for="(item, index) in timelineData"
        :key="index"
        class="timeline-item flex items-start mb-4"
      >
        <div class="timeline-marker flex-shrink-0 w-8 h-8 rounded-full border-2 flex items-center justify-center mr-4"
             :class="getMarkerClass(item.status)">
          <span class="text-xs font-medium">{{ index + 1 }}</span>
        </div>
        <div class="timeline-content flex-1">
          <div class="flex justify-between items-center mb-1">
            <h5 class="font-medium text-gray-800">{{ item.phase }}</h5>
            <span class="text-sm text-gray-500">{{ item.duration }}</span>
          </div>
          <p class="text-sm text-gray-600">{{ getPhaseDescription(item.phase) }}</p>
        </div>
      </div>
    </div>

    <div class="timeline-summary mt-6 p-4 bg-green-50 rounded-lg">
      <h5 class="font-medium text-green-900 mb-2">总体时间规划</h5>
      <p class="text-sm text-green-800">
        整个购房流程预计需要3-4个月时间。建议提前做好资金准备，关注市场动态，
        选择合适的时机入市。
      </p>
    </div>
  </div>
</template>

<script setup>
defineProps({
  timelineData: {
    type: Array,
    default: () => []
  }
})

const getMarkerClass = (status) => {
  switch (status) {
    case 'completed':
      return 'bg-green-100 border-green-400 text-green-700'
    case 'current':
      return 'bg-blue-100 border-blue-400 text-blue-700'
    default:
      return 'bg-gray-100 border-gray-300 text-gray-600'
  }
}

const getPhaseDescription = (phase) => {
  const descriptions = {
    '资金准备': '准备首付资金，整理相关证明材料',
    '看房选房': '实地考察房源，比较不同楼盘',
    '签约付款': '签订购房合同，支付首付款',
    '贷款审批': '提交贷款申请，等待银行审批',
    '过户交房': '办理过户手续，验收交房'
  }
  return descriptions[phase] || ''
}
</script>

<style scoped>
.timeline-item::before {
  content: '';
  position: absolute;
  left: 15px;
  top: 32px;
  width: 2px;
  height: calc(100% - 16px);
  background-color: #e5e7eb;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-list {
  position: relative;
}
</style>