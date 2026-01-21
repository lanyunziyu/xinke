<template>
  <div class="policy-interpretation">
    <div class="mb-4">
      <h4 class="font-medium text-gray-800 mb-2">政策解读</h4>
      <p class="text-sm text-gray-600">相关购房政策的详细解释</p>
    </div>

    <div class="policy-content">
      <el-alert
        :title="policyData.qualification ? '符合购房资格' : '购房资格受限'"
        :type="policyData.qualification ? 'success' : 'warning'"
        show-icon
        :closable="false"
      />

      <div class="mt-4 space-y-3">
        <div>
          <h5 class="font-medium text-gray-700 mb-2">适用政策</h5>
          <ul class="text-sm text-gray-600 space-y-1">
            <li>• 北京市住房限购政策</li>
            <li>• 首套房贷款优惠政策</li>
            <li>• 契税减免政策</li>
          </ul>
        </div>

        <div>
          <h5 class="font-medium text-gray-700 mb-2">注意事项</h5>
          <ul class="text-sm text-gray-600 space-y-1">
            <li>• 需持续缴纳社保或个税60个月</li>
            <li>• 购房资格审核周期约5-7个工作日</li>
            <li>• 贷款利率以银行最新政策为准</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  policyData: {
    type: Object,
    default: () => ({})
  }
})
</script>