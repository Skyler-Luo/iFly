<template>
    <div class="checkin-view">
        <div class="header-banner">
            <h1>在线值机</h1>
        </div>

        <div class="checkin-container">
            <div v-if="isLoading" class="loading-container">
                <div class="loading-spinner">
                    <i class="el-icon-loading"></i>
                </div>
                <p>正在加载机票信息...</p>
            </div>

            <div v-else class="checkin-content">
                <el-steps :active="activeStep" finish-status="success" align-center>
                    <el-step title="机票验证"></el-step>
                    <el-step title="选择座位"></el-step>
                    <el-step title="生成登机牌"></el-step>
                </el-steps>

                <!-- 步骤1: 机票验证 -->
                <div v-if="activeStep === 0" class="step-content">
                    <div class="ticket-info">
                        <h3>请确认您的机票信息</h3>
                        <div class="ticket-details">
                            <div class="info-row">
                                <span class="info-label">乘客：</span>
                                <span class="info-value">{{ ticket.passengerName }}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">航班：</span>
                                <span class="info-value">{{ ticket.flightNumber }}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">出发：</span>
                                <span class="info-value">{{ ticket.departureCity }} {{ ticket.departureTime }}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">到达：</span>
                                <span class="info-value">{{ ticket.arrivalCity }} {{ ticket.arrivalTime }}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">机票号：</span>
                                <span class="info-value">{{ ticket.ticketNumber }}</span>
                            </div>
                        </div>
                        <el-button type="primary" @click="nextStep">确认信息</el-button>
                    </div>
                </div>

                <!-- 步骤2: 选择座位 -->
                <div v-if="activeStep === 1" class="step-content">
                    <h3>请选择您的座位</h3>
                    <div class="seat-selection">
                        <div class="seat-map-container">
                            <seat-map :selected-seat="selectedSeat" @select-seat="onSeatSelect"></seat-map>
                        </div>
                        <div class="seat-legend">
                            <div class="legend-item">
                                <div class="seat-icon available"></div>
                                <span>可选座位</span>
                            </div>
                            <div class="legend-item">
                                <div class="seat-icon occupied"></div>
                                <span>已占座位</span>
                            </div>
                            <div class="legend-item">
                                <div class="seat-icon selected"></div>
                                <span>已选座位</span>
                            </div>
                        </div>
                        <div class="selected-seat-info">
                            <p v-if="selectedSeat">已选座位: <strong>{{ selectedSeat }}</strong></p>
                            <p v-else>请选择一个座位</p>
                        </div>
                        <div class="step-buttons">
                            <el-button @click="activeStep--">上一步</el-button>
                            <el-button type="primary" @click="confirmSeat" :disabled="!selectedSeat">确认座位</el-button>
                        </div>
                    </div>
                </div>

                <!-- 步骤3: 生成登机牌 -->
                <div v-if="activeStep === 2" class="step-content">
                    <h3>您的登机牌已生成</h3>
                    <div class="boarding-pass">
                        <div class="boarding-pass-header">
                            <div class="airline-logo"></div>
                            <div class="pass-title">登机牌</div>
                        </div>
                        <div class="boarding-pass-content">
                            <div class="pass-row">
                                <div class="pass-item">
                                    <div class="pass-label">乘客</div>
                                    <div class="pass-value">{{ ticket.passengerName }}</div>
                                </div>
                            </div>
                            <div class="pass-row">
                                <div class="pass-item">
                                    <div class="pass-label">航班</div>
                                    <div class="pass-value">{{ ticket.flightNumber }}</div>
                                </div>
                                <div class="pass-item">
                                    <div class="pass-label">座位</div>
                                    <div class="pass-value">{{ selectedSeat }}</div>
                                </div>
                            </div>
                            <div class="pass-row">
                                <div class="pass-item">
                                    <div class="pass-label">出发</div>
                                    <div class="pass-value">{{ ticket.departureCity }}</div>
                                    <div class="pass-subvalue">{{ ticket.departureTime }}</div>
                                </div>
                                <div class="pass-item">
                                    <div class="pass-label">到达</div>
                                    <div class="pass-value">{{ ticket.arrivalCity }}</div>
                                    <div class="pass-subvalue">{{ ticket.arrivalTime }}</div>
                                </div>
                            </div>
                            <div class="pass-row">
                                <div class="pass-item">
                                    <div class="pass-label">登机口</div>
                                    <div class="pass-value">{{ ticket.gate }}</div>
                                </div>
                                <div class="pass-item">
                                    <div class="pass-label">登机时间</div>
                                    <div class="pass-value">{{ ticket.boardingTime }}</div>
                                </div>
                            </div>
                            <div class="barcode">
                                <div class="barcode-image"></div>
                                <div class="barcode-number">{{ ticket.ticketNumber }}</div>
                            </div>
                        </div>
                    </div>
                    <div class="boarding-actions">
                        <el-button type="primary" @click="downloadBoardingPass">下载登机牌</el-button>
                        <el-button @click="goBack">完成</el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import SeatMap from '@/components/SeatMap.vue';

export default {
    name: 'CheckinView',
    components: {
        SeatMap
    },
    data() {
        return {
            isLoading: true,
            activeStep: 0,
            ticket: null,
            selectedSeat: null
        };
    },
    created() {
        // 模拟加载机票信息
        setTimeout(() => {
            // 模拟数据
            this.ticket = {
                id: this.$route.params.ticketId,
                ticketNumber: 'T' + Math.floor(Math.random() * 1000000),
                passengerName: '张三',
                flightNumber: 'CA1234',
                departureCity: '北京',
                arrivalCity: '上海',
                departureTime: '2023-12-20 08:30',
                arrivalTime: '2023-12-20 10:45',
                gate: 'A12',
                boardingTime: '08:00'
            };
            this.isLoading = false;
        }, 1000);
    },
    methods: {
        nextStep() {
            if (this.activeStep < 2) {
                this.activeStep++;
            }
        },
        onSeatSelect(seat) {
            this.selectedSeat = seat;
        },
        confirmSeat() {
            if (this.selectedSeat) {
                this.nextStep();
            } else {
                this.$message.warning('请先选择一个座位');
            }
        },
        downloadBoardingPass() {
            // 在实际应用中，这里会调用生成PDF或图片的逻辑
            this.$message.success('登机牌已下载到您的设备');
        },
        goBack() {
            this.$router.push('/orders');
        }
    }
};
</script>

<style scoped>
.checkin-view {
    padding: 20px;
    background-color: #f5f7fa;
    min-height: 100vh;
}

.header-banner {
    background: linear-gradient(135deg, #00468c, #0076c6);
    color: white;
    padding: 25px;
    border-radius: 8px;
    margin-bottom: 20px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0, 71, 140, 0.15);
}

.header-banner h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
}

.checkin-container {
    max-width: 800px;
    margin: 0 auto;
    background-color: white;
    border-radius: 8px;
    padding: 30px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 50px 0;
}

.loading-spinner {
    font-size: 40px;
    color: #0076c6;
    margin-bottom: 20px;
}

.checkin-content {
    text-align: center;
    padding: 30px 0;
}

.step-content {
    padding: 30px 0;
    max-width: 600px;
    margin: 0 auto;
}

.ticket-info {
    margin-top: 30px;
}

.ticket-details {
    background-color: #f9fcff;
    border: 1px solid #d8e5ee;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    text-align: left;
}

.info-row {
    display: flex;
    margin: 10px 0;
    padding: 5px 0;
    border-bottom: 1px solid #eee;
}

.info-row:last-child {
    border-bottom: none;
}

.info-label {
    width: 80px;
    color: #666;
}

.info-value {
    flex: 1;
    font-weight: 500;
}

.seat-selection {
    margin-top: 20px;
}

.seat-map-container {
    width: 100%;
    margin-bottom: 20px;
    border: 1px solid #ddd;
    border-radius: 5px;
    padding: 15px;
}

.seat-legend {
    display: flex;
    justify-content: center;
    margin-bottom: 20px;
}

.legend-item {
    display: flex;
    align-items: center;
    margin: 0 10px;
}

.seat-icon {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    margin-right: 5px;
}

.seat-icon.available {
    background-color: #67c23a;
}

.seat-icon.occupied {
    background-color: #909399;
}

.seat-icon.selected {
    background-color: #409eff;
}

.selected-seat-info {
    margin: 20px 0;
}

.step-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 30px;
}

.boarding-pass {
    max-width: 450px;
    margin: 30px auto;
    background-color: white;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.boarding-pass-header {
    background: linear-gradient(135deg, #0a4f94, #0076c6);
    color: white;
    padding: 15px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.airline-logo {
    width: 60px;
    height: 30px;
    background-color: rgba(255, 255, 255, 0.7);
    border-radius: 5px;
}

.pass-title {
    font-size: 18px;
    font-weight: bold;
}

.boarding-pass-content {
    padding: 20px;
}

.pass-row {
    display: flex;
    margin-bottom: 15px;
}

.pass-item {
    flex: 1;
    text-align: left;
}

.pass-label {
    font-size: 12px;
    color: #999;
    margin-bottom: 5px;
}

.pass-value {
    font-size: 16px;
    font-weight: 600;
}

.pass-subvalue {
    font-size: 13px;
    color: #666;
    margin-top: 3px;
}

.barcode {
    margin-top: 20px;
    text-align: center;
    padding: 10px 0;
    border-top: 1px dashed #ddd;
}

.barcode-image {
    height: 60px;
    background: repeating-linear-gradient(to right,
            #333 0px,
            #333 2px,
            transparent 2px,
            transparent 4px);
    margin: 0 auto 10px;
    max-width: 200px;
}

.barcode-number {
    font-family: monospace;
    font-size: 14px;
}

.boarding-actions {
    margin-top: 30px;
    display: flex;
    justify-content: center;
    gap: 15px;
}
</style>