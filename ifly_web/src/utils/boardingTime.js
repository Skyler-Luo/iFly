/**
 * 登机时间计算工具函数
 * 
 * 用于计算航班的登机时间（起飞时间 - 30 分钟）。
 * 
 * @module utils/boardingTime
 */

/**
 * 计算登机时间
 * 
 * 登机时间 = 起飞时间 - 30 分钟
 * 
 * @param {Date|string} departureTime - 起飞时间（Date 对象或 ISO 字符串）
 * @returns {Date|null} 登机时间（Date 对象），如果输入无效则返回 null
 * 
 * @example
 * calculateBoardingTime(new Date('2026-01-15T08:30:00Z'))
 * // 返回 Date 对象，表示 2026-01-15T08:00:00Z
 * 
 * calculateBoardingTime('2026-01-15T08:30:00Z')
 * // 返回 Date 对象，表示 2026-01-15T08:00:00Z
 */
export function calculateBoardingTime(departureTime) {
  // 处理空值
  if (!departureTime) {
    return null
  }

  // 将字符串转换为 Date 对象
  let departure
  if (typeof departureTime === 'string') {
    departure = new Date(departureTime)
  } else if (departureTime instanceof Date) {
    departure = new Date(departureTime.getTime())
  } else {
    return null
  }

  // 检查日期是否有效
  if (isNaN(departure.getTime())) {
    return null
  }

  // 减去 30 分钟（30 * 60 * 1000 毫秒）
  const boardingTime = new Date(departure.getTime() - 30 * 60 * 1000)
  
  return boardingTime
}

/**
 * 格式化登机时间为字符串
 * 
 * @param {Date|string} departureTime - 起飞时间
 * @param {string} locale - 地区设置，默认 'zh-CN'
 * @returns {string} 格式化的登机时间字符串
 * 
 * @example
 * formatBoardingTime(new Date('2026-01-15T08:30:00Z'))
 * // 返回 "08:00" 或类似格式
 */
export function formatBoardingTime(departureTime, locale = 'zh-CN') {
  const boardingTime = calculateBoardingTime(departureTime)
  
  if (!boardingTime) {
    return ''
  }

  return boardingTime.toLocaleTimeString(locale, {
    hour: '2-digit',
    minute: '2-digit'
  })
}

export default {
  calculateBoardingTime,
  formatBoardingTime
}
