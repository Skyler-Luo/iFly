/**
 * **Feature: online-checkin, Property 8: 过道位置计算**
 * **Validates: Requirements 3.7**
 * 
 * Property: For any seat column configuration, the aisle should be at the correct position:
 * - 6 columns: aisle after column 3 (index 3)
 * - 4 columns: aisle after column 2 (index 2)
 */

/* eslint-env jest */

const fc = require('fast-check')
const { 
  isAislePosition, 
  getAisleIndex,
  validateAislePosition
} = require('../utils/aislePosition')

describe('Property 8: 过道位置计算', () => {
  /**
   * Property Test: 6 列配置在第 3 列后显示过道
   */
  test('6 列配置应在索引 3 位置显示过道', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 5 }),
        (index) => {
          const columnCount = 6
          const isAisle = isAislePosition(index, columnCount)
          const expected = index === 3
          
          expect(isAisle).toBe(expected)
          return isAisle === expected
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 4 列配置在第 2 列后显示过道
   */
  test('4 列配置应在索引 2 位置显示过道', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 3 }),
        (index) => {
          const columnCount = 4
          const isAisle = isAislePosition(index, columnCount)
          const expected = index === 2
          
          expect(isAisle).toBe(expected)
          return isAisle === expected
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 每种列配置只有一个过道位置
   */
  test('每种列配置应只有一个过道位置', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(4, 6, 8),
        (columnCount) => {
          let aisleCount = 0
          
          for (let i = 0; i < columnCount; i++) {
            if (isAislePosition(i, columnCount)) {
              aisleCount++
            }
          }
          
          expect(aisleCount).toBe(1)
          return aisleCount === 1
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: getAisleIndex 应返回正确的过道索引
   */
  test('getAisleIndex 应返回正确的过道索引', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(4, 6),
        (columnCount) => {
          const aisleIndex = getAisleIndex(columnCount)
          
          if (columnCount === 6) {
            expect(aisleIndex).toBe(3)
            return aisleIndex === 3
          }
          
          if (columnCount === 4) {
            expect(aisleIndex).toBe(2)
            return aisleIndex === 2
          }
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: isAislePosition 和 getAisleIndex 应一致
   */
  test('isAislePosition 和 getAisleIndex 应返回一致的结果', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(4, 6, 8),
        fc.integer({ min: 0, max: 10 }),
        (columnCount, index) => {
          const aisleIndex = getAisleIndex(columnCount)
          const isAisle = isAislePosition(index, columnCount)
          
          // 如果索引等于过道索引，则应该是过道位置
          const expected = index === aisleIndex
          
          expect(isAisle).toBe(expected)
          return isAisle === expected
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 过道位置应在列范围的中间
   */
  test('过道位置应大致在列范围的中间', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(4, 6, 8, 10),
        (columnCount) => {
          const aisleIndex = getAisleIndex(columnCount)
          const middle = Math.floor(columnCount / 2)
          
          // 过道位置应该在中间位置
          expect(aisleIndex).toBe(middle)
          return aisleIndex === middle
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 无效输入应返回 false
   */
  test('无效输入应返回 false', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.constant({ index: -1, columnCount: 6 }),
          fc.constant({ index: 0, columnCount: 0 }),
          fc.constant({ index: 0, columnCount: -1 })
        ),
        ({ index, columnCount }) => {
          const isAisle = isAislePosition(index, columnCount)
          
          expect(isAisle).toBe(false)
          return isAisle === false
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 6 列配置的具体过道位置验证
   * A(0) B(1) C(2) | D(3) E(4) F(5)
   * 过道在索引 3 之前显示
   */
  test('6 列配置：A B C | D E F 布局验证', () => {
    const columnCount = 6
    
    fc.assert(
      fc.property(
        fc.constantFrom(0, 1, 2, 3, 4, 5),
        (index) => {
          const isAisle = isAislePosition(index, columnCount)
          
          // 只有索引 3 是过道位置
          if (index === 3) {
            expect(isAisle).toBe(true)
            return isAisle === true
          } else {
            expect(isAisle).toBe(false)
            return isAisle === false
          }
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 4 列配置的具体过道位置验证
   * A(0) B(1) | D(2) E(3)
   * 过道在索引 2 之前显示
   */
  test('4 列配置：A B | D E 布局验证', () => {
    const columnCount = 4
    
    fc.assert(
      fc.property(
        fc.constantFrom(0, 1, 2, 3),
        (index) => {
          const isAisle = isAislePosition(index, columnCount)
          
          // 只有索引 2 是过道位置
          if (index === 2) {
            expect(isAisle).toBe(true)
            return isAisle === true
          } else {
            expect(isAisle).toBe(false)
            return isAisle === false
          }
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: validateAislePosition 函数正确性
   */
  test('validateAislePosition 函数应正确验证过道位置', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 5 }),
        fc.constantFrom(4, 6),
        (index, columnCount) => {
          const actualIsAisle = isAislePosition(index, columnCount)
          
          // 验证函数应返回 true 当预期值正确时
          const validationResult = validateAislePosition(index, columnCount, actualIsAisle)
          
          expect(validationResult).toBe(true)
          return validationResult === true
        }
      ),
      { numRuns: 100 }
    )
  })
})
