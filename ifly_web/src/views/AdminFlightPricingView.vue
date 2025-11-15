<template>
    <div class="admin-flight-pricing">
        <h1 class="title">航班票价管理</h1>

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
            </div>
        </div>

        <div class="pricing-container">
            <div class="pricing-header">
                <h2>舱位价格设置</h2>
                <div class="currency-select">
                    <label>货币单位:</label>
                    <select v-model="selectedCurrency">
                        <option value="CNY">人民币 (¥)</option>
                        <option value="USD">美元 ($)</option>
                        <option value="EUR">欧元 (€)</option>
                    </select>
                </div>
            </div>

            <div class="cabin-pricing">
                <div class="cabin-class" v-for="(cabin, index) in cabinPricing" :key="index">
                    <div class="cabin-header">
                        <h3>{{ getCabinName(cabin.type) }}</h3>
                        <span class="seat-count">
                            可售座位数: {{ cabin.availableSeats }}/{{ cabin.totalSeats }}
                        </span>
                    </div>

                    <div class="price-settings">
                        <div class="price-group">
                            <label>基础票价</label>
                            <div class="price-input">
                                <span class="currency-symbol">{{ getCurrencySymbol() }}</span>
                                <input type="number" v-model="cabin.basePrice" min="0" step="10">
                            </div>
                        </div>

                        <div class="price-group">
                            <label>当前售价</label>
                            <div class="price-input">
                                <span class="currency-symbol">{{ getCurrencySymbol() }}</span>
                                <input type="number" v-model="cabin.currentPrice" min="0" step="10">
                            </div>
                        </div>

                        <div class="price-group">
                            <div class="slider-header">
                                <label>折扣率</label>
                                <span class="discount-value">{{ calculateDiscount(cabin) }}%</span>
                            </div>
                            <input type="range" v-model="cabin.discountPct" min="0" max="100" step="5"
                                @input="updateCurrentPrice(cabin)" class="discount-slider">
                        </div>
                    </div>

                    <div class="pricing-options">
                        <div class="option">
                            <label class="checkbox">
                                <input type="checkbox" v-model="cabin.specialMeal">
                                <span></span>
                                特殊餐食 (+¥{{ cabin.specialMealPrice }})
                            </label>
                        </div>

                        <div class="option">
                            <label class="checkbox">
                                <input type="checkbox" v-model="cabin.extraLegroom">
                                <span></span>
                                加大腿部空间 (+¥{{ cabin.extraLegroomPrice }})
                            </label>
                        </div>

                        <div class="option">
                            <label class="checkbox">
                                <input type="checkbox" v-model="cabin.priorityBoarding">
                                <span></span>
                                优先登机 (+¥{{ cabin.priorityBoardingPrice }})
                            </label>
                        </div>
                    </div>

                    <div class="baggage-allowance">
                        <h4>行李额度设置</h4>
                        <div class="baggage-inputs">
                            <div class="baggage-group">
                                <label>随身行李 (kg)</label>
                                <input type="number" v-model="cabin.carryOnAllowance" min="0" step="1">
                            </div>
                            <div class="baggage-group">
                                <label>托运行李 (kg)</label>
                                <input type="number" v-model="cabin.checkedBaggageAllowance" min="0" step="5">
                            </div>
                            <div class="baggage-group">
                                <label>额外行李费率 (¥/kg)</label>
                                <input type="number" v-model="cabin.extraBaggagePrice" min="0" step="10">
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="pricing-rules">
                <h3>动态定价规则</h3>

                <div class="rule-group">
                    <label>高峰期调价比例</label>
                    <div class="price-input">
                        <input type="number" v-model="pricingRules.peakSeasonFactor" min="1" max="3" step="0.05">
                        <span>倍</span>
                    </div>
                </div>

                <div class="rule-group">
                    <label>靠近起飞日期调价策略</label>
                    <div class="strategy-item" v-for="(strategy, index) in pricingRules.departureDateStrategies"
                        :key="index">
                        <span>起飞前 {{ strategy.days }} 天内</span>
                        <div class="price-input">
                            <input type="number" v-model="strategy.factor" min="1" max="3" step="0.05">
                            <span>倍</span>
                        </div>
                    </div>
                </div>

                <div class="rule-group">
                    <label>剩余座位数调价策略</label>
                    <div class="strategy-item" v-for="(strategy, index) in pricingRules.remainingSeatStrategies"
                        :key="index">
                        <span>剩余座位 {{ strategy.percentage }}% 以下</span>
                        <div class="price-input">
                            <input type="number" v-model="strategy.factor" min="1" max="3" step="0.05">
                            <span>倍</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="pricing-actions">
                <button @click="resetPricing" class="btn btn-secondary">
                    <i class="fas fa-undo"></i> 重置价格
                </button>
                <button @click="applyDynamicPricing" class="btn btn-secondary">
                    <i class="fas fa-bolt"></i> 应用动态定价
                </button>
                <button @click="savePricing" class="btn btn-primary">
                    <i class="fas fa-save"></i> 保存设置
                </button>
            </div>
        </div>

        <div v-if="showHistoryChart" class="price-history">
            <h3>价格历史走势</h3>
            <div class="chart-container">
                <!-- 此处在实际应用中应该渲染图表 -->
                <div class="chart-placeholder">
                    价格历史图表将在此显示（实际项目中可使用ECharts等图表库）
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AdminFlightPricingView',
    data() {
        return {
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
            },
            selectedCurrency: 'CNY',
            cabinPricing: [
                {
                    type: 'economy',
                    basePrice: 800,
                    currentPrice: 800,
                    discountPct: 0,
                    availableSeats: 120,
                    totalSeats: 150,
                    specialMeal: false,
                    specialMealPrice: 50,
                    extraLegroom: false,
                    extraLegroomPrice: 100,
                    priorityBoarding: false,
                    priorityBoardingPrice: 30,
                    carryOnAllowance: 5,
                    checkedBaggageAllowance: 20,
                    extraBaggagePrice: 50
                },
                {
                    type: 'business',
                    basePrice: 2000,
                    currentPrice: 2000,
                    discountPct: 0,
                    availableSeats: 25,
                    totalSeats: 30,
                    specialMeal: true,
                    specialMealPrice: 0,
                    extraLegroom: true,
                    extraLegroomPrice: 0,
                    priorityBoarding: true,
                    priorityBoardingPrice: 0,
                    carryOnAllowance: 10,
                    checkedBaggageAllowance: 30,
                    extraBaggagePrice: 50
                },
                {
                    type: 'first',
                    basePrice: 5000,
                    currentPrice: 5000,
                    discountPct: 0,
                    availableSeats: 8,
                    totalSeats: 10,
                    specialMeal: true,
                    specialMealPrice: 0,
                    extraLegroom: true,
                    extraLegroomPrice: 0,
                    priorityBoarding: true,
                    priorityBoardingPrice: 0,
                    carryOnAllowance: 15,
                    checkedBaggageAllowance: 40,
                    extraBaggagePrice: 30
                }
            ],
            pricingRules: {
                peakSeasonFactor: 1.2,
                departureDateStrategies: [
                    { days: 3, factor: 1.5 },
                    { days: 7, factor: 1.3 },
                    { days: 14, factor: 1.1 }
                ],
                remainingSeatStrategies: [
                    { percentage: 10, factor: 1.5 },
                    { percentage: 30, factor: 1.2 },
                    { percentage: 50, factor: 1.1 }
                ]
            },
            showHistoryChart: false,
            originalPricing: null
        }
    },
    created() {
        // 从路由参数获取航班ID
        const flightId = this.$route.params.flightId;
        // 实际应用中应该从API获取航班和价格数据
        this.loadFlightData(flightId);

        // 保存原始价格设置用于重置
        this.originalPricing = JSON.parse(JSON.stringify(this.cabinPricing));
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
        getCabinName(type) {
            const names = {
                economy: '经济舱',
                business: '商务舱',
                first: '头等舱'
            };
            return names[type] || type;
        },
        getCurrencySymbol() {
            const symbols = {
                CNY: '¥',
                USD: '$',
                EUR: '€'
            };
            return symbols[this.selectedCurrency] || '¥';
        },
        calculateDiscount(cabin) {
            if (cabin.basePrice === 0) return 0;
            const discount = 100 - Math.round((cabin.currentPrice / cabin.basePrice) * 100);
            return discount > 0 ? discount : 0;
        },
        updateCurrentPrice(cabin) {
            // 通过折扣率更新当前价格
            cabin.currentPrice = Math.round(cabin.basePrice * (1 - cabin.discountPct / 100));
        },
        loadFlightData(flightId) {
            // 在实际应用中，这里应该调用API获取航班详情和价格数据
            console.log('正在加载航班ID:', flightId);
            // 模拟API加载
            this.flight.id = flightId;
        },
        resetPricing() {
            // 重置价格设置
            this.cabinPricing = JSON.parse(JSON.stringify(this.originalPricing));
        },
        applyDynamicPricing() {
            // 应用动态定价规则
            this.cabinPricing.forEach(cabin => {
                // 这里只是一个简单的示例，实际应用中会有更复杂的定价算法
                let dynamicFactor = 1;

                // 根据剩余座位比例应用价格因子
                const seatPercentage = (cabin.availableSeats / cabin.totalSeats) * 100;
                for (const strategy of this.pricingRules.remainingSeatStrategies) {
                    if (seatPercentage <= strategy.percentage) {
                        dynamicFactor = Math.max(dynamicFactor, strategy.factor);
                        break;
                    }
                }

                // 应用动态价格
                cabin.currentPrice = Math.round(cabin.basePrice * dynamicFactor);

                // 更新折扣率
                if (cabin.basePrice > 0) {
                    cabin.discountPct = Math.max(0, 100 - Math.round((cabin.currentPrice / cabin.basePrice) * 100));
                }
            });

            alert('已应用动态定价规则');
        },
        savePricing() {
            // 在实际应用中，这里应该调用API保存价格设置
            alert('价格设置已保存');
            // 更新原始价格设置
            this.originalPricing = JSON.parse(JSON.stringify(this.cabinPricing));
        }
    }
}
</script>

<style scoped>
.admin-flight-pricing {
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
    flex: 1 1 25%;
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

.pricing-container {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
}

.pricing-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.pricing-header h2 {
    font-size: 18px;
    margin: 0;
}

.currency-select {
    display: flex;
    align-items: center;
}

.currency-select label {
    margin-right: 10px;
}

.currency-select select {
    padding: 5px 10px;
    border-radius: 4px;
    border: 1px solid #ddd;
}

.cabin-pricing {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 20px;
}

.cabin-class {
    flex: 1;
    min-width: 300px;
    border: 1px solid #eee;
    border-radius: 8px;
    padding: 15px;
    background: #f9f9f9;
}

.cabin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
}

.cabin-header h3 {
    margin: 0;
    font-size: 16px;
}

.seat-count {
    font-size: 13px;
    color: #666;
}

.price-settings {
    margin-bottom: 20px;
}

.price-group {
    margin-bottom: 10px;
}

.price-group label {
    display: block;
    margin-bottom: 5px;
    font-size: 14px;
    color: #555;
}

.price-input {
    position: relative;
    display: flex;
    align-items: center;
}

.price-input input {
    width: 100%;
    padding: 8px 12px 8px 25px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.currency-symbol {
    position: absolute;
    left: 10px;
    font-weight: bold;
}

.slider-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.discount-value {
    font-weight: bold;
    color: #3f51b5;
}

.discount-slider {
    width: 100%;
    margin-top: 5px;
}

.pricing-options {
    margin-bottom: 20px;
}

.option {
    margin-bottom: 8px;
}

.checkbox {
    display: inline-flex;
    align-items: center;
    cursor: pointer;
}

.checkbox input {
    position: absolute;
    opacity: 0;
    cursor: pointer;
}

.checkbox span {
    height: 18px;
    width: 18px;
    background-color: #eee;
    border-radius: 4px;
    margin-right: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s;
}

.checkbox span:after {
    content: '';
    width: 5px;
    height: 10px;
    border: solid white;
    border-width: 0 2px 2px 0;
    transform: rotate(45deg);
    display: none;
}

.checkbox input:checked~span {
    background-color: #3f51b5;
}

.checkbox input:checked~span:after {
    display: block;
}

.baggage-allowance h4 {
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 14px;
    color: #333;
}

.baggage-inputs {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.baggage-group {
    flex: 1;
    min-width: 100px;
}

.baggage-group label {
    display: block;
    font-size: 12px;
    margin-bottom: 5px;
    color: #666;
}

.baggage-group input {
    width: 100%;
    padding: 6px 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.pricing-rules {
    background: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
}

.pricing-rules h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 16px;
}

.rule-group {
    margin-bottom: 15px;
}

.rule-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 10px;
}

.strategy-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    padding: 8px;
    background: white;
    border-radius: 4px;
    border: 1px solid #eee;
}

.strategy-item .price-input {
    width: 100px;
}

.pricing-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
}

.btn {
    padding: 8px 16px;
    border-radius: 4px;
    border: none;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
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

.price-history {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

.price-history h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 16px;
}

.chart-container {
    height: 300px;
}

.chart-placeholder {
    height: 100%;
    background: #f9f9f9;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #999;
    border: 1px dashed #ddd;
    border-radius: 4px;
}

@media (max-width: 768px) {
    .flight-header {
        flex-direction: column;
        gap: 10px;
    }

    .cabin-pricing {
        flex-direction: column;
    }

    .baggage-inputs {
        flex-direction: column;
    }

    .strategy-item {
        flex-direction: column;
        align-items: stretch;
    }

    .strategy-item .price-input {
        width: 100%;
        margin-top: 5px;
    }
}
</style>