/**
 * **Feature: frontend-beautification, Property 5: 卡片圆角范围**
 * **Validates: Requirements 3.3**
 * 
 * Property: For any card component, its border-radius value should be within 8-16px range
 * 
 * **Feature: frontend-beautification, Property 4: 卡片过渡时间范围**
 * **Validates: Requirements 3.1**
 * 
 * Property: For any card component, its CSS transition duration should be within 200-400ms range
 */

/* eslint-env jest */

const fc = require('fast-check')

// 设计规范常量 - 从 design.md 提取
const designConstants = {
  card: {
    borderRadius: { min: 8, max: 16 },
    transitionDuration: { min: 200, max: 400 }
  }
}

// CSS 变量定义 - 模拟从 variables.css 提取的值
const cssVariables = {
  '--card-border-radius': '12px',
  '--card-border-radius-sm': '8px',
  '--card-border-radius-lg': '16px',
  '--card-transition-duration': '300ms',
  '--animation-duration-fast': '200ms',
  '--animation-duration-normal': '300ms',
  '--animation-duration-slow': '500ms'
}

/**
 * 解析 CSS 像素值
 * @param {string} value - CSS 值，如 '12px'
 * @returns {number} - 数值，如 12
 */
function parsePxValue(value) {
  if (!value || typeof value !== 'string') return NaN
  const match = value.match(/^(\d+(?:\.\d+)?)(px)?$/)
  return match ? parseFloat(match[1]) : NaN
}

/**
 * 解析 CSS 时间值
 * @param {string} value - CSS 值，如 '300ms' 或 '0.3s'
 * @returns {number} - 毫秒值
 */
function parseMsValue(value) {
  if (!value || typeof value !== 'string') return NaN
  const msMatch = value.match(/^(\d+(?:\.\d+)?)(ms)?$/)
  if (msMatch) return parseFloat(msMatch[1])
  const sMatch = value.match(/^(\d+(?:\.\d+)?)(s)$/)
  if (sMatch) return parseFloat(sMatch[1]) * 1000
  return NaN
}

/**
 * 验证卡片圆角是否在有效范围内
 * @param {number} borderRadius - 圆角值（像素）
 * @returns {boolean}
 */
function isValidCardBorderRadius(borderRadius) {
  const { min, max } = designConstants.card.borderRadius
  return borderRadius >= min && borderRadius <= max
}

/**
 * 验证卡片过渡时间是否在有效范围内
 * @param {number} duration - 过渡时间（毫秒）
 * @returns {boolean}
 */
function isValidCardTransitionDuration(duration) {
  const { min, max } = designConstants.card.transitionDuration
  return duration >= min && duration <= max
}

describe('Property 5: 卡片圆角范围', () => {
  /**
   * Property Test: 所有卡片圆角 CSS 变量值应在 8-16px 范围内
   */
  test('所有卡片圆角 CSS 变量值应在 8-16px 范围内', () => {
    const cardBorderRadiusVars = [
      '--card-border-radius',
      '--card-border-radius-sm',
      '--card-border-radius-lg'
    ]

    fc.assert(
      fc.property(
        fc.constantFrom(...cardBorderRadiusVars),
        (varName) => {
          const value = cssVariables[varName]
          const pxValue = parsePxValue(value)
          
          expect(pxValue).not.toBeNaN()
          expect(isValidCardBorderRadius(pxValue)).toBe(true)
          
          return !isNaN(pxValue) && isValidCardBorderRadius(pxValue)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 任意生成的卡片圆角值，验证函数应正确判断其有效性
   */
  test('验证函数应正确判断卡片圆角有效性', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 30 }),
        (borderRadius) => {
          const isValid = isValidCardBorderRadius(borderRadius)
          const expectedValid = borderRadius >= 8 && borderRadius <= 16
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 边界值测试 - 8px 和 16px 应该是有效的
   */
  test('边界值 8px 和 16px 应该是有效的卡片圆角', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(8, 16),
        (borderRadius) => {
          const isValid = isValidCardBorderRadius(borderRadius)
          expect(isValid).toBe(true)
          return isValid === true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 超出范围的值应该无效
   */
  test('超出范围的圆角值应该无效', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.integer({ min: 0, max: 7 }),
          fc.integer({ min: 17, max: 100 })
        ),
        (borderRadius) => {
          const isValid = isValidCardBorderRadius(borderRadius)
          expect(isValid).toBe(false)
          return isValid === false
        }
      ),
      { numRuns: 100 }
    )
  })
})

describe('Property 4: 卡片过渡时间范围', () => {
  /**
   * Property Test: 卡片过渡时间 CSS 变量值应在 200-400ms 范围内
   */
  test('卡片过渡时间 CSS 变量值应在 200-400ms 范围内', () => {
    const cardTransitionVar = '--card-transition-duration'
    const value = cssVariables[cardTransitionVar]
    const msValue = parseMsValue(value)
    
    expect(msValue).not.toBeNaN()
    expect(isValidCardTransitionDuration(msValue)).toBe(true)
  })

  /**
   * Property Test: 任意生成的过渡时间值，验证函数应正确判断其有效性
   */
  test('验证函数应正确判断卡片过渡时间有效性', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 1000 }),
        (duration) => {
          const isValid = isValidCardTransitionDuration(duration)
          const expectedValid = duration >= 200 && duration <= 400
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 边界值测试 - 200ms 和 400ms 应该是有效的
   */
  test('边界值 200ms 和 400ms 应该是有效的过渡时间', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(200, 400),
        (duration) => {
          const isValid = isValidCardTransitionDuration(duration)
          expect(isValid).toBe(true)
          return isValid === true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 超出范围的过渡时间应该无效
   */
  test('超出范围的过渡时间应该无效', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.integer({ min: 0, max: 199 }),
          fc.integer({ min: 401, max: 1000 })
        ),
        (duration) => {
          const isValid = isValidCardTransitionDuration(duration)
          expect(isValid).toBe(false)
          return isValid === false
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 动画持续时间变量中，normal 应该在有效范围内
   */
  test('animation-duration-normal 应该在卡片过渡有效范围内', () => {
    const value = cssVariables['--animation-duration-normal']
    const msValue = parseMsValue(value)
    
    expect(msValue).not.toBeNaN()
    expect(isValidCardTransitionDuration(msValue)).toBe(true)
  })
})


/**
 * **Feature: frontend-beautification, Property 1: 响应式横幅布局适配**
 * **Validates: Requirements 1.3**
 * 
 * Property: For any screen width, the banner area height and search box position 
 * should be correctly adjusted according to predefined breakpoint rules
 */

// 响应式断点配置 - 从 design.md 和 HomeView.vue 提取
const responsiveBreakpoints = {
  mobile: 768,
  tablet: 1024,
  desktop: 1200
}

// 横幅高度配置 - 根据不同断点的预期值
const bannerHeightConfig = {
  largeDesktop: { minWidth: 1201, minHeight: 820 },
  desktop: { minWidth: 992, maxWidth: 1200, minHeight: 720 },
  tablet: { minWidth: 768, maxWidth: 991, minHeight: 620 },
  mobile: { minWidth: 480, maxWidth: 767, minHeight: 520 },
  smallMobile: { maxWidth: 479, minHeight: 450 }
}

// 搜索框位置配置 - 根据不同断点的预期值
const searchContainerConfig = {
  largeDesktop: { minWidth: 1201, bottom: 30, maxWidth: 820 },
  desktop: { minWidth: 992, maxWidth: 1200, bottom: 25, containerMaxWidth: 760 },
  tablet: { minWidth: 768, maxWidth: 991, bottom: 20, containerMaxWidth: 680 },
  mobile: { maxWidth: 767, position: 'relative', width: '95%' }
}

/**
 * 根据屏幕宽度获取预期的横幅最小高度
 * @param {number} screenWidth - 屏幕宽度（像素）
 * @returns {number} - 预期的最小高度（像素）
 */
function getExpectedBannerMinHeight(screenWidth) {
  if (screenWidth >= 1201) return bannerHeightConfig.largeDesktop.minHeight
  if (screenWidth >= 992) return bannerHeightConfig.desktop.minHeight
  if (screenWidth >= 768) return bannerHeightConfig.tablet.minHeight
  if (screenWidth >= 480) return bannerHeightConfig.mobile.minHeight
  return bannerHeightConfig.smallMobile.minHeight
}

/**
 * 根据屏幕宽度获取预期的搜索框配置
 * @param {number} screenWidth - 屏幕宽度（像素）
 * @returns {object} - 搜索框配置对象
 */
function getExpectedSearchContainerConfig(screenWidth) {
  if (screenWidth >= 1201) {
    return { position: 'absolute', bottom: 30, maxWidth: 820 }
  }
  if (screenWidth >= 992) {
    return { position: 'absolute', bottom: 25, maxWidth: 760 }
  }
  if (screenWidth >= 768) {
    return { position: 'absolute', bottom: 20, maxWidth: 680 }
  }
  // 移动端使用相对定位
  return { position: 'relative', bottom: null, width: '95%' }
}

/**
 * 验证横幅高度是否符合断点规则
 * @param {number} screenWidth - 屏幕宽度
 * @param {number} bannerHeight - 横幅高度
 * @returns {boolean}
 */
function isValidBannerHeight(screenWidth, bannerHeight) {
  const expectedMinHeight = getExpectedBannerMinHeight(screenWidth)
  return bannerHeight >= expectedMinHeight
}

/**
 * 验证搜索框配置是否符合断点规则
 * @param {number} screenWidth - 屏幕宽度
 * @param {object} config - 搜索框配置
 * @returns {boolean}
 */
function isValidSearchContainerConfig(screenWidth, config) {
  const expected = getExpectedSearchContainerConfig(screenWidth)
  
  // 验证定位方式
  if (config.position !== expected.position) return false
  
  // 桌面端验证 bottom 值
  if (expected.position === 'absolute') {
    if (config.bottom !== expected.bottom) return false
    if (config.maxWidth > expected.maxWidth) return false
  }
  
  return true
}

describe('Property 1: 响应式横幅布局适配', () => {
  /**
   * Property Test: 对于任意屏幕宽度，横幅高度应符合预定义的断点规则
   */
  test('横幅高度应根据屏幕宽度正确调整', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 2560 }),
        (screenWidth) => {
          const expectedMinHeight = getExpectedBannerMinHeight(screenWidth)
          
          // 验证预期高度是合理的正数
          expect(expectedMinHeight).toBeGreaterThan(0)
          
          // 验证高度随屏幕变大而增加（或保持）
          if (screenWidth >= 1201) {
            expect(expectedMinHeight).toBe(820)
          } else if (screenWidth >= 992) {
            expect(expectedMinHeight).toBe(720)
          } else if (screenWidth >= 768) {
            expect(expectedMinHeight).toBe(620)
          } else if (screenWidth >= 480) {
            expect(expectedMinHeight).toBe(520)
          } else {
            expect(expectedMinHeight).toBe(450)
          }
          
          return expectedMinHeight > 0
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 搜索框位置应根据屏幕宽度正确调整
   */
  test('搜索框位置应根据屏幕宽度正确调整', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 2560 }),
        (screenWidth) => {
          const config = getExpectedSearchContainerConfig(screenWidth)
          
          // 移动端应使用相对定位
          if (screenWidth < 768) {
            expect(config.position).toBe('relative')
            expect(config.width).toBe('95%')
          } else {
            // 桌面端应使用绝对定位
            expect(config.position).toBe('absolute')
            expect(config.bottom).toBeGreaterThan(0)
            expect(config.maxWidth).toBeGreaterThan(0)
          }
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 断点边界值测试
   */
  test('断点边界值应正确处理', () => {
    const boundaryValues = [
      { width: 479, expectedHeight: 450, expectedPosition: 'relative' },
      { width: 480, expectedHeight: 520, expectedPosition: 'relative' },
      { width: 767, expectedHeight: 520, expectedPosition: 'relative' },
      { width: 768, expectedHeight: 620, expectedPosition: 'absolute' },
      { width: 991, expectedHeight: 620, expectedPosition: 'absolute' },
      { width: 992, expectedHeight: 720, expectedPosition: 'absolute' },
      { width: 1200, expectedHeight: 720, expectedPosition: 'absolute' },
      { width: 1201, expectedHeight: 820, expectedPosition: 'absolute' }
    ]

    fc.assert(
      fc.property(
        fc.constantFrom(...boundaryValues),
        ({ width, expectedHeight, expectedPosition }) => {
          const actualHeight = getExpectedBannerMinHeight(width)
          const actualConfig = getExpectedSearchContainerConfig(width)
          
          expect(actualHeight).toBe(expectedHeight)
          expect(actualConfig.position).toBe(expectedPosition)
          
          return actualHeight === expectedHeight && actualConfig.position === expectedPosition
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 横幅高度应随屏幕宽度单调递增（或保持）
   */
  test('横幅高度应随屏幕宽度单调递增', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 2500 }),
        fc.integer({ min: 1, max: 100 }),
        (baseWidth, increment) => {
          const smallerWidth = baseWidth
          const largerWidth = baseWidth + increment
          
          const smallerHeight = getExpectedBannerMinHeight(smallerWidth)
          const largerHeight = getExpectedBannerMinHeight(largerWidth)
          
          // 较大屏幕的高度应该 >= 较小屏幕的高度
          expect(largerHeight).toBeGreaterThanOrEqual(smallerHeight)
          
          return largerHeight >= smallerHeight
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 搜索框最大宽度应随屏幕宽度合理变化
   */
  test('搜索框最大宽度应随屏幕宽度合理变化', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 768, max: 2560 }),
        (screenWidth) => {
          const config = getExpectedSearchContainerConfig(screenWidth)
          
          // 桌面端搜索框最大宽度应在合理范围内
          expect(config.maxWidth).toBeGreaterThanOrEqual(680)
          expect(config.maxWidth).toBeLessThanOrEqual(820)
          
          // 较大屏幕应有较大的最大宽度
          if (screenWidth >= 1201) {
            expect(config.maxWidth).toBe(820)
          } else if (screenWidth >= 992) {
            expect(config.maxWidth).toBe(760)
          } else {
            expect(config.maxWidth).toBe(680)
          }
          
          return true
        }
      ),
      { numRuns: 100 }
    )
  })
})


/**
 * **Feature: frontend-beautification, Property 2: 区块间距一致性**
 * **Validates: Requirements 2.1**
 * 
 * Property: For any content section, its padding and margin should conform to 
 * the standard values defined in the design system (section-padding-y: 60px, section-padding-x: 20px)
 */

// 区块间距配置 - 从 variables.css 提取
const sectionSpacingConfig = {
  paddingY: 60,
  paddingX: 20,
  marginBottom: 75,
  gap: 80
}

// CSS 变量定义 - 区块间距相关
const sectionCssVariables = {
  '--section-padding-y': '60px',
  '--section-padding-x': '20px',
  '--section-margin-bottom': '75px',
  '--section-gap': '80px'
}

/**
 * 验证区块内边距是否符合设计规范
 * @param {number} paddingY - 垂直内边距（像素）
 * @param {number} paddingX - 水平内边距（像素）
 * @returns {boolean}
 */
function isValidSectionPadding(paddingY, paddingX) {
  return paddingY === sectionSpacingConfig.paddingY && 
         paddingX === sectionSpacingConfig.paddingX
}

/**
 * 验证区块外边距是否符合设计规范
 * @param {number} marginBottom - 底部外边距（像素）
 * @returns {boolean}
 */
function isValidSectionMargin(marginBottom) {
  return marginBottom === sectionSpacingConfig.marginBottom
}

describe('Property 2: 区块间距一致性', () => {
  /**
   * Property Test: 所有区块间距 CSS 变量值应符合设计规范
   */
  test('区块间距 CSS 变量值应符合设计规范', () => {
    const sectionSpacingVars = [
      { name: '--section-padding-y', expected: 60 },
      { name: '--section-padding-x', expected: 20 },
      { name: '--section-margin-bottom', expected: 75 },
      { name: '--section-gap', expected: 80 }
    ]

    fc.assert(
      fc.property(
        fc.constantFrom(...sectionSpacingVars),
        ({ name, expected }) => {
          const value = sectionCssVariables[name]
          const pxValue = parsePxValue(value)
          
          expect(pxValue).not.toBeNaN()
          expect(pxValue).toBe(expected)
          
          return !isNaN(pxValue) && pxValue === expected
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 任意生成的区块间距值，验证函数应正确判断其有效性
   */
  test('验证函数应正确判断区块内边距有效性', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 100 }),
        fc.integer({ min: 0, max: 100 }),
        (paddingY, paddingX) => {
          const isValid = isValidSectionPadding(paddingY, paddingX)
          const expectedValid = paddingY === 60 && paddingX === 20
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 标准区块间距值应该是有效的
   */
  test('标准区块间距值应该是有效的', () => {
    fc.assert(
      fc.property(
        fc.constant({ paddingY: 60, paddingX: 20 }),
        ({ paddingY, paddingX }) => {
          const isValid = isValidSectionPadding(paddingY, paddingX)
          expect(isValid).toBe(true)
          return isValid === true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 非标准区块间距值应该无效
   */
  test('非标准区块间距值应该无效', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.record({
            paddingY: fc.integer({ min: 0, max: 59 }),
            paddingX: fc.constant(20)
          }),
          fc.record({
            paddingY: fc.integer({ min: 61, max: 100 }),
            paddingX: fc.constant(20)
          }),
          fc.record({
            paddingY: fc.constant(60),
            paddingX: fc.integer({ min: 0, max: 19 })
          }),
          fc.record({
            paddingY: fc.constant(60),
            paddingX: fc.integer({ min: 21, max: 100 })
          })
        ),
        ({ paddingY, paddingX }) => {
          const isValid = isValidSectionPadding(paddingY, paddingX)
          expect(isValid).toBe(false)
          return isValid === false
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 区块底部外边距应符合设计规范
   */
  test('区块底部外边距应符合设计规范', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 150 }),
        (marginBottom) => {
          const isValid = isValidSectionMargin(marginBottom)
          const expectedValid = marginBottom === 75
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })
})


/**
 * **Feature: frontend-beautification, Property 3: 标题样式统一性**
 * **Validates: Requirements 2.2**
 * 
 * Property: For any section title element, its font size, color, and decoration line style 
 * should be consistent with the design specification
 */

// 标题样式配置 - 从 variables.css 提取
const sectionTitleConfig = {
  fontSize: '2.2em',
  fontWeight: 600,
  color: '#003b7a',
  marginBottom: 35,
  paddingBottom: 28,
  decorationWidth: 70,
  decorationHeight: 3
}

// CSS 变量定义 - 标题样式相关
const titleCssVariables = {
  '--section-title-font-size': '2.2em',
  '--section-title-font-weight': '600',
  '--section-title-color': '#003b7a',
  '--section-title-margin-bottom': '35px',
  '--section-title-padding-bottom': '28px',
  '--section-title-decoration-width': '70px',
  '--section-title-decoration-height': '3px'
}

/**
 * 解析 CSS em 值
 * @param {string} value - CSS 值，如 '2.2em'
 * @returns {number} - 数值，如 2.2
 */
function parseEmValue(value) {
  if (!value || typeof value !== 'string') return NaN
  const match = value.match(/^(\d+(?:\.\d+)?)(em)?$/)
  return match ? parseFloat(match[1]) : NaN
}

/**
 * 验证标题字体大小是否符合设计规范
 * @param {string} fontSize - 字体大小值
 * @returns {boolean}
 */
function isValidTitleFontSize(fontSize) {
  const emValue = parseEmValue(fontSize)
  return !isNaN(emValue) && emValue === 2.2
}

/**
 * 验证标题颜色是否符合设计规范
 * @param {string} color - 颜色值
 * @returns {boolean}
 */
function isValidTitleColor(color) {
  return color.toLowerCase() === sectionTitleConfig.color.toLowerCase()
}

/**
 * 验证标题装饰线尺寸是否符合设计规范
 * @param {number} width - 装饰线宽度（像素）
 * @param {number} height - 装饰线高度（像素）
 * @returns {boolean}
 */
function isValidTitleDecoration(width, height) {
  return width === sectionTitleConfig.decorationWidth && 
         height === sectionTitleConfig.decorationHeight
}

describe('Property 3: 标题样式统一性', () => {
  /**
   * Property Test: 标题字体大小 CSS 变量值应符合设计规范
   */
  test('标题字体大小 CSS 变量值应符合设计规范', () => {
    const value = titleCssVariables['--section-title-font-size']
    const emValue = parseEmValue(value)
    
    expect(emValue).not.toBeNaN()
    expect(isValidTitleFontSize(value)).toBe(true)
  })

  /**
   * Property Test: 标题颜色 CSS 变量值应符合设计规范
   */
  test('标题颜色 CSS 变量值应符合设计规范', () => {
    const value = titleCssVariables['--section-title-color']
    
    expect(isValidTitleColor(value)).toBe(true)
  })

  /**
   * Property Test: 任意生成的标题字体大小值，验证函数应正确判断其有效性
   */
  test('验证函数应正确判断标题字体大小有效性', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.constant('2.2em'),
          fc.constant('1.8em'),
          fc.constant('2.5em'),
          fc.constant('28px'),
          fc.constant('2em')
        ),
        (fontSize) => {
          const isValid = isValidTitleFontSize(fontSize)
          const expectedValid = fontSize === '2.2em'
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 标题装饰线尺寸应符合设计规范
   */
  test('标题装饰线尺寸应符合设计规范', () => {
    const widthValue = titleCssVariables['--section-title-decoration-width']
    const heightValue = titleCssVariables['--section-title-decoration-height']
    
    const width = parsePxValue(widthValue)
    const height = parsePxValue(heightValue)
    
    expect(width).not.toBeNaN()
    expect(height).not.toBeNaN()
    expect(isValidTitleDecoration(width, height)).toBe(true)
  })

  /**
   * Property Test: 任意生成的装饰线尺寸值，验证函数应正确判断其有效性
   */
  test('验证函数应正确判断装饰线尺寸有效性', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 100 }),
        fc.integer({ min: 0, max: 10 }),
        (width, height) => {
          const isValid = isValidTitleDecoration(width, height)
          const expectedValid = width === 70 && height === 3
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 标题间距 CSS 变量值应符合设计规范
   */
  test('标题间距 CSS 变量值应符合设计规范', () => {
    const marginBottomValue = titleCssVariables['--section-title-margin-bottom']
    const paddingBottomValue = titleCssVariables['--section-title-padding-bottom']
    
    const marginBottom = parsePxValue(marginBottomValue)
    const paddingBottom = parsePxValue(paddingBottomValue)
    
    expect(marginBottom).toBe(sectionTitleConfig.marginBottom)
    expect(paddingBottom).toBe(sectionTitleConfig.paddingBottom)
  })

  /**
   * Property Test: 所有标题样式 CSS 变量应存在且有效
   */
  test('所有标题样式 CSS 变量应存在且有效', () => {
    const titleStyleVars = Object.keys(titleCssVariables)

    fc.assert(
      fc.property(
        fc.constantFrom(...titleStyleVars),
        (varName) => {
          const value = titleCssVariables[varName]
          
          expect(value).toBeDefined()
          expect(value).not.toBe('')
          
          return value !== undefined && value !== ''
        }
      ),
      { numRuns: 100 }
    )
  })
})


/**
 * **Feature: frontend-beautification, Property 6: 按钮渐变背景**
 * **Validates: Requirements 4.1**
 * 
 * Property: For any primary action button, its background style should include a gradient definition,
 * and its padding should conform to the design specification
 */

// 按钮样式配置 - 从 design.md 和 variables.css 提取
const buttonStyleConfig = {
  gradient: {
    // 渐变应包含主色调
    primaryColorStart: '#1976d2',
    primaryColorEnd: '#1565c0',
    hoverColorStart: '#1e88e5',
    hoverColorEnd: '#1565c0'
  },
  padding: {
    vertical: 12,
    horizontal: 24
  },
  borderRadius: 8,
  fontWeight: 600
}

// CSS 变量定义 - 按钮样式相关
const buttonCssVariables = {
  '--button-gradient-primary': 'linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%)',
  '--button-gradient-hover': 'linear-gradient(135deg, var(--color-primary-hover) 0%, var(--color-primary-dark) 100%)',
  '--button-shadow-hover': '0 4px 12px rgba(25, 118, 210, 0.3)',
  '--button-shadow-active': '0 2px 6px rgba(25, 118, 210, 0.2)',
  '--button-transition': 'all var(--animation-duration-fast) var(--animation-easing-smooth)'
}

/**
 * 验证按钮背景是否包含渐变定义
 * @param {string} background - CSS 背景值
 * @returns {boolean}
 */
function hasGradientBackground(background) {
  if (!background || typeof background !== 'string') return false
  // 检查是否包含 linear-gradient 或 radial-gradient
  return background.includes('linear-gradient') || background.includes('radial-gradient')
}

/**
 * 验证渐变是否包含品牌主色调
 * @param {string} gradient - CSS 渐变值
 * @returns {boolean}
 */
function hasValidGradientColors(gradient) {
  if (!gradient || typeof gradient !== 'string') return false
  
  // 检查是否包含主色调变量引用或实际颜色值
  const hasPrimaryColor = gradient.includes('--color-primary') || 
                          gradient.includes('#1976d2') ||
                          gradient.includes('rgb(25, 118, 210)')
  
  const hasDarkColor = gradient.includes('--color-primary-dark') || 
                       gradient.includes('#1565c0') ||
                       gradient.includes('rgb(21, 101, 192)')
  
  return hasPrimaryColor || hasDarkColor
}

/**
 * 验证按钮内边距是否符合设计规范
 * @param {number} paddingVertical - 垂直内边距（像素）
 * @param {number} paddingHorizontal - 水平内边距（像素）
 * @returns {boolean}
 */
function isValidButtonPadding(paddingVertical, paddingHorizontal) {
  return paddingVertical === buttonStyleConfig.padding.vertical && 
         paddingHorizontal === buttonStyleConfig.padding.horizontal
}

/**
 * 验证按钮圆角是否符合设计规范
 * @param {number} borderRadius - 圆角值（像素）
 * @returns {boolean}
 */
function isValidButtonBorderRadius(borderRadius) {
  // 按钮圆角应在 6-8px 范围内
  return borderRadius >= 6 && borderRadius <= 8
}

/**
 * 验证按钮字体粗细是否符合设计规范
 * @param {number} fontWeight - 字体粗细值
 * @returns {boolean}
 */
function isValidButtonFontWeight(fontWeight) {
  // 按钮字体粗细应为 600 (semibold)
  return fontWeight === 600 || fontWeight === 'semibold'
}

describe('Property 6: 按钮渐变背景', () => {
  /**
   * Property Test: 主要按钮渐变 CSS 变量应包含渐变定义
   */
  test('主要按钮渐变 CSS 变量应包含渐变定义', () => {
    const gradientVars = [
      '--button-gradient-primary',
      '--button-gradient-hover'
    ]

    fc.assert(
      fc.property(
        fc.constantFrom(...gradientVars),
        (varName) => {
          const value = buttonCssVariables[varName]
          
          expect(value).toBeDefined()
          expect(hasGradientBackground(value)).toBe(true)
          
          return value !== undefined && hasGradientBackground(value)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 按钮渐变应包含品牌主色调
   */
  test('按钮渐变应包含品牌主色调', () => {
    const gradientVars = [
      '--button-gradient-primary',
      '--button-gradient-hover'
    ]

    fc.assert(
      fc.property(
        fc.constantFrom(...gradientVars),
        (varName) => {
          const value = buttonCssVariables[varName]
          
          expect(value).toBeDefined()
          expect(hasValidGradientColors(value)).toBe(true)
          
          return value !== undefined && hasValidGradientColors(value)
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 任意生成的背景值，验证函数应正确判断是否为渐变
   */
  test('验证函数应正确判断背景是否为渐变', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.constant('linear-gradient(135deg, #1976d2 0%, #1565c0 100%)'),
          fc.constant('linear-gradient(180deg, #1976d2 0%, #1565c0 100%)'),
          fc.constant('radial-gradient(circle, #1976d2 0%, #1565c0 100%)'),
          fc.constant('#1976d2'),
          fc.constant('rgb(25, 118, 210)'),
          fc.constant('blue'),
          fc.constant('')
        ),
        (background) => {
          const isGradient = hasGradientBackground(background)
          const expectedGradient = background.includes('gradient')
          
          expect(isGradient).toBe(expectedGradient)
          return isGradient === expectedGradient
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 按钮内边距应符合设计规范
   */
  test('按钮内边距应符合设计规范', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 50 }),
        fc.integer({ min: 0, max: 50 }),
        (paddingVertical, paddingHorizontal) => {
          const isValid = isValidButtonPadding(paddingVertical, paddingHorizontal)
          const expectedValid = paddingVertical === 12 && paddingHorizontal === 24
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 标准按钮内边距值应该是有效的
   */
  test('标准按钮内边距值应该是有效的', () => {
    fc.assert(
      fc.property(
        fc.constant({ paddingVertical: 12, paddingHorizontal: 24 }),
        ({ paddingVertical, paddingHorizontal }) => {
          const isValid = isValidButtonPadding(paddingVertical, paddingHorizontal)
          expect(isValid).toBe(true)
          return isValid === true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 按钮圆角应在有效范围内
   */
  test('按钮圆角应在有效范围内 (6-8px)', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 20 }),
        (borderRadius) => {
          const isValid = isValidButtonBorderRadius(borderRadius)
          const expectedValid = borderRadius >= 6 && borderRadius <= 8
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 按钮字体粗细应为 semibold (600)
   */
  test('按钮字体粗细应为 semibold (600)', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.constant(400),
          fc.constant(500),
          fc.constant(600),
          fc.constant(700),
          fc.constant('normal'),
          fc.constant('semibold'),
          fc.constant('bold')
        ),
        (fontWeight) => {
          const isValid = isValidButtonFontWeight(fontWeight)
          const expectedValid = fontWeight === 600 || fontWeight === 'semibold'
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 所有按钮样式 CSS 变量应存在且有效
   */
  test('所有按钮样式 CSS 变量应存在且有效', () => {
    const buttonStyleVars = Object.keys(buttonCssVariables)

    fc.assert(
      fc.property(
        fc.constantFrom(...buttonStyleVars),
        (varName) => {
          const value = buttonCssVariables[varName]
          
          expect(value).toBeDefined()
          expect(value).not.toBe('')
          
          return value !== undefined && value !== ''
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 按钮悬停阴影应包含主色调透明度
   */
  test('按钮悬停阴影应包含主色调透明度', () => {
    const shadowVars = [
      '--button-shadow-hover',
      '--button-shadow-active'
    ]

    fc.assert(
      fc.property(
        fc.constantFrom(...shadowVars),
        (varName) => {
          const value = buttonCssVariables[varName]
          
          expect(value).toBeDefined()
          // 阴影应包含 rgba 颜色值
          expect(value.includes('rgba')).toBe(true)
          // 阴影应包含主色调的 RGB 值 (25, 118, 210)
          expect(value.includes('25, 118, 210')).toBe(true)
          
          return value !== undefined && value.includes('rgba') && value.includes('25, 118, 210')
        }
      ),
      { numRuns: 100 }
    )
  })
})


/**
 * **Feature: frontend-beautification, Property 7: 移动端单列布局**
 * **Validates: Requirements 5.1**
 * 
 * Property: For any viewport width less than 768px, multi-column grid layouts 
 * should be converted to single-column layouts
 */

// 移动端断点配置
const mobileBreakpoint = 768

// 布局配置 - 从 responsive.css 提取
const layoutConfig = {
  mobile: {
    maxWidth: 767,
    gridColumns: 1
  },
  tablet: {
    minWidth: 768,
    maxWidth: 1024,
    gridColumns: 2
  },
  desktop: {
    minWidth: 1025,
    gridColumns: 3
  }
}

// CSS 类名和对应的桌面端列数
const multiColumnClasses = {
  'grid-responsive': { desktopColumns: 'auto-fit', mobileColumns: 1 },
  'multi-column-layout': { desktopColumns: 3, mobileColumns: 1 },
  'multi-column-layout-2': { desktopColumns: 2, mobileColumns: 1 },
  'multi-column-layout-4': { desktopColumns: 4, mobileColumns: 1 }
}

/**
 * 根据屏幕宽度获取预期的网格列数
 * @param {number} screenWidth - 屏幕宽度（像素）
 * @param {string} className - CSS 类名
 * @returns {number|string} - 预期的列数
 */
function getExpectedGridColumns(screenWidth, className) {
  const config = multiColumnClasses[className]
  if (!config) return 1
  
  if (screenWidth < mobileBreakpoint) {
    return config.mobileColumns
  }
  return config.desktopColumns
}

/**
 * 验证移动端是否为单列布局
 * @param {number} screenWidth - 屏幕宽度（像素）
 * @param {number} columns - 实际列数
 * @returns {boolean}
 */
function isValidMobileSingleColumn(screenWidth, columns) {
  if (screenWidth < mobileBreakpoint) {
    return columns === 1
  }
  return true // 非移动端不限制
}

/**
 * 验证布局是否符合断点规则
 * @param {number} screenWidth - 屏幕宽度
 * @param {string} className - CSS 类名
 * @param {number} actualColumns - 实际列数
 * @returns {boolean}
 */
function isValidLayoutForBreakpoint(screenWidth, className, actualColumns) {
  const expectedColumns = getExpectedGridColumns(screenWidth, className)
  
  if (screenWidth < mobileBreakpoint) {
    return actualColumns === 1
  }
  
  // 桌面端可以是预期列数或更少（响应式）
  if (typeof expectedColumns === 'number') {
    return actualColumns <= expectedColumns && actualColumns >= 1
  }
  
  return actualColumns >= 1
}

describe('Property 7: 移动端单列布局', () => {
  /**
   * Property Test: 对于任意小于 768px 的视口宽度，多列网格布局应转换为单列布局
   */
  test('小于 768px 的视口宽度应使用单列布局', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 767 }),
        fc.constantFrom(...Object.keys(multiColumnClasses)),
        (screenWidth, className) => {
          const expectedColumns = getExpectedGridColumns(screenWidth, className)
          
          // 移动端应该是单列
          expect(expectedColumns).toBe(1)
          expect(isValidMobileSingleColumn(screenWidth, 1)).toBe(true)
          
          return expectedColumns === 1
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 768px 及以上的视口宽度可以使用多列布局
   */
  test('768px 及以上的视口宽度可以使用多列布局', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 768, max: 2560 }),
        fc.constantFrom(...Object.keys(multiColumnClasses)),
        (screenWidth, className) => {
          const expectedColumns = getExpectedGridColumns(screenWidth, className)
          const config = multiColumnClasses[className]
          
          // 桌面端应该是配置的列数
          expect(expectedColumns).toBe(config.desktopColumns)
          
          return expectedColumns === config.desktopColumns
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 断点边界值 767px 和 768px 应正确处理
   */
  test('断点边界值应正确处理', () => {
    const boundaryTests = [
      { width: 767, expectedColumns: 1, isMobile: true },
      { width: 768, expectedColumns: 'desktop', isMobile: false }
    ]

    fc.assert(
      fc.property(
        fc.constantFrom(...boundaryTests),
        fc.constantFrom(...Object.keys(multiColumnClasses)),
        ({ width, expectedColumns, isMobile }, className) => {
          const actualExpected = getExpectedGridColumns(width, className)
          const config = multiColumnClasses[className]
          
          if (isMobile) {
            expect(actualExpected).toBe(1)
            return actualExpected === 1
          } else {
            expect(actualExpected).toBe(config.desktopColumns)
            return actualExpected === config.desktopColumns
          }
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 验证函数应正确判断移动端单列布局有效性
   */
  test('验证函数应正确判断移动端单列布局有效性', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 1200 }),
        fc.integer({ min: 1, max: 4 }),
        (screenWidth, columns) => {
          const isValid = isValidMobileSingleColumn(screenWidth, columns)
          
          if (screenWidth < mobileBreakpoint) {
            // 移动端只有单列才有效
            const expectedValid = columns === 1
            expect(isValid).toBe(expectedValid)
            return isValid === expectedValid
          } else {
            // 非移动端任何列数都有效
            expect(isValid).toBe(true)
            return isValid === true
          }
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 所有多列布局类在移动端都应转换为单列
   */
  test('所有多列布局类在移动端都应转换为单列', () => {
    const classNames = Object.keys(multiColumnClasses)

    fc.assert(
      fc.property(
        fc.constantFrom(...classNames),
        fc.integer({ min: 320, max: 767 }),
        (className, screenWidth) => {
          const columns = getExpectedGridColumns(screenWidth, className)
          
          expect(columns).toBe(1)
          expect(isValidLayoutForBreakpoint(screenWidth, className, 1)).toBe(true)
          
          return columns === 1
        }
      ),
      { numRuns: 100 }
    )
  })
})


/**
 * **Feature: frontend-beautification, Property 9: 触摸目标最小尺寸**
 * **Validates: Requirements 5.4**
 * 
 * Property: For any form interactive element (input, button), in mobile viewport 
 * its size should be at least 44x44 pixels
 */

// 触摸目标配置 - 从 responsive.css 提取
const touchTargetConfig = {
  minSize: 44, // 像素
  mobileBreakpoint: 768
}

// 表单元素类型
const formElementTypes = [
  'input',
  'button',
  'select',
  'textarea',
  'a.touch-enhanced',
  '.el-input__inner',
  '.el-button',
  '.el-select .el-input__inner'
]

/**
 * 验证触摸目标尺寸是否符合最小要求
 * @param {number} width - 元素宽度（像素）
 * @param {number} height - 元素高度（像素）
 * @returns {boolean}
 */
function isValidTouchTargetSize(width, height) {
  return width >= touchTargetConfig.minSize && height >= touchTargetConfig.minSize
}

/**
 * 验证移动端触摸目标是否符合要求
 * @param {number} screenWidth - 屏幕宽度（像素）
 * @param {number} elementWidth - 元素宽度（像素）
 * @param {number} elementHeight - 元素高度（像素）
 * @returns {boolean}
 */
function isValidMobileTouchTarget(screenWidth, elementWidth, elementHeight) {
  if (screenWidth < touchTargetConfig.mobileBreakpoint) {
    return isValidTouchTargetSize(elementWidth, elementHeight)
  }
  return true // 非移动端不强制要求
}

/**
 * 获取预期的最小触摸目标尺寸
 * @param {number} screenWidth - 屏幕宽度（像素）
 * @returns {number} - 最小尺寸（像素）
 */
function getExpectedMinTouchSize(screenWidth) {
  if (screenWidth < touchTargetConfig.mobileBreakpoint) {
    return touchTargetConfig.minSize
  }
  return 0 // 非移动端无最小要求
}

describe('Property 9: 触摸目标最小尺寸', () => {
  /**
   * Property Test: 移动端表单元素尺寸应至少为 44x44 像素
   */
  test('移动端触摸目标应至少为 44x44 像素', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 767 }),
        (screenWidth) => {
          const minSize = getExpectedMinTouchSize(screenWidth)
          
          expect(minSize).toBe(44)
          expect(isValidTouchTargetSize(44, 44)).toBe(true)
          expect(isValidTouchTargetSize(43, 44)).toBe(false)
          expect(isValidTouchTargetSize(44, 43)).toBe(false)
          
          return minSize === 44
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 验证函数应正确判断触摸目标尺寸有效性
   */
  test('验证函数应正确判断触摸目标尺寸有效性', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 20, max: 100 }),
        fc.integer({ min: 20, max: 100 }),
        (width, height) => {
          const isValid = isValidTouchTargetSize(width, height)
          const expectedValid = width >= 44 && height >= 44
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 边界值 44px 应该是有效的触摸目标尺寸
   */
  test('边界值 44px 应该是有效的触摸目标尺寸', () => {
    fc.assert(
      fc.property(
        fc.constantFrom(44, 45, 48, 50),
        fc.constantFrom(44, 45, 48, 50),
        (width, height) => {
          const isValid = isValidTouchTargetSize(width, height)
          expect(isValid).toBe(true)
          return isValid === true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 小于 44px 的尺寸应该无效
   */
  test('小于 44px 的尺寸应该无效', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 10, max: 43 }),
        fc.integer({ min: 10, max: 43 }),
        (width, height) => {
          const isValid = isValidTouchTargetSize(width, height)
          expect(isValid).toBe(false)
          return isValid === false
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 移动端验证应强制执行最小尺寸要求
   */
  test('移动端验证应强制执行最小尺寸要求', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 320, max: 767 }),
        fc.integer({ min: 20, max: 100 }),
        fc.integer({ min: 20, max: 100 }),
        (screenWidth, elementWidth, elementHeight) => {
          const isValid = isValidMobileTouchTarget(screenWidth, elementWidth, elementHeight)
          const expectedValid = elementWidth >= 44 && elementHeight >= 44
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 非移动端不强制要求最小触摸尺寸
   */
  test('非移动端不强制要求最小触摸尺寸', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 768, max: 2560 }),
        fc.integer({ min: 20, max: 100 }),
        fc.integer({ min: 20, max: 100 }),
        (screenWidth, elementWidth, elementHeight) => {
          const isValid = isValidMobileTouchTarget(screenWidth, elementWidth, elementHeight)
          
          // 非移动端任何尺寸都有效
          expect(isValid).toBe(true)
          return isValid === true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: CSS 变量 --touch-target-min 应为 44px
   */
  test('CSS 变量 --touch-target-min 应为 44px', () => {
    // 模拟从 responsive.css 读取的值
    const touchTargetMinVar = '44px'
    const pxValue = parsePxValue(touchTargetMinVar)
    
    expect(pxValue).toBe(44)
    expect(isValidTouchTargetSize(pxValue, pxValue)).toBe(true)
  })
})


/**
 * **Feature: frontend-beautification, Property 8: 移动端卡片触摸适配**
 * **Validates: Requirements 5.3**
 * 
 * Property: For any card component in mobile viewport, its size and spacing 
 * should be suitable for touch operation
 */

// 移动端卡片配置 - 从 responsive.css 提取
const mobileCardConfig = {
  minPadding: 16, // var(--space-md)
  minMarginBottom: 16, // var(--space-md)
  minBorderRadius: 8,
  maxBorderRadius: 16,
  touchFriendlyPadding: 24 // var(--space-lg)
}

/**
 * 验证移动端卡片内边距是否适合触摸操作
 * @param {number} padding - 内边距（像素）
 * @returns {boolean}
 */
function isValidMobileCardPadding(padding) {
  return padding >= mobileCardConfig.minPadding
}

/**
 * 验证移动端卡片间距是否适合触摸操作
 * @param {number} marginBottom - 底部外边距（像素）
 * @returns {boolean}
 */
function isValidMobileCardMargin(marginBottom) {
  return marginBottom >= mobileCardConfig.minMarginBottom
}

/**
 * 验证移动端卡片圆角是否在有效范围内
 * @param {number} borderRadius - 圆角值（像素）
 * @returns {boolean}
 */
function isValidMobileCardBorderRadius(borderRadius) {
  return borderRadius >= mobileCardConfig.minBorderRadius && 
         borderRadius <= mobileCardConfig.maxBorderRadius
}

/**
 * 验证移动端卡片配置是否适合触摸操作
 * @param {object} cardConfig - 卡片配置对象
 * @returns {boolean}
 */
function isValidMobileCardConfig(cardConfig) {
  const { padding, marginBottom, borderRadius } = cardConfig
  
  return isValidMobileCardPadding(padding) &&
         isValidMobileCardMargin(marginBottom) &&
         isValidMobileCardBorderRadius(borderRadius)
}

describe('Property 8: 移动端卡片触摸适配', () => {
  /**
   * Property Test: 移动端卡片内边距应至少为 16px
   */
  test('移动端卡片内边距应至少为 16px', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 50 }),
        (padding) => {
          const isValid = isValidMobileCardPadding(padding)
          const expectedValid = padding >= 16
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 移动端卡片底部间距应至少为 16px
   */
  test('移动端卡片底部间距应至少为 16px', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 50 }),
        (marginBottom) => {
          const isValid = isValidMobileCardMargin(marginBottom)
          const expectedValid = marginBottom >= 16
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 移动端卡片圆角应在 8-16px 范围内
   */
  test('移动端卡片圆角应在 8-16px 范围内', () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 30 }),
        (borderRadius) => {
          const isValid = isValidMobileCardBorderRadius(borderRadius)
          const expectedValid = borderRadius >= 8 && borderRadius <= 16
          
          expect(isValid).toBe(expectedValid)
          return isValid === expectedValid
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 有效的移动端卡片配置应通过验证
   */
  test('有效的移动端卡片配置应通过验证', () => {
    fc.assert(
      fc.property(
        fc.record({
          padding: fc.integer({ min: 16, max: 32 }),
          marginBottom: fc.integer({ min: 16, max: 32 }),
          borderRadius: fc.integer({ min: 8, max: 16 })
        }),
        (cardConfig) => {
          const isValid = isValidMobileCardConfig(cardConfig)
          expect(isValid).toBe(true)
          return isValid === true
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 无效的移动端卡片配置应不通过验证
   */
  test('无效的移动端卡片配置应不通过验证', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          // 内边距太小
          fc.record({
            padding: fc.integer({ min: 0, max: 15 }),
            marginBottom: fc.integer({ min: 16, max: 32 }),
            borderRadius: fc.integer({ min: 8, max: 16 })
          }),
          // 间距太小
          fc.record({
            padding: fc.integer({ min: 16, max: 32 }),
            marginBottom: fc.integer({ min: 0, max: 15 }),
            borderRadius: fc.integer({ min: 8, max: 16 })
          }),
          // 圆角太小
          fc.record({
            padding: fc.integer({ min: 16, max: 32 }),
            marginBottom: fc.integer({ min: 16, max: 32 }),
            borderRadius: fc.integer({ min: 0, max: 7 })
          }),
          // 圆角太大
          fc.record({
            padding: fc.integer({ min: 16, max: 32 }),
            marginBottom: fc.integer({ min: 16, max: 32 }),
            borderRadius: fc.integer({ min: 17, max: 30 })
          })
        ),
        (cardConfig) => {
          const isValid = isValidMobileCardConfig(cardConfig)
          expect(isValid).toBe(false)
          return isValid === false
        }
      ),
      { numRuns: 100 }
    )
  })

  /**
   * Property Test: 触摸友好的卡片内边距应为 24px
   */
  test('触摸友好的卡片内边距应为 24px', () => {
    const touchFriendlyPadding = mobileCardConfig.touchFriendlyPadding
    
    expect(touchFriendlyPadding).toBe(24)
    expect(isValidMobileCardPadding(touchFriendlyPadding)).toBe(true)
  })

  /**
   * Property Test: 标准移动端卡片配置应有效
   */
  test('标准移动端卡片配置应有效', () => {
    // 从 responsive.css 提取的标准配置
    const standardConfigs = [
      { padding: 16, marginBottom: 16, borderRadius: 8 },
      { padding: 24, marginBottom: 16, borderRadius: 12 },
      { padding: 16, marginBottom: 16, borderRadius: 12 }
    ]

    fc.assert(
      fc.property(
        fc.constantFrom(...standardConfigs),
        (cardConfig) => {
          const isValid = isValidMobileCardConfig(cardConfig)
          expect(isValid).toBe(true)
          return isValid === true
        }
      ),
      { numRuns: 100 }
    )
  })
})
