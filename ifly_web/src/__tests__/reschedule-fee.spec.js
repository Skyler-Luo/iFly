/**
 * 改签费用显示属性测试
 * Property 2: 差价显示正确性
 * Validates: Requirements 3.3, 3.4
 */

/* eslint-env jest */

const fc = require('fast-check')

/**
 * 计算费用预览数据
 * @param {number} originalPrice - 原票价
 * @param {number} newPrice - 新票价
 * @param {number} rescheduleFee - 改签手续费
 * @returns {object} - 费用预览对象
 */
function calculateFeePreview(originalPrice, newPrice, rescheduleFee = 50) {
  const priceDifference = newPrice - originalPrice
  
  return {
    originalPrice,
    newPrice,
    priceDifference,
    rescheduleFee,
    // 需补差价 = 差价 + 手续费（当差价为正时）
    totalToPay: priceDifference > 0 ? priceDifference + rescheduleFee : rescheduleFee,
    // 可退金额 = |差价| - 手续费（当差价为负时，且差价绝对值大于手续费）
    refundAmount: priceDifference < 0 ? Math.max(0, Math.abs(priceDifference) - rescheduleFee) : 0
  }
}

/**
 * 获取差价显示类型
 * @param {number} priceDifference - 差价
 * @returns {string} - 'pay' | 'refund' | 'none'
 */
function getDifferenceDisplayType(priceDifference) {
  if (priceDifference > 0) return 'pay'
  if (priceDifference < 0) return 'refund'
  return 'none'
}

/**
 * 获取差价显示文本
 * @param {number} priceDifference - 差价
 * @returns {string} - 显示文本
 */
function getDifferenceDisplayText(priceDifference) {
  if (priceDifference > 0) return '需补差价'
  if (priceDifference < 0) return '可退金额'
  return '无需补差价'
}

/**
 * 获取差价显示金额
 * @param {object} feePreview - 费用预览对象
 * @returns {number} - 显示金额
 */
function getDifferenceDisplayAmount(feePreview) {
  if (feePreview.priceDifference > 0) {
    return feePreview.totalToPay
  }
  if (feePreview.priceDifference < 0) {
    return feePreview.refundAmount
  }
  return 0
}

describe('Property 2: 差价显示正确性', () => {
  describe('差价计算', () => {
    it('should calculate positive difference when new price > original price', () => {
      const preview = calculateFeePreview(500, 800, 50)
      expect(preview.priceDifference).toBe(300)
      expect(preview.totalToPay).toBe(350) // 300 + 50
    })

    it('should calculate negative difference when new price < original price', () => {
      const preview = calculateFeePreview(800, 500, 50)
      expect(preview.priceDifference).toBe(-300)
      expect(preview.refundAmount).toBe(250) // 300 - 50
    })

    it('should calculate zero difference when prices are equal', () => {
      const preview = calculateFeePreview(500, 500, 50)
      expect(preview.priceDifference).toBe(0)
      expect(preview.totalToPay).toBe(50) // 只有手续费
      expect(preview.refundAmount).toBe(0)
    })
  })

  describe('显示类型判断', () => {
    it('should return "pay" when difference is positive', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 10000 }),
          (diff) => {
            expect(getDifferenceDisplayType(diff)).toBe('pay')
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should return "refund" when difference is negative', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: -10000, max: -1 }),
          (diff) => {
            expect(getDifferenceDisplayType(diff)).toBe('refund')
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should return "none" when difference is zero', () => {
      expect(getDifferenceDisplayType(0)).toBe('none')
    })
  })

  describe('显示文本正确性', () => {
    it('should display "需补差价" when difference is positive', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 1, max: 10000 }),
          (diff) => {
            expect(getDifferenceDisplayText(diff)).toBe('需补差价')
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should display "可退金额" when difference is negative', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: -10000, max: -1 }),
          (diff) => {
            expect(getDifferenceDisplayText(diff)).toBe('可退金额')
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should display "无需补差价" when difference is zero', () => {
      expect(getDifferenceDisplayText(0)).toBe('无需补差价')
    })
  })

  describe('显示金额一致性', () => {
    it('should display totalToPay when difference is positive', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 100, max: 5000 }),
          fc.integer({ min: 100, max: 5000 }),
          fc.integer({ min: 0, max: 200 }),
          (originalPrice, priceDiff, fee) => {
            const newPrice = originalPrice + priceDiff
            const preview = calculateFeePreview(originalPrice, newPrice, fee)
            
            if (preview.priceDifference > 0) {
              const displayAmount = getDifferenceDisplayAmount(preview)
              expect(displayAmount).toBe(preview.totalToPay)
              expect(displayAmount).toBe(priceDiff + fee)
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should display refundAmount when difference is negative', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 500, max: 5000 }),
          fc.integer({ min: 100, max: 400 }),
          fc.integer({ min: 0, max: 50 }),
          (originalPrice, priceDiff, fee) => {
            const newPrice = originalPrice - priceDiff
            const preview = calculateFeePreview(originalPrice, newPrice, fee)
            
            if (preview.priceDifference < 0) {
              const displayAmount = getDifferenceDisplayAmount(preview)
              expect(displayAmount).toBe(preview.refundAmount)
              // 退款金额 = 差价绝对值 - 手续费
              expect(displayAmount).toBe(Math.max(0, priceDiff - fee))
            }
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should display 0 when difference is zero', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 100, max: 5000 }),
          fc.integer({ min: 0, max: 200 }),
          (price, fee) => {
            const preview = calculateFeePreview(price, price, fee)
            const displayAmount = getDifferenceDisplayAmount(preview)
            expect(displayAmount).toBe(0)
          }
        ),
        { numRuns: 100 }
      )
    })
  })

  describe('退款金额边界情况', () => {
    it('should not refund when fee exceeds price difference', () => {
      // 当手续费大于差价时，退款金额应为0
      const preview = calculateFeePreview(500, 480, 50)
      expect(preview.priceDifference).toBe(-20)
      expect(preview.refundAmount).toBe(0) // 20 - 50 = -30, 取 max(0, -30) = 0
    })

    it('should refund correctly when difference exceeds fee', () => {
      const preview = calculateFeePreview(500, 300, 50)
      expect(preview.priceDifference).toBe(-200)
      expect(preview.refundAmount).toBe(150) // 200 - 50 = 150
    })
  })

  describe('费用预览完整性', () => {
    it('should always have all required fields', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 100, max: 5000 }),
          fc.integer({ min: 100, max: 5000 }),
          fc.integer({ min: 0, max: 200 }),
          (originalPrice, newPrice, fee) => {
            const preview = calculateFeePreview(originalPrice, newPrice, fee)
            
            expect(preview).toHaveProperty('originalPrice')
            expect(preview).toHaveProperty('newPrice')
            expect(preview).toHaveProperty('priceDifference')
            expect(preview).toHaveProperty('rescheduleFee')
            expect(preview).toHaveProperty('totalToPay')
            expect(preview).toHaveProperty('refundAmount')
            
            // 验证数值类型
            expect(typeof preview.originalPrice).toBe('number')
            expect(typeof preview.newPrice).toBe('number')
            expect(typeof preview.priceDifference).toBe('number')
            expect(typeof preview.rescheduleFee).toBe('number')
            expect(typeof preview.totalToPay).toBe('number')
            expect(typeof preview.refundAmount).toBe('number')
          }
        ),
        { numRuns: 100 }
      )
    })

    it('should have consistent price difference calculation', () => {
      fc.assert(
        fc.property(
          fc.integer({ min: 100, max: 5000 }),
          fc.integer({ min: 100, max: 5000 }),
          (originalPrice, newPrice) => {
            const preview = calculateFeePreview(originalPrice, newPrice, 50)
            expect(preview.priceDifference).toBe(newPrice - originalPrice)
          }
        ),
        { numRuns: 100 }
      )
    })
  })
})
