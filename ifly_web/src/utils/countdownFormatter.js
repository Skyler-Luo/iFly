/**
 * 倒计时格式化工具
 * 将秒数转换为 "MM:SS" 格式的字符串
 */

/**
 * 格式化倒计时秒数为 "MM:SS" 格式
 * @param {number} seconds - 剩余秒数
 * @returns {string} 格式化后的时间字符串
 */
export function formatCountdown(seconds) {
  // 处理无效输入
  if (typeof seconds !== 'number' || isNaN(seconds) || seconds < 0) {
    return '--:--'
  }

  // 取整
  const totalSeconds = Math.floor(seconds)

  // 计算分钟和秒
  const minutes = Math.floor(totalSeconds / 60)
  const secs = totalSeconds % 60

  // 格式化为两位数
  const paddedMinutes = String(minutes).padStart(2, '0')
  const paddedSeconds = String(secs).padStart(2, '0')

  return `${paddedMinutes}:${paddedSeconds}`
}

/**
 * 解析 "MM:SS" 格式的时间字符串为秒数
 * @param {string} timeStr - 时间字符串
 * @returns {number} 秒数，解析失败返回 -1
 */
export function parseCountdown(timeStr) {
  if (typeof timeStr !== 'string') {
    return -1
  }

  const match = timeStr.match(/^(\d+):(\d{2})$/)
  if (!match) {
    return -1
  }

  const minutes = parseInt(match[1], 10)
  const seconds = parseInt(match[2], 10)

  if (seconds >= 60) {
    return -1
  }

  return minutes * 60 + seconds
}

export default {
  formatCountdown,
  parseCountdown
}
