/**
 * 格式化工具函数
 */

/**
 * 生成唯一请求ID
 * @returns {string} 请求ID
 */
export function generateRequestId() {
  const timestamp = Date.now()
  const random = Math.random().toString(36).substr(2, 9)
  return `req_${timestamp}_${random}`
}

/**
 * 格式化金额（万元）
 * @param {number} amount - 金额
 * @param {boolean} showUnit - 是否显示单位
 * @returns {string} 格式化后的金额
 */
export function formatMoney(amount, showUnit = true) {
  if (!amount || amount === 0) return showUnit ? '0万元' : '0'

  // 如果金额大于10000，转换为亿元
  if (amount >= 10000) {
    const yi = (amount / 10000).toFixed(1)
    return showUnit ? `${yi}亿元` : yi
  }

  // 添加千分位分隔符
  const formatted = amount.toLocaleString()
  return showUnit ? `${formatted}万元` : formatted
}

/**
 * 格式化百分比
 * @param {number} value - 数值（0-100）
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的百分比
 */
export function formatPercentage(value, decimals = 1) {
  if (value === null || value === undefined) return '0%'
  return `${Number(value).toFixed(decimals)}%`
}

/**
 * 格式化日期
 * @param {Date|string|number} date - 日期
 * @param {string} format - 格式（'YYYY-MM-DD' | 'YYYY-MM-DD HH:mm:ss' | 'MM-DD'）
 * @returns {string} 格式化后的日期
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return ''

  const d = new Date(date)
  if (isNaN(d.getTime())) return ''

  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')
  const seconds = String(d.getSeconds()).padStart(2, '0')

  switch (format) {
    case 'YYYY-MM-DD':
      return `${year}-${month}-${day}`
    case 'YYYY-MM-DD HH:mm:ss':
      return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
    case 'MM-DD':
      return `${month}-${day}`
    case 'HH:mm':
      return `${hours}:${minutes}`
    default:
      return d.toLocaleDateString()
  }
}

/**
 * 格式化时间相对描述
 * @param {Date|string|number} date - 日期
 * @returns {string} 相对时间描述
 */
export function formatRelativeTime(date) {
  if (!date) return ''

  const now = new Date()
  const targetDate = new Date(date)
  const diff = now.getTime() - targetDate.getTime()

  const minute = 60 * 1000
  const hour = 60 * minute
  const day = 24 * hour
  const week = 7 * day

  if (diff < minute) {
    return '刚刚'
  } else if (diff < hour) {
    return `${Math.floor(diff / minute)}分钟前`
  } else if (diff < day) {
    return `${Math.floor(diff / hour)}小时前`
  } else if (diff < week) {
    return `${Math.floor(diff / day)}天前`
  } else {
    return formatDate(date, 'YYYY-MM-DD')
  }
}

/**
 * 格式化文件大小
 * @param {number} bytes - 文件大小（字节）
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes) {
  if (bytes === 0) return '0 B'

  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * 格式化电话号码
 * @param {string} phone - 电话号码
 * @returns {string} 格式化后的电话号码
 */
export function formatPhone(phone) {
  if (!phone) return ''

  const cleaned = phone.replace(/\D/g, '')

  if (cleaned.length === 11) {
    return cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1****$3')
  }

  return phone
}

/**
 * 格式化身份证号（脱敏）
 * @param {string} idCard - 身份证号
 * @returns {string} 脱敏后的身份证号
 */
export function formatIdCard(idCard) {
  if (!idCard) return ''

  if (idCard.length === 18) {
    return idCard.replace(/(\d{6})\d{8}(\d{4})/, '$1********$2')
  }

  return idCard
}

/**
 * 格式化房产证编号（脱敏）
 * @param {string} propertyNumber - 房产证编号
 * @returns {string} 脱敏后的房产证编号
 */
export function formatPropertyNumber(propertyNumber) {
  if (!propertyNumber) return ''

  const length = propertyNumber.length
  if (length <= 4) return propertyNumber

  const start = propertyNumber.substr(0, 2)
  const end = propertyNumber.substr(-2)
  const middle = '*'.repeat(length - 4)

  return start + middle + end
}

/**
 * 格式化贷款利率
 * @param {number} rate - 利率（小数形式，如0.05）
 * @returns {string} 格式化后的利率
 */
export function formatInterestRate(rate) {
  if (!rate) return '0%'

  return `${(rate * 100).toFixed(2)}%`
}

/**
 * 格式化面积
 * @param {number} area - 面积（平方米）
 * @returns {string} 格式化后的面积
 */
export function formatArea(area) {
  if (!area) return '0㎡'

  return `${area.toLocaleString()}㎡`
}

/**
 * 格式化户型
 * @param {object} layout - 户型对象 {rooms, halls, bathrooms}
 * @returns {string} 格式化后的户型
 */
export function formatLayout(layout) {
  if (!layout) return ''

  const { rooms = 0, halls = 0, bathrooms = 0 } = layout
  return `${rooms}室${halls}厅${bathrooms}卫`
}

/**
 * 截断文本
 * @param {string} text - 原始文本
 * @param {number} maxLength - 最大长度
 * @param {string} suffix - 截断后的后缀
 * @returns {string} 截断后的文本
 */
export function truncateText(text, maxLength = 50, suffix = '...') {
  if (!text) return ''

  if (text.length <= maxLength) return text

  return text.substr(0, maxLength - suffix.length) + suffix
}

/**
 * 驼峰命名转换为横线命名
 * @param {string} str - 驼峰命名字符串
 * @returns {string} 横线命名字符串
 */
export function camelToKebab(str) {
  return str.replace(/([A-Z])/g, '-$1').toLowerCase()
}

/**
 * 横线命名转换为驼峰命名
 * @param {string} str - 横线命名字符串
 * @returns {string} 驼峰命名字符串
 */
export function kebabToCamel(str) {
  return str.replace(/-([a-z])/g, (match, letter) => letter.toUpperCase())
}

/**
 * 生成随机颜色
 * @returns {string} 十六进制颜色值
 */
export function randomColor() {
  return '#' + Math.floor(Math.random() * 16777215).toString(16)
}

/**
 * 颜色值转换为RGBA
 * @param {string} color - 十六进制颜色值
 * @param {number} alpha - 透明度（0-1）
 * @returns {string} RGBA颜色值
 */
export function hexToRgba(color, alpha = 1) {
  const hex = color.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16)
  const g = parseInt(hex.substr(2, 2), 16)
  const b = parseInt(hex.substr(4, 2), 16)

  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}

/**
 * 深拷贝对象
 * @param {any} obj - 要拷贝的对象
 * @returns {any} 深拷贝后的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) return obj.map(item => deepClone(item))
  if (typeof obj === 'object') {
    const cloned = {}
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        cloned[key] = deepClone(obj[key])
      }
    }
    return cloned
  }
}

/**
 * 防抖函数
 * @param {function} fn - 要执行的函数
 * @param {number} delay - 延迟时间（毫秒）
 * @returns {function} 防抖后的函数
 */
export function debounce(fn, delay = 300) {
  let timeoutId = null

  return function (...args) {
    const context = this

    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => {
      fn.apply(context, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {function} fn - 要执行的函数
 * @param {number} interval - 时间间隔（毫秒）
 * @returns {function} 节流后的函数
 */
export function throttle(fn, interval = 300) {
  let lastTime = 0

  return function (...args) {
    const context = this
    const now = Date.now()

    if (now - lastTime >= interval) {
      lastTime = now
      fn.apply(context, args)
    }
  }
}