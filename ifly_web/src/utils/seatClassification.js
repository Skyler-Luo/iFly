/**
 * 座位分类工具函数
 * 用于在线值机功能中对座位进行分类
 * 
 * Requirements 3.2: 正确区分 available、occupied、current、selected 状态
 */

/**
 * 座位状态枚举
 */
export const SeatStatus = {
  OCCUPIED: 'occupied',   // 已被其他乘客占用
  SELECTED: 'selected',   // 当前选中的座位
  CURRENT: 'current',     // 乘客原有座位
  AVAILABLE: 'available'  // 可选座位
}

/**
 * 判断座位是否被占用
 * 
 * @param {string} seatNumber - 座位号，如 "12A"
 * @param {string[]} occupiedSeats - 已占用座位列表
 * @param {string} currentSeat - 乘客当前座位（不算占用）
 * @returns {boolean}
 */
export function isSeatOccupied(seatNumber, occupiedSeats, currentSeat) {
  // 当前座位不算占用（乘客可以保留当前座位）
  if (seatNumber === currentSeat) {
    return false
  }
  return occupiedSeats.includes(seatNumber)
}

/**
 * 判断座位是否被选中
 * 
 * @param {string} seatNumber - 座位号
 * @param {string|null} selectedSeat - 已选中的座位
 * @returns {boolean}
 */
export function isSeatSelected(seatNumber, selectedSeat) {
  return selectedSeat === seatNumber
}

/**
 * 判断是否为当前座位（乘客原有座位）
 * 只有在没有选择该座位时才返回 true
 * 
 * @param {string} seatNumber - 座位号
 * @param {string} currentSeat - 乘客当前座位
 * @param {string|null} selectedSeat - 已选中的座位
 * @returns {boolean}
 */
export function isCurrentSeat(seatNumber, currentSeat, selectedSeat) {
  // 当前座位且没有选择该座位时显示为 current 状态
  return currentSeat === seatNumber && selectedSeat !== seatNumber
}

/**
 * 获取座位的分类状态
 * 
 * Requirements 3.2: 正确区分 available、occupied、current、selected 状态
 * 
 * 状态优先级（从高到低）：
 * 1. occupied - 已被其他乘客占用
 * 2. selected - 当前选中的座位
 * 3. current - 乘客原有座位（未选择新座位时）
 * 4. available - 可选座位
 * 
 * @param {string} seatNumber - 座位号，如 "12A"
 * @param {string[]} occupiedSeats - 已占用座位列表
 * @param {string} currentSeat - 乘客当前座位
 * @param {string|null} selectedSeat - 已选中的座位
 * @returns {string} - 座位状态: 'occupied' | 'selected' | 'current' | 'available'
 */
export function classifySeat(seatNumber, occupiedSeats, currentSeat, selectedSeat) {
  // 1. 检查是否被占用（最高优先级）
  if (isSeatOccupied(seatNumber, occupiedSeats, currentSeat)) {
    return SeatStatus.OCCUPIED
  }
  
  // 2. 检查是否被选中
  if (isSeatSelected(seatNumber, selectedSeat)) {
    return SeatStatus.SELECTED
  }
  
  // 3. 检查是否为当前座位
  if (isCurrentSeat(seatNumber, currentSeat, selectedSeat)) {
    return SeatStatus.CURRENT
  }
  
  // 4. 默认为可选状态
  return SeatStatus.AVAILABLE
}

/**
 * 验证座位分类结果是否正确
 * 用于属性测试
 * 
 * @param {string} seatNumber - 座位号
 * @param {string[]} occupiedSeats - 已占用座位列表
 * @param {string} currentSeat - 乘客当前座位
 * @param {string|null} selectedSeat - 已选中的座位
 * @param {string} expectedStatus - 预期状态
 * @returns {boolean}
 */
export function validateSeatClassification(seatNumber, occupiedSeats, currentSeat, selectedSeat, expectedStatus) {
  const actualStatus = classifySeat(seatNumber, occupiedSeats, currentSeat, selectedSeat)
  return actualStatus === expectedStatus
}

export default {
  SeatStatus,
  isSeatOccupied,
  isSeatSelected,
  isCurrentSeat,
  classifySeat,
  validateSeatClassification
}
