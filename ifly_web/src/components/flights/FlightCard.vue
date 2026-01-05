 <template>
    <div class="flight-card"
        :class="{ 'low-seats': flight.availableSeats < 10, 'special-discount': flight.discount < 0.8 }">
        <div class="flight-header">
            <div class="airline-info">
                <div class="airline-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/>
                    </svg>
                </div>
                <div class="airline-details">
                    <div class="airline-name">{{ flight.airlineName }}</div>
                    <div class="flight-number">{{ flight.flightNumber }}</div>
                </div>
            </div>
            <div class="tags">
                <div class="seat-info tag-warning" v-if="flight.availableSeats < 10">
                    仅剩 {{ flight.availableSeats }} 座
                </div>
                <div class="discount-tag tag-success" v-if="flight.discount < 0.8">
                    超值特惠
                </div>
            </div>
        </div>

        <div class="flight-main">
            <div class="time-info">
                <div class="departure">
                    <div class="time">{{ formatTime(flight.departureTime) }}</div>
                    <div class="airport">{{ flight.departureAirport }}</div>
                </div>

                <div class="flight-path">
                    <div class="duration">{{ formatDuration(flight.duration) }}</div>
                    <div class="path-line">
                        <div class="airplane-icon"></div>
                    </div>
                    <div class="flight-type">{{ flight.aircraftType }}</div>
                </div>

                <div class="arrival">
                    <div class="time">{{ formatTime(flight.arrivalTime) }}</div>
                    <div class="airport">{{ flight.arrivalAirport }}</div>
                </div>
            </div>

            <div class="booking-info">
                <div class="price-container">
                    <div class="current-price">¥{{ Math.round(flight.price * flight.discount) }}</div>
                    <div class="original-price" v-if="flight.discount < 1">¥{{ flight.price }}</div>
                    <div class="discount" v-if="flight.discount < 1">{{ Math.round((1 - flight.discount) * 100) }}% 折扣
                    </div>
                </div>
                <el-button type="primary" @click="selectFlight" :disabled="flight.availableSeats === 0">
                    {{ flight.availableSeats > 0 ? '选择' : '已售罄' }}
                </el-button>
            </div>
        </div>

        <div class="flight-details" v-if="showDetails">
            <div class="details-section">
                <h4>航班详情</h4>
                <div class="detail-item">
                    <span class="label">飞机型号:</span>
                    <span>{{ flight.aircraftType }}</span>
                </div>
                <div class="detail-item">
                    <span class="label">餐食服务:</span>
                    <span>{{ flight.mealService ? '提供' : '不提供' }}</span>
                </div>
                <div class="detail-item">
                    <span class="label">行李额度:</span>
                    <span>{{ flight.baggageAllowance }}kg</span>
                </div>
            </div>

            <div class="details-section">
                <h4>舱位选择</h4>
                <el-radio-group v-model="selectedClass" class="cabin-options" @change="handleClassChange">
                    <el-radio value="economy" border>
                        经济舱
                        <span class="cabin-price">¥{{ Math.round(flight.price * flight.discount) }}</span>
                    </el-radio>
                    <el-radio value="business" border v-if="flight.businessAvailable">
                        商务舱
                        <span class="cabin-price">¥{{ Math.round(flight.price * flight.discount * 2.5) }}</span>
                    </el-radio>
                    <el-radio value="first" border v-if="flight.firstAvailable">
                        头等舱
                        <span class="cabin-price">¥{{ Math.round(flight.price * flight.discount * 4) }}</span>
                    </el-radio>
                </el-radio-group>
            </div>

            <div class="details-section amenities">
                <h4>舱内服务</h4>
                <div class="amenity-icons">
                    <div class="amenity-item" :class="{ 'inactive': !flight.wifi }">
                        <div class="amenity-icon wifi-icon"></div>
                        <div class="amenity-name">WiFi</div>
                    </div>
                    <div class="amenity-item" :class="{ 'inactive': !flight.powerOutlet }">
                        <div class="amenity-icon power-icon"></div>
                        <div class="amenity-name">电源</div>
                    </div>
                    <div class="amenity-item" :class="{ 'inactive': !flight.entertainment }">
                        <div class="amenity-icon entertainment-icon"></div>
                        <div class="amenity-name">娱乐系统</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="flight-footer">
            <el-button type="text" @click="toggleDetails">
                {{ showDetails ? '收起详情' : '查看详情' }}
                <i :class="showDetails ? 'el-icon-arrow-up' : 'el-icon-arrow-down'"></i>
            </el-button>
        </div>
    </div>
</template>

<script>
export default {
    name: 'FlightCard',
    props: {
        flight: {
            type: Object,
            required: true
        }
    },
    data() {
        return {
            showDetails: false,
            selectedClass: this.flight.selectedClass || 'economy'
        };
    },
    methods: {
        formatTime(timestamp) {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
        },
        formatDuration(minutes) {
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return `${hours}小时 ${mins}分钟`;
        },
        toggleDetails() {
            this.showDetails = !this.showDetails;
        },
        selectFlight() {
            this.$emit('select', {
                ...this.flight,
                selectedClass: this.selectedClass
            });
        },
        handleClassChange(value) {
            this.$emit('cabin-change', this.flight, value);
        }
    }
}
</script>

<style scoped>
/* 航班卡片样式 - 使用设计系统变量 (Requirements: 3.2, 3.3, 3.4) */
.flight-card {
    background: var(--color-bg-primary, #ffffff);
    /* 圆角统一为 8-16px 范围 (使用 12px) */
    border-radius: var(--card-border-radius, 12px);
    /* 默认阴影使用设计系统变量 */
    box-shadow: var(--card-shadow-default, 0 4px 12px rgba(0, 0, 0, 0.08));
    margin-bottom: 20px;
    padding: 20px;
    /* 过渡时间在 200-400ms 范围内 */
    transition: transform var(--card-transition-duration, 300ms) var(--animation-easing-smooth, cubic-bezier(0.4, 0, 0.2, 1)),
                box-shadow var(--card-transition-duration, 300ms) var(--animation-easing-smooth, cubic-bezier(0.4, 0, 0.2, 1)),
                border-color var(--card-transition-duration, 300ms) var(--animation-easing-smooth, cubic-bezier(0.4, 0, 0.2, 1)),
                background-color var(--card-transition-duration, 300ms) var(--animation-easing-smooth, cubic-bezier(0.4, 0, 0.2, 1));
    position: relative;
    overflow: hidden;
    /* 边框用于悬停高亮效果 */
    border: 2px solid transparent;
    /* 硬件加速优化 */
    will-change: transform, box-shadow, border-color;
    backface-visibility: hidden;
    cursor: pointer;
}

/* 悬停效果 - 边框高亮和背景色变化 (Requirements: 3.2) */
.flight-card:hover {
    transform: var(--card-hover-transform, translateY(-4px));
    box-shadow: var(--card-shadow-hover, 0 8px 24px rgba(0, 0, 0, 0.12)),
                0 4px 16px rgba(25, 118, 210, 0.1);
    /* 边框高亮效果 */
    border-color: var(--color-primary-light, #42a5f5);
    /* 微妙的背景色变化 */
    background-color: var(--color-cloud-white, #f8fcff);
}

/* 点击/激活状态视觉反馈 (Requirements: 3.4) */
.flight-card:active {
    transform: var(--card-active-transform, translateY(-2px)) scale(0.99);
    box-shadow: var(--card-shadow-active, 0 2px 8px rgba(0, 0, 0, 0.1));
    border-color: var(--color-primary, #1976d2);
    background-color: rgba(25, 118, 210, 0.02);
}

.flight-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
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

.tags {
    display: flex;
}

/* 标签样式 - 使用设计系统变量 (Requirements: 3.3) */
.tag-warning,
.tag-success {
    padding: 4px 10px;
    /* 圆角使用设计系统变量 */
    border-radius: var(--border-radius-sm, 4px);
    font-size: 12px;
    margin-left: 8px;
    font-weight: var(--font-weight-medium, 500);
    /* 过渡效果 */
    transition: all var(--animation-duration-fast, 200ms) var(--animation-easing-smooth, ease);
}

.tag-warning {
    background-color: rgba(230, 162, 60, 0.1);
    color: var(--color-warning-dark, #f57400);
    border: 1px solid rgba(230, 162, 60, 0.2);
}

.tag-warning:hover {
    background-color: rgba(230, 162, 60, 0.15);
}

.tag-success {
    background-color: rgba(103, 194, 58, 0.1);
    color: var(--color-success-dark, #388e3c);
    border: 1px solid rgba(103, 194, 58, 0.2);
}

.tag-success:hover {
    background-color: rgba(103, 194, 58, 0.15);
}

.flight-main {
    display: flex;
    justify-content: space-between;
    padding: 15px 0;
    border-top: 1px solid #ebeef5;
    border-bottom: 1px solid #ebeef5;
}

.time-info {
    display: flex;
    align-items: center;
    flex-grow: 1;
}

.departure,
.arrival {
    text-align: center;
    min-width: 120px;
}

.time {
    font-size: 22px;
    font-weight: bold;
}

.airport {
    color: #606266;
    font-size: 14px;
}

.flight-path {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    margin: 0 20px;
}

.path-line {
    width: 100%;
    height: 2px;
    background-color: #dcdfe6;
    position: relative;
    margin: 5px 0;
}

.airplane-icon {
    width: 20px;
    height: 20px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%23409EFF" d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"/></svg>');
    background-size: contain;
    position: absolute;
    top: -9px;
    left: calc(50% - 10px);
}

.duration {
    font-size: 14px;
    color: #606266;
    margin-bottom: 5px;
}

.flight-type {
    font-size: 12px;
    color: #909399;
    margin-top: 5px;
}

.booking-info {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: flex-end;
    min-width: 120px;
}

.price-container {
    margin-bottom: 10px;
    text-align: right;
}

.current-price {
    font-size: 22px;
    font-weight: bold;
    color: #f56c6c;
}

.original-price {
    text-decoration: line-through;
    color: #909399;
    font-size: 14px;
}

.discount {
    color: #67c23a;
    font-size: 12px;
}

/* 航班详情区域 - 使用设计系统变量 (Requirements: 3.3) */
.flight-details {
    padding: 20px 0 0;
    border-top: 1px dashed var(--color-border-light, #ebeef5);
    margin-top: 15px;
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 20px;
    /* 详情区域的微妙背景 */
    background: var(--color-bg-tertiary, #fafafa);
    margin-left: -20px;
    margin-right: -20px;
    margin-bottom: -20px;
    padding: 20px;
    border-radius: 0 0 var(--card-border-radius-sm, 8px) var(--card-border-radius-sm, 8px);
}

.details-section {
    margin-bottom: 15px;
}

.details-section h4 {
    margin-bottom: 10px;
    font-weight: 500;
    color: #303133;
}

.detail-item {
    margin-bottom: 8px;
    font-size: 14px;
}

.detail-item .label {
    color: #606266;
    margin-right: 5px;
}

.cabin-options {
    display: flex;
    flex-direction: column;
}

.cabin-options .el-radio {
    margin: 5px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.cabin-price {
    font-weight: bold;
    color: #f56c6c;
    margin-left: 15px;
}

.amenities .amenity-icons {
    display: flex;
    gap: 15px;
}

.amenity-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    opacity: 1;
}

.amenity-item.inactive {
    opacity: 0.3;
}

.amenity-icon {
    width: 24px;
    height: 24px;
    margin-bottom: 5px;
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;
}

.wifi-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%23409EFF" d="M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z"/></svg>');
}

.power-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%23409EFF" d="M16.01 7L16 3h-2v4h-4V3H8v4h-.01C7 6.99 6 7.99 6 8.99v5.49L9.5 18v3h5v-3l3.5-3.51v-5.5c0-1-1-2-1.99-1.99z"/></svg>');
}

.entertainment-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%23409EFF" d="M18 3v2h-2V3H8v2H6V3H4v18h2v-2h2v2h8v-2h2v2h2V3h-2zM8 17H6v-2h2v2zm0-4H6v-2h2v2zm0-4H6V7h2v2zm10 8h-2v-2h2v2zm0-4h-2v-2h2v2zm0-4h-2V7h2v2z"/></svg>');
}

.amenity-name {
    font-size: 12px;
    color: #606266;
}

.flight-footer {
    text-align: center;
    margin-top: 15px;
}

/* 特殊状态样式 - 增强视觉效果 (Requirements: 3.2, 3.3) */
.flight-card.low-seats {
    border-left: 4px solid var(--color-warning, #e6a23c);
    /* 低座位状态的微妙背景提示 */
    background: linear-gradient(90deg, rgba(230, 162, 60, 0.03) 0%, transparent 20%);
}

.flight-card.low-seats:hover {
    border-left-color: var(--color-warning-dark, #f57400);
    border-top-color: var(--color-primary-light, #42a5f5);
    border-right-color: var(--color-primary-light, #42a5f5);
    border-bottom-color: var(--color-primary-light, #42a5f5);
}

.flight-card.special-discount {
    border-left: 4px solid var(--color-success, #67c23a);
    /* 特惠状态的微妙背景提示 */
    background: linear-gradient(90deg, rgba(103, 194, 58, 0.03) 0%, transparent 20%);
}

.flight-card.special-discount:hover {
    border-left-color: var(--color-success-dark, #388e3c);
    border-top-color: var(--color-primary-light, #42a5f5);
    border-right-color: var(--color-primary-light, #42a5f5);
    border-bottom-color: var(--color-primary-light, #42a5f5);
}

/* 同时具有两种状态时 */
.flight-card.low-seats.special-discount {
    border-left: 4px solid var(--color-success, #67c23a);
    background: linear-gradient(90deg, rgba(103, 194, 58, 0.03) 0%, rgba(230, 162, 60, 0.02) 10%, transparent 25%);
}

@media (max-width: 768px) {
    .flight-main {
        flex-direction: column;
    }

    .booking-info {
        margin-top: 15px;
        flex-direction: row;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }

    .flight-details {
        grid-template-columns: 1fr;
    }
}
</style>