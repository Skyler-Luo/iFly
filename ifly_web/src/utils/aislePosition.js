/**
 * 过道位置计算工具函数
 * 用于在线值机功能中计算座位图的过道位置
 * 
 * Requirements 3.7: 在座位列之间显示过道以模拟真实机舱布局
 */

/**
 * 判断指定索引位置是否应该显示过道
 * 
 * 过道位置规则：
 * - 6 列配置 (A B C | D E F): 在第 3 列后显示过道（索引 3）
 * - 4 列配置 (A B | D E): 在第 2 列后显示过道（索引 2）
 * 
 * @param {number} index - 列索引（从 0 开始）
 * @param {number} columnCount - 总列数
 * @returns {boolean} - 是否应该在该位置显示过道
 */
export function isAislePosition(index, columnCount) {
  // 验证输入
  if (typeof index !== 'number' || typeof columnCount !== 'number') {
    return false
  }
  
  if (index < 0 || columnCount <= 0) {
    return false
  }
  
  // 6 列配置：A B C | D E F
  // 过道在第 3 列后（索引 3 之前）
  if (columnCount === 6) {
    return index === 3
  }
  
  // 4 列配置：A B | D E
  // 过道在第 2 列后（索引 2 之前）
  if (columnCount === 4) {
    return index === 2
  }
  
  // 其他配置：在中间位置显示过道
  // 例如 8 列配置在第 4 列后
  if (columnCount > 0) {
    return index === Math.floor(columnCount / 2)
  }
  
  return false
}

/**
 * 获取过道位置索引
 * 
 * @param {number} columnCount - 总列数
 * @returns {number} - 过道位置索引，如果没有过道则返回 -1
 */
export function getAisleIndex(columnCount) {
  if (typeof columnCount !== 'number' || columnCount <= 0) {
    return -1
  }
  
  if (columnCount === 6) {
    return 3
  }
  
  if (columnCount === 4) {
    return 2
  }
  
  // 其他配置：在中间位置
  return Math.floor(columnCount / 2)
}

/**
 * 验证过道位置计算是否正确
 * 用于属性测试
 * 
 * @param {number} index - 列索引
 * @param {number} columnCount - 总列数
 * @param {boolean} expectedIsAisle - 预期是否为过道位置
 * @returns {boolean}
 */
export function validateAislePosition(index, columnCount, expectedIsAisle) {
  const actualIsAisle = isAislePosition(index, columnCount)
  return actualIsAisle === expectedIsAisle
}

export default {
  isAislePosition,
  getAisleIndex,
  validateAislePosition
}
