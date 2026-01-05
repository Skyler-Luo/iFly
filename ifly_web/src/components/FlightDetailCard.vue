<template>
    <div class="flight-detail-card">
        <div class="flight-info-header">
            <div class="airline-info">
                <div class="airline-logo" :style="{ backgroundImage: `url(${flight.airlineLogo})` }">
                </div>
                <div>
                    <div class="airline-name">{{ flight.airlineName }}</div>
                    <div class="flight-number">{{ flight.flightNumber }}</div>
                </div>
            </div>
            <div class="cabin-badge" :class="cabinClass">
                {{ cabinLabel }}
            </div>
        </div>

        <div class="flight-main-info">
            <div class="flight-route">
                <div class="departure">
                    <div class="city">{{ flight.departureCity }}</div>
                    <div class="time">{{ formatTime(flight.departureTime) }}</div>
                    <div class="airport">{{ flight.departureAirport }}</div>
                </div>

                <div class="flight-duration">
                    <div class="duration-line">
                        <div class="plane-icon"></div>
                    </div>
                    <div class="duration-text">{{ formatDuration(flight.duration) }}</div>
                </div>

                <div class="arrival">
                    <div class="city">{{ flight.arrivalCity }}</div>
                    <div class="time">{{ formatTime(flight.arrivalTime) }}</div>
                    <div class="airport">{{ flight.arrivalAirport }}</div>
                </div>
            </div>

            <div class="flight-price">
                <div class="price-label">价格:</div>
                <div class="price-amount">¥{{ cabinPrice }}</div>
                <div class="price-unit">/ 人</div>
            </div>
        </div>

        <div class="flight-details">
            <div class="detail-item">
                <i class="el-icon-date"></i>
                <span>日期: {{ formatDate(flight.departureTime) }}</span>
            </div>
            <div class="detail-item">
                <i class="el-icon-suitcase"></i>
                <span>行李额度: {{ flight.baggageAllowance }}kg</span>
            </div>
            <div class="detail-item" v-if="flight.mealService">
                <i class="el-icon-food"></i>
                <span>提供餐食服务</span>
            </div>
            <div class="detail-item">
                <i class="el-icon-warning"></i>
                <span>剩余座位: {{ flight.availableSeats }}个</span>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'FlightDetailCard',
    props: {
        flight: {
            type: Object,
            required: true
        },
        cabinClass: {
            type: String,
            default: 'economy'
        },
        cabinLabel: {
            type: String,
            default: '经济舱'
        },
        cabinPrice: {
            type: [Number, String],
            default: '0'
        }
    },
    methods: {
        formatTime(dateTimeString) {
            if (!dateTimeString) return '';
            const date = new Date(dateTimeString);
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        },
        formatDate(dateTimeString) {
            if (!dateTimeString) return '';
            const date = new Date(dateTimeString);
            return date.toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
        },
        formatDuration(minutes) {
            if (!minutes) return '';
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return `${hours}h ${mins}m`;
        }
    }
}
</script>

<style scoped>
.flight-detail-card {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
}

.flight-info-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 15px;
    border-bottom: 1px solid #eaeaea;
}

.airline-info {
    display: flex;
    align-items: center;
}

.airline-logo {
    width: 40px;
    height: 40px;
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;
    margin-right: 12px;
}

.airline-name {
    font-weight: 600;
    font-size: 16px;
}

.flight-number {
    color: #666;
    font-size: 14px;
}

.cabin-badge {
    padding: 5px 12px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: 600;
}

.cabin-badge.economy {
    background-color: #e3f2fd;
    color: #1976d2;
}

.cabin-badge.business {
    background-color: #e8eaf6;
    color: #3f51b5;
}

.cabin-badge.first {
    background-color: #fce4ec;
    color: #c2185b;
}

.flight-main-info {
    padding: 20px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.flight-route {
    display: flex;
    align-items: center;
    flex: 1;
}

.departure,
.arrival {
    text-align: center;
    width: 100px;
}

.city {
    font-weight: bold;
    font-size: 16px;
}

.time {
    font-size: 22px;
    font-weight: 600;
    margin: 5px 0;
}

.airport {
    font-size: 12px;
    color: #666;
}

.flight-duration {
    flex: 1;
    text-align: center;
    position: relative;
    padding: 0 15px;
}

.duration-line {
    height: 2px;
    background: #ddd;
    position: relative;
    width: 100%;
    margin: 0 auto 8px;
}

.plane-icon {
    position: absolute;
    width: 24px;
    height: 24px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%231976d2" d="M21,16V14L13,9V3.5A1.5,1.5,0,0,0,11.5,2A1.5,1.5,0,0,0,10,3.5V9L2,14V16L10,13.5V19L8,20.5V22L11.5,21L15,22V20.5L13,19V13.5L21,16Z" /></svg>');
    background-repeat: no-repeat;
    background-position: center;
    top: -11px;
    left: 50%;
    transform: translateX(-50%);
}

.duration-text {
    font-size: 14px;
    color: #666;
}

.flight-price {
    text-align: right;
    min-width: 100px;
}

.price-label {
    font-size: 14px;
    color: #666;
}

.price-amount {
    font-size: 24px;
    font-weight: bold;
    color: #f44336;
}

.price-unit {
    font-size: 12px;
    color: #666;
}

.flight-details {
    display: flex;
    flex-wrap: wrap;
    border-top: 1px solid #eaeaea;
    padding-top: 15px;
}

.detail-item {
    margin-right: 24px;
    display: flex;
    align-items: center;
    font-size: 14px;
    color: #444;
}

.detail-item i {
    margin-right: 6px;
    color: #1976d2;
}
</style>