<template>
    <div class="admin-logs">
        <h1 class="title">系统日志</h1>

        <div class="filter-section">
            <div class="filter-item">
                <label>日志级别</label>
                <select v-model="levelFilter">
                    <option value="">全部级别</option>
                    <option value="ERROR">错误</option>
                    <option value="WARNING">警告</option>
                    <option value="INFO">信息</option>
                    <option value="DEBUG">调试</option>
                </select>
            </div>

            <div class="filter-item">
                <label>组件</label>
                <select v-model="componentFilter">
                    <option value="">全部组件</option>
                    <option v-for="component in components" :key="component" :value="component">
                        {{ component }}
                    </option>
                </select>
            </div>

            <div class="filter-item">
                <label>用户</label>
                <select v-model="userFilter">
                    <option value="">全部用户</option>
                    <option value="admin">管理员</option>
                    <option value="system">系统</option>
                    <option value="user">用户</option>
                </select>
            </div>

            <div class="filter-item date-range">
                <label>时间范围</label>
                <div class="date-inputs">
                    <input type="date" v-model="startDate" />
                    <span>至</span>
                    <input type="date" v-model="endDate" />
                </div>
            </div>

            <div class="filter-item search-box">
                <label>搜索</label>
                <div class="search-input">
                    <input type="text" v-model="searchQuery" placeholder="搜索日志内容..." />
                    <i class="fas fa-search"></i>
                </div>
            </div>

            <div class="filter-actions">
                <button class="btn-filter" @click="applyFilters">
                    应用筛选
                </button>
                <button class="btn-reset" @click="resetFilters">
                    重置
                </button>
            </div>
        </div>

        <div class="logs-container">
            <div class="logs-header">
                <div class="logs-stats">
                    共 {{ totalLogs }} 条日志，已筛选 {{ filteredLogs.length }} 条
                </div>
                <div class="logs-actions">
                    <button class="btn-export" @click="exportLogs">
                        <i class="fas fa-download"></i> 导出日志
                    </button>
                    <button class="btn-refresh" @click="refreshLogs">
                        <i class="fas fa-sync-alt"></i> 刷新
                    </button>
                </div>
            </div>

            <div class="logs-table">
                <table>
                    <thead>
                        <tr>
                            <th>时间</th>
                            <th>级别</th>
                            <th>组件</th>
                            <th>用户</th>
                            <th>内容</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(log, index) in paginatedLogs" :key="index">
                            <td class="timestamp">{{ formatDate(log.timestamp) }}</td>
                            <td>
                                <span class="log-level" :class="getLevelClass(log.level)">
                                    {{ log.level }}
                                </span>
                            </td>
                            <td>{{ log.component }}</td>
                            <td>{{ log.user }}</td>
                            <td class="log-message">{{ log.message }}</td>
                            <td>
                                <button class="btn-action view-btn" @click="viewLog(log)">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div class="logs-pagination">
                <button class="btn-page" :disabled="currentPage === 1" @click="currentPage--">
                    <i class="fas fa-chevron-left"></i>
                </button>

                <div class="page-numbers">
                    <button v-for="page in displayedPages" :key="page" class="btn-page-num"
                        :class="{ active: page === currentPage }" @click="currentPage = page">
                        {{ page }}
                    </button>
                </div>

                <button class="btn-page" :disabled="currentPage === totalPages" @click="currentPage++">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        </div>

        <!-- 日志详情对话框 -->
        <div class="log-detail-modal" v-if="showLogDetail">
            <div class="modal-overlay" @click="showLogDetail = false"></div>
            <div class="modal-container">
                <div class="modal-header">
                    <h2>日志详情</h2>
                    <button class="btn-close" @click="showLogDetail = false">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <div class="log-detail-item">
                        <div class="detail-label">时间</div>
                        <div class="detail-value">{{ formatDate(selectedLog.timestamp, true) }}</div>
                    </div>
                    <div class="log-detail-item">
                        <div class="detail-label">级别</div>
                        <div class="detail-value">
                            <span class="log-level" :class="getLevelClass(selectedLog.level)">
                                {{ selectedLog.level }}
                            </span>
                        </div>
                    </div>
                    <div class="log-detail-item">
                        <div class="detail-label">组件</div>
                        <div class="detail-value">{{ selectedLog.component }}</div>
                    </div>
                    <div class="log-detail-item">
                        <div class="detail-label">用户</div>
                        <div class="detail-value">{{ selectedLog.user }}</div>
                    </div>
                    <div class="log-detail-item">
                        <div class="detail-label">IP 地址</div>
                        <div class="detail-value">{{ selectedLog.ip || '-' }}</div>
                    </div>
                    <div class="log-detail-item full">
                        <div class="detail-label">内容</div>
                        <div class="detail-value message">{{ selectedLog.message }}</div>
                    </div>
                    <div class="log-detail-item full" v-if="selectedLog.details">
                        <div class="detail-label">详细信息</div>
                        <div class="detail-value">
                            <pre>{{ selectedLog.details }}</pre>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" @click="showLogDetail = false">关闭</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import api from '../services/api'

export default {
    name: 'AdminSystemLogsView',
    data() {
        return {
            logs: [],
            components: ['AuthService', 'BookingService', 'PaymentService', 'UserService', 'DatabaseService', 'SchedulerService', 'API', 'SystemService', 'SecurityService', 'NotificationService'],
            isLoading: false,
            levelFilter: '',
            componentFilter: '',
            userFilter: '',
            startDate: '',
            endDate: '',
            searchQuery: '',
            currentPage: 1,
            logsPerPage: 10,
            showLogDetail: false,
            selectedLog: {}
        }
    },
    computed: {
        filteredLogs() {
            return this.logs.filter(log => {
                // 级别筛选
                if (this.levelFilter && log.level !== this.levelFilter) {
                    return false;
                }

                // 组件筛选
                if (this.componentFilter && log.component !== this.componentFilter) {
                    return false;
                }

                // 用户筛选
                if (this.userFilter && log.user !== this.userFilter) {
                    return false;
                }

                // 日期筛选
                if (this.startDate) {
                    const logDate = new Date(log.timestamp);
                    const filterStartDate = new Date(this.startDate);
                    if (logDate < filterStartDate) {
                        return false;
                    }
                }

                if (this.endDate) {
                    const logDate = new Date(log.timestamp);
                    const filterEndDate = new Date(this.endDate);
                    // 设置结束日期为当天的23:59:59
                    filterEndDate.setHours(23, 59, 59, 999);
                    if (logDate > filterEndDate) {
                        return false;
                    }
                }

                // 搜索筛选
                if (this.searchQuery) {
                    const query = this.searchQuery.toLowerCase();
                    return log.message.toLowerCase().includes(query) ||
                        log.component.toLowerCase().includes(query) ||
                        log.user.toLowerCase().includes(query) ||
                        (log.details && log.details.toLowerCase().includes(query));
                }

                return true;
            });
        },
        totalLogs() {
            return this.logs.length;
        },
        paginatedLogs() {
            const start = (this.currentPage - 1) * this.logsPerPage;
            const end = start + this.logsPerPage;
            return this.filteredLogs.slice(start, end);
        },
        totalPages() {
            return Math.ceil(this.filteredLogs.length / this.logsPerPage);
        },
        displayedPages() {
            const pages = [];
            let startPage = Math.max(1, this.currentPage - 2);
            let endPage = Math.min(this.totalPages, startPage + 4);

            if (endPage - startPage < 4) {
                startPage = Math.max(1, endPage - 4);
            }

            for (let i = startPage; i <= endPage; i++) {
                pages.push(i);
            }

            return pages;
        }
    },
    methods: {
        formatDate(dateString, includeSeconds = false) {
            const date = new Date(dateString);

            if (includeSeconds) {
                return date.toLocaleString('zh-CN');
            }

            return date.toLocaleString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });
        },
        getLevelClass(level) {
            const classes = {
                'ERROR': 'level-error',
                'WARNING': 'level-warning',
                'INFO': 'level-info',
                'DEBUG': 'level-debug'
            };
            return classes[level] || '';
        },
        applyFilters() {
            this.currentPage = 1;
            // 实际应用中这里可能需要发送请求到服务器
            console.log('应用筛选条件', {
                level: this.levelFilter,
                component: this.componentFilter,
                user: this.userFilter,
                startDate: this.startDate,
                endDate: this.endDate,
                search: this.searchQuery
            });
        },
        resetFilters() {
            this.levelFilter = '';
            this.componentFilter = '';
            this.userFilter = '';
            this.startDate = '';
            this.endDate = '';
            this.searchQuery = '';
            this.currentPage = 1;
        },
        exportLogs() {
            // 实际应用中，这里应该生成并下载日志文件
            console.log('导出日志', this.filteredLogs);
            alert('日志导出功能在实际应用中将生成CSV或TXT文件');
        },
        async refreshLogs() {
            await this.fetchLogs()
        },
        viewLog(log) {
            this.selectedLog = log;
            this.showLogDetail = true;
        },
        async fetchLogs() {
            this.isLoading = true
            try {
                const params = {}
                if (this.levelFilter) params.level = this.levelFilter
                if (this.startDate) params.start_date = this.startDate
                if (this.endDate) params.end_date = this.endDate
                
                const response = await api.admin.logs.getSystemLogs(params)
                const data = response?.logs || response || []
                this.logs = Array.isArray(data) ? data.map(log => ({
                    timestamp: log.timestamp,
                    level: log.level,
                    component: log.source || log.component || 'System',
                    user: log.user || 'system',
                    message: log.message,
                    ip: log.ip || log.ipAddress,
                    details: log.details
                })) : []
            } catch (error) {
                console.error('获取日志失败:', error)
                this.logs = []
            } finally {
                this.isLoading = false
            }
        }
    },
    async created() {
        // 设置默认的日期范围为最近7天
        const today = new Date();
        const sevenDaysAgo = new Date();
        sevenDaysAgo.setDate(today.getDate() - 7);

        this.startDate = sevenDaysAgo.toISOString().split('T')[0];
        this.endDate = today.toISOString().split('T')[0];
        
        await this.fetchLogs()
    }
}
</script>

<style scoped>
.admin-logs {
    padding: 20px 40px;
    width: 100%;
    box-sizing: border-box;
}

.title {
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
    border-bottom: 2px solid #3f51b5;
    padding-bottom: 10px;
}

.filter-section {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
}

.filter-item {
    display: flex;
    flex-direction: column;
}

.filter-item label {
    font-size: 14px;
    color: #666;
    margin-bottom: 5px;
}

.filter-item select,
.filter-item input {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.date-range {
    grid-column: span 2;
}

.date-inputs {
    display: flex;
    align-items: center;
    gap: 10px;
}

.date-inputs span {
    color: #666;
}

.search-box {
    grid-column: span 2;
}

.search-input {
    position: relative;
}

.search-input input {
    width: 100%;
    padding-right: 30px;
}

.search-input i {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: #666;
}

.filter-actions {
    display: flex;
    gap: 10px;
    align-items: flex-end;
}

.btn-filter,
.btn-reset {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
}

.btn-filter {
    background-color: #3f51b5;
    color: white;
}

.btn-reset {
    background-color: #f5f5f5;
    color: #333;
}

.logs-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.logs-header {
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
}

.logs-stats {
    color: #666;
}

.logs-actions {
    display: flex;
    gap: 10px;
}

.btn-export,
.btn-refresh {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 5px;
}

.btn-export {
    background-color: #4caf50;
    color: white;
}

.btn-refresh {
    background-color: #f5f5f5;
    color: #333;
}

.logs-table {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th,
td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

th {
    font-weight: 600;
    color: #333;
    background-color: #f9f9f9;
}

.timestamp {
    white-space: nowrap;
}

.log-level {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 12px;
    font-weight: bold;
}

.level-error {
    background-color: rgba(244, 67, 54, 0.1);
    color: #f44336;
}

.level-warning {
    background-color: rgba(255, 152, 0, 0.1);
    color: #ff9800;
}

.level-info {
    background-color: rgba(33, 150, 243, 0.1);
    color: #2196f3;
}

.level-debug {
    background-color: rgba(158, 158, 158, 0.1);
    color: #757575;
}

.log-message {
    max-width: 400px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.btn-action {
    width: 32px;
    height: 32px;
    border-radius: 4px;
    border: none;
    background-color: transparent;
    color: #666;
    cursor: pointer;
    transition: all 0.3s;
}

.view-btn:hover {
    background-color: rgba(63, 81, 181, 0.1);
    color: #3f51b5;
}

.logs-pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    border-top: 1px solid #eee;
}

.btn-page {
    width: 32px;
    height: 32px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
}

.btn-page:disabled {
    color: #ccc;
    cursor: not-allowed;
}

.page-numbers {
    display: flex;
    margin: 0 10px;
}

.btn-page-num {
    min-width: 32px;
    height: 32px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: white;
    margin: 0 3px;
    cursor: pointer;
}

.btn-page-num.active {
    background-color: #3f51b5;
    color: white;
    border-color: #3f51b5;
}

.log-detail-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
}

.modal-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    width: 90%;
    max-width: 800px;
    max-height: 90%;
    display: flex;
    flex-direction: column;
    position: relative;
    z-index: 1001;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
}

.modal-header h2 {
    margin: 0;
    font-size: 18px;
}

.btn-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #666;
}

.modal-body {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
}

.log-detail-item {
    display: flex;
    margin-bottom: 15px;
}

.log-detail-item.full {
    flex-direction: column;
}

.detail-label {
    width: 100px;
    color: #666;
    font-weight: 500;
}

.log-detail-item.full .detail-label {
    margin-bottom: 5px;
}

.detail-value {
    flex: 1;
}

.detail-value.message {
    white-space: pre-line;
}

.detail-value pre {
    background-color: #f5f5f5;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    white-space: pre-wrap;
    font-family: monospace;
    margin: 0;
}

.modal-footer {
    padding: 15px 20px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
}

.btn-primary {
    padding: 8px 16px;
    background-color: #3f51b5;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
}

@media (max-width: 768px) {
    .filter-section {
        grid-template-columns: 1fr;
    }

    .date-range,
    .search-box {
        grid-column: span 1;
    }

    .date-inputs {
        flex-direction: column;
        align-items: flex-start;
    }

    .logs-header {
        flex-direction: column;
        gap: 10px;
        align-items: flex-start;
    }

    .logs-actions {
        width: 100%;
    }

    .btn-export,
    .btn-refresh {
        flex: 1;
        justify-content: center;
    }

    th:nth-child(3),
    th:nth-child(4),
    td:nth-child(3),
    td:nth-child(4) {
        display: none;
    }
}
</style>