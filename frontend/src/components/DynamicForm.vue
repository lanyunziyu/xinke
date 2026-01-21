<template>
  <div class="dynamic-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="140px"
      label-position="left"
    >
      <!-- 动态字段渲染 -->
      <div v-for="field in fieldConfigs" :key="field.key" class="form-field-group">
        <!-- 文本输入字段 -->
        <el-form-item
          v-if="field.type === 'input'"
          :label="field.label"
          :prop="field.key"
          :required="field.required"
        >
          <el-input
            v-model="formData[field.key]"
            :placeholder="field.placeholder"
            :maxlength="field.maxLength"
            :show-word-limit="field.showWordLimit"
            @change="handleFieldChange(field.key, formData[field.key])"
          />
        </el-form-item>

        <!-- 数字输入字段 -->
        <el-form-item
          v-else-if="field.type === 'number'"
          :label="field.label"
          :prop="field.key"
          :required="field.required"
        >
          <el-input-number
            v-model="formData[field.key]"
            :min="field.min"
            :max="field.max"
            :step="field.step"
            :precision="field.precision"
            :placeholder="field.placeholder"
            style="width: 100%"
            controls-position="right"
            @change="handleFieldChange(field.key, formData[field.key])"
          />
          <span v-if="field.suffix" class="field-suffix">{{ field.suffix }}</span>
        </el-form-item>

        <!-- 选择器字段 -->
        <el-form-item
          v-else-if="field.type === 'select'"
          :label="field.label"
          :prop="field.key"
          :required="field.required"
        >
          <el-select
            v-model="formData[field.key]"
            :placeholder="field.placeholder"
            style="width: 100%"
            :filterable="field.filterable"
            :multiple="field.multiple"
            :collapse-tags="field.multiple"
            @change="handleFieldChange(field.key, formData[field.key])"
          >
            <el-option
              v-for="option in field.options"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>

        <!-- 单选框字段 -->
        <el-form-item
          v-else-if="field.type === 'radio'"
          :label="field.label"
          :prop="field.key"
          :required="field.required"
        >
          <el-radio-group
            v-model="formData[field.key]"
            @change="handleFieldChange(field.key, formData[field.key])"
          >
            <el-radio
              v-for="option in field.options"
              :key="option.value"
              :label="option.value"
            >
              {{ option.label }}
            </el-radio>
          </el-radio-group>
          <div v-if="field.help" class="field-help">
            {{ field.help }}
          </div>
        </el-form-item>

        <!-- 复选框字段 -->
        <el-form-item
          v-else-if="field.type === 'checkbox'"
          :label="field.label"
          :prop="field.key"
          :required="field.required"
        >
          <el-checkbox-group
            v-model="formData[field.key]"
            @change="handleFieldChange(field.key, formData[field.key])"
          >
            <el-checkbox
              v-for="option in field.options"
              :key="option.value"
              :label="option.value"
            >
              {{ option.label }}
            </el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <!-- 开关字段 -->
        <el-form-item
          v-else-if="field.type === 'switch'"
          :label="field.label"
          :prop="field.key"
          :required="field.required"
        >
          <el-switch
            v-model="formData[field.key]"
            :active-text="field.activeText"
            :inactive-text="field.inactiveText"
            @change="handleFieldChange(field.key, formData[field.key])"
          />
        </el-form-item>

        <!-- 文本域字段 -->
        <el-form-item
          v-else-if="field.type === 'textarea'"
          :label="field.label"
          :prop="field.key"
          :required="field.required"
        >
          <el-input
            v-model="formData[field.key]"
            type="textarea"
            :rows="field.rows || 3"
            :placeholder="field.placeholder"
            :maxlength="field.maxLength"
            :show-word-limit="field.showWordLimit"
            @change="handleFieldChange(field.key, formData[field.key])"
          />
        </el-form-item>

        <!-- 日期选择字段 -->
        <el-form-item
          v-else-if="field.type === 'date'"
          :label="field.label"
          :prop="field.key"
          :required="field.required"
        >
          <el-date-picker
            v-model="formData[field.key]"
            :type="field.dateType || 'date'"
            :placeholder="field.placeholder"
            style="width: 100%"
            @change="handleFieldChange(field.key, formData[field.key])"
          />
        </el-form-item>
      </div>

      <!-- 提交按钮 -->
      <el-form-item class="form-submit-section">
        <div class="flex justify-center space-x-4">
          <el-button
            type="primary"
            :loading="loading"
            :disabled="!canSubmit"
            @click="handleSubmit"
          >
            <el-icon class="mr-2"><Check /></el-icon>
            {{ loading ? '提交中...' : '提交信息' }}
          </el-button>

          <el-button
            plain
            @click="handleReset"
            :disabled="loading"
          >
            <el-icon class="mr-2"><RefreshLeft /></el-icon>
            重置
          </el-button>
        </div>
      </el-form-item>
    </el-form>

    <!-- 字段说明 -->
    <div v-if="hasFieldHelp" class="field-explanations mt-4 p-4 bg-blue-50 rounded-lg">
      <h4 class="font-medium text-blue-900 mb-2 flex items-center">
        <el-icon class="mr-2"><InfoFilled /></el-icon>
        字段说明
      </h4>
      <ul class="text-sm text-blue-800 space-y-1">
        <li v-for="field in fieldConfigs" :key="field.key">
          <span v-if="field.description">
            <strong>{{ field.label }}:</strong> {{ field.description }}
          </span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  fields: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  initialData: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['submit', 'field-change', 'reset'])

// 表单引用
const formRef = ref()

// 表单数据
const formData = reactive({})

// 字段配置映射
const fieldConfigMap = {
  'identity_info.male_beijing_hukou': {
    key: 'male_beijing_hukou',
    type: 'radio',
    label: '男方北京户口',
    placeholder: '请选择',
    required: true,
    options: [
      { label: '是', value: true },
      { label: '否', value: false }
    ],
    help: '男方是否拥有北京户口',
    description: '影响购房资格和贷款政策'
  },
  'identity_info.female_beijing_hukou': {
    key: 'female_beijing_hukou',
    type: 'radio',
    label: '女方北京户口',
    placeholder: '请选择',
    required: true,
    options: [
      { label: '是', value: true },
      { label: '否', value: false }
    ],
    help: '女方是否拥有北京户口',
    description: '影响购房资格和贷款政策'
  },
  'identity_info.marital_status': {
    key: 'marital_status',
    type: 'select',
    label: '婚姻状况',
    placeholder: '请选择婚姻状况',
    required: true,
    options: [
      { label: '未婚', value: '未婚' },
      { label: '已婚', value: '已婚' },
      { label: '离异', value: '离异' },
      { label: '丧偶', value: '丧偶' }
    ],
    description: '影响购房政策适用条件'
  },
  'identity_info.purchase_as_married': {
    key: 'purchase_as_married',
    type: 'switch',
    label: '以已婚状态购房',
    activeText: '是',
    inactiveText: '否',
    description: '是否计划以已婚状态进行购房'
  },
  'residence_status.properties_in_beijing': {
    key: 'properties_in_beijing',
    type: 'number',
    label: '北京房产数量',
    placeholder: '请填写',
    required: true,
    min: 0,
    max: 10,
    step: 1,
    suffix: '套',
    description: '您在北京名下的房产数量，影响购房资格认定'
  },
  'residence_status.properties_nationwide': {
    key: 'properties_nationwide',
    type: 'number',
    label: '全国房产数量',
    placeholder: '请填写',
    min: 0,
    max: 20,
    step: 1,
    suffix: '套',
    description: '全国范围内名下房产总数'
  },
  'purchase_needs.purpose': {
    key: 'purpose',
    type: 'select',
    label: '购房目的',
    placeholder: '请选择购房目的',
    required: true,
    options: [
      { label: '自住', value: '自住' },
      { label: '改善居住', value: '改善居住' },
      { label: '投资', value: '投资' },
      { label: '过渡居住', value: '过渡居住' },
      { label: '其他', value: '其他' }
    ],
    description: '购房的主要目的，影响税费和贷款政策'
  },
  'purchase_needs.is_first_home': {
    key: 'is_first_home',
    type: 'radio',
    label: '首套房状态',
    required: true,
    options: [
      { label: '是首套房', value: true },
      { label: '不是首套房', value: false }
    ],
    description: '首套房享受更优惠的贷款政策'
  },
  'budget': {
    key: 'budget',
    type: 'number',
    label: '购房预算',
    placeholder: '请填写预算',
    required: true,
    min: 50,
    max: 10000,
    step: 50,
    suffix: '万元',
    description: '总的购房预算，包括首付和贷款总额'
  },
  'core_requirements.loan_preference': {
    key: 'loan_preference',
    type: 'select',
    label: '贷款偏好',
    placeholder: '请选择贷款方式',
    required: true,
    options: [
      { label: '商业贷款', value: '商贷' },
      { label: '公积金贷款', value: '公积金' },
      { label: '组合贷款', value: '组合贷' },
      { label: '全款购买', value: '全款' }
    ],
    description: '不同贷款方式有不同的利率和政策'
  },
  'core_requirements.concerns': {
    key: 'concerns',
    type: 'checkbox',
    label: '关注问题',
    options: [
      { label: '首付资金准备', value: '首付资金准备' },
      { label: '月供负担', value: '月供负担' },
      { label: '税费成本', value: '税费成本' },
      { label: '购房资格', value: '购房资格' },
      { label: '贷款额度', value: '贷款额度' },
      { label: '利率优惠', value: '利率优惠' },
      { label: '政策变化', value: '政策变化' },
      { label: '投资回报', value: '投资回报' }
    ],
    description: '您最关心的购房相关问题，我们会重点分析'
  },
  'location': {
    key: 'location',
    type: 'select',
    label: '意向区域',
    placeholder: '请选择区域',
    required: true,
    filterable: true,
    options: [
      { label: '东城区', value: '东城区' },
      { label: '西城区', value: '西城区' },
      { label: '朝阳区', value: '朝阳区' },
      { label: '海淀区', value: '海淀区' },
      { label: '丰台区', value: '丰台区' },
      { label: '石景山区', value: '石景山区' },
      { label: '通州区', value: '通州区' },
      { label: '昌平区', value: '昌平区' },
      { label: '大兴区', value: '大兴区' },
      { label: '房山区', value: '房山区' },
      { label: '门头沟区', value: '门头沟区' },
      { label: '怀柔区', value: '怀柔区' },
      { label: '密云区', value: '密云区' },
      { label: '延庆区', value: '延庆区' },
      { label: '顺义区', value: '顺义区' },
      { label: '平谷区', value: '平谷区' }
    ],
    description: '您希望购房的区域，不同区域有不同政策'
  }
}

// 计算属性
const fieldConfigs = computed(() => {
  return props.fields.map(fieldPath => {
    const config = fieldConfigMap[fieldPath]
    if (!config) {
      console.warn(`未找到字段配置: ${fieldPath}`)
      return {
        key: fieldPath,
        type: 'input',
        label: fieldPath,
        required: false
      }
    }
    return config
  }).filter(Boolean)
})

const formRules = computed(() => {
  const rules = {}
  fieldConfigs.value.forEach(field => {
    if (field.required) {
      rules[field.key] = [
        { required: true, message: `请填写${field.label}`, trigger: 'change' }
      ]
    }
  })
  return rules
})

const canSubmit = computed(() => {
  // 检查所有必填字段是否已填写
  return fieldConfigs.value
    .filter(field => field.required)
    .every(field => {
      const value = formData[field.key]
      return value !== null && value !== undefined && value !== '' &&
             !(Array.isArray(value) && value.length === 0)
    })
})

const hasFieldHelp = computed(() => {
  return fieldConfigs.value.some(field => field.description)
})

// 事件处理函数
const handleFieldChange = (field, value) => {
  emit('field-change', field, value)
}

const handleSubmit = async () => {
  if (!formRef.value) return

  try {
    const valid = await formRef.value.validate()
    if (valid) {
      // 转换数据格式，将平铺的数据转换为嵌套结构
      const submissionData = convertToNestedData(formData)
      emit('submit', submissionData)
    }
  } catch (error) {
    ElMessage.warning('请检查表单输入')
  }
}

const handleReset = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
  // 重置表单数据
  Object.keys(formData).forEach(key => {
    if (Array.isArray(formData[key])) {
      formData[key] = []
    } else {
      formData[key] = null
    }
  })
  emit('reset')
}

// 辅助函数
const convertToNestedData = (flatData) => {
  const nested = {}

  // 根据字段配置转换数据结构
  props.fields.forEach(fieldPath => {
    const config = fieldConfigMap[fieldPath]
    if (!config) return

    const value = flatData[config.key]
    if (value === null || value === undefined) return

    const pathParts = fieldPath.split('.')
    let current = nested

    for (let i = 0; i < pathParts.length - 1; i++) {
      const part = pathParts[i]
      if (!current[part]) {
        current[part] = {}
      }
      current = current[part]
    }

    current[pathParts[pathParts.length - 1]] = value
  })

  return nested
}

const initializeFormData = () => {
  // 初始化表单数据
  fieldConfigs.value.forEach(field => {
    if (field.type === 'checkbox') {
      formData[field.key] = []
    } else {
      formData[field.key] = null
    }
  })

  // 应用初始数据
  if (props.initialData) {
    Object.keys(props.initialData).forEach(key => {
      if (formData.hasOwnProperty(key)) {
        formData[key] = props.initialData[key]
      }
    })
  }
}

// 监听字段变化，重新初始化表单数据
watch(
  () => props.fields,
  () => {
    initializeFormData()
  },
  { immediate: true }
)

// 监听初始数据变化
watch(
  () => props.initialData,
  (newData) => {
    if (newData) {
      Object.keys(newData).forEach(key => {
        if (formData.hasOwnProperty(key)) {
          formData[key] = newData[key]
        }
      })
    }
  },
  { deep: true }
)

// 组件挂载时初始化
onMounted(() => {
  initializeFormData()
})
</script>

<style scoped>
.dynamic-form {
  max-width: 100%;
}

.form-field-group {
  margin-bottom: 20px;
}

.field-suffix {
  margin-left: 8px;
  color: #6b7280;
  font-size: 14px;
}

.field-help {
  margin-top: 4px;
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

.form-submit-section {
  margin-top: 32px;
  border-top: 1px solid #e5e7eb;
  padding-top: 24px;
}

.field-explanations {
  border-left: 4px solid #3b82f6;
}

/* 表单项样式调整 */
:deep(.el-form-item__label) {
  color: #374151;
  font-weight: 500;
}

:deep(.el-form-item__error) {
  color: #ef4444;
  font-size: 12px;
}

/* 输入框样式 */
:deep(.el-input__inner) {
  transition: all 0.2s ease;
}

:deep(.el-input__inner:focus) {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
}

/* 数字输入框样式 */
:deep(.el-input-number .el-input__inner) {
  text-align: left;
}

/* 选择器样式 */
:deep(.el-select .el-input__inner:focus) {
  border-color: #3b82f6;
}

/* 单选框样式 */
:deep(.el-radio__input.is-checked .el-radio__inner) {
  border-color: #3b82f6;
  background-color: #3b82f6;
}

:deep(.el-radio__input.is-checked + .el-radio__label) {
  color: #3b82f6;
}

/* 复选框样式 */
:deep(.el-checkbox__input.is-checked .el-checkbox__inner) {
  border-color: #3b82f6;
  background-color: #3b82f6;
}

:deep(.el-checkbox__input.is-checked + .el-checkbox__label) {
  color: #3b82f6;
}

/* 开关样式 */
:deep(.el-switch.is-checked .el-switch__core) {
  background-color: #3b82f6;
}

/* 响应式调整 */
@media (max-width: 768px) {
  :deep(.el-form-item) {
    flex-direction: column;
  }

  :deep(.el-form-item__label) {
    width: 100% !important;
    margin-bottom: 8px;
    text-align: left;
  }

  .field-explanations {
    padding: 12px;
  }
}
</style>