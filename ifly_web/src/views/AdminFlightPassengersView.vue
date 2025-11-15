<template>
    <div class="admin-flight-passengers">
        <h1 class="title">航班乘客管理</h1>

        <div class="flight-info">
            <div class="flight-header">
                <div class="flight-number">
                    <strong>航班号：</strong> {{ flight.flightNumber }}
                </div>
                <div class="flight-route">
                    <span>{{ flight.departureCity }}</span>
                    <i class="fas fa-arrow-right"></i>
                    <span>{{ flight.arrivalCity }}</span>
                </div>
                <div class="flight-date">
                    <strong>日期：</strong> {{ formatDate(flight.departureTime) }}
                </div>
            </div>
            <div class="flight-details">
                <div class="detail-item">
                    <div class="label">起飞时间</div>
                    <div class="value">{{ formatTime(flight.departureTime) }}</div>
                </div>
                <div class="detail-item">
                    <div class="label">到达时间</div>
                    <div class="value">{{ formatTime(flight.arrivalTime) }}</div>
                </div>
                <div class="detail-item">
                    <div class="label">飞行时间</div>
                    <div class="value">{{ flight.duration }}</div>
                </div>
                <div class="detail-item">
                    <div class="label">飞机型号</div>
                    <div class="value">{{ flight.aircraft }}</div>
                </div>
                <div class="detail-item">
                    <div class="label">机票总数</div>
                    <div class="value">{{ flight.totalSeats }}</div>
                </div>
                <div class="detail-item">
                    <div class="label">已售票数</div>
                    <div class="value">{{ flight.soldSeats }}</div>
                </div>
            </div>
        </div>

        <div class="passenger-filters">
            <div class="search-box">
                <input type="text" v-model="searchQuery" placeholder="搜索乘客姓名/身份证号/手机号">
                <button><i class="fas fa-search"></i></button>
            </div>

            <div class="filter-group">
                <select v-model="cabinFilter">
                    <option value="">所有舱位</option>
                    <option value="economy">经济舱</option>
                    <option value="business">商务舱</option>
                    <option value="first">头等舱</option>
                </select>
            </div>

            <div class="filter-group">
                <select v-model="checkinFilter">
                    <option value="">所有状态</option>
                    <option value="checked">已值机</option>
                    <option value="not_checked">未值机</option>
                </select>
            </div>

            <div class="export-btn">
                <button class="btn btn-secondary">
                    <i class="fas fa-download"></i> 导出乘客名单
                </button>
            </div>
        </div>

        <div class="passenger-table">
            <table>
                <thead>
                    <tr>
                        <th>座位号</th>
                        <th>姓名</th>
                        <th>身份证号</th>
                        <th>手机号码</th>
                        <th>舱位等级</th>
                        <th>值机状态</th>
                        <th>特殊服务</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="passenger in filteredPassengers" :key="passenger.id">
                        <td>{{ passenger.seatNumber || '-' }}</td>
                        <td>{{ passenger.name }}</td>
                        <td>{{ passenger.idNumber }}</td>
                        <td>{{ passenger.phone }}</td>
                        <td>
                            <span :class="getCabinClass(passenger.cabinClass)">
                                {{ getCabinName(passenger.cabinClass) }}
                            </span>
                        </td>
                        <td>
                            <span :class="getCheckinStatus(passenger.checkedIn)">
                                {{ passenger.checkedIn ? '已值机' : '未值机' }}
                            </span>
                        </td>
                        <td>{{ passenger.specialService || '无' }}</td>
                        <td>
                            <button class="action-btn edit-btn" @click="editPassenger(passenger)">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="action-btn checkin-btn" @click="toggleCheckin(passenger)"
                                :disabled="passenger.checkedIn">
                                <i class="fas fa-check-square"></i>
                            </button>
                            <button class="action-btn remove-btn" @click="removePassenger(passenger)">
                                <i class="fas fa-trash"></i>
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <div class="pagination">
            <button class="prev-btn" :disabled="currentPage === 1" @click="currentPage--">
                <i class="fas fa-chevron-left"></i>
            </button>
            <div class="page-info">
                {{ currentPage }} / {{ totalPages }}
            </div>
            <button class="next-btn" :disabled="currentPage === totalPages" @click="currentPage++">
                <i class="fas fa-chevron-right"></i>
            </button>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminFlightPassengersView',
    data() {
        return {
            searchQuery: '',
            cabinFilter: '',
            checkinFilter: '',
            currentPage: 1,
            perPage: 10,
            flight: {
                id: '',
                flightNumber: 'CA1234',
                departureCity: '北京',
                departureAirport: '首都国际机场',
                arrivalCity: '上海',
                arrivalAirport: '浦东国际机场',
                departureTime: '2023-07-25T08:00:00',
                arrivalTime: '2023-07-25T10:30:00',
                duration: '2小时30分钟',
                aircraft: 'Boeing 737-800',
                totalSeats: 180,
                soldSeats: 145
            },
            passengers: [
                {
                    id: 1,
                    name: '张三',
                    idNumber: '110101199001011234',
                    phone: '13800138000',
                    cabinClass: 'economy',
                    checkedIn: true,
                    seatNumber: '12A',
                    specialService: null
                },
                {
                    id: 2,
                    name: '李四',
                    idNumber: '310101199202022345',
                    phone: '13900139000',
                    cabinClass: 'business',
                    checkedIn: true,
                    seatNumber: '2C',
                    specialService: '素食餐'
                },
                {
                    id: 3,
                    name: '王五',
                    idNumber: '440101199303033456',
                    phone: '13700137000',
                    cabinClass: 'economy',
                    checkedIn: false,
                    seatNumber: null,
                    specialService: null
                },
                {
                    id: 4,
                    name: '赵六',
                    idNumber: '510101199404044567',
                    phone: '13600136000',
                    cabinClass: 'first',
                    checkedIn: true,
                    seatNumber: '1A',
                    specialService: '轮椅服务'
                },
                {
                    id: 5,
                    name: '钱七',
                    idNumber: '610101199505055678',
                    phone: '13500135000',
                    cabinClass: 'economy',
                    checkedIn: false,
                    seatNumber: null,
                    specialService: null
                }
            ]
        }
    },
    computed: {
        filteredPassengers() {
            let result = [...this.passengers];

            // 应用搜索过滤
            if (this.searchQuery) {
                const query = this.searchQuery.toLowerCase();
                result = result.filter(p =>
                    p.name.toLowerCase().includes(query) ||
                    p.idNumber.includes(query) ||
                    p.phone.includes(query)
                );
            }

            // 应用舱位过滤
            if (this.cabinFilter) {
                result = result.filter(p => p.cabinClass === this.cabinFilter);
            }

            // 应用值机状态过滤
            if (this.checkinFilter === 'checked') {
                result = result.filter(p => p.checkedIn);
            } else if (this.checkinFilter === 'not_checked') {
                result = result.filter(p => !p.checkedIn);
            }

            return result;
        },
        totalPages() {
            return Math.ceil(this.filteredPassengers.length / this.perPage);
        }
    },
    created() {
        // 从路由参数获取航班ID
        const flightId = this.$route.params.flightId;
        // 实际应用中应该从API获取航班和乘客数据
        this.loadFlightData(flightId);
    },
    methods: {
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('zh-CN');
        },
        formatTime(dateString) {
            const date = new Date(dateString);
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        },
        getCabinClass(cabin) {
            const classes = {
                economy: 'cabin-economy',
                business: 'cabin-business',
                first: 'cabin-first'
            };
            return classes[cabin] || '';
        },
        getCabinName(cabin) {
            const names = {
                economy: '经济舱',
                business: '商务舱',
                first: '头等舱'
            };
            return names[cabin] || cabin;
        },
        getCheckinStatus(isCheckedIn) {
            return isCheckedIn ? 'status-checked' : 'status-not-checked';
        },
        loadFlightData(flightId) {
            // 在实际应用中，这里应该调用API获取航班详情和乘客列表
            console.log('正在加载航班ID:', flightId);
            // 模拟API加载
            this.flight.id = flightId;
        },
        editPassenger(passenger) {
            // 编辑乘客信息的逻辑
            console.log('编辑乘客:', passenger);
        },
        toggleCheckin(passenger) {
            // 切换值机状态的逻辑
            console.log('切换值机状态:', passenger);
            passenger.checkedIn = !passenger.checkedIn;
        },
        removePassenger(passenger) {
            // 删除乘客的逻辑
            if (confirm(`确定要移除乘客 ${passenger.name} 吗？`)) {
                console.log('移除乘客:', passenger);
                const index = this.passengers.findIndex(p => p.id === passenger.id);
                if (index !== -1) {
                    this.passengers.splice(index, 1);
                }
            }
        }
    }
}
</script>

<style scoped>
.admin-flight-passengers {
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

.flight-info {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 15px;
    margin-bottom: 20px;
}

.flight-header {
    display: flex;
    justify-content: space-between;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.flight-route {
    display: flex;
    align-items: center;
    font-size: 18px;
    font-weight: bold;
}

.flight-route i {
    margin: 0 10px;
    color: #3f51b5;
}

.flight-details {
    display: flex;
    flex-wrap: wrap;
    margin-top: 10px;
}

.detail-item {
    flex: 1 1 30%;
    min-width: 150px;
    margin: 5px 0;
}

.detail-item .label {
    font-size: 12px;
    color: #666;
}

.detail-item .value {
    font-weight: bold;
}

.passenger-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 20px;
    align-items: center;
}

.search-box {
    flex: 1;
    min-width: 250px;
    position: relative;
}

.search-box input {
    width: 100%;
    padding: 8px 30px 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.search-box button {
    position: absolute;
    right: 0;
    top: 0;
    height: 100%;
    width: 30px;
    background: transparent;
    border: none;
    cursor: pointer;
}

.filter-group select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: white;
}

.export-btn {
    margin-left: auto;
}

.btn {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
}

.btn i {
    margin-right: 8px;
}

.btn-secondary {
    background: #f5f5f5;
    color: #333;
}

.btn-secondary:hover {
    background: #e0e0e0;
}

.passenger-table {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.passenger-table table {
    width: 100%;
    border-collapse: collapse;
}

.passenger-table th {
    background: #f9f9f9;
    padding: 12px 15px;
    text-align: left;
    font-weight: 600;
    color: #333;
}

.passenger-table td {
    padding: 12px 15px;
    border-top: 1px solid #eee;
}

.cabin-economy {
    background: #e3f2fd;
    color: #1565c0;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.cabin-business {
    background: #e8f5e9;
    color: #2e7d32;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.cabin-first {
    background: #fff8e1;
    color: #ff6f00;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
}

.status-checked {
    color: #4caf50;
    font-weight: bold;
}

.status-not-checked {
    color: #f44336;
}

.action-btn {
    width: 28px;
    height: 28px;
    border-radius: 4px;
    border: none;
    margin-right: 5px;
    cursor: pointer;
    transition: all 0.2s;
}

.edit-btn {
    background: #e3f2fd;
    color: #1565c0;
}

.edit-btn:hover {
    background: #bbdefb;
}

.checkin-btn {
    background: #e8f5e9;
    color: #2e7d32;
}

.checkin-btn:hover {
    background: #c8e6c9;
}

.checkin-btn:disabled {
    background: #f5f5f5;
    color: #999;
    cursor: not-allowed;
}

.remove-btn {
    background: #ffebee;
    color: #c62828;
}

.remove-btn:hover {
    background: #ffcdd2;
}

.pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
}

.pagination button {
    width: 32px;
    height: 32px;
    border-radius: 4px;
    background: white;
    border: 1px solid #ddd;
    color: #333;
    cursor: pointer;
}

.pagination button:disabled {
    color: #ccc;
    cursor: not-allowed;
}

.pagination .page-info {
    margin: 0 10px;
}

@media (max-width: 768px) {
    .flight-header {
        flex-direction: column;
        gap: 10px;
    }

    .passenger-filters {
        flex-direction: column;
        align-items: stretch;
    }

    .export-btn {
        margin-left: 0;
    }
}
</style>