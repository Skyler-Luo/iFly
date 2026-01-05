/**
 * 全局错误处理工具
 * 提供统一的错误捕获、记录和用户提示
 */

import { ElMessage } from 'element-plus'

// 错误类型枚举
export const ERROR_TYPES = {
  NETWORK: 'network',
  VALIDATION: 'validation',
  PERMISSION: 'permission',
  BUSINESS: 'business',
  SYSTEM: 'system',
  UNKNOWN: 'unknown'
}

// 错误严重程度
export const ERROR_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical'
}

class ErrorHandler {
  constructor() {
    this.errorQueue = []
    this.maxErrorQueueSize = 100
    this.initialized = false
  }

  // 初始化错误处理器
  init(app) {
    if (this.initialized) return
    
    // Vue全局错误处理
    app.config.errorHandler = (error, instance, info) => {
      this.handleVueError(error, instance, info)
    }
    
    // 全局未捕获的Promise异常
    window.addEventListener('unhandledrejection', (event) => {
      this.handlePromiseRejection(event)
    })
    
    // 全局JavaScript错误
    window.addEventListener('error', (event) => {
      this.handleGlobalError(event)
    })
    
    // 资源加载错误
    window.addEventListener('error', (event) => {
      if (event.target !== window) {
        this.handleResourceError(event)
      }
    }, true)
    
    this.initialized = true
    console.log('✅ 全局错误处理器已初始化')
  }

  // 处理Vue组件错误
  handleVueError(error, instance, info) {
    const errorInfo = {
      type: ERROR_TYPES.SYSTEM,
      level: ERROR_LEVELS.HIGH,
      message: error.message,
      stack: error.stack,
      component: instance?.$options.name || 'Unknown',
      info,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    }
    
    this.logError(errorInfo)
    this.showUserMessage('组件发生错误，请刷新页面重试', 'error')
  }

  // 处理Promise拒绝
  handlePromiseRejection(event) {
    const error = event.reason
    
    // 如果是已知的API错误，不重复处理
    if (error?.handled) {
      return
    }
    
    const errorInfo = {
      type: ERROR_TYPES.NETWORK,
      level: ERROR_LEVELS.MEDIUM,
      message: error?.message || 'Promise rejection',
      stack: error?.stack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    }
    
    this.logError(errorInfo)
    
    // 阻止在控制台显示未捕获的Promise错误
    event.preventDefault()
  }

  // 处理全局JavaScript错误
  handleGlobalError(event) {
    // 忽略 ResizeObserver 相关的无害警告
    if (event.message && event.message.includes('ResizeObserver')) {
      return
    }
    
    const errorInfo = {
      type: ERROR_TYPES.SYSTEM,
      level: ERROR_LEVELS.HIGH,
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      stack: event.error?.stack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    }
    
    this.logError(errorInfo)
    this.showUserMessage('系统发生错误，请刷新页面重试', 'error')
  }

  // 处理资源加载错误
  handleResourceError(event) {
    const target = event.target
    const errorInfo = {
      type: ERROR_TYPES.NETWORK,
      level: ERROR_LEVELS.LOW,
      message: `Resource failed to load: ${target.src || target.href}`,
      resourceType: target.tagName.toLowerCase(),
      resourceUrl: target.src || target.href,
      timestamp: new Date().toISOString(),
      url: window.location.href
    }
    
    this.logError(errorInfo)
  }

  // 手动处理业务错误
  handleBusinessError(error, context = {}) {
    const errorInfo = {
      type: ERROR_TYPES.BUSINESS,
      level: ERROR_LEVELS.MEDIUM,
      message: error.message || error,
      context,
      timestamp: new Date().toISOString(),
      url: window.location.href
    }
    
    this.logError(errorInfo)
    this.showUserMessage(error.message || error, 'warning')
  }

  // 处理网络错误
  handleNetworkError(error, context = {}) {
    const errorInfo = {
      type: ERROR_TYPES.NETWORK,
      level: ERROR_LEVELS.MEDIUM,
      message: error.message || '网络请求失败',
      status: error.status,
      statusText: error.statusText,
      url: error.config?.url,
      method: error.config?.method,
      context,
      timestamp: new Date().toISOString()
    }
    
    this.logError(errorInfo)
    
    // 根据错误状态码显示不同消息
    let userMessage = '网络请求失败'
    if (error.status === 404) {
      userMessage = '请求的资源不存在'
    } else if (error.status === 500) {
      userMessage = '服务器内部错误'
    } else if (error.status === 401) {
      userMessage = '登录已过期，请重新登录'
    } else if (error.status === 403) {
      userMessage = '权限不足，无法访问'
    }
    
    this.showUserMessage(userMessage, 'error')
  }

  // 记录错误日志
  logError(errorInfo) {
    // 添加到错误队列
    this.errorQueue.push(errorInfo)
    
    // 限制队列大小
    if (this.errorQueue.length > this.maxErrorQueueSize) {
      this.errorQueue.shift()
    }
    
    // 控制台输出（仅开发环境）
    if (process.env.NODE_ENV === 'development') {
      console.group(`🚨 ${errorInfo.type.toUpperCase()} ERROR - ${errorInfo.level.toUpperCase()}`)
      console.error('Message:', errorInfo.message)
      console.error('Details:', errorInfo)
      if (errorInfo.stack) {
        console.error('Stack:', errorInfo.stack)
      }
      console.groupEnd()
    }
    
    // 发送到服务器（生产环境）
    if (process.env.NODE_ENV === 'production') {
      this.sendErrorToServer(errorInfo)
    }
  }

  // 发送错误到服务器
  async sendErrorToServer(errorInfo) {
    try {
      // 简单的错误上报，避免循环依赖
      await fetch('/api/errors/report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(errorInfo)
      })
    } catch (error) {
      // 上报失败时静默处理，避免无限循环
      console.warn('Failed to report error to server:', error)
    }
  }

  // 显示用户消息
  showUserMessage(message, type = 'error') {
    // 防止重复显示相同消息
    const now = Date.now()
    const messageKey = `${type}_${message}`
    
    if (this.lastMessages && this.lastMessages[messageKey] && 
        now - this.lastMessages[messageKey] < 3000) {
      return
    }
    
    if (!this.lastMessages) {
      this.lastMessages = {}
    }
    this.lastMessages[messageKey] = now
    
    // 显示消息
    ElMessage({
      message,
      type,
      duration: 5000,
      showClose: true
    })
  }

  // 获取错误日志
  getErrorLogs(limit = 50) {
    return this.errorQueue.slice(-limit)
  }

  // 清空错误日志
  clearErrorLogs() {
    this.errorQueue = []
  }

  // 获取错误统计
  getErrorStats() {
    const stats = {
      total: this.errorQueue.length,
      byType: {},
      byLevel: {},
      recent: 0
    }
    
    const now = Date.now()
    const oneHourAgo = now - 60 * 60 * 1000
    
    this.errorQueue.forEach(error => {
      // 按类型统计
      stats.byType[error.type] = (stats.byType[error.type] || 0) + 1
      
      // 按级别统计
      stats.byLevel[error.level] = (stats.byLevel[error.level] || 0) + 1
      
      // 最近一小时统计
      if (new Date(error.timestamp).getTime() > oneHourAgo) {
        stats.recent++
      }
    })
    
    return stats
  }
}

// 创建全局实例
const errorHandler = new ErrorHandler()

// 导出便捷方法
export const handleBusinessError = (error, context) => {
  errorHandler.handleBusinessError(error, context)
}

export const handleNetworkError = (error, context) => {
  errorHandler.handleNetworkError(error, context)
}

export const getErrorLogs = (limit) => {
  return errorHandler.getErrorLogs(limit)
}

export const getErrorStats = () => {
  return errorHandler.getErrorStats()
}

export default errorHandler
