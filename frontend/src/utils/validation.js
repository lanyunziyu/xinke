/**
 * 表单验证工具函数
 */

/**
 * 验证是否为空
 * @param {any} value - 要验证的值
 * @returns {boolean} 是否为空
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string') return value.trim() === ''
  if (Array.isArray(value)) return value.length === 0
  if (typeof value === 'object') return Object.keys(value).length === 0
  return false
}

/**
 * 验证数字范围
 * @param {number} value - 要验证的数字
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {boolean} 是否在范围内
 */
export function isNumberInRange(value, min = -Infinity, max = Infinity) {
  if (typeof value !== 'number' || isNaN(value)) return false
  return value >= min && value <= max
}

/**
 * 验证购房预算
 * @param {number} budget - 购房预算（万元）
 * @returns {object} 验证结果
 */
export function validateBudget(budget) {
  if (isEmpty(budget)) {
    return { valid: false, message: '请填写购房预算' }
  }

  const num = Number(budget)
  if (isNaN(num)) {
    return { valid: false, message: '预算必须为数字' }
  }

  if (num <= 0) {
    return { valid: false, message: '预算必须大于0' }
  }

  if (num < 50) {
    return { valid: false, message: '在北京购房预算建议不少于50万元' }
  }

  if (num > 10000) {
    return { valid: false, message: '预算超出合理范围' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证购房区域
 * @param {string} location - 购房区域
 * @returns {object} 验证结果
 */
export function validateLocation(location) {
  if (isEmpty(location)) {
    return { valid: false, message: '请选择意向购房区域' }
  }

  const beijingDistricts = [
    '东城区', '西城区', '朝阳区', '海淀区', '丰台区', '石景山区',
    '通州区', '昌平区', '大兴区', '房山区', '门头沟区', '怀柔区',
    '密云区', '延庆区', '顺义区', '平谷区'
  ]

  const normalizedLocation = location.trim().replace(/区$/, '') + '区'
  if (!beijingDistricts.includes(normalizedLocation)) {
    return { valid: false, message: '请选择北京市内的有效区域' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证婚姻状况
 * @param {string} maritalStatus - 婚姻状况
 * @returns {object} 验证结果
 */
export function validateMaritalStatus(maritalStatus) {
  if (isEmpty(maritalStatus)) {
    return { valid: false, message: '请选择婚姻状况' }
  }

  const validStatuses = ['未婚', '已婚', '离异', '丧偶']
  if (!validStatuses.includes(maritalStatus)) {
    return { valid: false, message: '请选择有效的婚姻状况' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证购房目的
 * @param {string} purpose - 购房目的
 * @returns {object} 验证结果
 */
export function validatePurpose(purpose) {
  if (isEmpty(purpose)) {
    return { valid: false, message: '请选择购房目的' }
  }

  const validPurposes = ['自住', '投资', '改善居住', '过渡居住', '其他']
  if (!validPurposes.includes(purpose)) {
    return { valid: false, message: '请选择有效的购房目的' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证贷款偏好
 * @param {string} loanPreference - 贷款偏好
 * @returns {object} 验证结果
 */
export function validateLoanPreference(loanPreference) {
  if (isEmpty(loanPreference)) {
    return { valid: false, message: '请选择贷款偏好' }
  }

  const validPreferences = ['商贷', '公积金', '组合贷', '全款']
  if (!validPreferences.includes(loanPreference)) {
    return { valid: false, message: '请选择有效的贷款偏好' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证房产数量
 * @param {number} count - 房产数量
 * @returns {object} 验证结果
 */
export function validatePropertyCount(count) {
  if (isEmpty(count) && count !== 0) {
    return { valid: false, message: '请填写房产数量' }
  }

  const num = Number(count)
  if (isNaN(num)) {
    return { valid: false, message: '房产数量必须为数字' }
  }

  if (num < 0) {
    return { valid: false, message: '房产数量不能为负数' }
  }

  if (num > 10) {
    return { valid: false, message: '房产数量超出合理范围' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证户口状态
 * @param {boolean} hasHukou - 是否有户口
 * @returns {object} 验证结果
 */
export function validateHukou(hasHukou) {
  if (hasHukou === null || hasHukou === undefined) {
    return { valid: false, message: '请选择户口状态' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证首套房状态
 * @param {boolean} isFirstHome - 是否首套房
 * @returns {object} 验证结果
 */
export function validateFirstHome(isFirstHome) {
  if (isFirstHome === null || isFirstHome === undefined) {
    return { valid: false, message: '请选择是否为首套房' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证电话号码
 * @param {string} phone - 电话号码
 * @returns {object} 验证结果
 */
export function validatePhone(phone) {
  if (isEmpty(phone)) {
    return { valid: false, message: '请填写电话号码' }
  }

  const phoneRegex = /^1[3-9]\d{9}$/
  if (!phoneRegex.test(phone)) {
    return { valid: false, message: '请填写有效的手机号码' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证身份证号码
 * @param {string} idCard - 身份证号码
 * @returns {object} 验证结果
 */
export function validateIdCard(idCard) {
  if (isEmpty(idCard)) {
    return { valid: false, message: '请填写身份证号码' }
  }

  const idCardRegex = /^[1-9]\d{5}(19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dX]$/
  if (!idCardRegex.test(idCard)) {
    return { valid: false, message: '请填写有效的身份证号码' }
  }

  return { valid: true, message: '' }
}

/**
 * 验证完整的用户画像
 * @param {object} userProfile - 用户画像对象
 * @returns {object} 验证结果
 */
export function validateUserProfile(userProfile) {
  const errors = {}

  // 验证身份信息
  if (userProfile.identity_info) {
    const { male_beijing_hukou, female_beijing_hukou, marital_status } = userProfile.identity_info

    const maleHukouResult = validateHukou(male_beijing_hukou)
    if (!maleHukouResult.valid) {
      errors['identity_info.male_beijing_hukou'] = maleHukouResult.message
    }

    const femaleHukouResult = validateHukou(female_beijing_hukou)
    if (!femaleHukouResult.valid) {
      errors['identity_info.female_beijing_hukou'] = femaleHukouResult.message
    }

    const maritalResult = validateMaritalStatus(marital_status)
    if (!maritalResult.valid) {
      errors['identity_info.marital_status'] = maritalResult.message
    }
  }

  // 验证居住状况
  if (userProfile.residence_status) {
    const { properties_in_beijing, properties_nationwide } = userProfile.residence_status

    const beijingPropertiesResult = validatePropertyCount(properties_in_beijing)
    if (!beijingPropertiesResult.valid) {
      errors['residence_status.properties_in_beijing'] = beijingPropertiesResult.message
    }

    if (properties_nationwide !== null && properties_nationwide !== undefined) {
      const nationwidePropertiesResult = validatePropertyCount(properties_nationwide)
      if (!nationwidePropertiesResult.valid) {
        errors['residence_status.properties_nationwide'] = nationwidePropertiesResult.message
      }
    }
  }

  // 验证购房需求
  if (userProfile.purchase_needs) {
    const { purpose, is_first_home } = userProfile.purchase_needs

    const purposeResult = validatePurpose(purpose)
    if (!purposeResult.valid) {
      errors['purchase_needs.purpose'] = purposeResult.message
    }

    const firstHomeResult = validateFirstHome(is_first_home)
    if (!firstHomeResult.valid) {
      errors['purchase_needs.is_first_home'] = firstHomeResult.message
    }
  }

  // 验证预算
  const budgetResult = validateBudget(userProfile.budget)
  if (!budgetResult.valid) {
    errors['budget'] = budgetResult.message
  }

  // 验证核心需求
  if (userProfile.core_requirements) {
    const { loan_preference } = userProfile.core_requirements

    const loanResult = validateLoanPreference(loan_preference)
    if (!loanResult.valid) {
      errors['core_requirements.loan_preference'] = loanResult.message
    }
  }

  // 验证区域
  const locationResult = validateLocation(userProfile.location)
  if (!locationResult.valid) {
    errors['location'] = locationResult.message
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  }
}

/**
 * 获取缺失的必填字段
 * @param {object} userProfile - 用户画像对象
 * @returns {array} 缺失字段列表
 */
export function getMissingRequiredFields(userProfile) {
  const requiredFields = [
    'identity_info.male_beijing_hukou',
    'identity_info.female_beijing_hukou',
    'identity_info.marital_status',
    'residence_status.properties_in_beijing',
    'purchase_needs.purpose',
    'purchase_needs.is_first_home',
    'budget',
    'core_requirements.loan_preference',
    'location'
  ]

  const missingFields = []

  requiredFields.forEach(field => {
    const value = getNestedValue(userProfile, field)
    if (value === null || value === undefined || value === '') {
      missingFields.push(field)
    }
  })

  return missingFields
}

/**
 * 获取嵌套对象的值
 * @param {object} obj - 对象
 * @param {string} path - 路径字符串（如 'a.b.c'）
 * @returns {any} 值
 */
function getNestedValue(obj, path) {
  return path.split('.').reduce((current, key) => {
    return current && current[key] !== undefined ? current[key] : null
  }, obj)
}

/**
 * 批量验证表单字段
 * @param {object} formData - 表单数据
 * @param {object} rules - 验证规则
 * @returns {object} 验证结果
 */
export function validateForm(formData, rules) {
  const errors = {}

  for (const field in rules) {
    const fieldRules = Array.isArray(rules[field]) ? rules[field] : [rules[field]]
    const value = formData[field]

    for (const rule of fieldRules) {
      if (typeof rule === 'function') {
        const result = rule(value)
        if (!result.valid) {
          errors[field] = result.message
          break
        }
      }
    }
  }

  return {
    valid: Object.keys(errors).length === 0,
    errors
  }
}

/**
 * 创建验证规则
 * @param {function} validator - 验证函数
 * @param {string} message - 错误消息
 * @returns {function} 验证规则函数
 */
export function createRule(validator, message) {
  return (value) => {
    const isValid = validator(value)
    return {
      valid: isValid,
      message: isValid ? '' : message
    }
  }
}

// 常用验证规则
export const rules = {
  required: (message = '此字段为必填项') => createRule(value => !isEmpty(value), message),
  minLength: (min, message) => createRule(value => !value || value.length >= min, message || `最少需要${min}个字符`),
  maxLength: (max, message) => createRule(value => !value || value.length <= max, message || `最多只能${max}个字符`),
  pattern: (regex, message) => createRule(value => !value || regex.test(value), message || '格式不正确'),
  range: (min, max, message) => createRule(value => !value || isNumberInRange(Number(value), min, max), message || `值必须在${min}到${max}之间`)
}