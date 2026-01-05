/**
 * 证件号码脱敏工具函数
 *
 * 用于在前端对证件号码进行脱敏处理，保护用户隐私。
 *
 * @module utils/idMasking
 */

/**
 * 证件号码脱敏函数
 *
 * 保留前4位和后4位，中间用星号替代，脱敏后长度与原长度相同。
 * 如果证件号码长度小于等于8位，则全部用星号替代。
 *
 * @param {string} idNumber - 原始证件号码
 * @returns {string} 脱敏后的证件号码
 *
 * @example
 * maskIdNumber('110101199001011234') // 返回 '1101**********1234'
 * maskIdNumber('G12345678') // 返回 'G123*5678'
 * maskIdNumber('12345678') // 返回 '********'
 * maskIdNumber('') // 返回 ''
 */
export function maskIdNumber(idNumber) {
  // 处理空值或非字符串
  if (!idNumber || typeof idNumber !== 'string') {
    return ''
  }

  const length = idNumber.length

  // 长度小于等于8位，全部用星号替代
  if (length <= 8) {
    return '*'.repeat(length)
  }

  // 保留前4位和后4位，中间用星号替代
  const middleLength = length - 8
  return idNumber.slice(0, 4) + '*'.repeat(middleLength) + idNumber.slice(-4)
}

export default {
  maskIdNumber
}
