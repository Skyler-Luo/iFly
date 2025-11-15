<template>
    <div class="admin-flights">
        <h1 class="title">航班管理</h1>

        <div class="top-actions">
            <div class="search-bar">
                <input type="text" v-model="searchQuery" placeholder="搜索航班号、目的地..." />
                <button @click="handleSearch" class="btn-search">
                    <i class="fas fa-search"></i>
                </button>
            </div>

            <div class="filter-options">
                <select v-model="statusFilter">
                    <option value="">所有状态</option>
                    <option value="scheduled">计划中</option>
                    <option value="boarding">登机中</option>
                    <option value="departed">已起飞</option>
                    <option value="arrived">已到达</option>
                    <option value="cancelled">已取消</option>
                    <option value="delayed">已延误</option>
                </select>

                <div class="date-filter">
                    <input type="date" v-model="dateFilter" />
                </div>
            </div>

            <button @click="showAddFlightModal = true" class="btn btn-primary">
                <i class="fas fa-plus"></i> 添加航班
            </button>
        </div>

        <div v-if="isLoading" class="loading-container">
            <div class="spinner"></div>
            <p>正在加载数据...</p>
        </div>

        <div v-else-if="error" class="error-container">
            <i class="fas fa-exclamation-triangle"></i>
            <p>{{ error }}</p>
            <button @click="fetchFlights" class="btn btn-primary">重新加载</button>
        </div>

        <div class="data-table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th @click="sortBy('flightNumber')">
                            航班号
                            <i class="fas" :class="getSortIconClass('flightNumber')"></i>
                        </th>
                        <th @click="sortBy('departure')">
                            出发地
                            <i class="fas" :class="getSortIconClass('departure')"></i>
                        </th>
                        <th @click="sortBy('destination')">
                            目的地
                            <i class="fas" :class="getSortIconClass('destination')"></i>
                        </th>
                        <th @click="sortBy('departureTime')">
                            起飞时间
                            <i class="fas" :class="getSortIconClass('departureTime')"></i>
                        </th>
                        <th @click="sortBy('arrivalTime')">
                            到达时间
                            <i class="fas" :class="getSortIconClass('arrivalTime')"></i>
                        </th>
                        <th @click="sortBy('status')">
                            状态
                            <i class="fas" :class="getSortIconClass('status')"></i>
                        </th>
                        <th @click="sortBy('capacity')">
                            座位数
                            <i class="fas" :class="getSortIconClass('capacity')"></i>
                        </th>
                        <th @click="sortBy('ticketsSold')">
                            已售票数
                            <i class="fas" :class="getSortIconClass('ticketsSold')"></i>
                        </th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="flight in filteredFlights" :key="flight.id">
                        <td>{{ flight.flightNumber }}</td>
                        <td>{{ flight.departure }}</td>
                        <td>{{ flight.destination }}</td>
                        <td>{{ formatDateTime(flight.departureTime) }}</td>
                        <td>{{ formatDateTime(flight.arrivalTime) }}</td>
                        <td>
                            <span class="status-badge" :class="'status-' + flight.status">
                                {{ getStatusText(flight.status) }}
                            </span>
                        </td>
                        <td>{{ flight.capacity }}</td>
                        <td>{{ flight.ticketsSold }}</td>
                        <td class="actions-cell">
                            <button @click="editFlight(flight)" class="btn-icon">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button @click="openDeleteConfirm(flight)" class="btn-icon">
                                <i class="fas fa-trash-alt"></i>
                            </button>
                            <div class="dropdown">
                                <button class="btn-icon dropdown-toggle">
                                    <i class="fas fa-ellipsis-v"></i>
                                </button>
                                <div class="dropdown-menu">
                                    <a @click="updateFlightStatus(flight.id, 'scheduled')">设为计划</a>
                                    <a @click="updateFlightStatus(flight.id, 'boarding')">设为登机中</a>
                                    <a @click="updateFlightStatus(flight.id, 'departed')">设为已起飞</a>
                                    <a @click="updateFlightStatus(flight.id, 'arrived')">设为已到达</a>
                                    <a @click="updateFlightStatus(flight.id, 'delayed')">设为已延误</a>
                                    <a @click="updateFlightStatus(flight.id, 'cancelled')">设为已取消</a>
                                    <a @click="viewPassengers(flight.id)">查看乘客</a>
                                    <a @click="managePricing(flight.id)">管理价格</a>
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

        <!-- 添加航班弹窗 -->
        <div v-if="showAddFlightModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>{{ isEditing ? '编辑航班' : '添加航班' }}</h2>
                    <button @click="closeModal" class="close-btn">&times;</button>
                </div>
                <div class="modal-body">
                    <form @submit.prevent="submitFlightForm">
                        <div class="form-group">
                            <label>航班号</label>
                            <input type="text" v-model="flightForm.flightNumber" required />
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>出发地</label>
                                <input type="text" v-model="flightForm.departure" required />
                            </div>

                            <div class="form-group">
                                <label>目的地</label>
                                <input type="text" v-model="flightForm.destination" required />
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>起飞时间</label>
                                <input type="datetime-local" v-model="flightForm.departureTime" required />
                            </div>

                            <div class="form-group">
                                <label>到达时间</label>
                                <input type="datetime-local" v-model="flightForm.arrivalTime" required />
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>飞机型号</label>
                                <input type="text" v-model="flightForm.aircraft" required />
                            </div>

                            <div class="form-group">
                                <label>座位数</label>
                                <input type="number" v-model="flightForm.capacity" min="1" required />
                            </div>
                        </div>

                        <div class="form-row">
                            <div class="form-group">
                                <label>状态</label>
                                <select v-model="flightForm.status" required>
                                    <option value="scheduled">计划中</option>
                                    <option value="boarding">登机中</option>
                                    <option value="departed">已起飞</option>
                                    <option value="arrived">已到达</option>
                                    <option value="cancelled">已取消</option>
                                    <option value="delayed">已延误</option>
                                </select>
                            </div>

                            <div class="form-group">
                                <label>机组人员</label>
                                <input type="number" v-model="flightForm.crewCount" min="1" required />
                            </div>
                        </div>

                        <div class="form-group">
                            <label>航班描述</label>
                            <textarea v-model="flightForm.description" rows="3"></textarea>
                        </div>

                        <div class="form-actions">
                            <button type="button" @click="closeModal" class="btn btn-secondary">取消</button>
                            <button type="submit" class="btn btn-primary">{{ isEditing ? '保存修改' : '添加航班' }}</button>
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
                    <p>确定要删除航班 {{ selectedFlight?.flightNumber }} 吗？此操作不可撤销。</p>
                    <div class="form-actions">
                        <button @click="showDeleteConfirm = false" class="btn btn-secondary">取消</button>
                        <button @click="deleteFlight" class="btn btn-danger">确认删除</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import api from '../services/api';

export default {
    name: 'AdminFlightsView',
    data() {
        return {
            flights: [],
            isLoading: false,
            error: null,
            searchQuery: '',
            statusFilter: '',
            dateFilter: '',
            sortKey: '',
            sortDirection: 'asc',
            currentPage: 1,
            pageSize: 5,
            showAddFlightModal: false,
            showDeleteConfirm: false,
            selectedFlight: null,
            isEditing: false,
            flightForm: {
                flightNumber: '',
                departure: '',
                destination: '',
                departureTime: '',
                arrivalTime: '',
                status: 'scheduled',
                capacity: 180,
                aircraft: '',
                crewCount: 6,
                description: ''
            }
        }
    },
    computed: {
        filteredFlights() {
            let result = [...this.flights]

            // 应用搜索
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase()
                result = result.filter(flight =>
                    flight.flightNumber.toLowerCase().includes(query) ||
                    flight.departure.toLowerCase().includes(query) ||
                    flight.destination.toLowerCase().includes(query)
                )
            }

            // 应用状态过滤
            if (this.statusFilter) {
                result = result.filter(flight => flight.status === this.statusFilter)
            }

            // 应用日期过滤
            if (this.dateFilter) {
                const filterDate = new Date(this.dateFilter).toISOString().split('T')[0]
                result = result.filter(flight => {
                    const flightDate = new Date(flight.departureTime).toISOString().split('T')[0]
                    return flightDate === filterDate
                })
            }

            // 应用排序
            if (this.sortKey) {
                result.sort((a, b) => {
                    let aValue = a[this.sortKey]
                    let bValue = b[this.sortKey]

                    // 日期时间排序特殊处理
                    if (this.sortKey === 'departureTime' || this.sortKey === 'arrivalTime') {
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
            let filtered = [...this.flights]

            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase()
                filtered = filtered.filter(flight =>
                    flight.flightNumber.toLowerCase().includes(query) ||
                    flight.departure.toLowerCase().includes(query) ||
                    flight.destination.toLowerCase().includes(query)
                )
            }

            if (this.statusFilter) {
                filtered = filtered.filter(flight => flight.status === this.statusFilter)
            }

            if (this.dateFilter) {
                const filterDate = new Date(this.dateFilter).toISOString().split('T')[0]
                filtered = filtered.filter(flight => {
                    const flightDate = new Date(flight.departureTime).toISOString().split('T')[0]
                    return flightDate === filterDate
                })
            }

            return Math.ceil(filtered.length / this.pageSize)
        }
    },
    methods: {
        handleSearch() {
            this.currentPage = 1;
            this.fetchFlights();
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
        formatDateTime(dateTimeStr) {
            const date = new Date(dateTimeStr)
            return `${date.toLocaleDateString()} ${date.toLocaleTimeString().substring(0, 5)}`
        },
        getStatusText(status) {
            const statusMap = {
                scheduled: '计划中',
                boarding: '登机中',
                departed: '已起飞',
                arrived: '已到达',
                cancelled: '已取消',
                delayed: '已延误'
            }
            return statusMap[status] || status
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
        editFlight(flight) {
            this.isEditing = true
            this.flightForm = { ...flight }
            this.showAddFlightModal = true
        },
        openDeleteConfirm(flight) {
            this.selectedFlight = flight
            this.showDeleteConfirm = true
        },
        closeModal() {
            this.showAddFlightModal = false
            this.isEditing = false
            this.resetForm()
        },
        resetForm() {
            this.flightForm = {
                flightNumber: '',
                departure: '',
                destination: '',
                departureTime: '',
                arrivalTime: '',
                status: 'scheduled',
                capacity: 180,
                aircraft: '',
                crewCount: 6,
                description: ''
            }
        },
        submitFlightForm() {
            if (this.isEditing) {
                this.updateFlight();
            } else {
                this.addFlight();
            }
        },
        async fetchFlights() {
            this.isLoading = true;
            this.error = null;

            try {
                const params = {};
                if (this.searchQuery) params.search = this.searchQuery;
                if (this.statusFilter) params.status = this.statusFilter;
                if (this.dateFilter) params.date = this.dateFilter;

                const response = await api.admin.flights.getList(params);
                if (Array.isArray(response.data)) {
                    this.flights = response.data;
                } else {
                    console.warn('API返回的数据不是数组，使用空数组');
                    this.flights = [];
                }

                console.log('获取到航班数据:', this.flights);

                // 如果返回的数据为空，使用模拟数据
                if (!this.flights || this.flights.length === 0) {
                    console.warn('API返回的数据为空，使用默认数据');
                    this.useDefaultData();
                }
            } catch (error) {
                console.error('获取航班数据失败:', error);
                this.error = '获取航班数据失败，请稍后再试';

                // API调用失败，确保flights是数组
                this.flights = [];
                // 使用模拟数据
                this.useDefaultData();
            } finally {
                this.isLoading = false;
            }
        },
        async addFlight() {
            try {
                const response = await api.admin.flights.create(this.flightForm);
                this.flights.push(response.data);
                this.closeModal();
                this.fetchFlights(); // 重新获取所有航班数据
            } catch (error) {
                console.error('添加航班失败:', error);
                alert('添加航班失败，请稍后再试');
            }
        },
        async updateFlight() {
            try {
                await api.admin.flights.update(this.selectedFlight.id, this.flightForm);
                this.closeModal();
                this.fetchFlights(); // 重新获取所有航班数据
            } catch (error) {
                console.error('更新航班失败:', error);
                alert('更新航班失败，请稍后再试');
            }
        },
        async deleteFlight() {
            try {
                await api.admin.flights.delete(this.selectedFlight.id);
                this.flights = this.flights.filter(flight => flight.id !== this.selectedFlight.id);
                this.showDeleteConfirm = false;
            } catch (error) {
                console.error('删除航班失败:', error);
                alert('删除航班失败，请稍后再试');
            }
        },
        async updateFlightStatus(flightId, status) {
            try {
                await api.admin.flights.updateStatus(flightId, status);
                const index = this.flights.findIndex(flight => flight.id === flightId);
                if (index !== -1) {
                    this.flights[index].status = status;
                }
            } catch (error) {
                console.error('更新航班状态失败:', error);
                alert('更新航班状态失败，请稍后再试');
            }
        },
        async viewPassengers(flightId) {
            try {
                const response = await api.admin.flights.getPassengers(flightId);
                console.log('乘客数据:', response.data);
                // 这里可以添加显示乘客数据的逻辑
            } catch (error) {
                console.error('获取乘客信息失败:', error);
                alert('获取乘客信息失败，请稍后再试');
            }
        },
        async managePricing(flightId) {
            try {
                const response = await api.admin.flights.getPricing(flightId);
                console.log('价格数据:', response.data);
                // 这里可以添加管理价格的逻辑
            } catch (error) {
                console.error('获取价格信息失败:', error);
                alert('获取价格信息失败，请稍后再试');
            }
        },
        useDefaultData() {
            this.flights = [
                {
                    id: 1,
                    flightNumber: 'CA1234',
                    departure: '北京',
                    destination: '上海',
                    departureTime: '2023-07-10T08:00:00',
                    arrivalTime: '2023-07-10T10:30:00',
                    status: 'scheduled',
                    capacity: 180,
                    ticketsSold: 165,
                    aircraft: 'Boeing 737-800',
                    crewCount: 6,
                    description: '往返航班，餐饮服务'
                },
                {
                    id: 2,
                    flightNumber: 'MU5678',
                    departure: '广州',
                    destination: '成都',
                    departureTime: '2023-07-10T12:15:00',
                    arrivalTime: '2023-07-10T14:45:00',
                    status: 'boarding',
                    capacity: 220,
                    ticketsSold: 198,
                    aircraft: 'Airbus A320',
                    crewCount: 7,
                    description: '提供机上WiFi服务'
                },
                {
                    id: 3,
                    flightNumber: 'CZ3961',
                    departure: '深圳',
                    destination: '北京',
                    departureTime: '2023-07-10T15:30:00',
                    arrivalTime: '2023-07-10T18:20:00',
                    status: 'departed',
                    capacity: 280,
                    ticketsSold: 260,
                    aircraft: 'Boeing 777-300ER',
                    crewCount: 10,
                    description: '宽体机，全舱娱乐系统'
                }
            ];
        }
    },
    mounted() {
        this.fetchFlights();
    }
}
</script>

<style scoped>
.admin-flights {
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

.filter-options select,
.filter-options input {
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

.status-scheduled {
    background: #e3f2fd;
    color: #1976d2;
}

.status-boarding {
    background: #e8f5e9;
    color: #2e7d32;
}

.status-departed {
    background: #ede7f6;
    color: #5e35b1;
}

.status-arrived {
    background: #e0f2f1;
    color: #00796b;
}

.status-cancelled {
    background: #ffebee;
    color: #c62828;
}

.status-delayed {
    background: #fff8e1;
    color: #ff8f00;
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