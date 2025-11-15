<template>
    <div class="booking-view">
        <div class="booking-header">
            <h1>预订航班</h1>
            <p>完成以下信息以预订您的航班</p>
            <div class="steps-container">
                <el-steps :active="currentStep" finish-status="success" simple>
                    <el-step title="确认航班" icon="el-icon-plane"></el-step>
                    <el-step title="乘客信息" icon="el-icon-user"></el-step>
                    <el-step title="选择座位" icon="el-icon-tickets"></el-step>
                    <el-step title="支付订单" icon="el-icon-wallet"></el-step>
                </el-steps>
            </div>
        </div>

        <div class="booking-container">
            <!-- 加载中状态 -->
            <div v-if="isLoading" class="loading-container">
                <div class="loading-animation">
                    <div class="loading-plane"></div>
                </div>
                <p>正在加载航班信息...</p>
            </div>

            <div v-else>
                <!-- 步骤1: 确认航班信息 -->
                <div v-show="currentStep === 0">
                    <div class="section-title">
                        <h2>航班信息</h2>
                        <el-button link icon="el-icon-back" @click="goBack">返回选择其他航班</el-button>
                    </div>

                    <flight-summary :flight="flight" :cabin-class="cabinClass" />

                    <div class="section-action">
                        <el-button type="primary" @click="nextStep" :disabled="isNextDisabled">
                            继续填写乘客信息 <i class="el-icon-arrow-right"></i>
                        </el-button>
                    </div>
                </div>

                <!-- 步骤2: 乘客信息 -->
                <div v-show="currentStep === 1">
                    <passenger-list :passengers="passengers" :has-saved-passengers="hasSavedPassengers"
                        @passenger-save="updatePassenger" @use-existing="useExistingPassenger" ref="passengerList" />

                    <contact-form :contact="contactInfo" ref="contactForm" />

                    <div class="section-action">
                        <el-button @click="prevStep" icon="el-icon-arrow-left">返回</el-button>
                        <el-button type="primary" @click="validateAndNextStep">
                            继续选择座位 <i class="el-icon-arrow-right"></i>
                        </el-button>
                    </div>
                </div>

                <!-- 步骤3: 座位选择 -->
                <div v-show="currentStep === 2">
                    <div class="section-title">
                        <h2>座位选择</h2>
                        <div class="cabin-type">{{ cabinLabel }}</div>
                    </div>

                    <div class="seat-selection-container">
                        <div class="seat-map-legend">
                            <div class="legend-item">
                                <div class="seat-icon available"></div>
                                <span>可选座位</span>
                            </div>
                            <div class="legend-item">
                                <div class="seat-icon selected"></div>
                                <span>已选座位</span>
                            </div>
                            <div class="legend-item">
                                <div class="seat-icon occupied"></div>
                                <span>已售座位</span>
                            </div>
                        </div>

                        <div class="aircraft-cabin">
                            <div class="cabin-header">
                                <div class="cabin-exit left">出口</div>
                                <div class="cabin-name">{{ cabinLabel }}</div>
                                <div class="cabin-exit right">出口</div>
                            </div>

                            <div class="seat-map">
                                <div class="aisle-label">
                                    <span v-for="col in columns" :key="col">{{ col }}</span>
                                </div>

                                <div v-for="row in rows" :key="row" class="seat-row">
                                    <div class="row-label">{{ row }}</div>

                                    <div class="row-seats">
                                        <template v-for="col in columns" :key="`${row}-${col}`">
                                            <div v-if="col === 'C' || col === 'D'" class="aisle"></div>

                                            <div class="seat" :class="getSeatClass(row, col)"
                                                @click="toggleSeat(row, col)">
                                                {{ row }}{{ col }}
                                            </div>
                                        </template>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div class="selected-seats-summary">
                            <h3>已选座位</h3>
                            <div v-if="selectedSeats.length > 0" class="seats-list">
                                <div v-for="(seat, index) in selectedSeats" :key="index" class="seat-assignment">
                                    <div class="passenger-name">乘客 {{ index + 1 }}: {{ passengers[index].name ||
                                        `乘客${index + 1}` }}</div>
                                    <div class="seat-number">{{ seat }}</div>
                                    <el-button size="small" type="danger" icon="el-icon-delete" circle
                                        @click="removeSeat(index)"></el-button>
                                </div>
                            </div>
                            <div v-else class="no-seats-selected">
                                <i class="el-icon-warning-outline"></i>
                                <span>尚未选择座位</span>
                            </div>
                        </div>
                    </div>

                    <div class="section-action">
                        <el-button @click="prevStep"><i class="el-icon-arrow-left"></i> 返回</el-button>
                        <el-button type="primary" @click="nextStep" :disabled="selectedSeats.length !== passengerCount">
                            继续支付 <i class="el-icon-arrow-right"></i>
                        </el-button>
                    </div>
                </div>

                <!-- 步骤4: 支付 -->
                <div v-show="currentStep === 3">
                    <div class="section-title">
                        <h2>确认订单并支付</h2>
                    </div>

                    <div class="order-summary">
                        <h3>订单摘要</h3>

                        <div class="summary-card" v-if="flight">
                            <div class="summary-flight">
                                <div class="summary-route">{{ flight.departure_city }} → {{ flight.arrival_city }}</div>
                                <div class="summary-date">{{ formatDate(flight.departure_time) }}</div>
                                <div class="summary-time">{{ formatTime(flight.departure_time) }} - {{
                                    formatTime(flight.arrival_time) }}
                                </div>
                                <div class="summary-flight-number">{{ flight.flight_number }} · {{ cabinLabel }}</div>
                            </div>

                            <div class="summary-passengers">
                                <h4>乘客信息</h4>
                                <div v-for="(passenger, index) in passengers" :key="index" class="summary-passenger">
                                    <div class="passenger-details">
                                        <div class="passenger-name">{{ passenger.name }}</div>
                                        <div class="passenger-id">{{ getIdTypeLabel(passenger.idType) }}: {{
                                            passenger.idNumber }}</div>
                                    </div>
                                    <div class="passenger-seat">座位: {{ selectedSeats[index] }}</div>
                                </div>
                            </div>

                            <div class="summary-contact">
                                <h4>联系人信息</h4>
                                <div class="contact-details">
                                    <div>{{ contactInfo.name }}</div>
                                    <div>{{ contactInfo.phone }}</div>
                                    <div>{{ contactInfo.email }}</div>
                                </div>
                            </div>
                        </div>
                        <div v-else class="error-message">
                            <el-alert title="无法加载航班信息" type="error" description="请返回首页重新选择航班" show-icon>
                            </el-alert>
                        </div>

                        <div class="price-breakdown">
                            <h3>费用明细</h3>
                            <div class="price-item" v-if="flight">
                                <div class="price-desc">{{ cabinLabel }} × {{ passengerCount }}</div>
                                <div class="price-amount">¥{{ cabinPrice }} × {{ passengerCount }}</div>
                            </div>
                            <div class="price-item" v-if="flight">
                                <div class="price-desc">机场建设费</div>
                                <div class="price-amount">¥50 × {{ passengerCount }}</div>
                            </div>
                            <div class="price-item" v-if="flight">
                                <div class="price-desc">燃油附加费</div>
                                <div class="price-amount">¥30 × {{ passengerCount }}</div>
                            </div>
                            <div class="price-total" v-if="flight">
                                <div class="total-label">总计</div>
                                <div class="total-amount">¥{{ totalPrice }}</div>
                            </div>
                            <div v-else class="error-message">
                                <p>无法计算价格，航班信息不完整</p>
                            </div>
                        </div>
                    </div>

                    <div class="payment-options">
                        <h3>支付方式</h3>
                        <el-radio-group v-model="paymentMethod">
                            <el-radio value="alipay">
                                <div class="payment-option">
                                    <img src="https://picsum.photos/id/17/30/30" alt="支付宝" />
                                    <span>支付宝</span>
                                </div>
                            </el-radio>
                            <el-radio value="wechat">
                                <div class="payment-option">
                                    <img src="https://picsum.photos/id/18/30/30" alt="微信支付" />
                                    <span>微信支付</span>
                                </div>
                            </el-radio>
                            <el-radio value="creditcard">
                                <div class="payment-option">
                                    <img src="https://picsum.photos/id/19/30/30" alt="信用卡" />
                                    <span>信用卡</span>
                                </div>
                            </el-radio>
                        </el-radio-group>

                        <div class="payment-agreement">
                            <el-checkbox v-model="agreementChecked">我已阅读并同意</el-checkbox>
                            <el-button link>《购票协议》</el-button>和
                            <el-button link>《隐私政策》</el-button>
                        </div>
                    </div>

                    <div class="section-action">
                        <el-button @click="prevStep"><i class="el-icon-arrow-left"></i> 返回</el-button>
                        <el-button type="primary" @click="submitOrder" :loading="isSubmitting"
                            :disabled="!agreementChecked || !paymentMethod">
                            确认支付 ¥{{ totalPrice }}
                        </el-button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 订单成功弹窗 -->
        <el-dialog title="订单提交成功" v-model="orderSuccessVisible" width="400px" :show-close="false"
            :close-on-click-modal="false" :close-on-press-escape="false">
            <div class="success-dialog">
                <div class="success-icon">
                    <i class="el-icon-success"></i>
                </div>
                <h2>订单提交成功</h2>
                <p>您的订单号: {{ orderNumber }}</p>
                <p>订单详情已发送至您的邮箱</p>
                <div class="dialog-footer">
                    <el-button type="primary" @click="goToOrderDetail">查看订单详情</el-button>
                    <el-button @click="goToHome">返回首页</el-button>
                </div>
            </div>
        </el-dialog>
    </div>
</template>

<script>
import FlightSummary from '@/components/flights/FlightSummary.vue'
import PassengerList from '@/components/booking/PassengerList.vue'
import ContactForm from '@/components/ContactForm.vue'
import api from '@/services/api'

export default {
    name: 'BookingView',
    components: {
        FlightSummary,
        PassengerList,
        ContactForm
    },
    data() {
        return {
            isLoading: true,
            currentStep: 0,
            flight: null,
            cabinClass: '',
            passengerCount: 0,
            passengers: [],
            activePassengers: [0],
            selectedSeats: [],
            occupiedSeats: [],
            columns: ['A', 'B', 'C', 'D', 'E', 'F'],
            rows: Array.from({ length: 30 }, (_, i) => i + 1),
            contactInfo: {
                name: '',
                phone: '',
                email: ''
            },
            paymentMethod: '',
            agreementChecked: false,
            isSubmitting: false,
            orderSuccessVisible: false,
            orderNumber: '',
            selectedPassengerIds: [], // 存储选中的乘客ID

            // 表单验证规则
            passengerRules: {
                name: [
                    { required: true, message: '请输入乘客姓名', trigger: 'blur' },
                    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
                ],
                gender: [
                    { required: true, message: '请选择性别', trigger: 'change' }
                ],
                idType: [
                    { required: true, message: '请选择证件类型', trigger: 'change' }
                ],
                idNumber: [
                    { required: true, message: '请输入证件号码', trigger: 'blur' },
                    {
                        validator: (rule, value, callback) => {
                            this.validateIdNumber(rule, value, callback);
                        },
                        trigger: 'blur'
                    }
                ],
                birthDate: [
                    { required: true, message: '请选择出生日期', trigger: 'change' }
                ],
                phone: [
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
                ]
            },
            contactRules: {
                name: [
                    { required: true, message: '请输入联系人姓名', trigger: 'blur' }
                ],
                phone: [
                    { required: true, message: '请输入联系电话', trigger: 'blur' },
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
                ],
                email: [
                    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
                    { type: 'email', message: '请输入正确的电子邮箱格式', trigger: 'blur' }
                ]
            }
        };
    },
    computed: {
        cabinLabel() {
            const cabinMap = {
                'economy': '经济舱',
                'business': '商务舱',
                'first': '头等舱'
            };
            return cabinMap[this.cabinClass] || '经济舱';
        },
        cabinPrice() {
            if (!this.flight) return 0;
            console.log('计算舱位价格:', this.flight);

            // 直接使用API返回的舱位价格
            const price = this.flight.cabin_price || this.flight.cabinPrice || this.flight.price || 0;
            console.log('使用价格:', price);
            return price;
        },
        totalPrice() {
            // 基础票价 + 机场建设费(50) + 燃油附加费(30)
            const perPersonPrice = this.cabinPrice + 50 + 30;
            return (perPersonPrice * this.passengerCount).toFixed(2);
        },
        hasSavedPassengers() {
            // 检查是否有保存的乘客信息
            return localStorage.getItem('savedPassengers') !== null;
        },
        isNextDisabled() {
            return !this.flight;
        },
        canProceedToSeats() {
            // 检查所有乘客信息是否已完成
            return this.passengers.every(p => p.isComplete) && this.contactInfo.name && this.contactInfo.phone && this.contactInfo.email;
        }
    },
    created() {
        this.initializeBooking();
    },
    mounted() {
        // 检查是否有保存的预订状态（从登录页面返回）
        this.restoreBookingState();
    },
    methods: {
        // 恢复保存的预订状态
        restoreBookingState() {
            const savedState = sessionStorage.getItem('bookingState');
            if (savedState) {
                try {
                    const state = JSON.parse(savedState);
                    console.log('恢复预订状态:', state);

                    // 如果当前页面的航班ID与保存的状态一致，则恢复状态
                    if (state.flightId === this.$route.params.flightId) {
                        this.selectedSeats = state.selectedSeats || [];
                        this.passengers = state.passengers || [];
                        this.contactInfo = state.contactInfo || { name: '', phone: '', email: '' };
                        this.paymentMethod = state.paymentMethod || 'alipay';

                        // 恢复到最后一步
                        if (this.selectedSeats.length > 0) {
                            this.currentStep = 3; // 支付步骤
                        }
                    }

                    // 清除保存的状态
                    sessionStorage.removeItem('bookingState');
                } catch (e) {
                    console.error('恢复预订状态失败:', e);
                    sessionStorage.removeItem('bookingState');
                }
            }
        },

        initializeBooking() {
            // 从路由参数获取数据
            const flightId = this.$route.params.flightId;
            console.log('从URL参数中获取flightId:', flightId);
            this.cabinClass = this.$route.query.class || 'economy';
            this.passengerCount = parseInt(this.$route.query.passengers) || 1;

            // 初始化乘客数组
            this.passengers = Array.from({ length: this.passengerCount }, () => ({
                name: '',
                gender: '',
                idType: 'idcard',
                idNumber: '',
                birthDate: '',
                phone: '',
                isComplete: false
            }));

            if (!flightId) {
                console.error('航班ID未在URL参数中找到');
                this.$message.error('无法加载航班信息，ID缺失');
                this.isLoading = false;
                return;
            }

            // 使用真实API获取航班数据
            api.flights.getBookingInfo(flightId, { cabin_class: this.cabinClass })
                .then(response => {
                    console.log('航班详情原始响应:', response);

                    // 确保response是有效对象
                    if (!response) {
                        throw new Error('航班数据返回为空');
                    }

                    // 检查是否需要从response.data中获取数据
                    const data = response.data ? response.data : response;

                    // 统一数据格式 (兼容snake_case和camelCase)
                    this.flight = {
                        id: data.id || flightId,
                        flightNumber: data.flight_number || data.flightNumber || '未知航班',
                        airlineName: data.airline_name || data.airlineName || '未知航空',
                        airlineLogo: data.airline_logo || data.airlineLogo || '',
                        departureCity: data.departure_city || data.departureCity || '出发城市',
                        arrivalCity: data.arrival_city || data.arrivalCity || '到达城市',
                        departureTime: data.departure_time || data.departureTime,
                        arrivalTime: data.arrival_time || data.arrivalTime,
                        duration: data.duration || 0,
                        price: data.price || 0,
                        cabinPrice: data.cabin_price || data.cabinPrice || data.price || 0,
                        discount: data.discount || 1,
                        availableSeats: data.available_seats || data.availableSeats || 0,
                        aircraft: data.aircraft || '未知机型',
                        airports: {
                            departure: {
                                code: (data.airports && data.airports.departure && data.airports.departure.code) || '',
                                name: (data.airports && data.airports.departure && data.airports.departure.name) ||
                                    `${data.departure_city || data.departureCity || ''}国际机场`
                            },
                            arrival: {
                                code: (data.airports && data.airports.arrival && data.airports.arrival.code) || '',
                                name: (data.airports && data.airports.arrival && data.airports.arrival.name) ||
                                    `${data.arrival_city || data.arrivalCity || ''}国际机场`
                            }
                        },
                        status: data.status || '准时',
                        // 保留原始字段，确保兼容性
                        flight_number: data.flight_number || data.flightNumber || '未知航班',
                        airline_name: data.airline_name || data.airlineName || '未知航空',
                        airline_logo: data.airline_logo || data.airlineLogo || '',
                        departure_city: data.departure_city || data.departureCity || '出发城市',
                        arrival_city: data.arrival_city || data.arrivalCity || '到达城市',
                        departure_time: data.departure_time || data.departureTime,
                        arrival_time: data.arrival_time || data.arrivalTime,
                        available_seats: data.available_seats || data.availableSeats || 0,
                        cabin_price: data.cabin_price || data.cabinPrice || data.price || 0,
                    };

                    console.log('获取到航班数据，ID:', this.flight.id);
                    console.log('处理后的航班数据:', this.flight);

                    // 确保数据已经更新到视图
                    this.$nextTick(() => {
                        console.log('视图更新后的航班数据:', this.flight);
                        this.initSeatMap();
                    });

                    this.isLoading = false;
                })
                .catch(error => {
                    console.error('获取航班数据失败', error);
                    this.$message.error('获取航班数据失败，请稍后重试');
                    this.isLoading = false;
                });
        },

        initSeatMap() {
            // 如果没有航班数据，不进行初始化
            if (!this.flight) return;

            // 确保存在有效的航班ID
            const flightId = this.flight.id;
            if (!flightId) {
                console.error('航班ID不存在，无法获取座位信息');
                this.$message.warning('无法获取座位信息，将使用默认座位布局');
                this.generateRandomOccupiedSeats();
                return;
            }

            // 更新座位行列信息
            // 根据舱位类别确定显示的座位范围
            if (this.cabinClass === 'economy') {
                // 经济舱通常在后部
                this.rows = Array.from({ length: 20 }, (_, i) => i + 11);
            } else if (this.cabinClass === 'business') {
                // 商务舱通常在中部
                this.rows = Array.from({ length: 5 }, (_, i) => i + 6);
            } else if (this.cabinClass === 'first') {
                // 头等舱通常在前部
                this.rows = Array.from({ length: 5 }, (_, i) => i + 1);
            }

            console.log('正在获取座位信息，航班ID:', flightId);

            // 简化的座位数据处理逻辑
            api.flights.getAvailableSeats(flightId)
                .then(response => {
                    console.log('座位数据响应:', response);
                    this.occupiedSeats = [];

                    try {
                        // 尝试解析不同格式的座位数据
                        if (response && response.seat_map && Array.isArray(response.seat_map)) {
                            // 标准格式
                            response.seat_map.forEach(row => {
                                if (Array.isArray(row)) {
                                    row.forEach(seat => {
                                        if (seat && seat.taken && seat.seat) {
                                            this.occupiedSeats.push(seat.seat);
                                        }
                                    });
                                }
                            });
                        } else if (response && response.seats && Array.isArray(response.seats)) {
                            // 备选格式1
                            response.seats.forEach(seat => {
                                if (seat && seat.occupied) {
                                    this.occupiedSeats.push(seat.id || `${seat.row}${seat.column}`);
                                }
                            });
                        } else if (response && response.occupied_seats && Array.isArray(response.occupied_seats)) {
                            // 备选格式2
                            this.occupiedSeats = [...response.occupied_seats];
                        } else if (response && response.data) {
                            // 尝试从response.data中获取座位数据
                            const data = response.data;

                            if (data.seat_map && Array.isArray(data.seat_map)) {
                                // 标准格式
                                data.seat_map.forEach(row => {
                                    if (Array.isArray(row)) {
                                        row.forEach(seat => {
                                            if (seat && seat.taken && seat.seat) {
                                                this.occupiedSeats.push(seat.seat);
                                            }
                                        });
                                    }
                                });
                            } else if (data.seats && Array.isArray(data.seats)) {
                                // 备选格式1
                                data.seats.forEach(seat => {
                                    if (seat && seat.occupied) {
                                        this.occupiedSeats.push(seat.id || `${seat.row}${seat.column}`);
                                    }
                                });
                            } else if (data.occupied_seats && Array.isArray(data.occupied_seats)) {
                                // 备选格式2
                                this.occupiedSeats = [...data.occupied_seats];
                            } else {
                                console.warn('返回的座位数据格式不匹配任何预期格式，使用随机座位', response);
                                this.generateRandomOccupiedSeats();
                                return;
                            }
                        } else {
                            console.warn('返回的座位数据格式不匹配任何预期格式，使用随机座位', response);
                            this.generateRandomOccupiedSeats();
                            return;
                        }

                        console.log('已加载座位图，占用座位:', this.occupiedSeats);
                    } catch (err) {
                        console.error('解析座位数据出错', err);
                        this.generateRandomOccupiedSeats();
                    }
                })
                .catch(error => {
                    console.error('获取座位信息失败', error);
                    this.$message.warning('获取座位信息失败，将使用默认座位布局');
                    this.generateRandomOccupiedSeats(); // 使用随机座位作为后备
                });
        },

        // 生成随机占用座位（作为API调用失败的后备方案）
        generateRandomOccupiedSeats() {
            // 模拟一些已占用的座位
            const totalSeats = this.rows.length * this.columns.length;
            const occupiedCount = Math.round(totalSeats * 0.7); // 假设70%的座位已被占用

            this.occupiedSeats = [];
            for (let i = 0; i < occupiedCount; i++) {
                const row = this.rows[Math.floor(Math.random() * this.rows.length)];
                const colIndex = Math.floor(Math.random() * this.columns.length);
                const col = this.columns[colIndex];
                const seat = `${row}${col}`;

                if (!this.occupiedSeats.includes(seat)) {
                    this.occupiedSeats.push(seat);
                }
            }
        },

        formatDate(date) {
            if (!date) return '未知日期';
            try {
                // 处理字符串格式的日期
                if (typeof date === 'string') {
                    const d = new Date(date);
                    // 检查日期是否有效
                    if (isNaN(d.getTime())) {
                        return '未知日期';
                    }
                    return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, '0')}-${d.getDate().toString().padStart(2, '0')}`;
                }

                // 处理Date对象
                if (date instanceof Date) {
                    // 检查日期是否有效
                    if (isNaN(date.getTime())) {
                        return '未知日期';
                    }
                    return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
                }

                return '未知日期';
            } catch (e) {
                console.error('日期格式化错误:', e);
                return '未知日期';
            }
        },

        formatTime(date) {
            if (!date) return '--:--';
            try {
                const d = new Date(date);
                // 检查日期是否有效
                if (isNaN(d.getTime())) {
                    return '--:--';
                }
                return `${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
            } catch (e) {
                console.error('时间格式化错误:', e);
                return '--:--';
            }
        },

        formatDuration(minutes) {
            if (!minutes || isNaN(minutes)) return '0小时';
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return `${hours}小时${mins > 0 ? ` ${mins}分钟` : ''}`;
        },

        getIdTypeLabel(idType) {
            const idTypeMap = {
                'idcard': '身份证',
                'passport': '护照',
                'military': '军官证'
            };
            return idTypeMap[idType] || '身份证';
        },

        validateIdNumber(rule, value, callback) {
            if (!value) {
                callback(new Error('请输入证件号码'));
                return;
            }

            const passenger = this.passengers.find(p => p.idNumber === value);
            const idType = passenger ? passenger.idType : '';

            if (idType === 'idcard') {
                // 简单的身份证号码验证
                if (!/^\d{17}[\dXx]$/.test(value)) {
                    callback(new Error('请输入正确的身份证号码'));
                    return;
                }
            } else if (idType === 'passport') {
                // 简单的护照号码验证
                if (!/^[A-Z0-9]{6,9}$/.test(value)) {
                    callback(new Error('请输入正确的护照号码'));
                    return;
                }
            }

            callback();
        },

        validateAndNextStep() {
            const passengerValidation = this.$refs.passengerList.validateAllPassengers();
            const contactValidation = this.$refs.contactForm.validate();

            Promise.all([passengerValidation, contactValidation])
                .then(([passengersValid, contactData]) => {
                    if (passengersValid) {
                        this.contactInfo = contactData;
                        this.nextStep();
                    } else {
                        this.$message.error('请完成所有乘客信息');
                    }
                })
                .catch(error => {
                    this.$message.error(error || '请完成所有必填信息');
                });
        },

        updatePassenger(passenger, index) {
            this.passengers.splice(index, 1, passenger);
            this.checkPassengersComplete();
        },

        useExistingPassenger(/* index */) {
            // 从本地存储获取已保存的乘客信息
            const savedPassengers = JSON.parse(localStorage.getItem('savedPassengers') || '[]');

            if (savedPassengers.length === 0) {
                this.$message.warning('没有已保存的乘客信息');
                return;
            }

            this.openPassengerSelectionDialog(savedPassengers);
        },

        // 打开乘客选择对话框
        openPassengerSelectionDialog(savedPassengers) {
            this.selectedPassengerIds = []; // 初始化选中的乘客ID列表

            // 使用HTML字符串创建对话框
            this.$msgbox({
                title: '选择乘客',
                message: this.generatePassengerSelectionHTML(savedPassengers),
                dangerouslyUseHTMLString: true,
                customClass: 'passenger-selector-dialog',
                showCancelButton: true,
                confirmButtonText: '确定',
                cancelButtonText: '取消',
                beforeClose: (action, instance, done) => {
                    if (action === 'confirm') {
                        // 获取选中的乘客ID
                        const selectedIds = this.selectedPassengerIds;
                        if (selectedIds.length === 0) {
                            this.$message.warning('请至少选择一位乘客');
                            return;
                        }

                        // 应用选择的乘客信息
                        this.applySelectedPassengers(savedPassengers, selectedIds);
                        done();
                    } else {
                        // 取消选择，移除事件监听器
                        document.removeEventListener('passenger-checkbox-change', this.handlePassengerCheckboxChange);
                        done();
                    }
                }
            }).then(() => {
                // 成功选择，已在beforeClose中处理
                document.removeEventListener('passenger-checkbox-change', this.handlePassengerCheckboxChange);
            }).catch(() => {
                // 取消选择，移除事件监听器
                document.removeEventListener('passenger-checkbox-change', this.handlePassengerCheckboxChange);
            });
        },

        // 生成乘客选择HTML
        generatePassengerSelectionHTML(savedPassengers) {
            let html = '<div class="saved-passengers-selection">';

            // 添加提示信息
            html += '<div class="selection-help-text">可以选择多位乘客，一次性添加</div>';

            // 生成每个乘客的选择项
            savedPassengers.forEach((passenger, idx) => {
                html += `
                <div class="saved-passenger-item">
                    <input type="checkbox" id="passenger-${idx}" class="passenger-checkbox" 
                           data-idx="${idx}" onclick="document.dispatchEvent(new CustomEvent('passenger-checkbox-change', {detail: {idx: ${idx}, checked: this.checked}}))">
                    <div class="saved-passenger-info">
                        <div class="saved-passenger-name">${passenger.name}</div>
                        <div>
                            <span>${this.getIdTypeLabel(passenger.idType)}: ${passenger.idNumber}</span>
                            <span class="passenger-gender">${passenger.gender === 'male' ? '男' : '女'}</span>
                        </div>
                    </div>
                </div>`;
            });

            html += '</div>';

            // 添加事件监听器
            setTimeout(() => {
                document.addEventListener('passenger-checkbox-change', this.handlePassengerCheckboxChange);
            }, 100);

            return html;
        },

        // 处理乘客复选框变化事件
        handlePassengerCheckboxChange(event) {
            const { idx, checked } = event.detail;

            if (checked) {
                // 添加选中的乘客ID
                if (!this.selectedPassengerIds.includes(idx)) {
                    this.selectedPassengerIds.push(idx);
                }
            } else {
                // 移除取消选中的乘客ID
                const index = this.selectedPassengerIds.indexOf(idx);
                if (index > -1) {
                    this.selectedPassengerIds.splice(index, 1);
                }
            }
        },

        // 应用已选择的乘客
        applySelectedPassengers(savedPassengers, selectedIds) {
            if (selectedIds.length === 0) return;

            // 获取选中的乘客信息
            const selectedPassengers = selectedIds.map(idx => savedPassengers[idx]);

            // 更新当前乘客列表
            for (let i = 0; i < selectedPassengers.length; i++) {
                if (i < this.passengers.length) {
                    // 更新已存在的乘客位置
                    const updatedPassenger = {
                        ...selectedPassengers[i],
                        isComplete: true
                    };
                    this.updatePassenger(updatedPassenger, i);
                }
            }

            this.$message.success(`已应用${selectedPassengers.length}位乘客信息`);
        },

        checkPassengersComplete() {
            // 检查所有乘客信息是否已完成
            const allComplete = this.passengers.every(p => p.isComplete);
            if (allComplete) {
                // 可以做一些UI提示或者其他操作
            }
        },

        getSeatClass(row, col) {
            const seatId = `${row}${col}`;
            if (this.selectedSeats.includes(seatId)) {
                return 'selected';
            }
            if (this.occupiedSeats.includes(seatId)) {
                return 'occupied';
            }
            return 'available';
        },

        toggleSeat(row, col) {
            const seatId = `${row}${col}`;

            // 如果座位已被占用，不做任何操作
            if (this.occupiedSeats.includes(seatId)) {
                return;
            }

            const seatIndex = this.selectedSeats.indexOf(seatId);

            if (seatIndex > -1) {
                // 取消选择
                this.selectedSeats.splice(seatIndex, 1);
            } else {
                // 如果已选座位数量已达到乘客数量，替换最早选择的座位
                if (this.selectedSeats.length >= this.passengerCount) {
                    this.selectedSeats.shift();
                }
                // 添加新选择的座位
                this.selectedSeats.push(seatId);
            }
        },

        removeSeat(index) {
            if (index >= 0 && index < this.selectedSeats.length) {
                this.selectedSeats.splice(index, 1);
            }
        },

        submitOrder() {
            if (this.isSubmitting) {
                return;
            }
            this.isSubmitting = true;

            // 检查用户是否已登录
            const token = localStorage.getItem('token');
            if (!token) {
                this.isSubmitting = false;
                this.$message.error('请先登录后再提交订单');

                // 提示用户登录并保存当前页面状态
                this.$confirm('您需要登录才能提交订单，是否立即登录?', '未登录', {
                    confirmButtonText: '去登录',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    // 保存当前页面状态
                    sessionStorage.setItem('bookingState', JSON.stringify({
                        flightId: this.flight.id,
                        cabinClass: this.cabinClass,
                        passengerCount: this.passengerCount,
                        selectedSeats: this.selectedSeats,
                        passengers: this.passengers,
                        contactInfo: this.contactInfo,
                        paymentMethod: this.paymentMethod
                    }));

                    // 跳转到登录页面，并设置登录后返回当前页面
                    this.$router.push({
                        path: '/login',
                        query: { redirect: this.$route.fullPath }
                    });
                }).catch(() => {
                    this.$message.info('已取消提交订单');
                });
                return;
            }

            // 构建订单数据
            const orderData = {
                flight_id: this.flight.id,
                cabin_class: this.cabinClass,
                seat_numbers: this.selectedSeats,
                passengers: this.passengers.map((p, idx) => ({
                    name: p.name,
                    gender: p.gender,
                    id_type: p.idType,
                    id_number: p.idNumber,
                    // 确保日期格式正确 (YYYY-MM-DD)
                    birth_date: this.formatStandardDate(p.birthDate),
                    phone: p.phone,
                    seat_number: this.selectedSeats[idx]
                })),
                contact_info: {
                    name: this.contactInfo.name,
                    phone: this.contactInfo.phone,
                    email: this.contactInfo.email
                },
                payment_method: this.paymentMethod,
                // 确保所有价格字段都转换为字符串
                total_price: String(parseFloat(this.totalPrice)),
                cabin_price: String(parseFloat(this.cabinPrice)),
                base_price: String(parseFloat(this.flight.price || 0)),
                discount: String(parseFloat(this.flight.discount || 1))
            };

            // 数据有效性验证
            let isValid = true;
            const errors = [];

            if (!orderData.flight_id) {
                isValid = false;
                errors.push("航班ID缺失");
            }

            if (!orderData.passengers || orderData.passengers.length === 0) {
                isValid = false;
                errors.push("乘客信息缺失");
            } else {
                // 检查乘客数据
                orderData.passengers.forEach((passenger, index) => {
                    if (!passenger.name || !passenger.id_number) {
                        isValid = false;
                        errors.push(`乘客 ${index + 1} 信息不完整`);
                    }
                });
            }

            if (!orderData.seat_numbers || orderData.seat_numbers.length !== orderData.passengers.length) {
                isValid = false;
                errors.push("座位数量与乘客数量不匹配");
            }

            if (!isValid) {
                this.isSubmitting = false;
                const errorMsg = `提交数据验证失败: ${errors.join(', ')}`;
                console.error(errorMsg);
                this.$message.error(errorMsg);
                return;
            }

            // 记录调试信息
            console.log('提交订单数据:', JSON.stringify(orderData));

            // 提交订单
            api.orders.create(orderData)
                .then(response => {
                    this.isSubmitting = false;
                    console.log('订单提交成功:', response);
                    this.orderNumber = response.order_number || response.data?.order_number;
                    this.orderSuccessVisible = true;

                    // 保存乘客信息到本地存储
                    this.savePassengersToLocalStorage();
                })
                .catch(error => {
                    this.isSubmitting = false;
                    console.error('订单提交失败', error);

                    // 获取更详细的错误信息
                    let errorMessage = '订单提交失败，请稍后重试';
                    if (error.response) {
                        // 服务器返回了错误响应
                        const status = error.response.status;
                        const data = error.response.data;

                        // 记录完整的错误响应以便调试
                        console.log('错误响应状态:', status);
                        console.log('错误响应数据:', data);

                        if (status === 401) {
                            errorMessage = '您的登录已过期，请重新登录';
                            // 清除无效的token
                            localStorage.removeItem('token');

                            // 提示用户重新登录
                            this.$confirm('您的登录已过期，需要重新登录才能提交订单，是否立即登录?', '登录已过期', {
                                confirmButtonText: '去登录',
                                cancelButtonText: '取消',
                                type: 'warning'
                            }).then(() => {
                                // 保存当前页面状态
                                sessionStorage.setItem('bookingState', JSON.stringify({
                                    flightId: this.flight.id,
                                    cabinClass: this.cabinClass,
                                    passengerCount: this.passengerCount,
                                    selectedSeats: this.selectedSeats,
                                    passengers: this.passengers,
                                    contactInfo: this.contactInfo,
                                    paymentMethod: this.paymentMethod
                                }));

                                // 跳转到登录页面
                                this.$router.push({
                                    path: '/login',
                                    query: { redirect: this.$route.fullPath }
                                });
                            }).catch(() => {
                                this.$message.info('已取消提交订单');
                            });
                            return;
                        } else if (status === 500) {
                            errorMessage = '服务器内部错误，请联系客服或稍后再试';
                        } else if (data && data.detail) {
                            errorMessage = `订单提交失败: ${data.detail}`;
                        } else if (data && data.message) {
                            errorMessage = `订单提交失败: ${data.message}`;
                        } else if (data && typeof data === 'string') {
                            errorMessage = `订单提交失败: ${data}`;
                        }

                        // 针对常见错误给出更具体的提示
                        if (error.response.status === 400) {
                            // 尝试解析所有错误字段
                            if (typeof data === 'object') {
                                const errorDetails = [];
                                for (const key in data) {
                                    if (Array.isArray(data[key])) {
                                        errorDetails.push(`${key}: ${data[key].join(', ')}`);
                                    } else if (typeof data[key] === 'string') {
                                        errorDetails.push(`${key}: ${data[key]}`);
                                    } else if (data[key] !== null && typeof data[key] === 'object') {
                                        // 处理嵌套对象
                                        for (const nestedKey in data[key]) {
                                            errorDetails.push(`${key}.${nestedKey}: ${data[key][nestedKey]}`);
                                        }
                                    }
                                }

                                if (errorDetails.length > 0) {
                                    errorMessage = `请求数据错误: ${errorDetails.join('; ')}`;
                                }
                            }
                        }
                    }

                    this.$message.error(errorMessage);

                    // 如果是API连接问题，提供重试选项
                    if (error.message === 'Network Error' || error.code === 'ECONNABORTED') {
                        this.$confirm('网络连接错误，是否重试?', '提交失败', {
                            confirmButtonText: '重试',
                            cancelButtonText: '取消',
                            type: 'warning'
                        }).then(() => {
                            this.submitOrder(); // 重试提交
                        }).catch(() => {
                            this.$message.info('已取消重试');
                        });
                    }
                });
        },

        // 保存乘客信息到本地存储
        savePassengersToLocalStorage() {
            try {
                // 获取已保存的乘客
                const existingPassengers = JSON.parse(localStorage.getItem('savedPassengers') || '[]');

                // 合并并去重
                const allPassengers = [...existingPassengers];
                this.passengers.forEach(newP => {
                    if (!allPassengers.some(p => p.idNumber === newP.idNumber)) {
                        allPassengers.push({
                            name: newP.name,
                            gender: newP.gender,
                            idType: newP.idType,
                            idNumber: newP.idNumber,
                            birthDate: newP.birthDate,
                            phone: newP.phone
                        });
                    }
                });

                // 保存到本地存储
                localStorage.setItem('savedPassengers', JSON.stringify(allPassengers));
            } catch (e) {
                console.error('保存乘客信息失败', e);
            }
        },

        goToOrderDetail() {
            this.$router.push({
                name: 'orderDetail',
                params: { orderId: this.orderNumber }
            });
        },

        goToHome() {
            this.$router.push('/');
        },

        goBack() {
            this.$router.go(-1);
        },

        prevStep() {
            if (this.currentStep > 0) {
                this.currentStep--;
            }
        },

        nextStep() {
            if (this.currentStep < 3) {
                this.currentStep++;
            }
        },

        formatStandardDate(date) {
            if (!date) return '';
            try {
                // 处理字符串格式的日期
                if (typeof date === 'string') {
                    // 如果已经是YYYY-MM-DD格式，直接返回
                    if (/^\d{4}-\d{2}-\d{2}$/.test(date)) {
                        return date;
                    }

                    // 尝试解析其他格式的日期字符串
                    const d = new Date(date);
                    if (!isNaN(d.getTime())) {
                        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
                    }
                }

                // 处理Date对象
                if (date instanceof Date) {
                    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
                }

                console.warn('无法格式化日期:', date);
                return '';
            } catch (e) {
                console.error('日期格式化错误:', e);
                return '';
            }
        }
    }
}
</script>

<style scoped>
.booking-view {
    padding: 20px;
    min-height: 100vh;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.booking-header {
    background: linear-gradient(135deg, #00468c, #0076c6);
    color: white;
    padding: 30px;
    text-align: center;
    margin-bottom: 30px;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.booking-header h1 {
    margin: 0;
    font-size: 28px;
    font-weight: 600;
}

.booking-header p {
    margin: 10px 0 20px;
    font-size: 16px;
    opacity: 0.9;
}

.steps-container {
    max-width: 800px;
    margin: 0 auto;
    padding-top: 20px;
}

.booking-container {
    max-width: 1000px;
    margin: 0 auto;
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
    margin-bottom: 40px;
}

.loading-container {
    text-align: center;
    padding: 40px 0;
}

.loading-animation {
    display: inline-block;
    width: 80px;
    height: 80px;
    position: relative;
    margin-bottom: 20px;
}

.loading-plane {
    position: absolute;
    width: 60px;
    height: 60px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%230076c6"><path d="M22,16.5L12,7.5L2,16.5H5L12,10.5L19,16.5H22Z"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
    animation: loading-plane-anim 1.5s infinite ease-in-out;
}

@keyframes loading-plane-anim {
    0% {
        transform: translateY(0) rotate(0);
    }

    50% {
        transform: translateY(-15px) rotate(5deg);
    }

    100% {
        transform: translateY(0) rotate(0);
    }
}

.section-title {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.section-title h2 {
    margin: 0;
    font-size: 22px;
    color: #333;
}

.flight-detail-card {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}

.flight-detail-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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

.airline-logo {
    width: 40px;
    height: 40px;
    background-size: cover;
    border-radius: 50%;
    margin-right: 10px;
}

.airline-name {
    font-weight: 600;
    color: #333;
}

.flight-number {
    color: #666;
    font-size: 14px;
}

.cabin-badge {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
}

.cabin-badge.economy {
    background-color: #e8f5e9;
    color: #43a047;
}

.cabin-badge.business {
    background-color: #e3f2fd;
    color: #1976d2;
}

.cabin-badge.first {
    background-color: #fff8e1;
    color: #ffb300;
}

.flight-main-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
}

.flight-route {
    display: flex;
    align-items: center;
    flex: 1;
}

.departure,
.arrival {
    text-align: center;
    padding: 0 10px;
}

.city {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 5px;
}

.time {
    font-size: 24px;
    font-weight: 700;
    color: #0076c6;
    margin-bottom: 5px;
}

.airport {
    font-size: 14px;
    color: #666;
}

.flight-duration {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0 20px;
}

.duration-line {
    position: relative;
    width: 100px;
    height: 2px;
    background-color: #ddd;
    margin: 15px 0 5px;
}

.plane-icon {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 20px;
    height: 20px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%230076c6"><path d="M21,16.5C21,16.88 20.79,17.21 20.47,17.38L12.57,21.82C12.41,21.94 12.21,22 12,22C11.79,22 11.59,21.94 11.43,21.82L3.53,17.38C3.21,17.21 3,16.88 3,16.5V7.5C3,7.12 3.21,6.79 3.53,6.62L11.43,2.18C11.59,2.06 11.79,2 12,2C12.21,2 12.41,2.06 12.57,2.18L20.47,6.62C20.79,6.79 21,7.12 21,7.5V16.5M12,4.15L5,8.09V15.91L12,19.85L19,15.91V8.09L12,4.15Z"/></svg>');
    background-size: contain;
    background-repeat: no-repeat;
}

.duration-text {
    font-size: 14px;
    color: #666;
}

.flight-price {
    display: flex;
    align-items: baseline;
    padding: 10px 0;
}

.price-label {
    font-size: 14px;
    color: #666;
    margin-right: 5px;
}

.price-amount {
    font-size: 24px;
    font-weight: 700;
    color: #f44336;
}

.price-unit {
    font-size: 14px;
    color: #666;
    margin-left: 5px;
}

.flight-details {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    padding-top: 15px;
    border-top: 1px dashed #ddd;
}

.detail-item {
    display: flex;
    align-items: center;
    color: #666;
    font-size: 14px;
}

.detail-item i {
    margin-right: 5px;
    color: #0076c6;
}

.section-action {
    display: flex;
    justify-content: flex-end;
    margin-top: 30px;
}

.passenger-count {
    display: inline-block;
    padding: 5px 10px;
    background-color: #f5f5f5;
    border-radius: 4px;
    font-size: 14px;
    color: #666;
}

.passengers-container {
    margin-bottom: 30px;
}

.form-actions {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
}

.contact-info-section {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
    margin-top: 30px;
}

.section-desc {
    font-size: 14px;
    color: #666;
    margin-bottom: 20px;
}

.seat-selection-container {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 20px;
}

.seat-map-legend {
    display: flex;
    justify-content: center;
    gap: 20px;
    margin-bottom: 20px;
}

.legend-item {
    display: flex;
    align-items: center;
}

.seat-icon {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    margin-right: 8px;
}

.seat-icon.available {
    background-color: #fff;
    border: 1px solid #ddd;
}

.seat-icon.selected {
    background-color: #0076c6;
    border: 1px solid #0076c6;
}

.seat-icon.occupied {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    position: relative;
}

.seat-icon.occupied::after {
    content: "×";
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: #999;
    font-size: 18px;
}

.aircraft-cabin {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}

.cabin-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.cabin-exit {
    padding: 3px 8px;
    background-color: #ffebee;
    color: #e53935;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
}

.cabin-name {
    font-size: 18px;
    font-weight: 600;
    color: #333;
}

.seat-map {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.aisle-label {
    display: flex;
    margin-bottom: 10px;
}

.aisle-label span {
    width: 30px;
    height: 30px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 600;
    color: #666;
}

.seat-row {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.row-label {
    width: 30px;
    height: 30px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-weight: 600;
    color: #666;
    margin-right: 10px;
}

.row-seats {
    display: flex;
}

.seat {
    width: 30px;
    height: 30px;
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 4px;
    margin: 0 2px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.seat.available {
    background-color: white;
    border: 1px solid #ddd;
    color: #666;
}

.seat.available:hover {
    background-color: #e3f2fd;
    border-color: #0076c6;
}

.seat.selected {
    background-color: #0076c6;
    border: 1px solid #0076c6;
    color: white;
}

.seat.occupied {
    background-color: #f5f5f5;
    border: 1px solid #ddd;
    color: #999;
    cursor: not-allowed;
    position: relative;
}

.seat.occupied::after {
    content: "×";
    position: absolute;
    font-size: 18px;
}

.aisle {
    width: 15px;
}

.selected-seats-summary {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    margin-top: 20px;
}

.selected-seats-summary h3 {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 18px;
    color: #333;
}

.seats-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.seat-assignment {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background-color: #f5f5f5;
    border-radius: 4px;
}

.passenger-name {
    font-weight: 500;
}

.seat-number {
    font-weight: 600;
    color: #0076c6;
    padding: 2px 8px;
    background-color: #e3f2fd;
    border-radius: 4px;
}

.no-seats-selected {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    color: #999;
}

.no-seats-selected i {
    margin-right: 5px;
}

.order-summary {
    margin-bottom: 30px;
}

.summary-card {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.summary-flight {
    padding-bottom: 15px;
    margin-bottom: 15px;
    border-bottom: 1px dashed #ddd;
}

.summary-route {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 5px;
}

.summary-date {
    color: #666;
    margin-bottom: 5px;
}

.summary-time {
    font-weight: 500;
    color: #0076c6;
    margin-bottom: 5px;
}

.summary-flight-number {
    color: #666;
    font-size: 14px;
}

.summary-passengers h4,
.summary-contact h4 {
    font-size: 16px;
    margin: 15px 0 10px;
}

.summary-passenger {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background-color: #f5f5f5;
    border-radius: 4px;
    margin-bottom: 10px;
}

.passenger-details {
    display: flex;
    flex-direction: column;
}

.passenger-id {
    font-size: 14px;
    color: #666;
}

.passenger-seat {
    font-weight: 500;
    color: #0076c6;
}

.contact-details {
    display: flex;
    flex-direction: column;
    gap: 5px;
    color: #666;
}

.price-breakdown {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.price-item {
    display: flex;
    justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid #eee;
}

.price-total {
    display: flex;
    justify-content: space-between;
    padding: 15px 0 5px;
    font-weight: 600;
}

.total-amount {
    font-size: 20px;
    color: #f44336;
}

.payment-options {
    background-color: white;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.payment-options h3 {
    margin-top: 0;
    margin-bottom: 15px;
}

.payment-option {
    display: flex;
    align-items: center;
    gap: 10px;
    margin: 10px 0;
}

.payment-option img {
    border-radius: 4px;
}

.payment-agreement {
    margin-top: 20px;
    display: flex;
    align-items: center;
    gap: 5px;
}

.success-dialog {
    text-align: center;
}

.success-icon {
    font-size: 60px;
    color: #4caf50;
    margin-bottom: 20px;
}

.success-dialog h2 {
    margin-bottom: 10px;
}

.dialog-footer {
    margin-top: 20px;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
    .booking-container {
        padding: 15px;
    }

    .flight-main-info {
        flex-direction: column;
    }

    .flight-price {
        margin-top: 15px;
        justify-content: center;
    }

    .seat-map {
        overflow-x: auto;
        width: 100%;
    }

    .summary-passenger {
        flex-direction: column;
        gap: 10px;
    }
}

/* 乘客选择样式 */
.saved-passengers-selection {
    max-height: 400px;
    overflow-y: auto;
    padding: 10px 0;
}

.selection-help-text {
    color: #606266;
    font-size: 14px;
    margin-bottom: 15px;
    padding: 8px 12px;
    background-color: #f0f9eb;
    border-radius: 4px;
}

.saved-passenger-item {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding: 12px 15px;
    border-radius: 4px;
    border-bottom: 1px solid #eee;
}

.saved-passenger-item:hover {
    background-color: #f5f9ff;
}

.passenger-checkbox {
    margin-right: 15px;
    width: 18px;
    height: 18px;
    cursor: pointer;
}

.saved-passenger-info {
    margin-left: 10px;
    flex-grow: 1;
}

.passenger-gender {
    margin-left: 15px;
}

/* 已保存乘客选择对话框 */
.passenger-selector-dialog .el-message-box__message {
    padding: 0;
    margin: 0;
}

.saved-passengers-list {
    max-height: 300px;
    overflow-y: auto;
}

/* 多选乘客样式 */
.saved-passengers-selection {
    max-height: 400px;
    overflow-y: auto;
    padding: 10px 0;
}

.selection-help-text {
    color: #606266;
    font-size: 14px;
    margin-bottom: 15px;
    padding: 8px 12px;
    background-color: #f0f9eb;
    border-radius: 4px;
}

.saved-passenger-item {
    display: flex;
    align-items: center;
    padding: 12px 15px;
    border-bottom: 1px solid #eee;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.saved-passenger-item:hover {
    background-color: #f5f9ff;
}

.saved-passenger-item:last-child {
    border-bottom: none;
}

.saved-passenger-name {
    font-size: 16px;
    font-weight: 500;
    margin-bottom: 5px;
}

.saved-passenger-info {
    display: flex;
    flex: 1;
    margin-left: 15px;
    justify-content: space-between;
    font-size: 14px;
    color: #666;
}

.passenger-gender {
    margin-left: 15px;
}
</style>