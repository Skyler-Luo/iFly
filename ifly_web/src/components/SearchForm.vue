<template>
    <div class="search-box">
        <!-- 顶部标签栏 -->
        <div class="tab-header">
            <button 
                :class="['tab-btn', { active: activeTab === 'search' }]"
                @click="activeTab = 'search'"
            >航班搜索</button>
            <button 
                :class="['tab-btn', { active: activeTab === 'checkin' }]"
                @click="activeTab = 'checkin'"
            >选座值机</button>
            <button 
                :class="['tab-btn', { active: activeTab === 'status' }]"
                @click="activeTab = 'status'"
            >航班动态</button>
        </div>

        <!-- 搜索表单内容 -->
        <div class="search-content" v-show="activeTab === 'search'">
            <!-- 行程类型 -->
            <div class="trip-type-row">
                <label class="trip-radio" :class="{ active: searchForm.tripType === 'oneway' }">
                    <input type="radio" v-model="searchForm.tripType" value="oneway" />
                    <span class="radio-dot"></span>
                    <span>单程</span>
                </label>
                <label class="trip-radio" :class="{ active: searchForm.tripType === 'roundtrip' }">
                    <input type="radio" v-model="searchForm.tripType" value="roundtrip" />
                    <span class="radio-dot"></span>
                    <span>往返</span>
                </label>
            </div>

            <!-- 主搜索行 -->
            <div class="main-search-row">
                <!-- 出发城市 -->
                <div class="field-group city-group">
                    <label class="field-label">出发</label>
                    <div class="field-input">
                        <i class="field-icon">📍</i>
                        <el-select 
                            v-model="searchForm.departureCity" 
                            placeholder="选择出发城市" 
                            filterable
                            class="city-select"
                        >
                            <el-option 
                                v-for="(cityItem, index) in cities" 
                                :key="'dep-' + index"
                                :label="getCityName(cityItem)" 
                                :value="getCityName(cityItem)" 
                            />
                        </el-select>
                    </div>
                </div>

                <!-- 交换按钮 -->
                <div class="swap-btn" @click="swapCities">
                    <span>⇄</span>
                </div>

                <!-- 目的城市 -->
                <div class="field-group city-group">
                    <label class="field-label">到达</label>
                    <div class="field-input">
                        <i class="field-icon">📍</i>
                        <el-select 
                            v-model="searchForm.arrivalCity" 
                            placeholder="选择目的城市" 
                            filterable
                            class="city-select"
                        >
                            <el-option 
                                v-for="(cityItem, index) in cities" 
                                :key="'arr-' + index"
                                :label="getCityName(cityItem)" 
                                :value="getCityName(cityItem)" 
                            />
                        </el-select>
                    </div>
                </div>

                <!-- 分隔线 -->
                <div class="field-divider"></div>

                <!-- 出发日期 -->
                <div class="field-group date-group">
                    <label class="field-label">出发</label>
                    <div class="field-input">
                        <i class="field-icon">📅</i>
                        <el-date-picker 
                            v-model="searchForm.departureDate" 
                            type="date" 
                            placeholder="选择日期"
                            format="YYYY-MM-DD"
                            value-format="YYYY-MM-DD"
                            :disabled-date="disabledDate"
                            class="date-picker"
                        />
                    </div>
                </div>

                <!-- 返程日期 -->
                <div class="field-group date-group" v-if="searchForm.tripType === 'roundtrip'">
                    <label class="field-label">返程</label>
                    <div class="field-input">
                        <i class="field-icon">📅</i>
                        <el-date-picker 
                            v-model="searchForm.returnDate" 
                            type="date" 
                            placeholder="选择日期"
                            format="YYYY-MM-DD"
                            value-format="YYYY-MM-DD"
                            :disabled-date="disabledReturnDate"
                            class="date-picker"
                        />
                    </div>
                </div>

                <!-- 搜索按钮 -->
                <button class="search-btn" @click="searchFlights">
                    搜索
                </button>
            </div>
        </div>

        <!-- 选座值机内容 -->
        <div class="search-content" v-show="activeTab === 'checkin'">
            <div class="checkin-form">
                <div class="checkin-row">
                    <!-- 姓名 -->
                    <div class="field-group checkin-field">
                        <label class="field-label"><span class="required">*</span> 姓名 <span class="field-hint">请输入与证件相同的姓名，如：张三/MING</span></label>
                        <div class="field-input">
                            <i class="field-icon">👤</i>
                            <el-input 
                                v-model="checkinForm.passengerName" 
                                placeholder="请输入订票时的姓名"
                                class="checkin-input"
                            />
                        </div>
                    </div>
                    <!-- 证件号 -->
                    <div class="field-group checkin-field">
                        <label class="field-label"><span class="required">*</span> 证件号</label>
                        <div class="field-input">
                            <i class="field-icon">🪪</i>
                            <el-input 
                                v-model="checkinForm.idNumber" 
                                placeholder="请输入购票证件号"
                                class="checkin-input"
                            />
                        </div>
                    </div>
                    <!-- 票号 -->
                    <div class="field-group checkin-field">
                        <label class="field-label"><span class="required">*</span> 票号</label>
                        <div class="field-input">
                            <i class="field-icon">🎫</i>
                            <el-input 
                                v-model="checkinForm.ticketNumber" 
                                placeholder="请输入机票票号（13位数字）"
                                class="checkin-input"
                            />
                        </div>
                    </div>
                </div>
                <div class="checkin-row">
                    <!-- 航班号 -->
                    <div class="field-group checkin-field small">
                        <label class="field-label"><span class="required">*</span> 航班号</label>
                        <div class="field-input">
                            <i class="field-icon">✈️</i>
                            <el-input 
                                v-model="checkinForm.flightNumber" 
                                placeholder="如CA5101"
                                class="checkin-input"
                            />
                        </div>
                    </div>
                    <!-- 手机号码 -->
                    <div class="field-group checkin-field">
                        <label class="field-label"><span class="required">*</span> 手机号码</label>
                        <div class="field-input phone-input">
                            <span class="phone-prefix">+86</span>
                            <el-input 
                                v-model="checkinForm.phone" 
                                placeholder="请输入订票手机号"
                                class="checkin-input"
                            />
                        </div>
                    </div>
                    <!-- 查询按钮 -->
                    <button class="search-btn checkin-btn" @click="handleCheckin">
                        查 询
                    </button>
                </div>
                <div class="checkin-agreement">
                    <el-checkbox v-model="checkinForm.agreed">阅读并同意</el-checkbox>
                    <a href="#" class="agreement-link">《选座须知》</a>
                    <span>及</span>
                    <a href="#" class="agreement-link">《登机牌办理须知》</a>
                </div>
            </div>
        </div>

        <!-- 航班动态内容 -->
        <div class="search-content" v-show="activeTab === 'status'">
            <div class="status-form">
                <!-- 查询方式切换 -->
                <div class="trip-type-row">
                    <label class="trip-radio" :class="{ active: statusForm.queryType === 'flightNo' }">
                        <input type="radio" v-model="statusForm.queryType" value="flightNo" />
                        <span class="radio-dot"></span>
                        <span>航班号</span>
                    </label>
                    <label class="trip-radio" :class="{ active: statusForm.queryType === 'route' }">
                        <input type="radio" v-model="statusForm.queryType" value="route" />
                        <span class="radio-dot"></span>
                        <span>出发/到达城市</span>
                    </label>
                </div>

                <!-- 按航班号查询 -->
                <div class="main-search-row" v-if="statusForm.queryType === 'flightNo'">
                    <div class="field-group">
                        <label class="field-label">航班号</label>
                        <div class="field-input">
                            <i class="field-icon">✈️</i>
                            <el-input 
                                v-model="statusForm.flightNumber" 
                                placeholder="例如：MU565或565"
                                class="status-input"
                            />
                        </div>
                    </div>
                    <div class="field-group date-group">
                        <label class="field-label">日期 <span class="field-hint">（离港/到港日期月期）</span></label>
                        <div class="field-input">
                            <i class="field-icon">📅</i>
                            <el-date-picker 
                                v-model="statusForm.flightDate" 
                                type="date" 
                                placeholder="选择日期"
                                format="YYYY-MM-DD"
                                value-format="YYYY-MM-DD"
                                class="date-picker"
                            />
                        </div>
                    </div>
                    <button class="search-btn" @click="queryFlightStatus">
                        搜索
                    </button>
                </div>

                <!-- 按出发/到达城市查询 -->
                <div class="main-search-row" v-else>
                    <div class="field-group city-group">
                        <label class="field-label">出发城市</label>
                        <div class="field-input">
                            <i class="field-icon">📍</i>
                            <el-select 
                                v-model="statusForm.departureCity" 
                                placeholder="选择出发城市" 
                                filterable
                                class="city-select"
                            >
                                <el-option 
                                    v-for="(cityItem, index) in cities" 
                                    :key="'status-dep-' + index"
                                    :label="getCityName(cityItem)" 
                                    :value="getCityName(cityItem)" 
                                />
                            </el-select>
                        </div>
                    </div>
                    <div class="swap-btn" @click="swapStatusCities">
                        <span>⇄</span>
                    </div>
                    <div class="field-group city-group">
                        <label class="field-label">到达城市</label>
                        <div class="field-input">
                            <i class="field-icon">📍</i>
                            <el-select 
                                v-model="statusForm.arrivalCity" 
                                placeholder="选择到达城市" 
                                filterable
                                class="city-select"
                            >
                                <el-option 
                                    v-for="(cityItem, index) in cities" 
                                    :key="'status-arr-' + index"
                                    :label="getCityName(cityItem)" 
                                    :value="getCityName(cityItem)" 
                                />
                            </el-select>
                        </div>
                    </div>
                    <div class="field-divider"></div>
                    <div class="field-group date-group">
                        <label class="field-label">日期</label>
                        <div class="field-input">
                            <i class="field-icon">📅</i>
                            <el-date-picker 
                                v-model="statusForm.flightDate" 
                                type="date" 
                                placeholder="选择日期"
                                format="YYYY-MM-DD"
                                value-format="YYYY-MM-DD"
                                class="date-picker"
                            />
                        </div>
                    </div>
                    <button class="search-btn" @click="queryFlightStatus">
                        搜索
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
import axios from 'axios';

export default {
    name: 'SearchForm',
    data() {
        return {
            activeTab: 'search',
            searchForm: {
                tripType: 'oneway',
                departureCity: '上海',
                arrivalCity: '北京',
                departureDate: new Date(),
                returnDate: '',
                cabinClass: 'economy',
                passengerCount: 1,
                airline: ''
            },
            checkinForm: {
                passengerName: '',
                idNumber: '',
                ticketNumber: '',
                flightNumber: '',
                phone: '',
                agreed: false
            },
            statusForm: {
                queryType: 'flightNo',
                flightNumber: '',
                flightDate: new Date().toISOString().split('T')[0],
                departureCity: '',
                arrivalCity: ''
            },
            cities: []
        }
    },
    created() {
        this.setDefaultCities();
        this.fetchCities();
    },
    methods: {
        swapCities() {
            const temp = this.searchForm.departureCity;
            this.searchForm.departureCity = this.searchForm.arrivalCity;
            this.searchForm.arrivalCity = temp;
        },
        async fetchCities() {
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/core/cities/')
                if (response.data && Array.isArray(response.data)) {
                    this.cities = response.data;
                } else {
                    this.setDefaultCities();
                }
            } catch (error) {
                console.error('获取城市列表失败', error)
                this.setDefaultCities();
            }
        },
        setDefaultCities() {
            this.cities = [
                { name: '北京', code: 'BJS' },
                { name: '上海', code: 'SHA' },
                { name: '广州', code: 'CAN' },
                { name: '深圳', code: 'SZX' },
                { name: '成都', code: 'CTU' },
                { name: '杭州', code: 'HGH' },
                { name: '西安', code: 'XIY' },
                { name: '重庆', code: 'CKG' },
                { name: '南京', code: 'NKG' },
                { name: '武汉', code: 'WUH' },
                { name: '厦门', code: 'XMN' },
                { name: '长沙', code: 'CSX' }
            ];
        },
        disabledDate(time) {
            return time.getTime() < Date.now() - 8.64e7;
        },
        disabledReturnDate(time) {
            if (!this.searchForm.departureDate) return false;
            const depDate = new Date(this.searchForm.departureDate);
            return time.getTime() < depDate.getTime();
        },
        searchFlights() {
            if (!this.searchForm.departureCity) {
                this.$message.error('请选择出发城市');
                return;
            }
            if (!this.searchForm.arrivalCity) {
                this.$message.error('请选择目的城市');
                return;
            }
            if (!this.searchForm.departureDate) {
                this.$message.error('请选择出发日期');
                return;
            }
            if (this.searchForm.tripType === 'roundtrip' && !this.searchForm.returnDate) {
                this.$message.error('请选择返程日期');
                return;
            }
            
            const formattedDepartureDate = this.formatDate(this.searchForm.departureDate);
            
            this.$emit('search', {
                departureCity: this.searchForm.departureCity,
                arrivalCity: this.searchForm.arrivalCity,
                departureDate: formattedDepartureDate,
                returnDate: this.searchForm.returnDate ? this.formatDate(this.searchForm.returnDate) : null,
                passengerCount: this.searchForm.passengerCount,
                cabinClass: this.searchForm.cabinClass
            });
        },
        formatDate(date) {
            if (!date) return '';
            if (typeof date === 'string') return date;
            const d = new Date(date);
            const year = d.getFullYear();
            const month = String(d.getMonth() + 1).padStart(2, '0');
            const day = String(d.getDate()).padStart(2, '0');
            return `${year}-${month}-${day}`;
        },
        setRoute(route) {
            if (route && route.from && route.to) {
                this.searchForm.departureCity = route.from;
                this.searchForm.arrivalCity = route.to;
                if (!this.searchForm.departureDate) {
                    this.searchForm.departureDate = new Date();
                }
                this.$message.success(`已选择航线: ${route.from} → ${route.to}`);
            }
        },
        getCityName(city) {
            if (typeof city === 'string') return city;
            if (typeof city === 'object' && city.name) return city.name;
            return '';
        },
        // 选座值机
        handleCheckin() {
            if (!this.checkinForm.passengerName) {
                this.$message.error('请输入乘客姓名');
                return;
            }
            if (!this.checkinForm.idNumber) {
                this.$message.error('请输入证件号');
                return;
            }
            if (!this.checkinForm.ticketNumber) {
                this.$message.error('请输入票号');
                return;
            }
            if (!this.checkinForm.flightNumber) {
                this.$message.error('请输入航班号');
                return;
            }
            if (!this.checkinForm.phone) {
                this.$message.error('请输入手机号码');
                return;
            }
            if (!this.checkinForm.agreed) {
                this.$message.warning('请先阅读并同意相关须知');
                return;
            }
            // 跳转到值机选座页面
            this.$router.push({
                path: '/checkin',
                query: {
                    name: this.checkinForm.passengerName,
                    idNumber: this.checkinForm.idNumber,
                    ticketNo: this.checkinForm.ticketNumber,
                    flightNo: this.checkinForm.flightNumber,
                    phone: this.checkinForm.phone
                }
            });
        },
        // 航班动态查询
        queryFlightStatus() {
            if (this.statusForm.queryType === 'flightNo') {
                if (!this.statusForm.flightNumber) {
                    this.$message.error('请输入航班号');
                    return;
                }
            } else {
                if (!this.statusForm.departureCity || !this.statusForm.arrivalCity) {
                    this.$message.error('请选择出发和到达城市');
                    return;
                }
            }
            // 跳转到航班动态页面
            this.$router.push({
                path: '/flight-status',
                query: this.statusForm.queryType === 'flightNo' 
                    ? { flightNo: this.statusForm.flightNumber, date: this.statusForm.flightDate }
                    : { from: this.statusForm.departureCity, to: this.statusForm.arrivalCity, date: this.statusForm.flightDate }
            });
        },
        // 交换航班动态城市
        swapStatusCities() {
            const temp = this.statusForm.departureCity;
            this.statusForm.departureCity = this.statusForm.arrivalCity;
            this.statusForm.arrivalCity = temp;
        }
    }
}
</script>


<style scoped>
.search-box {
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
    overflow: hidden;
}

/* 顶部标签栏 */
.tab-header {
    display: flex;
    justify-content: center;
    gap: 0;
    padding: 0;
    background: linear-gradient(135deg, #1a4b8c 0%, #2d6cb5 100%);
}

.tab-btn {
    padding: 16px 36px;
    font-size: 16px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.7);
    background: transparent;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
}

.tab-btn:hover {
    color: #ffffff;
}

.tab-btn.active {
    color: #ffffff;
    background: rgba(255, 255, 255, 0.15);
    border-radius: 8px 8px 0 0;
}

.tab-btn.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 40px;
    height: 3px;
    background: #ffffff;
    border-radius: 2px;
}

/* 搜索内容区 */
.search-content {
    padding: 24px 32px 28px;
}

/* 行程类型 */
.trip-type-row {
    display: flex;
    gap: 32px;
    margin-bottom: 20px;
}

.trip-radio {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    font-size: 14px;
    color: #666;
}

.trip-radio input {
    display: none;
}

.radio-dot {
    width: 16px;
    height: 16px;
    border: 2px solid #ccc;
    border-radius: 50%;
    position: relative;
    transition: all 0.2s ease;
}

.trip-radio.active .radio-dot {
    border-color: #1a4b8c;
}

.trip-radio.active .radio-dot::after {
    content: '';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 8px;
    height: 8px;
    background: #1a4b8c;
    border-radius: 50%;
}

.trip-radio.active {
    color: #1a4b8c;
    font-weight: 500;
}

/* 主搜索行 */
.main-search-row {
    display: flex;
    align-items: flex-end;
    gap: 0;
    background: #f8f9fa;
    border-radius: 12px;
    padding: 4px;
    border: 1px solid #e8eef5;
}

.field-group {
    flex: 1;
    padding: 12px 16px;
    background: #ffffff;
    position: relative;
}

.field-group:first-child {
    border-radius: 10px 0 0 10px;
}

.city-group {
    min-width: 160px;
}

.date-group {
    min-width: 140px;
}

.field-label {
    display: block;
    font-size: 12px;
    color: #999;
    margin-bottom: 4px;
}

.field-input {
    display: flex;
    align-items: center;
    gap: 8px;
}

.field-icon {
    font-size: 16px;
    color: #1a4b8c;
    font-style: normal;
}

/* 交换按钮 */
.swap-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: #ffffff;
    border-radius: 50%;
    cursor: pointer;
    color: #1a4b8c;
    font-size: 18px;
    font-weight: bold;
    transition: all 0.3s ease;
    margin: 0 -18px;
    z-index: 10;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.swap-btn:hover {
    background: #1a4b8c;
    color: #ffffff;
    transform: rotate(180deg);
}

/* 分隔线 */
.field-divider {
    width: 1px;
    height: 40px;
    background: #e8eef5;
    margin: 0 8px;
    align-self: center;
}

/* 搜索按钮 */
.search-btn {
    padding: 0 40px;
    height: 56px;
    background: linear-gradient(135deg, #e85a4f 0%, #d64545 100%);
    color: #ffffff;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    white-space: nowrap;
}

.search-btn:hover {
    background: linear-gradient(135deg, #f06b5d 0%, #e85a4f 100%);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(232, 90, 79, 0.4);
}

/* Element Plus 样式覆盖 */
:deep(.city-select),
:deep(.date-picker) {
    width: 100%;
}

:deep(.el-select .el-select__wrapper),
:deep(.el-date-editor.el-input__wrapper) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0;
    min-height: auto;
}

:deep(.el-select .el-select__wrapper .el-select__selected-item),
:deep(.el-input__inner) {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
    padding: 0;
    height: auto;
    line-height: 1.4;
}

:deep(.el-select__suffix),
:deep(.el-input__suffix) {
    display: none;
}

:deep(.el-select__placeholder),
:deep(.el-input__inner::placeholder) {
    color: #999;
    font-weight: 400;
}

/* 占位内容 */
.placeholder-content {
    padding: 40px;
    text-align: center;
    color: #999;
}

/* 选座值机表单 */
.checkin-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.checkin-row {
    display: flex;
    align-items: flex-end;
    gap: 16px;
    background: #f8f9fa;
    border-radius: 12px;
    padding: 8px;
    border: 1px solid #e8eef5;
}

.checkin-field {
    flex: 1;
    min-width: 180px;
    background: #ffffff;
    border-radius: 8px;
}

.checkin-field.small {
    flex: 0.6;
    min-width: 120px;
}

.field-label .required {
    color: #e85a4f;
    margin-right: 2px;
}

.field-hint {
    font-size: 11px;
    color: #999;
    font-weight: 400;
    margin-left: 4px;
}

.checkin-btn {
    min-width: 100px;
    height: 56px;
}

.phone-input {
    display: flex;
    align-items: center;
}

.phone-prefix {
    color: #1a4b8c;
    font-weight: 600;
    font-size: 14px;
    margin-right: 8px;
    padding: 4px 8px;
    background: #f0f5fa;
    border-radius: 4px;
}

.checkin-agreement {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 13px;
    color: #666;
    padding-left: 8px;
}

.agreement-link {
    color: #1a4b8c;
    text-decoration: none;
}

.agreement-link:hover {
    text-decoration: underline;
}

:deep(.checkin-input .el-input__wrapper) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0;
}

:deep(.checkin-input .el-input__inner) {
    font-size: 15px;
    font-weight: 500;
    color: #1a1a1a;
}

/* 航班动态表单 */
.status-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

:deep(.status-input .el-input__wrapper) {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0;
}

:deep(.status-input .el-input__inner) {
    font-size: 16px;
    font-weight: 600;
    color: #1a1a1a;
}

/* 响应式 */
@media (max-width: 900px) {
    .main-search-row {
        flex-wrap: wrap;
    }
    
    .field-group {
        flex: 1 1 45%;
    }
    
    .swap-btn {
        margin: 0;
    }
    
    .field-divider {
        display: none;
    }
    
    .search-btn {
        flex: 1 1 100%;
        margin-top: 8px;
    }
    
    .checkin-row {
        flex-wrap: wrap;
    }
    
    .checkin-field {
        flex: 1 1 45%;
        min-width: 140px;
    }
    
    .checkin-btn {
        flex: 1 1 100%;
        margin-top: 8px;
    }
}

@media (max-width: 600px) {
    .tab-btn {
        padding: 12px 20px;
        font-size: 14px;
    }
    
    .search-content {
        padding: 16px;
    }
    
    .field-group {
        flex: 1 1 100%;
    }
    
    .checkin-field {
        flex: 1 1 100%;
    }
    
    .checkin-agreement {
        flex-wrap: wrap;
        font-size: 12px;
    }
}
</style>
