/**
 * **Feature: online-checkin, Property 5: 座位分类正确性**
 * **Validates: Requirements 3.2**
 * 
 * Property: For any seat and its occupation status, the seat classification function 
 * should correctly return one of: occupied, selected, current, available
 */

/* eslint-env jest */

const fc = require('fast-check')
const { 
  classifySeat, 
  SeatStatus,
  isSeatOccupied,
  isSeatSelected,
  isCurrentSeat
} = require('../utils/seatClassification')

/**
 * 生成有效的座位号
 * 格式: 行号(1-30) + 列标签(A-F)
 */
const seatNumberArb = fc.tuple(
  fc.integer({ min: 1, max: 30 }),
  fc.constantFrom('A', 'B', 'C', 'D', 'E', 'F')
).map(([row, col]) => `${row}${col}`)

/**
 * 生成座位号列表（用于已占用座位）
 */
const occupiedSeatsArb = fc.array(seatNumberArb, { minLength: 0, maxLength: 20 })

describe('Property 5: 座位分类正确性', () => {
  /**
   * Property Test: 座位分类函数应返回四种状态之一
   */
  test('座位分类函数应返回四种有效状态之一', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        occupiedSeatsArb,
        seatNumberArb,
        fc.option(seatNumberArb, { nil: null }),
        (seatNumber, occupiedSeats, currentSeat, selectedSeat) => {
          const status = classifySeat(seatNumber, occupiedSeats, currentSeat, selectedSeat)
          
          const validStatuses = [
            SeatStatus.OCCUPIED,
            SeatStatus.SELECTED,
            SeatStatus.CURRENT,
            SeatStatus.AVAILABLE
          ]
          
          expect(validStatuses).toContain(status)
          return validStatuses.includes(status)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 已占用座位应返回 occupied 状态（除非是当前座位）
   */
  test('已占用座位应返回 occupied 状态（除非是当前座位）', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        fc.array(seatNumberArb, { minLength: 1, maxLength: 10 }),
        seatNumberArb,
        fc.option(seatNumberArb, { nil: null }),
        (seatNumber, occupiedSeats, currentSeat, selectedSeat) => {
          // 确保座位在占用列表中
          const occupiedWithSeat = [...occupiedSeats, seatNumber]
          
          const status = classifySeat(seatNumber, occupiedWithSeat, currentSeat, selectedSeat)
          
          // 如果座位是当前座位，则不应该是 occupied
          if (seatNumber === currentSeat) {
            expect(status).not.toBe(SeatStatus.OCCUPIED)
            return status !== SeatStatus.OCCUPIED
          }
          
          // 否则应该是 occupied
          expect(status).toBe(SeatStatus.OCCUPIED)
          return status === SeatStatus.OCCUPIED
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 选中的座位应返回 selected 状态（如果未被占用）
   */
  test('选中的座位应返回 selected 状态（如果未被占用）', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        seatNumberArb,
        (seatNumber, currentSeat) => {
          // 空的占用列表，座位未被占用
          const occupiedSeats = []
          // 选中该座位
          const selectedSeat = seatNumber
          
          const status = classifySeat(seatNumber, occupiedSeats, currentSeat, selectedSeat)
          
          expect(status).toBe(SeatStatus.SELECTED)
          return status === SeatStatus.SELECTED
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 当前座位在未选择新座位时应返回 current 状态
   */
  test('当前座位在未选择新座位时应返回 current 状态', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        (seatNumber) => {
          // 空的占用列表
          const occupiedSeats = []
          // 当前座位就是该座位
          const currentSeat = seatNumber
          // 没有选择新座位
          const selectedSeat = null
          
          const status = classifySeat(seatNumber, occupiedSeats, currentSeat, selectedSeat)
          
          expect(status).toBe(SeatStatus.CURRENT)
          return status === SeatStatus.CURRENT
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 当前座位被选中时应返回 selected 状态
   */
  test('当前座位被选中时应返回 selected 状态', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        (seatNumber) => {
          // 空的占用列表
          const occupiedSeats = []
          // 当前座位就是该座位
          const currentSeat = seatNumber
          // 选中当前座位
          const selectedSeat = seatNumber
          
          const status = classifySeat(seatNumber, occupiedSeats, currentSeat, selectedSeat)
          
          expect(status).toBe(SeatStatus.SELECTED)
          return status === SeatStatus.SELECTED
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 未占用、未选中、非当前座位应返回 available 状态
   */
  test('未占用、未选中、非当前座位应返回 available 状态', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        seatNumberArb,
        fc.option(seatNumberArb, { nil: null }),
        (seatNumber, currentSeat, selectedSeat) => {
          // 确保座位不在占用列表中
          const occupiedSeats = []
          
          // 确保座位不是当前座位
          fc.pre(seatNumber !== currentSeat)
          // 确保座位不是选中座位
          fc.pre(seatNumber !== selectedSeat)
          
          const status = classifySeat(seatNumber, occupiedSeats, currentSeat, selectedSeat)
          
          expect(status).toBe(SeatStatus.AVAILABLE)
          return status === SeatStatus.AVAILABLE
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 状态优先级 - occupied > selected > current > available
   */
  test('状态优先级应正确：occupied > selected > current > available', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        (seatNumber) => {
          // 场景1: 座位被占用且被选中 -> 应返回 occupied
          const occupiedSeats1 = [seatNumber]
          const currentSeat1 = '99Z' // 不同的座位
          const selectedSeat1 = seatNumber
          const status1 = classifySeat(seatNumber, occupiedSeats1, currentSeat1, selectedSeat1)
          expect(status1).toBe(SeatStatus.OCCUPIED)
          
          // 场景2: 座位未被占用但被选中且是当前座位 -> 应返回 selected
          const occupiedSeats2 = []
          const currentSeat2 = seatNumber
          const selectedSeat2 = seatNumber
          const status2 = classifySeat(seatNumber, occupiedSeats2, currentSeat2, selectedSeat2)
          expect(status2).toBe(SeatStatus.SELECTED)
          
          return status1 === SeatStatus.OCCUPIED && status2 === SeatStatus.SELECTED
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 当前座位不应被视为占用
   */
  test('当前座位不应被视为占用', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        (seatNumber) => {
          // 座位在占用列表中，但也是当前座位
          const occupiedSeats = [seatNumber]
          const currentSeat = seatNumber
          const selectedSeat = null
          
          const isOccupied = isSeatOccupied(seatNumber, occupiedSeats, currentSeat)
          
          expect(isOccupied).toBe(false)
          return isOccupied === false
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: isSeatSelected 函数正确性
   */
  test('isSeatSelected 函数应正确判断座位是否被选中', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        fc.option(seatNumberArb, { nil: null }),
        (seatNumber, selectedSeat) => {
          const isSelected = isSeatSelected(seatNumber, selectedSeat)
          const expected = seatNumber === selectedSeat
          
          expect(isSelected).toBe(expected)
          return isSelected === expected
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: isCurrentSeat 函数正确性
   */
  test('isCurrentSeat 函数应正确判断是否为当前座位', () => {
    fc.assert(
      fc.property(
        seatNumberArb,
        seatNumberArb,
        fc.option(seatNumberArb, { nil: null }),
        (seatNumber, currentSeat, selectedSeat) => {
          const isCurrent = isCurrentSeat(seatNumber, currentSeat, selectedSeat)
          // 当前座位且未被选中时才返回 true
          const expected = seatNumber === currentSeat && seatNumber !== selectedSeat
          
          expect(isCurrent).toBe(expected)
          return isCurrent === expected
        }
      ),
      { numRuns: 100 }
    )
  })
})
