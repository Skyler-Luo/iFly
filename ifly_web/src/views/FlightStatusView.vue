<template>
    <div class="flight-status-view">
        <div class="header-banner">
            <h1>航班动态</h1>
            <p>实时掌握航班最新动态</p>
        </div>

        <div class="search-container">
            <el-card class="search-box">
                <el-tabs v-model="searchType" @tab-click="resetForm">
                    <el-tab-pane label="按航班号查询" name="flightNumber">
                        <el-form :model="searchForm" label-width="100px">
                            <el-row :gutter="20">
                                <el-col :span="16">
                                    <el-form-item label="航班号">
                                        <el-input v-model="searchForm.flightNumber" placeholder="例如: CA1234"></el-input>
                                    </el-form-item>
                                </el-col>
                                <el-col :span="8">
                                    <el-form-item label="日期">
                                        <el-date-picker v-model="searchForm.date" type="date" placeholder="选择日期"
                                            style="width: 100%;"></el-date-picker>
                                    </el-form-item>
                                </el-col>
                            </el-row>
                            <el-form-item>
                                <el-button type="primary" @click="searchFlight" :loading="isSearching">
                                    <i class="el-icon-search"></i> 查询航班
                                </el-button>
                            </el-form-item>
                        </el-form>
                    </el-tab-pane>
                    <el-tab-pane label="按起降地查询" name="route">
                        <el-form :model="searchForm" label-width="100px">
                            <el-row :gutter="20">
                                <el-col :span="8">
                                    <el-form-item label="出发城市">
                                        <el-select v-model="searchForm.departureCity" placeholder="选择出发城市" filterable>
                                            <el-option v-for="city in cities" :key="city" :label="city"
                                                :value="city"></el-option>
                                        </el-select>
                                    </el-form-item>
                                </el-col>
                                <el-col :span="8">
                                    <el-form-item label="到达城市">
                                        <el-select v-model="searchForm.arrivalCity" placeholder="选择到达城市" filterable>
                                            <el-option v-for="city in cities" :key="city" :label="city"
                                                :value="city"></el-option>
                                        </el-select>
                                    </el-form-item>
                                </el-col>
                                <el-col :span="8">
                                    <el-form-item label="日期">
                                        <el-date-picker v-model="searchForm.date" type="date" placeholder="选择日期"
                                            style="width: 100%;"></el-date-picker>
                                    </el-form-item>
                                </el-col>
                            </el-row>
                            <el-form-item>
                                <el-button type="primary" @click="searchFlight" :loading="isSearching">
                                    <i class="el-icon-search"></i> 查询航班
                                </el-button>
                            </el-form-item>
                        </el-form>
                    </el-tab-pane>
                </el-tabs>
            </el-card>
        </div>

        <div class="status-results" v-if="flightResults.length > 0">
            <h2 class="result-title">航班动态查询结果</h2>
            <div class="flight-status-list">
                <div v-for="(flight, index) in flightResults" :key="index" class="flight-status-card">
                    <div class="status-header">
                        <div class="flight-info">
                            <div class="flight-number">{{ flight.flightNumber }}</div>
                            <div class="airline">{{ flight.airline }}</div>
                        </div>
                        <div :class="['status-badge', flight.statusClass]">{{ flight.statusText }}</div>
                    </div>

                    <div class="flight-route">
                        <div class="departure">
                            <div class="city">{{ flight.departureCity }}</div>
                            <div class="airport">{{ flight.departureAirport }}</div>
                            <div class="terminal">{{ flight.departureTerminal }}</div>
                            <div :class="['time', flight.departureDelayedClass]">
                                {{ flight.scheduledDepartureTime }}
                                <span v-if="flight.actualDepartureTime !== flight.scheduledDepartureTime"
                                    class="actual-time">
                                    {{ flight.actualDepartureTime }}
                                </span>
                            </div>
                        </div>

                        <div class="flight-path">
                            <div class="duration">{{ flight.duration }}</div>
                            <div class="route-line">
                                <div :class="['flight-icon', flight.statusClass]"></div>
                            </div>
                        </div>

                        <div class="arrival">
                            <div class="city">{{ flight.arrivalCity }}</div>
                            <div class="airport">{{ flight.arrivalAirport }}</div>
                            <div class="terminal">{{ flight.arrivalTerminal }}</div>
                            <div :class="['time', flight.arrivalDelayedClass]">
                                {{ flight.scheduledArrivalTime }}
                                <span v-if="flight.actualArrivalTime !== flight.scheduledArrivalTime"
                                    class="actual-time">
                                    {{ flight.actualArrivalTime }}
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="status-details">
                        <div v-if="flight.statusText === '已延误'" class="delay-info">
                            <i class="el-icon-warning"></i>
                            <span>延误原因: {{ flight.delayReason }}</span>
                        </div>

                        <div class="status-progress">
                            <div class="progress-title">航班进度</div>
                            <el-steps :active="flight.progressStep" finish-status="success" simple>
                                <el-step title="计划"></el-step>
                                <el-step title="值机"></el-step>
                                <el-step title="登机"></el-step>
                                <el-step title="起飞"></el-step>
                                <el-step title="到达"></el-step>
                            </el-steps>
                        </div>

                        <div class="status-info">
                            <div class="info-item">
                                <i class="el-icon-place"></i>
                                <span>机型: {{ flight.aircraft }}</span>
                            </div>
                        </div>

                        <div class="track-button" v-if="flight.statusText !== '已到达' && flight.statusText !== '已取消'">
                            <el-button type="primary" size="small" @click="subscribeFlightUpdates(flight)">
                                订阅航班动态
                            </el-button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="no-results" v-else-if="hasSearched">
            <div class="empty-state">
                <i class="el-icon-warning"></i>
                <p>未找到符合条件的航班，请调整搜索条件重试</p>
            </div>
        </div>

        <div class="flight-status-tips" v-if="!hasSearched">
            <h3>航班动态查询说明</h3>
            <ul>
                <li>您可以通过航班号或出发/到达城市查询航班动态</li>
                <li>航班状态实时更新，提供最新的延误、登机口变更等信息</li>
                <li>订阅航班动态可以通过APP通知获取航班最新状态</li>
                <li>如需帮助，请联系我们的客服热线400-123-4567</li>
            </ul>

            <div class="popular-routes">
                <h3>热门航线状态</h3>
                <el-table :data="popularRoutes" style="width: 100%">
                    <el-table-column prop="route" label="航线"></el-table-column>
                    <el-table-column prop="flightNumber" label="航班号"></el-table-column>
                    <el-table-column prop="scheduledTime" label="计划时间"></el-table-column>
                    <el-table-column prop="status" label="状态">
                        <template #default="scope">
                            <el-tag :type="scope.row.statusType">{{ scope.row.status }}</el-tag>
                        </template>
                    </el-table-column>
                    <el-table-column label="操作" width="120">
                        <template #default="scope">
                            <el-button size="mini" type="text" @click="quickSearch(scope.row)">
                                详情
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>
            </div>
        </div>
    </div>
</template>

<script>
import api from '@/services/api'

export default {
    name: 'FlightStatusView',
    data() {
        return {
            searchType: 'flightNumber',
            searchForm: {
                flightNumber: '',
                departureCity: '',
                arrivalCity: '',
                date: new Date()
            },
            isSearching: false,
            hasSearched: false,
            flightResults: [],
            cities: [
                '北京', '上海', '广州', '深圳', '成都', '杭州',
                '西安', '重庆', '南京', '武汉', '厦门', '长沙'
            ],
            popularRoutes: [],
            isLoadingPopular: false
        };
    },
    created() {
        this.loadPopularRoutes();
    },
    methods: {
        resetForm() {
            if (this.searchType === 'flightNumber') {
                this.searchForm.departureCity = '';
                this.searchForm.arrivalCity = '';
            } else {
                this.searchForm.flightNumber = '';
            }
        },
        async searchFlight() {
            if (this.searchType === 'flightNumber' && !this.searchForm.flightNumber) {
                this.$message.warning('请输入航班号');
                return;
            }
            if (this.searchType === 'route' && (!this.searchForm.departureCity || !this.searchForm.arrivalCity)) {
                this.$message.warning('请选择出发和到达城市');
                return;
            }
            if (!this.searchForm.date) {
                this.$message.warning('请选择日期');
                return;
            }

            this.isSearching = true;
            this.hasSearched = true;
            this.flightResults = [];

            try {
                let response;
                const dateStr = this.formatDate(this.searchForm.date);
                
                if (this.searchType === 'flightNumber') {
                    // 按航班号查询
                    response = await api.flights.getList({ 
                        flight_number: this.searchForm.flightNumber.toUpperCase()
                    });
                } else {
                    // 按航线查询
                    response = await api.flights.search({
                        departure_city: this.searchForm.departureCity,
                        arrival_city: this.searchForm.arrivalCity,
                        departure_date: dateStr
                    });
                }
                
                // 处理响应数据
                const flights = Array.isArray(response) ? response : (response.results || []);
                this.flightResults = this.transformFlightData(flights);
                
                if (this.flightResults.length === 0) {
                    this.$message.info('未找到符合条件的航班');
                }
            } catch (error) {
                console.error('查询航班失败:', error);
                this.$message.error('查询失败，请稍后重试');
            } finally {
                this.isSearching = false;
            }
        },
        transformFlightData(flights) {
            return flights.map(flight => {
                const statusInfo = this.getStatusInfo(flight.status);
                const durationMinutes = this.calculateDuration(flight.departure_time, flight.arrival_time);
                
                return {
                    flightNumber: flight.flight_number,
                    airline: flight.airline_name || '未知航空',
                    departureCity: flight.departure_city,
                    departureAirport: this.getAirportName(flight.departure_city),
                    departureTerminal: 'T2',
                    arrivalCity: flight.arrival_city,
                    arrivalAirport: this.getAirportName(flight.arrival_city),
                    arrivalTerminal: 'T2',
                    scheduledDepartureTime: this.formatTime(flight.departure_time),
                    actualDepartureTime: this.formatTime(flight.departure_time),
                    scheduledArrivalTime: this.formatTime(flight.arrival_time),
                    actualArrivalTime: this.formatTime(flight.arrival_time),
                    duration: this.formatDuration(durationMinutes),
                    statusText: statusInfo.text,
                    statusClass: statusInfo.class,
                    departureDelayedClass: flight.status === 'delayed' ? 'delayed' : '',
                    arrivalDelayedClass: flight.status === 'delayed' ? 'delayed' : '',
                    delayReason: flight.status === 'delayed' ? '航空管制' : '',
                    progressStep: this.getProgressStep(flight.status),
                    gate: '',
                    checkInCounter: '',
                    baggageClaim: '',
                    aircraft: flight.aircraft_type || '未知机型'
                };
            });
        },
        getStatusInfo(status) {
            const statusMap = {
                'scheduled': { text: '计划中', class: 'on-time' },
                'full': { text: '已满', class: 'on-time' },
                'departed': { text: '已起飞', class: 'on-time' },
                'canceled': { text: '已取消', class: 'cancelled' },
                'delayed': { text: '已延误', class: 'delayed' }
            };
            return statusMap[status] || { text: '正常', class: 'on-time' };
        },
        getProgressStep(status) {
            const stepMap = {
                'scheduled': 1,
                'full': 2,
                'departed': 4,
                'canceled': 0
            };
            return stepMap[status] || 1;
        },
        getAirportName(city) {
            const airportMap = {
                '北京': '首都国际机场',
                '上海': '浦东国际机场',
                '广州': '白云国际机场',
                '深圳': '宝安国际机场',
                '成都': '双流国际机场',
                '杭州': '萧山国际机场',
                '西安': '咸阳国际机场',
                '重庆': '江北国际机场',
                '南京': '禄口国际机场',
                '武汉': '天河国际机场',
                '厦门': '高崎国际机场',
                '长沙': '黄花国际机场'
            };
            return airportMap[city] || `${city}机场`;
        },
        calculateDuration(departureTime, arrivalTime) {
            const dep = new Date(departureTime);
            const arr = new Date(arrivalTime);
            return Math.round((arr - dep) / (1000 * 60));
        },
        formatDuration(minutes) {
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return hours > 0 ? `${hours}小时${mins}分` : `${mins}分钟`;
        },
        formatTime(dateTimeStr) {
            if (!dateTimeStr) return '--:--';
            const date = new Date(dateTimeStr);
            const hours = String(date.getHours()).padStart(2, '0');
            const minutes = String(date.getMinutes()).padStart(2, '0');
            return `${hours}:${minutes}`;
        },
        async loadPopularRoutes() {
            this.isLoadingPopular = true;
            try {
                // 获取一些航班作为热门航线展示
                const response = await api.flights.getList({ page_size: 5 });
                const flights = Array.isArray(response) ? response : (response.results || []);
                
                this.popularRoutes = flights.map(flight => {
                    const statusInfo = this.getStatusInfo(flight.status);
                    return {
                        route: `${flight.departure_city}-${flight.arrival_city}`,
                        flightNumber: flight.flight_number,
                        scheduledTime: this.formatTime(flight.departure_time),
                        status: statusInfo.text,
                        statusType: this.getStatusType(flight.status)
                    };
                });
            } catch (error) {
                console.error('加载热门航线失败:', error);
                // 失败时显示空列表
                this.popularRoutes = [];
            } finally {
                this.isLoadingPopular = false;
            }
        },
        getStatusType(status) {
            const typeMap = {
                'scheduled': 'success',
                'full': 'warning',
                'departed': 'info',
                'canceled': 'danger',
                'delayed': 'warning'
            };
            return typeMap[status] || 'success';
        },
        subscribeFlightUpdates(flight) {
            this.$message.success(`已订阅 ${flight.flightNumber} 航班动态，我们将通过APP通知您最新状态`);
        },
        quickSearch(routeInfo) {
            this.searchType = 'flightNumber';
            this.searchForm.flightNumber = routeInfo.flightNumber;
            this.searchFlight();
        },
        formatDate(date) {
            const d = new Date(date);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        }
    }
};
</script>

<style scoped>
.flight-status-view {
    padding: 20px 40px;
    background-color: #f5f7fa;
    width: 100%;
    box-sizing: border-box;
}

.header-banner {
    background: linear-gradient(135deg, #00468c, #0076c6);
    color: white;
    padding: 25px;
    border-radius: 8px;
    text-align: center;
    margin-bottom: 25px;
    box-shadow: 0 4px 12px rgba(0, 71, 140, 0.15);
}

.header-banner h1 {
    margin: 0 0 10px;
    font-size: 28px;
    font-weight: 600;
}

.header-banner p {
    margin: 0;
    font-size: 16px;
    opacity: 0.9;
}

.search-container {
    margin-bottom: 30px;
}

.search-box {
    width: 100%;
    padding: 0 40px;
    box-sizing: border-box;
}

.result-title {
    margin: 20px 0;
    font-size: 22px;
    font-weight: 500;
}

.flight-status-card {
    background: white;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    overflow: hidden;
}

.status-header {
    background: #f9f9f9;
    padding: 15px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
}

.flight-info {
    display: flex;
    align-items: center;
}

.flight-number {
    font-size: 20px;
    font-weight: bold;
    margin-right: 10px;
}

.airline {
    font-size: 14px;
    color: #666;
}

.status-badge {
    padding: 5px 12px;
    border-radius: 15px;
    font-size: 14px;
    font-weight: 500;
}

.status-badge.on-time {
    background-color: #67C23A;
    color: white;
}

.status-badge.delayed {
    background-color: #E6A23C;
    color: white;
}

.status-badge.cancelled {
    background-color: #F56C6C;
    color: white;
}

.flight-route {
    display: flex;
    padding: 25px 20px;
    border-bottom: 1px solid #eee;
}

.departure,
.arrival {
    flex: 1;
}

.departure {
    text-align: left;
}

.arrival {
    text-align: right;
}

.city {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 5px;
}

.airport,
.terminal {
    color: #666;
    font-size: 14px;
    margin-bottom: 3px;
}

.time {
    font-size: 22px;
    font-weight: 600;
    margin-top: 10px;
}

.time.delayed {
    color: #E6A23C;
}

.actual-time {
    font-size: 14px;
    background-color: #fdf6ec;
    color: #E6A23C;
    padding: 2px 5px;
    margin-left: 5px;
    border-radius: 3px;
}

.flight-path {
    width: 150px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 0 15px;
}

.duration {
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
}

.route-line {
    width: 100%;
    height: 3px;
    background-color: #ddd;
    position: relative;
    margin: 10px 0;
}

.flight-icon {
    position: absolute;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background-color: #409EFF;
    top: 50%;
    left: 30%;
    transform: translate(-50%, -50%);
}

.flight-icon.delayed {
    background-color: #E6A23C;
}

.flight-icon.cancelled {
    background-color: #F56C6C;
}

.status-details {
    padding: 20px;
}

.delay-info {
    background-color: #fdf6ec;
    color: #E6A23C;
    padding: 10px;
    border-radius: 5px;
    margin-bottom: 15px;
    display: flex;
    align-items: center;
}

.delay-info i {
    margin-right: 10px;
    font-size: 18px;
}

.status-progress {
    margin: 20px 0;
}

.progress-title {
    margin-bottom: 10px;
    font-weight: 500;
}

.status-info {
    margin-top: 20px;
    display: flex;
    flex-wrap: wrap;
}

.info-item {
    width: 50%;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}

.info-item i {
    margin-right: 8px;
    color: #409EFF;
}

.track-button {
    margin-top: 15px;
    text-align: center;
}

.no-results {
    padding: 50px 0;
    text-align: center;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    color: #909399;
}

.empty-state i {
    font-size: 60px;
    margin-bottom: 20px;
}

.flight-status-tips {
    width: 100%;
    margin: 40px 0;
    padding: 0 40px;
    background-color: white;
    box-sizing: border-box;
    border-radius: 8px;
    padding: 25px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.flight-status-tips h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 18px;
    position: relative;
    padding-bottom: 10px;
}

.flight-status-tips h3:after {
    content: '';
    position: absolute;
    left: 0;
    bottom: 0;
    width: 30px;
    height: 3px;
    background-color: #0076c6;
}

.flight-status-tips ul {
    padding-left: 20px;
    color: #666;
}

.flight-status-tips li {
    margin-bottom: 10px;
}

.popular-routes {
    margin-top: 30px;
}
</style>