/**
 * 倒计时格式化工具属性测试
 * Property 4: 倒计时格式正确性
 * Validates: Requirements 5.1, 5.5
 */
import fc from 'fast-check'
import { formatCountdown, parseCountdown } from '@/utils/countdownFormatter'

describe('countdownFormatter', () => {
  describe('formatCountdown', () => {
    // 基本功能测试
    it('should format 0 seconds as "00:00"', () => {
      expect(formatCountdown(0)).toBe('00:00')
    })

    it('should format 59 seconds as "00:59"', () => {
      expect(formatCountdown(59)).toBe('00:59')
    })

    it('should format 60 seconds as "01:00"', () => {
      expect(formatCountdown(60)).toBe('01:00')
    })

    it('should format 90 seconds as "01:30"', () => {
      expect(formatCountdown(90)).toBe('01:30')
    })

    it('should format 3600 seconds as "60:00"', () => {
      expect(formatCountdown(3600)).toBe('60:00')
    })

    // 无效输入测试
    it('should return "--:--" for negative numbers', () => {
      expect(formatCountdown(-1)).toBe('--:--')
      expect(formatCountdown(-100)).toBe('--:--')
    })

    it('should return "--:--" for NaN', () => {
      expect(formatCountdown(NaN)).toBe('--:--')
    })

    it('should return "--:--" for non-number types', () => {
      expect(formatCountdown(null)).toBe('--:--')
      expect(formatCountdown(undefined)).toBe('--:--')
      expect(formatCountdown('60')).toBe('--:--')
    })

    // Property 4: 倒计时格式正确性 - 属性测试
    describe('Property 4: 倒计时格式正确性', () => {
      it('should format any positive seconds correctly (MM:SS format)', () => {
        fc.assert(
          fc.property(fc.integer({ min: 0, max: 7200 }), (seconds) => {
            const result = formatCountdown(seconds)
            // 验证格式为 MM:SS
            const match = result.match(/^(\d+):(\d{2})$/)
            expect(match).not.toBeNull()
            
            const [, mins, secs] = match
            const parsedMins = parseInt(mins, 10)
            const parsedSecs = parseInt(secs, 10)
            
            // 验证秒数在 0-59 范围内
            expect(parsedSecs).toBeGreaterThanOrEqual(0)
            expect(parsedSecs).toBeLessThan(60)
            
            // 验证转换回秒数正确
            expect(parsedMins * 60 + parsedSecs).toBe(seconds)
          }),
          { numRuns: 100 }
        )
      })

      it('should always produce two-digit seconds', () => {
        fc.assert(
          fc.property(fc.integer({ min: 0, max: 3600 }), (seconds) => {
            const result = formatCountdown(seconds)
            const parts = result.split(':')
            expect(parts[1].length).toBe(2)
          }),
          { numRuns: 100 }
        )
      })

      it('should handle decimal seconds by flooring', () => {
        fc.assert(
          fc.property(fc.float({ min: 0, max: 3600, noNaN: true }), (seconds) => {
            if (seconds < 0) return true // skip negative
            const result = formatCountdown(seconds)
            const floored = Math.floor(seconds)
            const expected = formatCountdown(floored)
            expect(result).toBe(expected)
          }),
          { numRuns: 100 }
        )
      })
    })
  })

  describe('parseCountdown', () => {
    it('should parse "00:00" as 0', () => {
      expect(parseCountdown('00:00')).toBe(0)
    })

    it('should parse "01:30" as 90', () => {
      expect(parseCountdown('01:30')).toBe(90)
    })

    it('should parse "60:00" as 3600', () => {
      expect(parseCountdown('60:00')).toBe(3600)
    })

    it('should return -1 for invalid format', () => {
      expect(parseCountdown('invalid')).toBe(-1)
      expect(parseCountdown('1:2:3')).toBe(-1)
      expect(parseCountdown('')).toBe(-1)
    })

    it('should return -1 for seconds >= 60', () => {
      expect(parseCountdown('01:60')).toBe(-1)
      expect(parseCountdown('01:99')).toBe(-1)
    })

    // 往返测试：format -> parse 应该得到原值
    it('should be inverse of formatCountdown', () => {
      fc.assert(
        fc.property(fc.integer({ min: 0, max: 3600 }), (seconds) => {
          const formatted = formatCountdown(seconds)
          const parsed = parseCountdown(formatted)
          expect(parsed).toBe(seconds)
        }),
        { numRuns: 100 }
      )
    })
  })
})
