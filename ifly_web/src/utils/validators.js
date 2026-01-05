/**
 * 通用验证工具
 * 提供统一的表单验证和组件props验证
 */

// 常用的正则表达式
export const REGEX_PATTERNS = {
  // 手机号
  mobile: /^1[3456789]\d{9}$/,
  // 邮箱
  email: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  // 身份证号
  idCard: /^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/,
  // 护照号
  passport: /^[a-zA-Z0-9]{5,17}$/,
  // 航班号
  flightNumber: /^[A-Z]{2}\d{3,4}$/,
  // 中文姓名
  chineseName: /^[\u4e00-\u9fa5]{2,20}$/,
  // 英文姓名
  englishName: /^[a-zA-Z\s]{2,50}$/,
  // 密码强度（至少8位，包含数字和字母）
  password: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/
}

// 表单验证规则生成器
export const createValidationRules = {
  // 必填验证
  required: (message = '此项为必填项') => ({
    required: true,
    message,
    trigger: 'blur'
  }),

  // 手机号验证
  mobile: (required = true) => {
    const rules = []
    if (required) {
      rules.push({ required: true, message: '请输入手机号', trigger: 'blur' })
    }
    rules.push({
      pattern: REGEX_PATTERNS.mobile,
      message: '请输入正确的手机号码',
      trigger: 'blur'
    })
    return rules
  },

  // 邮箱验证
  email: (required = true) => {
    const rules = []
    if (required) {
      rules.push({ required: true, message: '请输入邮箱', trigger: 'blur' })
    }
    rules.push({
      type: 'email',
      message: '请输入正确的邮箱地址',
      trigger: 'blur'
    })
    return rules
  },

  // 身份证验证
  idCard: (required = true) => {
    const rules = []
    if (required) {
      rules.push({ required: true, message: '请输入身份证号', trigger: 'blur' })
    }
    rules.push({
      pattern: REGEX_PATTERNS.idCard,
      message: '请输入正确的身份证号码',
      trigger: 'blur'
    })
    return rules
  },

  // 密码验证
  password: (required = true) => {
    const rules = []
    if (required) {
      rules.push({ required: true, message: '请输入密码', trigger: 'blur' })
    }
    rules.push({
      min: 8,
      message: '密码长度不能少于8位',
      trigger: 'blur'
    })
    rules.push({
      pattern: REGEX_PATTERNS.password,
      message: '密码必须包含至少一个字母和一个数字',
      trigger: 'blur'
    })
    return rules
  },

  // 确认密码验证
  confirmPassword: (passwordRef, required = true) => {
    const rules = []
    if (required) {
      rules.push({ required: true, message: '请再次输入密码', trigger: 'blur' })
    }
    rules.push({
      validator: (rule, value, callback) => {
        if (value !== passwordRef) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    })
    return rules
  },

  // 中文姓名验证
  chineseName: (required = true) => {
    const rules = []
    if (required) {
      rules.push({ required: true, message: '请输入姓名', trigger: 'blur' })
    }
    rules.push({
      pattern: REGEX_PATTERNS.chineseName,
      message: '请输入2-20位中文姓名',
      trigger: 'blur'
    })
    return rules
  },

  // 长度验证
  length: (min = 0, max = 100, required = true) => {
    const rules = []
    if (required) {
      rules.push({ required: true, message: '此项不能为空', trigger: 'blur' })
    }
    if (min > 0) {
      rules.push({ min, message: `长度不能少于${min}个字符`, trigger: 'blur' })
    }
    if (max > 0) {
      rules.push({ max, message: `长度不能超过${max}个字符`, trigger: 'blur' })
    }
    return rules
  },

  // 数值范围验证
  number: (min = null, max = null, required = true) => {
    const rules = []
    if (required) {
      rules.push({ required: true, message: '请输入数值', trigger: 'blur' })
    }
    rules.push({ type: 'number', message: '请输入有效的数值', trigger: 'blur' })
    if (min !== null) {
      rules.push({
        validator: (rule, value, callback) => {
          if (value < min) {
            callback(new Error(`数值不能小于${min}`))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      })
    }
    if (max !== null) {
      rules.push({
        validator: (rule, value, callback) => {
          if (value > max) {
            callback(new Error(`数值不能大于${max}`))
          } else {
            callback()
          }
        },
        trigger: 'blur'
      })
    }
    return rules
  }
}

// 组件Props验证器
export const propValidators = {
  // 字符串类型验证
  string: (defaultValue = '', required = false) => ({
    type: String,
    required,
    default: defaultValue,
    validator: (value) => typeof value === 'string'
  }),

  // 数字类型验证
  number: (defaultValue = 0, required = false, min = null, max = null) => ({
    type: Number,
    required,
    default: defaultValue,
    validator: (value) => {
      if (typeof value !== 'number') return false
      if (min !== null && value < min) return false
      if (max !== null && value > max) return false
      return true
    }
  }),

  // 布尔类型验证
  boolean: (defaultValue = false, required = false) => ({
    type: Boolean,
    required,
    default: defaultValue
  }),

  // 数组类型验证
  array: (defaultValue = () => [], required = false) => ({
    type: Array,
    required,
    default: defaultValue,
    validator: (value) => Array.isArray(value)
  }),

  // 对象类型验证
  object: (defaultValue = () => ({}), required = false) => ({
    type: Object,
    required,
    default: defaultValue,
    validator: (value) => typeof value === 'object' && value !== null
  }),

  // 枚举值验证
  enum: (validValues = [], defaultValue = null, required = false) => ({
    type: String,
    required,
    default: defaultValue || validValues[0],
    validator: (value) => validValues.includes(value)
  }),

  // ID验证
  id: (required = false) => ({
    type: [String, Number],
    required,
    validator: (value) => {
      if (typeof value === 'string') {
        return value.length > 0
      }
      if (typeof value === 'number') {
        return value > 0
      }
      return false
    }
  }),

  // 函数类型验证
  function: (defaultValue = () => {}, required = false) => ({
    type: Function,
    required,
    default: defaultValue
  }),

  // 航班信息验证
  flight: (required = false) => ({
    type: Object,
    required,
    default: () => ({}),
    validator: (value) => {
      if (!value || typeof value !== 'object') return false
      // 基本的航班信息字段验证
      const requiredFields = ['id', 'flight_number']
      return requiredFields.every(field => Object.prototype.hasOwnProperty.call(value, field))
    }
  }),

  // 用户信息验证
  user: (required = false) => ({
    type: Object,
    required,
    default: () => ({}),
    validator: (value) => {
      if (!value || typeof value !== 'object') return false
      // 基本的用户信息字段验证
      const requiredFields = ['id', 'username']
      return requiredFields.every(field => Object.prototype.hasOwnProperty.call(value, field))
    }
  })
}

// 数据验证函数
export const validateData = {
  // 验证手机号
  mobile: (value) => REGEX_PATTERNS.mobile.test(value),

  // 验证邮箱
  email: (value) => REGEX_PATTERNS.email.test(value),

  // 验证身份证
  idCard: (value) => REGEX_PATTERNS.idCard.test(value),

  // 验证密码强度
  password: (value) => REGEX_PATTERNS.password.test(value),

  // 验证中文姓名
  chineseName: (value) => REGEX_PATTERNS.chineseName.test(value),

  // 验证航班号
  flightNumber: (value) => REGEX_PATTERNS.flightNumber.test(value),

  // 验证非空字符串
  notEmpty: (value) => typeof value === 'string' && value.trim().length > 0,

  // 验证正整数
  positiveInteger: (value) => Number.isInteger(value) && value > 0,

  // 验证日期格式
  date: (value) => {
    const date = new Date(value)
    return date instanceof Date && !isNaN(date)
  },

  // 验证未来日期
  futureDate: (value) => {
    const date = new Date(value)
    return validateData.date(value) && date > new Date()
  }
}

// 通用错误处理
export const handleValidationError = (error, fieldMap = {}) => {
  const errors = {}
  
  if (error && error.data && typeof error.data === 'object') {
    Object.keys(error.data).forEach(key => {
      const fieldName = fieldMap[key] || key
      const messages = error.data[key]
      
      if (Array.isArray(messages)) {
        errors[fieldName] = messages[0]
      } else if (typeof messages === 'string') {
        errors[fieldName] = messages
      }
    })
  }
  
  return errors
}

export default {
  REGEX_PATTERNS,
  createValidationRules,
  propValidators,
  validateData,
  handleValidationError
}
