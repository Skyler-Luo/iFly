<template>
    <div class="admin-promotions">
        <h1 class="title">优惠活动管理</h1>

        <div class="top-actions">
            <div class="search-bar">
                <input type="text" v-model="searchQuery" placeholder="搜索活动名称、代码..." />
                <button @click="handleSearch" class="btn-search">
                    <i class="fas fa-search"></i>
                </button>
            </div>

            <div class="filter-options">
                <select v-model="statusFilter">
                    <option value="">所有状态</option>
                    <option value="active">进行中</option>
                    <option value="upcoming">即将开始</option>
                    <option value="expired">已结束</option>
                </select>

                <select v-model="typeFilter">
                    <option value="">所有类型</option>
                    <option value="discount">折扣</option>
                    <option value="fixed">固定金额</option>
                    <option value="free">免费赠品</option>
                    <option value="points">积分奖励</option>
                </select>
            </div>

            <button @click="showAddPromoModal = true" class="btn btn-primary">
                <i class="fas fa-plus"></i> 添加活动
            </button>
        </div>

        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th @click="sortBy('id')">
                            ID
                            <i class="fas" :class="getSortIconClass('id')"></i>
                        </th>
                        <th @click="sortBy('name')">
                            活动名称
                            <i class="fas" :class="getSortIconClass('name')"></i>
                        </th>
                        <th @click="sortBy('code')">
                            优惠码
                            <i class="fas" :class="getSortIconClass('code')"></i>
                        </th>
                        <th @click="sortBy('type')">
                            类型
                            <i class="fas" :class="getSortIconClass('type')"></i>
                        </th>
                        <th @click="sortBy('value')">
                            优惠值
                            <i class="fas" :class="getSortIconClass('value')"></i>
                        </th>
                        <th @click="sortBy('startDate')">
                            开始日期
                            <i class="fas" :class="getSortIconClass('startDate')"></i>
                        </th>
                        <th @click="sortBy('endDate')">
                            结束日期
                            <i class="fas" :class="getSortIconClass('endDate')"></i>
                        </th>
                        <th @click="sortBy('usageCount')">
                            使用次数
                            <i class="fas" :class="getSortIconClass('usageCount')"></i>
                        </th>
                        <th @click="sortBy('status')">
                            状态
                            <i class="fas" :class="getSortIconClass('status')"></i>
                        </th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="promo in filteredPromotions" :key="promo.id">
                        <td>{{ promo.id }}</td>
                        <td>{{ promo.name }}</td>
                        <td>{{ promo.code }}</td>
                        <td>{{ getTypeText(promo.type) }}</td>
                        <td>{{ formatValue(promo) }}</td>
                        <td>{{ formatDate(promo.startDate) }}</td>
                        <td>{{ formatDate(promo.endDate) }}</td>
                        <td>{{ promo.usageCount }}</td>
                        <td>
                            <span class="status-badge" :class="'status-' + promo.status">
                                {{ getStatusText(promo.status) }}
                            </span>
                        </td>
                        <td class="actions-cell">
                            <button @click="editPromotion(promo)" class="btn-icon">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button @click="openDeleteConfirm(promo)" class="btn-icon">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                            <div class="dropdown">
                                <button class="btn-icon dropdown-toggle">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <div class="dropdown-menu">
                                    <a @click="togglePromotionStatus(promo.id)" v-if="promo.status !== 'expired'">
                                        {{ promo.status === 'active' ? '暂停活动' : '激活活动' }}
                                    </a>
                                    <a @click="duplicatePromotion(promo)">复制活动</a>
                                    <a @click="viewUsageHistory(promo.id)">使用记录</a>
                                    <a @click="generateReport(promo.id)">生成报告</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>

            <div class="pagination">
                <button @click="prevPage" :disabled="currentPage === 1" class="btn-page">
                    <i class="fas fa-chevron-left"></i>
                </button>
                <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
                <button @click="nextPage" :disabled="currentPage === totalPages" class="btn-page">
                    <i class="fas fa-chevron-right"></i>
                </button>
            </div>
        </div>

        <!-- 添加/编辑优惠活动弹窗 -->
        <div v-if="showAddPromoModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>{{ isEditing ? '编辑优惠活动' : '添加优惠活动' }}</h2>
                    <button @click="closeModal" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="submitPromoForm">
                        <div class="form-row">
                            <div class="form-group">
                                <label>活动名称</label>
                                <input type="text" v-model="promoForm.name" required />
                            </div>

                            <div class="form-group">
                                <label>优惠码</label>
                                <input type="text" v-model="promoForm.code" required />
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>活动类型</label>
                                <select v-model="promoForm.type" required>
                                    <option value="discount">折扣</option>
                                    <option value="fixed">固定金额</option>
                                    <option value="free">免费赠品</option>
                                    <option value="points">积分奖励</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label>优惠值</label>
                                <div class="value-input">
                                    <input type="number" v-model="promoForm.value" min="0" required />
                                    <span class="value-unit">
                                        {{ promoForm.type === 'discount' ? '%' :
                                            promoForm.type === 'fixed' ? '元' :
                                                promoForm.type === 'points' ? '积分' : '' }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>开始日期</label>
                                <input type="datetime-local" v-model="promoForm.startDate" required />
                            </div>

                            <div class="form-group">
                                <label>结束日期</label>
                                <input type="datetime-local" v-model="promoForm.endDate" required />
                            </div>
                        </div>

                        <div class="form-group">
                            <label>活动描述</label>
                            <textarea v-model="promoForm.description" rows="3" required></textarea>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>最低消费金额</label>
                                <input type="number" v-model="promoForm.minPurchase" min="0" />
                            </div>

                            <div class="form-group">
                                <label>最高优惠金额</label>
                                <input type="number" v-model="promoForm.maxDiscount" min="0" />
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>每用户使用次数限制</label>
                                <input type="number" v-model="promoForm.perUserLimit" min="1" required />
                            </div>

                            <div class="form-group">
                                <label>总使用次数限制</label>
                                <input type="number" v-model="promoForm.totalLimit" min="1" required />
                            </div>
                        </div>

                        <div class="form-actions">
                            <button type="button" @click="closeModal" class="btn btn-secondary">取消</button>
                            <button type="submit" class="btn btn-primary">{{ isEditing ? '保存修改' : '添加活动' }}</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>

        <!-- 确认删除弹窗 -->
        <div v-if="showDeleteConfirm" class="modal">
            <div class="modal-content modal-sm">
                <div class="modal-header">
                    <h2>确认删除</h2>
                    <button @click="showDeleteConfirm = false" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <p>确定要删除优惠活动 "{{ selectedPromotion?.name }}" 吗？此操作不可撤销。</p>
                    <div class="form-actions">
                        <button @click="showDeleteConfirm = false" class="btn btn-secondary">取消</button>
                        <button @click="deletePromotion" class="btn btn-danger">确认删除</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminPromotionsView',
    data() {
        return {
            promotions: [
                {
                    id: 1,
                    name: '春节特惠',
                    code: 'SPRING2023',
                    type: 'discount',
                    value: 15, // 15% 折扣
                    startDate: '2023-01-15T00:00:00',
                    endDate: '2023-02-15T23:59:59',
                    usageCount: 245,
                    status: 'expired',
                    description: '春节期间预订任意航线可享受85折优惠',
                    minPurchase: 500,
                    maxDiscount: 500,
                    perUserLimit: 2,
                    totalLimit: 500
                },
                {
                    id: 2,
                    name: '暑期亲子游',
                    code: 'SUMMER2023',
                    type: 'discount',
                    value: 20, // 20% 折扣
                    startDate: '2023-06-01T00:00:00',
                    endDate: '2023-08-31T23:59:59',
                    usageCount: 189,
                    status: 'active',
                    description: '暑期亲子航线可享8折优惠',
                    minPurchase: 1000,
                    maxDiscount: 800,
                    perUserLimit: 3,
                    totalLimit: 1000
                },
                {
                    id: 3,
                    name: '新用户专享',
                    code: 'NEWUSER',
                    type: 'fixed',
                    value: 100, // 直减100元
                    startDate: '2023-01-01T00:00:00',
                    endDate: '2023-12-31T23:59:59',
                    usageCount: 532,
                    status: 'active',
                    description: '新用户首次预订立减100元',
                    minPurchase: 300,
                    maxDiscount: 100,
                    perUserLimit: 1,
                    totalLimit: 1000
                },
                {
                    id: 4,
                    name: '商务舱升级',
                    code: 'BUSINESS50',
                    type: 'fixed',
                    value: 500, // 直减500元
                    startDate: '2023-05-10T00:00:00',
                    endDate: '2023-06-10T23:59:59',
                    usageCount: 78,
                    status: 'expired',
                    description: '经济舱升级商务舱立减500元',
                    minPurchase: 2000,
                    maxDiscount: 500,
                    perUserLimit: 1,
                    totalLimit: 200
                },
                {
                    id: 5,
                    name: '周末特惠',
                    code: 'WEEKEND',
                    type: 'discount',
                    value: 10, // 10% 折扣
                    startDate: '2023-06-01T00:00:00',
                    endDate: '2023-12-31T23:59:59',
                    usageCount: 315,
                    status: 'active',
                    description: '周末出发航班可享9折优惠',
                    minPurchase: 300,
                    maxDiscount: 300,
                    perUserLimit: 5,
                    totalLimit: 2000
                },
                {
                    id: 6,
                    name: '积分奖励',
                    code: 'POINTS500',
                    type: 'points',
                    value: 500, // 赠送500积分
                    startDate: '2023-07-01T00:00:00',
                    endDate: '2023-08-15T23:59:59',
                    usageCount: 158,
                    status: 'active',
                    description: '订单完成后赠送500积分',
                    minPurchase: 1000,
                    maxDiscount: 0,
                    perUserLimit: 2,
                    totalLimit: 1000
                },
                {
                    id: 7,
                    name: '国庆特惠',
                    code: 'NATIONAL2023',
                    type: 'discount',
                    value: 15, // 15% 折扣
                    startDate: '2023-09-15T00:00:00',
                    endDate: '2023-10-15T23:59:59',
                    usageCount: 0,
                    status: 'upcoming',
                    description: '国庆期间预订可享85折优惠',
                    minPurchase: 500,
                    maxDiscount: 500,
                    perUserLimit: 2,
                    totalLimit: 1000
                },
                {
                    id: 8,
                    name: '会员日特惠',
                    code: 'MEMBER0825',
                    type: 'discount',
                    value: 25, // 25% 折扣
                    startDate: '2023-08-25T00:00:00',
                    endDate: '2023-08-25T23:59:59',
                    usageCount: 0,
                    status: 'upcoming',
                    description: '会员日当天所有航线可享75折优惠',
                    minPurchase: 300,
                    maxDiscount: 1000,
                    perUserLimit: 1,
                    totalLimit: 3000
                }
            ],
            searchQuery: '',
            statusFilter: '',
            typeFilter: '',
            sortKey: '',
            sortDirection: 'asc',
            currentPage: 1,
            pageSize: 5,
            showAddPromoModal: false,
            showDeleteConfirm: false,
            selectedPromotion: null,
            isEditing: false,
            promoForm: {
                name: '',
                code: '',
                type: 'discount',
                value: 0,
                startDate: '',
                endDate: '',
                description: '',
                minPurchase: 0,
                maxDiscount: 0,
                perUserLimit: 1,
                totalLimit: 1000
            }
        }
    },
    computed: {
        filteredPromotions() {
            let result = [...this.promotions]

            // 应用搜索
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase()
                result = result.filter(promo =>
                    promo.name.toLowerCase().includes(query) ||
                    promo.code.toLowerCase().includes(query) ||
                    promo.description.toLowerCase().includes(query)
                )
            }

            // 应用状态过滤
            if (this.statusFilter) {
                result = result.filter(promo => promo.status === this.statusFilter)
            }

            // 应用类型过滤
            if (this.typeFilter) {
                result = result.filter(promo => promo.type === this.typeFilter)
            }

            // 应用排序
            if (this.sortKey) {
                result.sort((a, b) => {
                    let aValue = a[this.sortKey]
                    let bValue = b[this.sortKey]

                    // 日期排序特殊处理
                    if (this.sortKey === 'startDate' || this.sortKey === 'endDate') {
                        aValue = new Date(aValue).getTime()
                        bValue = new Date(bValue).getTime()
                    }

                    if (aValue < bValue) return this.sortDirection === 'asc' ? -1 : 1
                    if (aValue > bValue) return this.sortDirection === 'asc' ? 1 : -1
                    return 0
                })
            }

            // 分页
            const startIndex = (this.currentPage - 1) * this.pageSize
            const endIndex = startIndex + this.pageSize
            return result.slice(startIndex, endIndex)
        },
        totalPages() {
            // 应用所有过滤条件后的总页数
            let filtered = [...this.promotions]

            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase()
                filtered = filtered.filter(promo =>
                    promo.name.toLowerCase().includes(query) ||
                    promo.code.toLowerCase().includes(query) ||
                    promo.description.toLowerCase().includes(query)
                )
            }

            if (this.statusFilter) {
                filtered = filtered.filter(promo => promo.status === this.statusFilter)
            }

            if (this.typeFilter) {
                filtered = filtered.filter(promo => promo.type === this.typeFilter)
            }

            return Math.ceil(filtered.length / this.pageSize)
        }
    },
    methods: {
        handleSearch() {
            this.currentPage = 1 // 重置页码
        },
        sortBy(key) {
            if (this.sortKey === key) {
                // 如果已经按这个键排序，切换排序方向
                this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc'
            } else {
                // 如果是新的排序键，设置为升序
                this.sortKey = key
                this.sortDirection = 'asc'
            }
        },
        getSortIconClass(key) {
            if (this.sortKey !== key) return 'fa-sort'
            return this.sortDirection === 'asc' ? 'fa-sort-up' : 'fa-sort-down'
        },
        formatDate(dateStr) {
            const date = new Date(dateStr)
            return date.toLocaleDateString()
        },
        getTypeText(type) {
            const typeMap = {
                discount: '折扣',
                fixed: '固定金额',
                free: '免费赠品',
                points: '积分奖励'
            }
            return typeMap[type] || type
        },
        getStatusText(status) {
            const statusMap = {
                active: '进行中',
                upcoming: '即将开始',
                expired: '已结束'
            }
            return statusMap[status] || status
        },
        formatValue(promo) {
            switch (promo.type) {
                case 'discount':
                    return promo.value + '%'
                case 'fixed':
                    return '¥' + promo.value
                case 'points':
                    return promo.value + '积分'
                case 'free':
                    return '赠品'
                default:
                    return promo.value
            }
        },
        prevPage() {
            if (this.currentPage > 1) {
                this.currentPage--
            }
        },
        nextPage() {
            if (this.currentPage < this.totalPages) {
                this.currentPage++
            }
        },
        editPromotion(promo) {
            this.isEditing = true
            this.promoForm = { ...promo }

            // 格式化日期输入
            this.promoForm.startDate = this.formatDateForInput(promo.startDate)
            this.promoForm.endDate = this.formatDateForInput(promo.endDate)

            this.showAddPromoModal = true
        },
        formatDateForInput(dateStr) {
            const date = new Date(dateStr)
            return date.toISOString().slice(0, 16) // 格式: YYYY-MM-DDTHH:MM
        },
        openDeleteConfirm(promo) {
            this.selectedPromotion = promo
            this.showDeleteConfirm = true
        },
        closeModal() {
            this.showAddPromoModal = false
            this.isEditing = false
            this.resetForm()
        },
        resetForm() {
            const now = new Date()
            const futureDate = new Date()
            futureDate.setMonth(futureDate.getMonth() + 1)

            this.promoForm = {
                name: '',
                code: '',
                type: 'discount',
                value: 0,
                startDate: now.toISOString().slice(0, 16),
                endDate: futureDate.toISOString().slice(0, 16),
                description: '',
                minPurchase: 0,
                maxDiscount: 0,
                perUserLimit: 1,
                totalLimit: 1000
            }
        },
        submitPromoForm() {
            if (this.isEditing) {
                // 更新优惠活动
                const index = this.promotions.findIndex(p => p.id === this.promoForm.id)
                if (index !== -1) {
                    // 处理日期
                    const formData = { ...this.promoForm }
                    this.promotions[index] = formData
                }
            } else {
                // 添加新优惠活动
                const newId = Math.max(...this.promotions.map(p => p.id), 0) + 1
                const now = new Date()

                // 确定状态
                let status = 'upcoming'
                const startDate = new Date(this.promoForm.startDate)
                const endDate = new Date(this.promoForm.endDate)

                if (now >= startDate && now <= endDate) {
                    status = 'active'
                } else if (now > endDate) {
                    status = 'expired'
                }

                const newPromo = {
                    ...this.promoForm,
                    id: newId,
                    usageCount: 0,
                    status
                }

                this.promotions.push(newPromo)
            }

            this.closeModal()
            // 在实际应用中，这里应该调用API来保存数据
        },
        deletePromotion() {
            if (this.selectedPromotion) {
                this.promotions = this.promotions.filter(p => p.id !== this.selectedPromotion.id)
                this.showDeleteConfirm = false
                this.selectedPromotion = null

                // 检查是否需要更新当前页
                if (this.filteredPromotions.length === 0 && this.currentPage > 1) {
                    this.currentPage--
                }
            }
        },
        togglePromotionStatus(promoId) {
            const promo = this.promotions.find(p => p.id === promoId)
            if (promo) {
                if (promo.status === 'active') {
                    promo.status = 'upcoming' // 暂停活动
                } else if (promo.status === 'upcoming') {
                    const now = new Date()
                    const startDate = new Date(promo.startDate)
                    const endDate = new Date(promo.endDate)

                    if (now >= startDate && now <= endDate) {
                        promo.status = 'active' // 激活活动
                    }
                }
            }
        },
        duplicatePromotion(promo) {
            const newId = Math.max(...this.promotions.map(p => p.id), 0) + 1
            const now = new Date()
            const futureDate = new Date()
            futureDate.setMonth(futureDate.getMonth() + 1)

            // 复制活动并修改部分信息
            const newPromo = {
                ...promo,
                id: newId,
                name: promo.name + ' (复制)',
                code: promo.code + '_COPY',
                startDate: now.toISOString(),
                endDate: futureDate.toISOString(),
                usageCount: 0,
                status: 'upcoming'
            }

            this.promotions.push(newPromo)
        },
        viewUsageHistory(promoId) {
            // 跳转到使用记录页面
            this.$router.push(`/admin/promotions/${promoId}/usage`)
        },
        generateReport(promoId) {
            // 在实际应用中，这里会生成报告
            alert(`已生成ID为${promoId}的优惠活动报告，请到报表中心查看。`)
        }
    }
}
</script>

<style scoped>
.admin-promotions {
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

.top-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 10px;
}

.search-bar {
    display: flex;
    align-items: center;
    background: white;
    border-radius: 4px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    flex: 1;
    max-width: 400px;
}

.search-bar input {
    border: none;
    padding: 10px 15px;
    flex: 1;
    outline: none;
    font-size: 14px;
}

.btn-search {
    background: #f5f5f5;
    border: none;
    height: 40px;
    width: 40px;
    cursor: pointer;
    color: #555;
}

.btn-search:hover {
    background: #eaeaea;
}

.filter-options {
    display: flex;
    gap: 10px;
}

.filter-options select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    outline: none;
    font-size: 14px;
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

.btn-danger {
    background: #f44336;
    color: white;
}

.btn-danger:hover {
    background: #d32f2f;
}

.data-table-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
}

.data-table th,
.data-table td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #eee;
}

.data-table th {
    background: #f9f9f9;
    color: #333;
    font-weight: 600;
    cursor: pointer;
    user-select: none;
    position: relative;
}

.data-table th i {
    margin-left: 5px;
    font-size: 12px;
}

.data-table th:hover {
    background: #f0f0f0;
}

.data-table tbody tr:hover {
    background: #f9f9f9;
}

.data-table tbody tr:last-child td {
    border-bottom: none;
}

.status-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    display: inline-block;
}

.status-active {
    background: #e8f5e9;
    color: #2e7d32;
}

.status-upcoming {
    background: #e3f2fd;
    color: #1976d2;
}

.status-expired {
    background: #f5f5f5;
    color: #757575;
}

.actions-cell {
    white-space: nowrap;
    display: flex;
    gap: 5px;
}

.btn-icon {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 5px;
    border-radius: 4px;
    transition: all 0.2s;
}

.btn-icon:hover {
    background: #f0f0f0;
    color: #333;
}

.dropdown {
    position: relative;
    display: inline-block;
}

.dropdown-toggle {
    background: none;
    border: none;
    cursor: pointer;
    padding: 5px 8px;
}

.dropdown-menu {
    position: absolute;
    right: 0;
    top: 100%;
    background: white;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.2);
    border-radius: 4px;
    padding: 5px 0;
    min-width: 150px;
    z-index: 10;
    display: none;
}

.dropdown:hover .dropdown-menu {
    display: block;
}

.dropdown-menu a {
    display: block;
    padding: 8px 15px;
    color: #333;
    text-decoration: none;
    font-size: 14px;
    cursor: pointer;
}

.dropdown-menu a:hover {
    background: #f5f5f5;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 15px;
    border-top: 1px solid #eee;
}

.btn-page {
    background: #f5f5f5;
    border: none;
    width: 32px;
    height: 32px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #555;
}

.btn-page:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.btn-page:not(:disabled):hover {
    background: #e0e0e0;
}

.page-info {
    margin: 0 15px;
    font-size: 14px;
    color: #666;
}

.value-input {
    position: relative;
    display: flex;
    align-items: center;
}

.value-unit {
    position: absolute;
    right: 12px;
    color: #666;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-sm {
    max-width: 400px;
}

.modal-header {
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.modal-header h2 {
    font-size: 18px;
    color: #333;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    font-size: 24px;
    color: #999;
    cursor: pointer;
}

.close-btn:hover {
    color: #333;
}

.modal-body {
    padding: 20px;
}

.form-group {
    margin-bottom: 15px;
    width: 100%;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-size: 14px;
    color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    outline: none;
}

.form-row {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

@media (max-width: 768px) {
    .top-actions {
        flex-direction: column;
        align-items: stretch;
    }

    .search-bar {
        max-width: none;
    }

    .filter-options {
        flex-direction: column;
    }

    .data-table {
        display: block;
        overflow-x: auto;
    }

    .form-row {
        flex-direction: column;
        gap: 0;
    }
}
</style>