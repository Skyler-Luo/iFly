/**
 * **Feature: online-checkin, Property 4: 证件号码脱敏**
 * **Validates: Requirements 2.5**
 * 
 * Property: For any ID number with length > 8, the masked result should:
 * - Preserve the first 4 characters
 * - Preserve the last 4 characters
 * - Replace middle characters with asterisks
 * - Have the same length as the original
 */

/* eslint-env jest */

const fc = require('fast-check')
const { maskIdNumber } = require('../utils/idMasking')

/**
 * 生成有效的证件号码字符（数字和大写字母）
 */
const idCharArb = fc.constantFrom(
  '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
  'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
  'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
  'U', 'V', 'W', 'X', 'Y', 'Z'
)

/**
 * 生成长度大于8的证件号码
 */
const longIdNumberArb = fc.array(idCharArb, { minLength: 9, maxLength: 18 })
  .map(chars => chars.join(''))

/**
 * 生成长度小于等于8的证件号码
 */
const shortIdNumberArb = fc.array(idCharArb, { minLength: 1, maxLength: 8 })
  .map(chars => chars.join(''))

describe('Property 4: 证件号码脱敏', () => {
  /**
   * Property Test: 长证件号码脱敏后长度应与原长度相同
   */
  test('长证件号码脱敏后长度应与原长度相同', () => {
    fc.assert(
      fc.property(
        longIdNumberArb,
        (idNumber) => {
          const masked = maskIdNumber(idNumber)
          
          expect(masked.length).toBe(idNumber.length)
          return masked.length === idNumber.length
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 长证件号码脱敏后前4位应保持不变
   */
  test('长证件号码脱敏后前4位应保持不变', () => {
    fc.assert(
      fc.property(
        longIdNumberArb,
        (idNumber) => {
          const masked = maskIdNumber(idNumber)
          
          expect(masked.slice(0, 4)).toBe(idNumber.slice(0, 4))
          return masked.slice(0, 4) === idNumber.slice(0, 4)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 长证件号码脱敏后后4位应保持不变
   */
  test('长证件号码脱敏后后4位应保持不变', () => {
    fc.assert(
      fc.property(
        longIdNumberArb,
        (idNumber) => {
          const masked = maskIdNumber(idNumber)
          
          expect(masked.slice(-4)).toBe(idNumber.slice(-4))
          return masked.slice(-4) === idNumber.slice(-4)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 长证件号码脱敏后中间部分应全为星号
   */
  test('长证件号码脱敏后中间部分应全为星号', () => {
    fc.assert(
      fc.property(
        longIdNumberArb,
        (idNumber) => {
          const masked = maskIdNumber(idNumber)
          const middle = masked.slice(4, -4)
          
          const allAsterisks = middle.split('').every(char => char === '*')
          expect(allAsterisks).toBe(true)
          return allAsterisks
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 长证件号码脱敏后中间星号数量应正确
   */
  test('长证件号码脱敏后中间星号数量应正确', () => {
    fc.assert(
      fc.property(
        longIdNumberArb,
        (idNumber) => {
          const masked = maskIdNumber(idNumber)
          const middle = masked.slice(4, -4)
          const expectedLength = idNumber.length - 8
          
          expect(middle.length).toBe(expectedLength)
          return middle.length === expectedLength
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 短证件号码（长度<=8）应全部用星号替代
   */
  test('短证件号码应全部用星号替代', () => {
    fc.assert(
      fc.property(
        shortIdNumberArb,
        (idNumber) => {
          const masked = maskIdNumber(idNumber)
          
          // 长度应相同
          expect(masked.length).toBe(idNumber.length)
          
          // 全部应为星号
          const allAsterisks = masked.split('').every(char => char === '*')
          expect(allAsterisks).toBe(true)
          
          return masked.length === idNumber.length && allAsterisks
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 空字符串应返回空字符串
   */
  test('空字符串应返回空字符串', () => {
    const masked = maskIdNumber('')
    expect(masked).toBe('')
  })

  /**
   * Property Test: null 或 undefined 应返回空字符串
   */
  test('null 或 undefined 应返回空字符串', () => {
    expect(maskIdNumber(null)).toBe('')
    expect(maskIdNumber(undefined)).toBe('')
  })

  /**
   * Property Test: 非字符串类型应返回空字符串
   */
  test('非字符串类型应返回空字符串', () => {
    expect(maskIdNumber(123456789)).toBe('')
    expect(maskIdNumber({})).toBe('')
    expect(maskIdNumber([])).toBe('')
  })

  /**
   * Property Test: 脱敏函数应是幂等的（对已脱敏的结果再次脱敏不会改变结构）
   * 注意：这不是严格的幂等性，因为星号会被保留
   */
  test('脱敏后的结果应包含星号', () => {
    fc.assert(
      fc.property(
        longIdNumberArb,
        (idNumber) => {
          const masked = maskIdNumber(idNumber)
          
          // 应该包含星号
          expect(masked).toContain('*')
          return masked.includes('*')
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 典型身份证号码脱敏示例
   */
  test('典型身份证号码脱敏示例', () => {
    // 18位身份证
    const id18 = '110101199001011234'
    const masked18 = maskIdNumber(id18)
    expect(masked18).toBe('1101**********1234')
    expect(masked18.length).toBe(18)

    // 15位身份证 (110101900101123 -> 1101 + ******* + 1123)
    const id15 = '110101900101123'
    const masked15 = maskIdNumber(id15)
    expect(masked15).toBe('1101*******1123')
    expect(masked15.length).toBe(15)

    // 护照号
    const passport = 'G12345678'
    const maskedPassport = maskIdNumber(passport)
    expect(maskedPassport).toBe('G123*5678')
    expect(maskedPassport.length).toBe(9)
  })
})
