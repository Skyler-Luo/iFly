<template>
    <el-card class="search-box">
        <h2>航班查询</h2>
        <el-form :model="searchForm" label-width="100px">
            <div class="trip-type">
                <el-radio-group v-model="searchForm.tripType">
                    <el-radio value="oneway">单程</el-radio>
                    <el-radio value="roundtrip">往返</el-radio>
                </el-radio-group>
            </div>

            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="出发城市">
                        <div v-if="cities.length === 0" style="color: red;">加载城市数据中...</div>
                        <el-select v-model="searchForm.departureCity" placeholder="请选择出发城市" filterable>
                            <el-option v-for="(cityItem, index) in cities" :key="'dep-' + index"
                                :label="getCityName(cityItem)" :value="getCityName(cityItem)">
                            </el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="目的城市">
                        <div v-if="cities.length === 0" style="color: red;">加载城市数据中...</div>
                        <el-select v-model="searchForm.arrivalCity" placeholder="请选择目的城市" filterable>
                            <el-option v-for="(cityItem, index) in cities" :key="'arr-' + index"
                                :label="getCityName(cityItem)" :value="getCityName(cityItem)">
                            </el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
            </el-row>

            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="出发日期">
                        <el-date-picker v-model="searchForm.departureDate" type="date" placeholder="选择日期"
                            :disabled-date="disabledDate" style="width: 100%;">
                        </el-date-picker>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="返程日期" v-if="searchForm.tripType === 'roundtrip'">
                        <el-date-picker v-model="searchForm.returnDate" type="date" placeholder="选择日期"
                            :disabled-date="disabledReturnDate" style="width: 100%;">
                        </el-date-picker>
                    </el-form-item>
                </el-col>
            </el-row>

            <!-- 添加高级搜索选项 -->
            <el-collapse>
                <el-collapse-item title="高级搜索选项">
                    <div class="advanced-options">
                        <el-row :gutter="20">
                            <el-col :span="12">
                                <el-form-item label="舱位等级">
                                    <el-select v-model="searchForm.cabinClass" placeholder="请选择舱位等级"
                                        style="width: 100%;">
                                        <el-option label="经济舱" value="economy"></el-option>
                                        <el-option label="商务舱" value="business"></el-option>
                                        <el-option label="头等舱" value="first"></el-option>
                                    </el-select>
                                </el-form-item>
                            </el-col>
                            <el-col :span="12">
                                <el-form-item label="乘客人数">
                                    <el-input-number v-model="searchForm.passengerCount" :min="1" :max="9"
                                        style="width: 100%;"></el-input-number>
                                </el-form-item>
                            </el-col>
                        </el-row>

                        <el-row>
                            <el-col :span="24">
                                <el-form-item label="航空公司">
                                    <el-select v-model="searchForm.airline" placeholder="不限航空公司" clearable
                                        style="width: 100%;">
                                        <el-option v-for="airline in airlines" :key="airline.code" :label="airline.name"
                                            :value="airline.code"></el-option>
                                    </el-select>
                                </el-form-item>
                            </el-col>
                        </el-row>
                    </div>
                </el-collapse-item>
            </el-collapse>

            <el-form-item>
                <el-button type="primary" @click="searchFlights" style="width: 100%;">搜索航班</el-button>
            </el-form-item>
        </el-form>
    </el-card>
</template>

<script>
import axios from 'axios';

export default {
    name: 'SearchForm',
    data() {
        return {
            searchForm: {
                tripType: 'oneway',
                departureCity: '北京',
                arrivalCity: '上海',
                departureDate: new Date(),
                returnDate: '',
                cabinClass: 'economy',
                passengerCount: 1,
                airline: ''
            },
            cities: [],
            airlines: [
                { code: 'CA', name: '中国国际航空' },
                { code: 'MU', name: '东方航空' },
                { code: 'CZ', name: '南方航空' },
                { code: 'HU', name: '海南航空' },
                { code: '3U', name: '四川航空' },
                { code: 'MF', name: '厦门航空' }
            ]
        }
    },
    created() {
        // 先设置默认城市，然后再尝试从API获取
        this.setDefaultCities();
        this.fetchCities();

        // 添加调试信息
        console.log('SearchForm组件已创建');
        console.log('初始城市列表:', this.cities);
    },
    mounted() {
        this.fetchCities();
        
        // 打印日志，确认表单已经加载
        console.log('SearchForm loaded with initial data:', this.searchForm);
    },
    methods: {
        async fetchCities() {
            try {
                // 直接使用axios而不是API服务
                const response = await axios.get('http://127.0.0.1:8000/api/core/cities/')
                if (response.data && Array.isArray(response.data)) {
                    this.cities = response.data;
                } else {
                    // 如果API返回的格式不正确，使用默认城市列表
                    this.setDefaultCities();
                }
                console.log('获取到城市列表:', this.cities)
            } catch (error) {
                console.error('获取城市列表失败', error)
                // 如果API调用失败，使用默认城市列表
                this.setDefaultCities();
            }
        },
        setDefaultCities() {
            // 设置默认城市作为后备
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

            // 添加调试信息
            console.log('已设置默认城市列表:', this.cities);

            // 确保select组件能够正常显示
            setTimeout(() => {
                // 手动强制更新组件
                if (this.$forceUpdate) {
                    this.$forceUpdate();
                }
            }, 100);
        },
        disabledDate(time) {
            return time.getTime() < Date.now() - 8.64e7 // 不能选择今天之前的日期
        },
        disabledReturnDate(time) {
            if (!this.searchForm.departureDate) return false
            return time.getTime() < this.searchForm.departureDate.getTime() // 不能选择出发日期之前的日期
        },
        searchFlights() {
            // 校验表单
            if (!this.searchForm.departureCity) {
                this.$message.error('请选择出发城市')
                return
            }
            if (!this.searchForm.arrivalCity) {
                this.$message.error('请选择目的城市')
                return
            }
            if (!this.searchForm.departureDate) {
                this.$message.error('请选择出发日期')
                return
            }
            if (this.searchForm.tripType === 'roundtrip' && !this.searchForm.returnDate) {
                this.$message.error('请选择返程日期')
                return
            }
            
            console.log('提交搜索参数:', JSON.stringify(this.searchForm));
            
            // 确保出发日期是有效的
            const formattedDepartureDate = this.formatDate(this.searchForm.departureDate);
            console.log('格式化的出发日期:', formattedDepartureDate);
            
            // 发送查询航班事件
            this.$emit('search', {
                departureCity: this.searchForm.departureCity,
                arrivalCity: this.searchForm.arrivalCity,
                departureDate: formattedDepartureDate,
                returnDate: this.searchForm.returnDate ? this.formatDate(this.searchForm.returnDate) : null,
                passengerCount: this.searchForm.passengerCount,
                cabinClass: this.searchForm.cabinClass,
                adultCount: this.searchForm.passengerCount,
                childCount: 0,
                infantCount: 0
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
        setRouteData(from, to) {
            this.searchForm.departureCity = from
            this.searchForm.arrivalCity = to
            this.searchForm.departureDate = new Date()
        },
        setRoute(route) {
            // 更新以接收从地图选择的航线
            if (route && route.from && route.to) {
                this.searchForm.departureCity = route.from
                this.searchForm.arrivalCity = route.to

                // 如果未设置日期，则设置为当前日期
                if (!this.searchForm.departureDate) {
                    this.searchForm.departureDate = new Date()
                }

                // 自动滚动到搜索框
                const searchBox = document.querySelector('.search-box')
                if (searchBox) {
                    searchBox.scrollIntoView({ behavior: 'smooth' })
                }

                // 显示选择成功的消息
                this.$message.success(`已选择航线: ${route.from} → ${route.to}`)

                console.log('设置航线后的表单数据:', this.searchForm);
            }
        },
        setDestination(cityName) {
            if (!cityName) return;

            this.searchForm.arrivalCity = cityName
            console.log(`设置目的地: ${cityName}`);

            // 如果出发城市为空，设置为默认城市
            if (!this.searchForm.departureCity && this.cities.length > 0) {
                // 尝试找到名为"北京"的城市对象，如果没有就用第一个
                const defaultCity = this.cities.find(city => city.name === '北京');
                this.searchForm.departureCity = defaultCity ? defaultCity.name : this.cities[0].name;
                console.log(`设置默认出发城市: ${this.searchForm.departureCity}`);
            }
        },
        getCityName(city) {
            if (typeof city === 'string') {
                return city;
            } else if (typeof city === 'object' && city.name) {
                return city.name;
            } else {
                console.warn('城市数据格式不正确');
                return '';
            }
        }
    }
}
</script>

<style scoped>
.search-box {
    width: 100%;
    max-width: 800px;
    margin: 0 auto;
}

.trip-type {
    margin-bottom: 20px;
    text-align: center;
}

.advanced-options {
    padding: 5px;
    background-color: rgba(255, 255, 255, 0.7);
    border-radius: 8px;
}

/* 确保选择框对齐 */
:deep(.el-select) {
    width: 100%;
}

:deep(.el-input-number) {
    width: 100%;
}

:deep(.el-collapse-item__header) {
    font-weight: 600;
    color: #1976d2;
    padding: 5px 0;
}

:deep(.el-collapse) {
    border: none;
    margin-bottom: 15px;
}

:deep(.el-collapse-item__wrap) {
    background-color: transparent;
    border-bottom: none;
}

:deep(.el-collapse-item__content) {
    padding-bottom: 10px;
}
</style>