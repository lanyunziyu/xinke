<template>
  <div class="cost-breakdown">
    <div class="mb-4">
      <h4 class="font-medium text-gray-800 mb-2">资金构成明细</h4>
      <p class="text-sm text-gray-600">详细的购房成本分解，帮助您了解资金流向</p>
    </div>

    <div class="cost-items space-y-3">
      <div class="cost-item">
        <div class="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-blue-500 rounded-full mr-3"></div>
            <span class="font-medium">首付金额</span>
          </div>
          <span class="font-semibold text-blue-600">{{ formatMoney(costData.downPayment) }}</span>
        </div>
      </div>

      <div class="cost-item">
        <div class="flex justify-between items-center p-3 bg-green-50 rounded-lg">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
            <span class="font-medium">贷款金额</span>
          </div>
          <span class="font-semibold text-green-600">{{ formatMoney(costData.loanAmount) }}</span>
        </div>
      </div>

      <div class="cost-item">
        <div class="flex justify-between items-center p-3 bg-orange-50 rounded-lg">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-orange-500 rounded-full mr-3"></div>
            <span class="font-medium">税费</span>
          </div>
          <span class="font-semibold text-orange-600">{{ formatMoney(costData.taxes) }}</span>
        </div>
      </div>

      <div class="cost-item">
        <div class="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
          <div class="flex items-center">
            <div class="w-3 h-3 bg-purple-500 rounded-full mr-3"></div>
            <span class="font-medium">其他费用</span>
          </div>
          <span class="font-semibold text-purple-600">{{ formatMoney(costData.fees) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatMoney } from '../../utils/format'

defineProps({
  costData: {
    type: Object,
    default: () => ({})
  }
})
</script>