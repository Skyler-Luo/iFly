/**
 * **Feature: online-checkin, Property 12: 登机时间计算**
 * **Validates: Requirements 5.4**
 * 
 * Property: For any flight, the boarding time should equal departure time minus 30 minutes.
 */

/* eslint-env jest */

const fc = require('fast-check')
const { calculateBoardingTime, formatBoardingTime } = require('../utils/boardingTime')

/**
 * 生成有效的日期时间
 */
const dateTimeArb = fc.record({
  year: fc.integer({ min: 2024, max: 2030 }),
  month: fc.integer({ min: 1, max: 12 }),
  day: fc.integer({ min: 1, max: 28 }), // 使用28避免月份天数问题
  hour: fc.integer({ min: 0, max: 23 }),
  minute: fc.integer({ min: 0, max: 59 })
}).map(({ year, month, day, hour, minute }) => 
  new Date(year, month - 1, day, hour, minute)
)

describe('Property 12: 登机时间计算', () => {
  /**
   * Property Test: 登机时间应等于起飞时间减去30分钟
   */
  test('登机时间应等于起飞时间减去30分钟', () => {
    fc.assert(
      fc.property(
        dateTimeArb,
        (departureTime) => {
          const boardingTime = calculateBoardingTime(departureTime)
          
          // 计算时间差（毫秒）
          const timeDiff = departureTime.getTime() - boardingTime.getTime()
          
          // 应该正好是30分钟（30 * 60 * 1000 毫秒）
          expect(timeDiff).toBe(30 * 60 * 1000)
          return timeDiff === 30 * 60 * 1000
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 登机时间应是有效的 Date 对象
   */
  test('登机时间应是有效的 Date 对象', () => {
    fc.assert(
      fc.property(
        dateTimeArb,
        (departureTime) => {
          const boardingTime = calculateBoardingTime(departureTime)
          
          expect(boardingTime).toBeInstanceOf(Date)
          expect(isNaN(boardingTime.getTime())).toBe(false)
          
          return boardingTime instanceof Date && !isNaN(boardingTime.getTime())
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 登机时间应早于起飞时间
   */
  test('登机时间应早于起飞时间', () => {
    fc.assert(
      fc.property(
        dateTimeArb,
        (departureTime) => {
          const boardingTime = calculateBoardingTime(departureTime)
          
          expect(boardingTime.getTime()).toBeLessThan(departureTime.getTime())
          return boardingTime.getTime() < departureTime.getTime()
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 字符串输入应正确处理
   */
  test('ISO 字符串输入应正确处理', () => {
    fc.assert(
      fc.property(
        dateTimeArb,
        (departureTime) => {
          const isoString = departureTime.toISOString()
          const boardingTime = calculateBoardingTime(isoString)
          
          // 计算时间差
          const timeDiff = departureTime.getTime() - boardingTime.getTime()
          
          // 应该正好是30分钟
          expect(timeDiff).toBe(30 * 60 * 1000)
          return timeDiff === 30 * 60 * 1000
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 跨午夜场景应正确处理
   */
  test('凌晨起飞时登机时间应正确计算（可能跨越到前一天）', () => {
    // 测试 00:15 起飞的航班
    const departure = new Date(2026, 0, 15, 0, 15) // 2026-01-15 00:15
    const boarding = calculateBoardingTime(departure)
    
    // 登机时间应该是前一天 23:45
    expect(boarding.getDate()).toBe(14)
    expect(boarding.getHours()).toBe(23)
    expect(boarding.getMinutes()).toBe(45)
  })

  /**
   * Property Test: 跨年场景应正确处理
   */
  test('跨年场景应正确处理', () => {
    // 测试 2026-01-01 00:15 起飞的航班
    const departure = new Date(2026, 0, 1, 0, 15) // 2026-01-01 00:15
    const boarding = calculateBoardingTime(departure)
    
    // 登机时间应该是 2025-12-31 23:45
    expect(boarding.getFullYear()).toBe(2025)
    expect(boarding.getMonth()).toBe(11) // 12月
    expect(boarding.getDate()).toBe(31)
    expect(boarding.getHours()).toBe(23)
    expect(boarding.getMinutes()).toBe(45)
  })

  /**
   * Property Test: null 输入应返回 null
   */
  test('null 输入应返回 null', () => {
    expect(calculateBoardingTime(null)).toBeNull()
  })

  /**
   * Property Test: undefined 输入应返回 null
   */
  test('undefined 输入应返回 null', () => {
    expect(calculateBoardingTime(undefined)).toBeNull()
  })

  /**
   * Property Test: 无效字符串应返回 null
   */
  test('无效字符串应返回 null', () => {
    expect(calculateBoardingTime('invalid-date')).toBeNull()
    expect(calculateBoardingTime('')).toBeNull()
  })

  /**
   * Property Test: 非日期类型应返回 null
   */
  test('非日期类型应返回 null', () => {
    expect(calculateBoardingTime(123)).toBeNull()
    expect(calculateBoardingTime({})).toBeNull()
    expect(calculateBoardingTime([])).toBeNull()
  })

  /**
   * Property Test: formatBoardingTime 应返回格式化的时间字符串
   */
  test('formatBoardingTime 应返回格式化的时间字符串', () => {
    const departure = new Date(2026, 0, 15, 8, 30) // 08:30
    const formatted = formatBoardingTime(departure)
    
    // 应该返回 08:00 格式的字符串
    expect(formatted).toMatch(/08:00/)
  })

  /**
   * Property Test: formatBoardingTime 对无效输入应返回空字符串
   */
  test('formatBoardingTime 对无效输入应返回空字符串', () => {
    expect(formatBoardingTime(null)).toBe('')
    expect(formatBoardingTime(undefined)).toBe('')
    expect(formatBoardingTime('invalid')).toBe('')
  })

  /**
   * Property Test: 典型航班时间示例
   */
  test('典型航班时间示例', () => {
    // 08:30 起飞 -> 08:00 登机
    const departure1 = new Date(2026, 0, 15, 8, 30)
    const boarding1 = calculateBoardingTime(departure1)
    expect(boarding1.getHours()).toBe(8)
    expect(boarding1.getMinutes()).toBe(0)

    // 14:45 起飞 -> 14:15 登机
    const departure2 = new Date(2026, 0, 15, 14, 45)
    const boarding2 = calculateBoardingTime(departure2)
    expect(boarding2.getHours()).toBe(14)
    expect(boarding2.getMinutes()).toBe(15)

    // 00:00 起飞 -> 23:30 登机（前一天）
    const departure3 = new Date(2026, 0, 15, 0, 0)
    const boarding3 = calculateBoardingTime(departure3)
    expect(boarding3.getDate()).toBe(14)
    expect(boarding3.getHours()).toBe(23)
    expect(boarding3.getMinutes()).toBe(30)
  })
})
