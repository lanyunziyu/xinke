<template>
  <div class="loan-plan">
    <div class="mb-4">
      <h4 class="font-medium text-gray-800 mb-2">贷款方案</h4>
      <p class="text-sm text-gray-600">推荐的贷款方案和还款计划</p>
    </div>

    <div class="loan-details space-y-4">
      <div class="grid grid-cols-2 gap-4">
        <div class="stat-item">
          <div class="text-sm text-gray-500">贷款金额</div>
          <div class="text-lg font-semibold text-gray-900">{{ formatMoney(loanData.loanAmount) }}</div>
        </div>
        <div class="stat-item">
          <div class="text-sm text-gray-500">贷款利率</div>
          <div class="text-lg font-semibold text-gray-900">{{ loanData.interestRate }}%</div>
        </div>
        <div class="stat-item">
          <div class="text-sm text-gray-500">贷款期限</div>
          <div class="text-lg font-semibold text-gray-900">{{ loanData.loanTerm }}年</div>
        </div>
        <div class="stat-item">
          <div class="text-sm text-gray-500">月供金额</div>
          <div class="text-lg font-semibold text-blue-600">{{ formatMoney(loanData.monthlyPayment) }}</div>
        </div>
      </div>

      <div class="loan-recommendation bg-blue-50 p-4 rounded-lg">
        <h5 class="font-medium text-blue-900 mb-2">推荐方案</h5>
        <p class="text-sm text-blue-800">
          基于您的情况，建议选择组合贷款方案，公积金贷款120万元（利率3.25%），商业贷款680万元（利率4.3%），
          可以有效降低利息成本。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatMoney } from '../../utils/format'

defineProps({
  loanData: {
    type: Object,
    default: () => ({})
  }
})
</script>

<style scoped>
.stat-item {
  @apply p-3 bg-gray-50 rounded-lg text-center;
}
</style>