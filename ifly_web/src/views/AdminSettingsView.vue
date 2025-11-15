<template>
    <div class="admin-settings">
        <h1 class="title">系统设置</h1>

        <div class="settings-container">
            <div class="settings-sidebar">
                <ul class="settings-nav">
                    <li v-for="(section, index) in settingSections" :key="index"
                        :class="{ active: activeSection === section.id }" @click="activeSection = section.id">
                        <i :class="section.icon"></i>
                        {{ section.name }}
                    </li>
                </ul>
            </div>

            <div class="settings-content">
                <!-- 基本设置 -->
                <div v-if="activeSection === 'general'" class="settings-section">
                    <h2>基本设置</h2>

                    <div class="form-group">
                        <label>网站名称</label>
                        <input type="text" v-model="settings.siteName" />
                    </div>

                    <div class="form-group">
                        <label>公司名称</label>
                        <input type="text" v-model="settings.companyName" />
                    </div>

                    <div class="form-group">
                        <label>联系电话</label>
                        <input type="text" v-model="settings.contactPhone" />
                    </div>

                    <div class="form-group">
                        <label>联系邮箱</label>
                        <input type="email" v-model="settings.contactEmail" />
                    </div>

                    <div class="form-group">
                        <label>网站描述</label>
                        <textarea v-model="settings.siteDescription" rows="3"></textarea>
                    </div>

                    <div class="form-group">
                        <label>网站语言</label>
                        <select v-model="settings.language">
                            <option value="zh-CN">简体中文</option>
                            <option value="en-US">English</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>时区设置</label>
                        <select v-model="settings.timezone">
                            <option value="Asia/Shanghai">中国标准时间 (GMT+8)</option>
                            <option value="America/New_York">美国东部时间</option>
                            <option value="Europe/London">英国标准时间</option>
                            <option value="Asia/Tokyo">日本标准时间</option>
                        </select>
                    </div>
                </div>

                <!-- 支付设置 -->
                <div v-if="activeSection === 'payment'" class="settings-section">
                    <h2>支付设置</h2>

                    <div class="form-group">
                        <label>货币单位</label>
                        <select v-model="settings.currency">
                            <option value="CNY">人民币 (¥)</option>
                            <option value="USD">美元 ($)</option>
                            <option value="EUR">欧元 (€)</option>
                        </select>
                    </div>

                    <h3>支付宝配置</h3>
                    <div class="form-group">
                        <label>启用支付宝</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="alipay-toggle" v-model="settings.alipayEnabled" />
                            <label for="alipay-toggle"></label>
                        </div>
                    </div>

                    <div class="form-group" v-if="settings.alipayEnabled">
                        <label>支付宝 App ID</label>
                        <input type="text" v-model="settings.alipayAppId" />
                    </div>

                    <div class="form-group" v-if="settings.alipayEnabled">
                        <label>支付宝公钥</label>
                        <textarea v-model="settings.alipayPublicKey" rows="3"></textarea>
                    </div>

                    <div class="form-group" v-if="settings.alipayEnabled">
                        <label>支付宝私钥</label>
                        <textarea v-model="settings.alipayPrivateKey" rows="3"></textarea>
                    </div>

                    <h3>微信支付配置</h3>
                    <div class="form-group">
                        <label>启用微信支付</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="wechat-toggle" v-model="settings.wechatPayEnabled" />
                            <label for="wechat-toggle"></label>
                        </div>
                    </div>

                    <div class="form-group" v-if="settings.wechatPayEnabled">
                        <label>微信支付商户号</label>
                        <input type="text" v-model="settings.wechatPayMerchantId" />
                    </div>

                    <div class="form-group" v-if="settings.wechatPayEnabled">
                        <label>微信支付 API 密钥</label>
                        <input type="password" v-model="settings.wechatPayApiKey" />
                    </div>

                    <div class="form-group" v-if="settings.wechatPayEnabled">
                        <label>微信支付 App ID</label>
                        <input type="text" v-model="settings.wechatPayAppId" />
                    </div>
                </div>

                <!-- 邮件设置 -->
                <div v-if="activeSection === 'email'" class="settings-section">
                    <h2>邮件设置</h2>

                    <div class="form-group">
                        <label>SMTP 服务器</label>
                        <input type="text" v-model="settings.smtpServer" />
                    </div>

                    <div class="form-group">
                        <label>SMTP 端口</label>
                        <input type="number" v-model="settings.smtpPort" />
                    </div>

                    <div class="form-group">
                        <label>SMTP 用户名</label>
                        <input type="text" v-model="settings.smtpUsername" />
                    </div>

                    <div class="form-group">
                        <label>SMTP 密码</label>
                        <input type="password" v-model="settings.smtpPassword" />
                    </div>

                    <div class="form-group">
                        <label>发件人邮箱</label>
                        <input type="email" v-model="settings.emailFrom" />
                    </div>

                    <div class="form-group">
                        <label>发件人名称</label>
                        <input type="text" v-model="settings.emailFromName" />
                    </div>

                    <div class="form-group">
                        <label>使用 SSL</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="ssl-toggle" v-model="settings.smtpUseSsl" />
                            <label for="ssl-toggle"></label>
                        </div>
                    </div>

                    <div class="form-group">
                        <button @click="testEmailSettings" class="btn btn-secondary">
                            <i class="fas fa-paper-plane"></i> 发送测试邮件
                        </button>
                    </div>
                </div>

                <!-- 安全设置 -->
                <div v-if="activeSection === 'security'" class="settings-section">
                    <h2>安全设置</h2>

                    <div class="form-group">
                        <label>启用双因素认证</label>
                        <div class="toggle-switch">
                            <input type="checkbox" id="2fa-toggle" v-model="settings.twoFactorEnabled" />
                            <label for="2fa-toggle"></label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>密码最小长度</label>
                        <input type="number" v-model="settings.passwordMinLength" min="6" max="20" />
                    </div>

                    <div class="form-group">
                        <label>密码复杂度要求</label>
                        <div class="checkbox-group">
                            <div class="checkbox-item">
                                <input type="checkbox" id="require-uppercase"
                                    v-model="settings.passwordRequireUppercase" />
                                <label for="require-uppercase">必须包含大写字母</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="require-lowercase"
                                    v-model="settings.passwordRequireLowercase" />
                                <label for="require-lowercase">必须包含小写字母</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="require-number" v-model="settings.passwordRequireNumber" />
                                <label for="require-number">必须包含数字</label>
                            </div>
                            <div class="checkbox-item">
                                <input type="checkbox" id="require-special" v-model="settings.passwordRequireSpecial" />
                                <label for="require-special">必须包含特殊字符</label>
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label>会话超时时间（分钟）</label>
                        <input type="number" v-model="settings.sessionTimeout" min="5" />
                    </div>

                    <div class="form-group">
                        <label>IP 登录限制</label>
                        <textarea v-model="settings.ipRestrictions" rows="3"
                            placeholder="每行输入一个 IP 地址或 IP 范围，留空表示不限制"></textarea>
                    </div>
                </div>

                <!-- 系统日志 -->
                <div v-if="activeSection === 'logs'" class="settings-section">
                    <h2>系统日志</h2>

                    <div class="log-filters">
                        <div class="form-group">
                            <label>日志级别</label>
                            <select v-model="logFilter.level">
                                <option value="">全部级别</option>
                                <option value="info">信息</option>
                                <option value="warning">警告</option>
                                <option value="error">错误</option>
                                <option value="critical">严重错误</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label>开始日期</label>
                            <input type="date" v-model="logFilter.startDate" />
                        </div>

                        <div class="form-group">
                            <label>结束日期</label>
                            <input type="date" v-model="logFilter.endDate" />
                        </div>

                        <button @click="filterLogs" class="btn btn-primary">
                            <i class="fas fa-filter"></i> 筛选
                        </button>

                        <button @click="exportLogs" class="btn btn-secondary">
                            <i class="fas fa-download"></i> 导出日志
                        </button>
                    </div>

                    <div class="log-table-container">
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>时间</th>
                                    <th>级别</th>
                                    <th>来源</th>
                                    <th>消息</th>
                                    <th>IP 地址</th>
                                    <th>用户</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr v-for="(log, index) in filteredLogs" :key="index" :class="'log-' + log.level">
                                    <td>{{ formatDate(log.timestamp) }}</td>
                                    <td>{{ getLogLevelText(log.level) }}</td>
                                    <td>{{ log.source }}</td>
                                    <td>{{ log.message }}</td>
                                    <td>{{ log.ipAddress }}</td>
                                    <td>{{ log.username || '系统' }}</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="settings-actions">
                    <button @click="resetSettings" class="btn btn-secondary">
                        <i class="fas fa-undo"></i> 重置
                    </button>
                    <button @click="saveSettings" class="btn btn-primary">
                        <i class="fas fa-save"></i> 保存设置
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminSettingsView',
    data() {
        return {
            activeSection: 'general',
            settingSections: [
                { id: 'general', name: '基本设置', icon: 'fas fa-cog' },
                { id: 'payment', name: '支付设置', icon: 'fas fa-credit-card' },
                { id: 'email', name: '邮件设置', icon: 'fas fa-envelope' },
                { id: 'security', name: '安全设置', icon: 'fas fa-shield-alt' },
                { id: 'logs', name: '系统日志', icon: 'fas fa-list-alt' }
            ],
            settings: {
                // 基本设置
                siteName: 'iFly航空',
                companyName: 'iFly航空科技有限公司',
                contactPhone: '400-123-4567',
                contactEmail: 'support@ifly.com',
                siteDescription: 'iFly航空 - 您身边的航空出行专家',
                language: 'zh-CN',
                timezone: 'Asia/Shanghai',

                // 支付设置
                currency: 'CNY',
                alipayEnabled: true,
                alipayAppId: '2021000000000000',
                alipayPublicKey: 'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...',
                alipayPrivateKey: 'MIIEvQIBADANBgkqhkiG9w0BAQEFAASCB...',
                wechatPayEnabled: true,
                wechatPayMerchantId: '1900000109',
                wechatPayApiKey: 'a12b34c56d78e90f1a2b3c4d5e6f7g8h',
                wechatPayAppId: 'wx1234567890abcdef',

                // 邮件设置
                smtpServer: 'smtp.ifly.com',
                smtpPort: 465,
                smtpUsername: 'noreply@ifly.com',
                smtpPassword: 'password123',
                emailFrom: 'noreply@ifly.com',
                emailFromName: 'iFly航空',
                smtpUseSsl: true,

                // 安全设置
                twoFactorEnabled: false,
                passwordMinLength: 8,
                passwordRequireUppercase: true,
                passwordRequireLowercase: true,
                passwordRequireNumber: true,
                passwordRequireSpecial: false,
                sessionTimeout: 30,
                ipRestrictions: ''
            },
            logFilter: {
                level: '',
                startDate: '',
                endDate: ''
            },
            logs: [
                {
                    timestamp: '2023-07-20T10:15:30',
                    level: 'info',
                    source: '用户系统',
                    message: '用户登录成功',
                    ipAddress: '192.168.1.100',
                    username: 'admin'
                },
                {
                    timestamp: '2023-07-20T10:30:45',
                    level: 'warning',
                    source: '支付系统',
                    message: '支付超时',
                    ipAddress: '192.168.1.101',
                    username: 'user123'
                },
                {
                    timestamp: '2023-07-20T11:05:22',
                    level: 'error',
                    source: '数据库',
                    message: '数据库连接失败',
                    ipAddress: '192.168.1.1',
                    username: null
                },
                {
                    timestamp: '2023-07-20T12:45:10',
                    level: 'info',
                    source: '订单系统',
                    message: '新订单创建',
                    ipAddress: '192.168.1.102',
                    username: 'user456'
                },
                {
                    timestamp: '2023-07-20T13:20:05',
                    level: 'critical',
                    source: '系统安全',
                    message: '多次登录失败，账户锁定',
                    ipAddress: '192.168.1.103',
                    username: 'user789'
                }
            ],
            originalSettings: null
        }
    },
    computed: {
        filteredLogs() {
            return this.logs.filter(log => {
                // 级别筛选
                if (this.logFilter.level && log.level !== this.logFilter.level) {
                    return false
                }

                // 日期筛选
                if (this.logFilter.startDate || this.logFilter.endDate) {
                    const logDate = new Date(log.timestamp)

                    if (this.logFilter.startDate) {
                        const startDate = new Date(this.logFilter.startDate)
                        if (logDate < startDate) return false
                    }

                    if (this.logFilter.endDate) {
                        const endDate = new Date(this.logFilter.endDate)
                        endDate.setHours(23, 59, 59, 999) // 设置为当天结束时间
                        if (logDate > endDate) return false
                    }
                }

                return true
            })
        }
    },
    created() {
        // 保存原始设置以便重置
        this.originalSettings = JSON.parse(JSON.stringify(this.settings))
    },
    methods: {
        formatDate(dateStr) {
            const date = new Date(dateStr)
            return date.toLocaleString()
        },
        getLogLevelText(level) {
            const levelMap = {
                info: '信息',
                warning: '警告',
                error: '错误',
                critical: '严重错误'
            }
            return levelMap[level] || level
        },
        saveSettings() {
            // 在实际应用中，这里应该调用API保存设置
            alert('设置已保存')
            // 更新原始设置
            this.originalSettings = JSON.parse(JSON.stringify(this.settings))
        },
        resetSettings() {
            // 重置为原始设置
            this.settings = JSON.parse(JSON.stringify(this.originalSettings))
        },
        testEmailSettings() {
            // 在实际应用中，这里应该调用API发送测试邮件
            alert('测试邮件已发送')
        },
        filterLogs() {
            // 已通过计算属性实现
        },
        exportLogs() {
            // 在实际应用中，这里应该调用API导出日志
            alert('日志导出中，请稍候...')
        }
    }
}
</script>

<style scoped>
.admin-settings {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
}

.title {
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
    border-bottom: 2px solid #3f51b5;
    padding-bottom: 10px;
}

.settings-container {
    display: flex;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.settings-sidebar {
    width: 220px;
    background: #f5f5f5;
    border-right: 1px solid #eee;
}

.settings-nav {
    list-style: none;
    padding: 0;
    margin: 0;
}

.settings-nav li {
    padding: 15px 20px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
    transition: all 0.3s;
    display: flex;
    align-items: center;
}

.settings-nav li i {
    margin-right: 10px;
    width: 20px;
    text-align: center;
    color: #666;
}

.settings-nav li:hover {
    background: #e0e0e0;
}

.settings-nav li.active {
    background: #3f51b5;
    color: white;
}

.settings-nav li.active i {
    color: white;
}

.settings-content {
    flex: 1;
    padding: 20px;
    max-height: 700px;
    overflow-y: auto;
}

.settings-section h2 {
    font-size: 20px;
    color: #333;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.settings-section h3 {
    font-size: 16px;
    color: #555;
    margin: 20px 0 10px;
}

.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-size: 14px;
    color: #555;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="password"],
.form-group input[type="number"],
.form-group input[type="date"],
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    outline: none;
}

.form-group textarea {
    resize: vertical;
    min-height: 80px;
}

.checkbox-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.checkbox-item {
    display: flex;
    align-items: center;
}

.checkbox-item input[type="checkbox"] {
    margin-right: 8px;
}

.toggle-switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 24px;
}

.toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
}

.toggle-switch label {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 24px;
}

.toggle-switch label:before {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
}

.toggle-switch input:checked+label {
    background-color: #3f51b5;
}

.toggle-switch input:checked+label:before {
    transform: translateX(26px);
}

.btn {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    font-size: 14px;
    transition: all 0.3s;
}

.btn i {
    margin-right: 8px;
}

.btn-primary {
    background: #3f51b5;
    color: white;
}

.btn-primary:hover {
    background: #303f9f;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
    background: #f5f5f5;
    color: #333;
}

.btn-secondary:hover {
    background: #e0e0e0;
}

.settings-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
    border-top: 1px solid #eee;
    padding-top: 20px;
}

.log-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 20px;
    align-items: flex-end;
}

.log-filters .form-group {
    flex: 1;
    min-width: 150px;
    margin-bottom: 0;
}

.log-table-container {
    margin-top: 20px;
    max-height: 400px;
    overflow-y: auto;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: 10px 12px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

.data-table th {
    background: #f9f9f9;
    color: #333;
    font-weight: 600;
}

.log-info {
    background-color: #f0f8ff;
}

.log-warning {
    background-color: #fff8e1;
}

.log-error {
    background-color: #ffebee;
}

.log-critical {
    background-color: #ffcdd2;
}

@media (max-width: 768px) {
    .settings-container {
        flex-direction: column;
    }

    .settings-sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 1px solid #eee;
    }

    .settings-nav {
        display: flex;
        overflow-x: auto;
    }

    .settings-nav li {
        border-bottom: none;
        border-right: 1px solid #eee;
        white-space: nowrap;
    }

    .log-filters {
        flex-direction: column;
        align-items: stretch;
    }

    .log-filters .form-group {
        margin-bottom: 10px;
    }
}
</style>