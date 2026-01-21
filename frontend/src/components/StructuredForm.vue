<template>
  <div class="structured-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="120px"
      label-position="left"
      class="space-y-4"
    >
      <!-- 基本需求 -->
      <div class="form-section">
        <h3 class="section-title">基本需求</h3>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="意向区域" prop="location">
              <el-select
                v-model="formData.location"
                placeholder="请选择区域"
                style="width: 100%"
                filterable
              >
                <el-option
                  v-for="district in beijingDistricts"
                  :key="district"
                  :label="district"
                  :value="district"
                />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="购房预算" prop="budget">
              <el-input-number
                v-model="formData.budget"
                :min="50"
                :max="10000"
                :step="50"
                style="width: 100%"
                controls-position="right"
              />
              <span class="input-suffix">万元</span>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="购房目的" prop="purpose">
              <el-select v-model="formData.purpose" placeholder="请选择" style="width: 100%">
                <el-option label="自住" value="自住" />
                <el-option label="改善居住" value="改善居住" />
                <el-option label="投资" value="投资" />
                <el-option label="过渡居住" value="过渡居住" />
                <el-option label="其他" value="其他" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="首套房状态" prop="is_first_home">
              <el-radio-group v-model="formData.is_first_home">
                <el-radio :label="true">是首套房</el-radio>
                <el-radio :label="false">非首套房</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 身份信息 -->
      <div class="form-section">
        <h3 class="section-title">身份信息</h3>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="婚姻状况" prop="marital_status">
              <el-select v-model="formData.marital_status" placeholder="请选择" style="width: 100%">
                <el-option label="未婚" value="未婚" />
                <el-option label="已婚" value="已婚" />
                <el-option label="离异" value="离异" />
                <el-option label="丧偶" value="丧偶" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="男方北京户口" prop="male_beijing_hukou">
              <el-radio-group v-model="formData.male_beijing_hukou">
                <el-radio :label="true">是</el-radio>
                <el-radio :label="false">否</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="女方北京户口" prop="female_beijing_hukou">
              <el-radio-group v-model="formData.female_beijing_hukou">
                <el-radio :label="true">是</el-radio>
                <el-radio :label="false">否</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="以已婚状态购房">
              <el-radio-group v-model="formData.purchase_as_married">
                <el-radio :label="true">是</el-radio>
                <el-radio :label="false">否</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 房产状况 -->
      <div class="form-section">
        <h3 class="section-title">房产状况</h3>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="北京房产数量" prop="properties_in_beijing">
              <el-input-number
                v-model="formData.properties_in_beijing"
                :min="0"
                :max="10"
                :step="1"
                style="width: 100%"
                controls-position="right"
              />
              <span class="input-suffix">套</span>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="全国房产数量">
              <el-input-number
                v-model="formData.properties_nationwide"
                :min="0"
                :max="20"
                :step="1"
                style="width: 100%"
                controls-position="right"
              />
              <span class="input-suffix">套</span>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 贷款偏好 -->
      <div class="form-section">
        <h3 class="section-title">贷款偏好</h3>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="贷款方式" prop="loan_preference">
              <el-select v-model="formData.loan_preference" placeholder="请选择" style="width: 100%">
                <el-option label="商业贷款" value="商贷" />
                <el-option label="公积金贷款" value="公积金" />
                <el-option label="组合贷款" value="组合贷" />
                <el-option label="全款购买" value="全款" />
              </el-select>
            </el-form-item>
          </el-col>

          <el-col :span="12">
            <el-form-item label="关注问题">
              <el-select
                v-model="formData.concerns"
                placeholder="请选择关注的问题"
                style="width: 100%"
                multiple
                collapse-tags
                collapse-tags-tooltip
              >
                <el-option label="首付资金准备" value="首付资金准备" />
                <el-option label="月供负担" value="月供负担" />
                <el-option label="税费成本" value="税费成本" />
                <el-option label="购房资格" value="购房资格" />
                <el-option label="贷款额度" value="贷款额度" />
                <el-option label="利率优惠" value="利率优惠" />
                <el-option label="政策变化" value="政策变化" />
                <el-option label="投资回报" value="投资回报" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </div>

      <!-- 表单完整度指示器 -->
      <div class="completion-indicator">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-gray-600">信息完整度</span>
          <span class="text-sm font-medium" :class="completionClass">{{ completionRate }}%</span>
        </div>
        <el-progress
          :percentage="completionRate"
          :color="progressColor"
          :stroke-width="6"
        />
      </div>
    </el-form>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { validateBudget, validateLocation, validateMaritalStatus, validatePurpose, validateLoanPreference, validatePropertyCount, validateHukou, validateFirstHome } from '../utils/validation'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'change'])

// 表单引用
const formRef = ref()

// 表单数据
const formData = ref({
  // 基本需求
  location: '',
  budget: null,
  purpose: '',
  is_first_home: null,

  // 身份信息
  marital_status: '',
  male_beijing_hukou: null,
  female_beijing_hukou: null,
  purchase_as_married: null,

  // 房产状况
  properties_in_beijing: null,
  properties_nationwide: null,

  // 贷款偏好
  loan_preference: '',
  concerns: []
})

// 北京行政区划
const beijingDistricts = ref([
  '东城区', '西城区', '朝阳区', '海淀区', '丰台区', '石景山区',
  '通州区', '昌平区', '大兴区', '房山区', '门头沟区', '怀柔区',
  '密云区', '延庆区', '顺义区', '平谷区'
])

// 表单验证规则
const formRules = {
  location: [
    { required: true, message: '请选择意向区域', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validateLocation(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ],
  budget: [
    { required: true, message: '请填写购房预算', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validateBudget(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ],
  purpose: [
    { required: true, message: '请选择购房目的', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validatePurpose(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ],
  is_first_home: [
    { required: true, message: '请选择首套房状态', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validateFirstHome(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ],
  marital_status: [
    { required: true, message: '请选择婚姻状况', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validateMaritalStatus(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ],
  male_beijing_hukou: [
    { required: true, message: '请选择男方户口状态', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validateHukou(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ],
  female_beijing_hukou: [
    { required: true, message: '请选择女方户口状态', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validateHukou(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ],
  properties_in_beijing: [
    { required: true, message: '请填写北京房产数量', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validatePropertyCount(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ],
  loan_preference: [
    { required: true, message: '请选择贷款方式', trigger: 'change' },
    { validator: (rule, value, callback) => {
      const result = validateLoanPreference(value)
      result.valid ? callback() : callback(new Error(result.message))
    }, trigger: 'change' }
  ]
}

// 计算属性
const completionRate = computed(() => {
  const requiredFields = [
    'location', 'budget', 'purpose', 'is_first_home',
    'marital_status', 'male_beijing_hukou', 'female_beijing_hukou',
    'properties_in_beijing', 'loan_preference'
  ]

  const completedFields = requiredFields.filter(field => {
    const value = formData.value[field]
    return value !== null && value !== undefined && value !== ''
  })

  return Math.round((completedFields.length / requiredFields.length) * 100)
})

const completionClass = computed(() => {
  const rate = completionRate.value
  if (rate >= 90) return 'text-green-600'
  if (rate >= 70) return 'text-yellow-600'
  if (rate >= 50) return 'text-orange-600'
  return 'text-red-600'
})

const progressColor = computed(() => {
  const rate = completionRate.value
  if (rate >= 90) return '#10b981'  // green
  if (rate >= 70) return '#f59e0b'  // yellow
  if (rate >= 50) return '#f97316'  // orange
  return '#ef4444'  // red
})

// 监听表单数据变化
watch(formData, (newData) => {
  emit('update:modelValue', newData)
  emit('change', newData)
}, { deep: true })

// 监听props变化
watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    formData.value = { ...formData.value, ...newValue }
  }
}, { deep: true, immediate: true })

// 暴露表单验证方法
defineExpose({
  validate: () => {
    return new Promise((resolve) => {
      formRef.value.validate((valid) => {
        resolve(valid)
      })
    })
  },
  resetForm: () => {
    formRef.value.resetFields()
  }
})
</script>

<style scoped>
.structured-form {
  max-width: 100%;
}

.form-section {
  @apply mb-8 p-4 bg-gray-50 rounded-lg;
}

.section-title {
  @apply text-lg font-semibold text-gray-800 mb-4 pb-2 border-b border-gray-200;
}

.input-suffix {
  @apply ml-2 text-sm text-gray-500;
}

.completion-indicator {
  @apply mt-6 p-4 bg-blue-50 rounded-lg;
}

/* 表单项样式调整 */
:deep(.el-form-item__label) {
  @apply text-gray-700 font-medium;
}

:deep(.el-form-item__error) {
  @apply text-red-500 text-xs;
}

/* 输入框样式 */
:deep(.el-input__inner) {
  @apply transition-all duration-200;
}

:deep(.el-input__inner:focus) {
  @apply border-primary-500 shadow-sm;
}

/* 选择器样式 */
:deep(.el-select .el-input__inner:focus) {
  @apply border-primary-500;
}

/* 单选框样式 */
:deep(.el-radio__input.is-checked .el-radio__inner) {
  @apply border-primary-600 bg-primary-600;
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  @apply text-primary-600;
}

/* 数字输入框样式 */
:deep(.el-input-number .el-input__inner) {
  text-align: left;
}

/* 多选标签样式 */
:deep(.el-select .el-tag) {
  @apply bg-primary-100 text-primary-700 border-primary-200;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .form-section {
    @apply p-3;
  }

  :deep(.el-col) {
    width: 100% !important;
    margin-bottom: 16px;
  }

  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}</style>