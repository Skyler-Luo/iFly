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
                                <i class="el-icon-time"></i>
                                <span>登机口: {{ flight.gate }}</span>
                            </div>
                            <div class="info-item">
                                <i class="el-icon-tickets"></i>
                                <span>值机柜台: {{ flight.checkInCounter }}</span>
                            </div>
                            <div class="info-item">
                                <i class="el-icon-location-information"></i>
                                <span>行李转盘: {{ flight.baggageClaim }}</span>
                            </div>
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
                <li>订阅航班动态可以通过短信或APP通知获取航班最新状态</li>
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
            popularRoutes: [
                {
                    route: '北京-上海',
                    flightNumber: 'CA1234',
                    scheduledTime: '08:30',
                    status: '正常',
                    statusType: 'success'
                },
                {
                    route: '广州-上海',
                    flightNumber: 'CZ3901',
                    scheduledTime: '10:15',
                    status: '延误',
                    statusType: 'warning'
                },
                {
                    route: '成都-北京',
                    flightNumber: '3U8888',
                    scheduledTime: '13:45',
                    status: '正常',
                    statusType: 'success'
                },
                {
                    route: '深圳-杭州',
                    flightNumber: 'ZH1573',
                    scheduledTime: '16:20',
                    status: '已起飞',
                    statusType: 'info'
                },
                {
                    route: '上海-西安',
                    flightNumber: 'MU2153',
                    scheduledTime: '19:50',
                    status: '取消',
                    statusType: 'danger'
                }
            ]
        };
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
        searchFlight() {
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

            // 模拟API调用
            setTimeout(() => {
                this.isSearching = false;
                this.hasSearched = true;

                // 模拟返回数据
                if (this.searchType === 'flightNumber' && this.searchForm.flightNumber === 'CA1234' ||
                    this.searchType === 'route' && this.searchForm.departureCity === '北京' && this.searchForm.arrivalCity === '上海') {
                    this.flightResults = [
                        {
                            flightNumber: 'CA1234',
                            airline: '中国国际航空公司',
                            departureCity: '北京',
                            departureAirport: '首都国际机场',
                            departureTerminal: 'T3',
                            arrivalCity: '上海',
                            arrivalAirport: '虹桥国际机场',
                            arrivalTerminal: 'T2',
                            scheduledDepartureTime: '08:30',
                            actualDepartureTime: '09:15',
                            scheduledArrivalTime: '10:30',
                            actualArrivalTime: '11:10',
                            duration: '2小时',
                            statusText: '已延误',
                            statusClass: 'delayed',
                            departureDelayedClass: 'delayed',
                            arrivalDelayedClass: 'delayed',
                            delayReason: '天气原因',
                            progressStep: 3,
                            gate: 'C12',
                            checkInCounter: '45-48',
                            baggageClaim: '7号',
                            aircraft: 'Boeing 737-800'
                        }
                    ];
                } else if (this.searchForm.flightNumber === 'MU2153' ||
                    (this.searchForm.departureCity === '上海' && this.searchForm.arrivalCity === '西安')) {
                    this.flightResults = [
                        {
                            flightNumber: 'MU2153',
                            airline: '东方航空公司',
                            departureCity: '上海',
                            departureAirport: '浦东国际机场',
                            departureTerminal: 'T1',
                            arrivalCity: '西安',
                            arrivalAirport: '咸阳国际机场',
                            arrivalTerminal: 'T3',
                            scheduledDepartureTime: '19:50',
                            actualDepartureTime: '取消',
                            scheduledArrivalTime: '22:05',
                            actualArrivalTime: '取消',
                            duration: '2小时15分',
                            statusText: '已取消',
                            statusClass: 'cancelled',
                            departureDelayedClass: '',
                            arrivalDelayedClass: '',
                            delayReason: '',
                            progressStep: 0,
                            gate: '-',
                            checkInCounter: '-',
                            baggageClaim: '-',
                            aircraft: 'Airbus A320'
                        }
                    ];
                } else {
                    this.flightResults = [];
                }
            }, 1000);
        },
        subscribeFlightUpdates(flight) {
            this.$message.success(`已订阅 ${flight.flightNumber} 航班动态，我们将通过短信和APP通知您最新状态`);
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
    padding: 20px;
    background-color: #f5f7fa;
    min-height: 100vh;
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
    max-width: 800px;
    margin: 0 auto;
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
    max-width: 800px;
    margin: 40px auto;
    background-color: white;
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