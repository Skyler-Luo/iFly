<template>
    <div class="flight-detail-card">
        <div class="flight-info-header">
            <div class="airline-info">
                <div class="airline-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
                    </svg>
                </div>
                <div>
                    <div class="airline-name">{{ flight.airline_name || flight.airlineName }}</div>
                    <div class="flight-number">{{ flight.flight_number || flight.flightNumber }}</div>
                </div>
            </div>
            <div class="cabin-badge" :class="cabinClass">
                {{ cabinLabel }}
            </div>
        </div>

        <div class="flight-main-info">
            <div class="flight-route">
                <div class="departure">
                    <div class="city">{{ flight.departure_city || flight.departureCity }}</div>
                    <div class="time">{{ formatTime(flight.departure_time || flight.departureTime) }}</div>
                    <div class="airport">{{ getAirportName('departure') }}</div>
                </div>

                <div class="flight-duration">
                    <div class="duration-line">
                        <div class="plane-icon"></div>
                    </div>
                    <div class="duration-text">{{ formatDuration(flight.duration) }}</div>
                </div>

                <div class="arrival">
                    <div class="city">{{ flight.arrival_city || flight.arrivalCity }}</div>
                    <div class="time">{{ formatTime(flight.arrival_time || flight.arrivalTime) }}</div>
                    <div class="airport">{{ getAirportName('arrival') }}</div>
                </div>
            </div>

            <div class="flight-price">
                <div class="price-label">价格:</div>
                <div class="price-amount">¥{{ calculateCabinPrice() }}</div>
                <div class="price-unit">/ 人</div>
            </div>
        </div>

        <div class="flight-details">
            <div class="detail-item">
                <i class="el-icon-date"></i>
                <span>日期: {{ formatDate(flight.departure_time || flight.departureTime) }}</span>
            </div>
            <div class="detail-item">
                <i class="el-icon-suitcase"></i>
                <span>行李额度: {{ flight.baggage_allowance || flight.baggageAllowance || 20 }}kg</span>
            </div>
            <div class="detail-item" v-if="flight.meal_service || flight.mealService">
                <i class="el-icon-food"></i>
                <span>提供餐食服务</span>
            </div>
            <div class="detail-item">
                <i class="el-icon-warning"></i>
                <span>剩余座位: {{ flight.available_seats || flight.availableSeats || 0 }}个</span>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'FlightSummary',
    props: {
        flight: {
            type: Object,
            required: true
        },
        cabinClass: {
            type: String,
            default: 'economy'
        }
    },
    computed: {
        cabinLabel() {
            const cabinLabels = {
                economy: '经济舱',
                business: '商务舱',
                first: '头等舱'
            };
            return cabinLabels[this.cabinClass] || '经济舱';
        }
    },
    methods: {
        formatTime(timestamp) {
            if (!timestamp) return '--:--';
            try {
                // 尝试创建日期对象
                const date = new Date(timestamp);

                // 检查日期是否有效
                if (isNaN(date.getTime())) {
                    console.warn('无效的时间戳:', timestamp);
                    return '--:--';
                }

                // 使用更可靠的方法格式化时间
                const hours = date.getHours().toString().padStart(2, '0');
                const minutes = date.getMinutes().toString().padStart(2, '0');
                return `${hours}:${minutes}`;
            } catch (e) {
                console.error('formatTime错误:', e, timestamp);
                return '--:--';
            }
        },
        formatDuration(minutes) {
            if (!minutes && minutes !== 0) return '未知';
            try {
                // 确保minutes是数字
                const mins = Number(minutes);
                if (isNaN(mins)) {
                    return '未知';
                }

                const hours = Math.floor(mins / 60);
                const remainingMins = mins % 60;
                return `${hours}小时 ${remainingMins > 0 ? `${remainingMins}分钟` : ''}`;
            } catch (e) {
                console.error('formatDuration错误:', e, minutes);
                return '未知';
            }
        },
        formatDate(timestamp) {
            if (!timestamp) return '未知日期';
            try {
                // 尝试创建日期对象
                const date = new Date(timestamp);

                // 检查日期是否有效
                if (isNaN(date.getTime())) {
                    console.warn('无效的日期时间戳:', timestamp);
                    return '未知日期';
                }

                // 使用更可靠的方法格式化日期
                const year = date.getFullYear();
                const month = date.getMonth() + 1;
                const day = date.getDate();
                return `${year}年${month}月${day}日`;
            } catch (e) {
                console.error('formatDate错误:', e, timestamp);
                return '未知日期';
            }
        },
        calculateCabinPrice() {
            try {
                // 优先使用API返回的舱位价格
                if (this.flight && this.flight.cabin_price) {
                    return Math.round(this.flight.cabin_price);
                }

                // 尝试获取price字段
                if (this.flight && (this.flight.price || this.flight.price === 0)) {
                    const price = this.flight.price;
                    const discount = this.flight.discount || 1;
                    const basePrice = Math.round(price * discount);

                    switch (this.cabinClass) {
                        case 'business':
                            return Math.round(basePrice * 2.5);
                        case 'first':
                            return Math.round(basePrice * 4);
                        default:
                            return basePrice;
                    }
                }

                // 无法获取价格信息
                console.warn('无法获取航班价格信息');
                return 0;
            } catch (e) {
                console.error('calculateCabinPrice错误:', e);
                return 0;
            }
        },
        getAirportName(type) {
            try {
                // 如果有airports对象
                if (this.flight && this.flight.airports && this.flight.airports[type]) {
                    if (this.flight.airports[type].name) {
                        return this.flight.airports[type].name;
                    }
                    if (this.flight.airports[type].code) {
                        return this.flight.airports[type].code;
                    }
                }

                // 兼容旧版本
                if (type === 'departure') {
                    // 尝试多种可能的属性名
                    const city = this.flight.departure_city || this.flight.departureCity || '出发城市';
                    return this.flight.departureAirport || `${city}机场`;
                } else {
                    const city = this.flight.arrival_city || this.flight.arrivalCity || '到达城市';
                    return this.flight.arrivalAirport || `${city}机场`;
                }
            } catch (e) {
                console.error('getAirportName错误:', e);
                return type === 'departure' ? '出发机场' : '到达机场';
            }
        }
    }
}
</script>

<style scoped>
.flight-detail-card {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
}

.flight-info-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.airline-info {
    display: flex;
    align-items: center;
}

.airline-icon {
    width: 40px;
    height: 40px;
    margin-right: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1976d2, #42a5f5);
    border-radius: 8px;
    color: white;
}

.airline-icon svg {
    width: 24px;
    height: 24px;
}

.airline-name {
    font-weight: 500;
    font-size: 16px;
}

.flight-number {
    color: #606266;
    font-size: 14px;
}

.cabin-badge {
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 14px;
}

.cabin-badge.economy {
    background-color: #ecf5ff;
    color: #409EFF;
}

.cabin-badge.business {
    background-color: #f2f6fc;
    color: #67c23a;
}

.cabin-badge.first {
    background-color: #fef0f0;
    color: #f56c6c;
}

.flight-main-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    padding: 15px 0;
    border-top: 1px solid #ebeef5;
    border-bottom: 1px solid #ebeef5;
}

.flight-route {
    display: flex;
    align-items: center;
    flex-grow: 1;
}

.departure,
.arrival {
    text-align: center;
}

.city {
    font-size: 18px;
    font-weight: bold;
    margin-bottom: 5px;
}

.time {
    font-size: 20px;
    font-weight: bold;
    color: #303133;
}

.airport {
    font-size: 14px;
    color: #606266;
}

.flight-duration {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0 30px;
    min-width: 150px;
}

.duration-line {
    width: 100%;
    height: 2px;
    background-color: #dcdfe6;
    position: relative;
    margin: 10px 0;
}

.plane-icon {
    width: 20px;
    height: 20px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%23409EFF" d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>');
    background-size: contain;
    position: absolute;
    top: -9px;
    left: calc(50% - 10px);
}

.duration-text {
    font-size: 14px;
    color: #606266;
}

.flight-price {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    justify-content: center;
}

.price-label {
    color: #909399;
    font-size: 14px;
}

.price-amount {
    font-size: 22px;
    color: #f56c6c;
    font-weight: bold;
    margin: 5px 0;
}

.price-unit {
    color: #909399;
    font-size: 12px;
}

.flight-details {
    display: flex;
    flex-wrap: wrap;
}

.detail-item {
    margin-right: 20px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    color: #606266;
}

.detail-item i {
    margin-right: 5px;
    color: #909399;
}

@media (max-width: 768px) {
    .flight-main-info {
        flex-direction: column;
    }

    .flight-price {
        flex-direction: row;
        align-items: center;
        justify-content: flex-start;
        margin-top: 15px;
    }

    .price-label {
        margin-right: 10px;
    }

    .price-amount {
        margin: 0 5px;
    }
}
</style>