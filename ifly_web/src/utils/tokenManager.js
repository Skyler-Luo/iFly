/**
 * 安全的Token管理工具
 * 提供加密存储和自动过期机制
 * 支持"记住我"功能：勾选时使用 localStorage（持久化），否则使用 sessionStorage（关闭浏览器失效）
 */

class TokenManager {
  constructor() {
    this.tokenKey = 'ifly_auth_token'
    this.userKey = 'ifly_user_data'
    this.expiryKey = 'ifly_token_expiry'
    this.storageTypeKey = 'ifly_storage_type'
  }

  /**
   * 获取当前使用的存储对象
   * @returns {Storage}
   */
  getStorage() {
    const storageType = localStorage.getItem(this.storageTypeKey)
    return storageType === 'session' ? sessionStorage : localStorage
  }

  /**
   * 简单的Base64编码（不是真正的加密，但比明文好）
   */
  encode(data) {
    try {
      return btoa(JSON.stringify(data))
    } catch (e) {
      console.warn('编码失败:', e)
      return data
    }
  }

  /**
   * Base64解码
   */
  decode(encodedData) {
    try {
      return JSON.parse(atob(encodedData))
    } catch (e) {
      console.warn('解码失败:', e)
      return null
    }
  }

  /**
   * 设置Token和用户信息
   * @param {string} token - 认证token 
   * @param {object} user - 用户信息
   * @param {number} expiresIn - 过期时间（毫秒）
   * @param {boolean} useSession - 是否使用 sessionStorage（不记住我）
   */
  setToken(token, user, expiresIn = 24 * 60 * 60 * 1000, useSession = false) {
    try {
      const now = new Date().getTime()
      const expiryTime = now + expiresIn

      // 记录存储类型（始终存在 localStorage 中，用于判断）
      localStorage.setItem(this.storageTypeKey, useSession ? 'session' : 'local')
      
      // 选择存储对象
      const storage = useSession ? sessionStorage : localStorage

      // 编码存储token
      storage.setItem(this.tokenKey, this.encode(token))
      
      // 编码存储用户信息（移除敏感信息）
      const safeUserData = {
        id: user.id,
        username: user.username,
        role: user.role,
        email: user.email,
        // 不存储敏感信息如密码、完整身份证号等
      }
      storage.setItem(this.userKey, this.encode(safeUserData))
      
      // 存储过期时间
      storage.setItem(this.expiryKey, expiryTime.toString())
    } catch (e) {
      console.error('存储Token失败:', e)
    }
  }

  /**
   * 获取Token
   * @returns {string|null}
   */
  getToken() {
    try {
      if (this.isTokenExpired()) {
        this.clearToken()
        return null
      }

      const storage = this.getStorage()
      const encodedToken = storage.getItem(this.tokenKey)
      if (!encodedToken) return null

      return this.decode(encodedToken)
    } catch (e) {
      console.error('获取Token失败:', e)
      return null
    }
  }

  /**
   * 获取用户信息
   * @returns {object|null}
   */
  getUser() {
    try {
      if (this.isTokenExpired()) {
        this.clearToken()
        return null
      }

      const storage = this.getStorage()
      const encodedUser = storage.getItem(this.userKey)
      if (!encodedUser) return null

      return this.decode(encodedUser)
    } catch (e) {
      console.error('获取用户信息失败:', e)
      return null
    }
  }

  /**
   * 检查Token是否过期
   * @returns {boolean}
   */
  isTokenExpired() {
    try {
      const storage = this.getStorage()
      const expiryTime = storage.getItem(this.expiryKey)
      if (!expiryTime) return true

      const now = new Date().getTime()
      return now > parseInt(expiryTime)
    } catch (e) {
      console.error('检查Token过期状态失败:', e)
      return true
    }
  }

  /**
   * 检查用户是否已登录
   * @returns {boolean}
   */
  isAuthenticated() {
    return this.getToken() !== null
  }

  /**
   * 检查用户是否为管理员
   * @returns {boolean}
   */
  isAdmin() {
    const user = this.getUser()
    return user && user.role === 'admin'
  }

  /**
   * 刷新Token过期时间
   * @param {number} expiresIn - 新的过期时间（毫秒）
   */
  refreshToken(expiresIn = 24 * 60 * 60 * 1000) {
    try {
      if (this.isAuthenticated()) {
        const now = new Date().getTime()
        const newExpiryTime = now + expiresIn
        const storage = this.getStorage()
        storage.setItem(this.expiryKey, newExpiryTime.toString())
      }
    } catch (e) {
      console.error('刷新Token失败:', e)
    }
  }

  /**
   * 清除所有认证信息
   */
  clearToken() {
    try {
      // 清除两种存储中的数据
      localStorage.removeItem(this.tokenKey)
      localStorage.removeItem(this.userKey)
      localStorage.removeItem(this.expiryKey)
      localStorage.removeItem(this.storageTypeKey)
      sessionStorage.removeItem(this.tokenKey)
      sessionStorage.removeItem(this.userKey)
      sessionStorage.removeItem(this.expiryKey)
    } catch (e) {
      console.error('清除Token失败:', e)
    }
  }

  /**
   * 安全存储临时数据（带过期时间）
   * @param {string} key - 存储键
   * @param {any} data - 数据
   * @param {number} expiresIn - 过期时间（毫秒）
   */
  setTempData(key, data, expiresIn = 60 * 60 * 1000) { // 默认1小时
    try {
      const now = new Date().getTime()
      const expiryTime = now + expiresIn
      const tempData = {
        data: data,
        expiry: expiryTime
      }
      localStorage.setItem(`temp_${key}`, this.encode(tempData))
    } catch (e) {
      console.error('存储临时数据失败:', e)
    }
  }

  /**
   * 获取临时数据
   * @param {string} key - 存储键
   * @returns {any|null}
   */
  getTempData(key) {
    try {
      const encodedData = localStorage.getItem(`temp_${key}`)
      if (!encodedData) return null

      const tempData = this.decode(encodedData)
      if (!tempData) return null

      const now = new Date().getTime()
      if (now > tempData.expiry) {
        localStorage.removeItem(`temp_${key}`)
        return null
      }

      return tempData.data
    } catch (e) {
      console.error('获取临时数据失败:', e)
      return null
    }
  }

  /**
   * 清理所有过期的临时数据
   */
  clearExpiredTempData() {
    try {
      const keys = Object.keys(localStorage)
      const tempKeys = keys.filter(key => key.startsWith('temp_'))
      const now = new Date().getTime()

      tempKeys.forEach(key => {
        const encodedData = localStorage.getItem(key)
        if (encodedData) {
          const tempData = this.decode(encodedData)
          if (tempData && now > tempData.expiry) {
            localStorage.removeItem(key)
          }
        }
      })
    } catch (e) {
      console.error('清理过期数据失败:', e)
    }
  }
}

// 创建单例实例
const tokenManager = new TokenManager()

// 定期清理过期数据
setInterval(() => {
  tokenManager.clearExpiredTempData()
}, 60 * 60 * 1000) // 每小时清理一次

export default tokenManager
