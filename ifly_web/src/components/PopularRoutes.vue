<template>
    <div class="popular-routes">
        <h2 class="section-title">热门航线推荐</h2>
        <p class="section-subtitle">精选最受欢迎的国内外航线，价格实惠，出行便捷</p>
        <el-row :gutter="20">
            <el-col :xs="24" :sm="12" :md="8" v-for="route in popularRoutes" :key="route.id">
                <el-card class="route-card" shadow="hover" @click="selectRoute(route)">
                    <div class="route-info">
                        <div class="cities">
                            <span class="from">{{ route.from }}</span>
                            <el-icon><arrow-right /></el-icon>
                            <span class="to">{{ route.to }}</span>
                        </div>
                        <div class="price">
                            <span>¥{{ route.price }}</span>起
                        </div>
                    </div>
                    <div class="discount" v-if="route.discount < 1">
                        {{ Math.floor((1 - route.discount) * 100) }}% 优惠
                    </div>
                </el-card>
            </el-col>
        </el-row>
    </div>
</template>

<script>
import axios from 'axios'

export default {
    name: 'PopularRoutes',
    data() {
        return {
            popularRoutes: []
        }
    },
    created() {
        this.fetchPopularRoutes()
    },
    methods: {
        async fetchPopularRoutes() {
            try {
                // 直接使用axios而不是api服务
                const response = await axios.get('http://127.0.0.1:8000/api/flights/search/')
                
                const flights = response.data
                if (flights && flights.length > 0) {
                    // 按城市对生成热门航线
                    const routes = []
                    const routeMap = new Map()

                    flights.forEach(flight => {
                        const routeKey = `${flight.departure_city}-${flight.arrival_city}`
                        if (!routeMap.has(routeKey)) {
                            routeMap.set(routeKey, {
                                id: routes.length + 1,
                                from: flight.departure_city,
                                to: flight.arrival_city,
                                price: parseFloat(flight.price),
                                discount: parseFloat(flight.discount)
                            })
                            routes.push(routeMap.get(routeKey))
                        } else {
                            // 如果已存在该航线，更新为更低价格
                            const route = routeMap.get(routeKey)
                            const flightPrice = parseFloat(flight.price) * parseFloat(flight.discount)
                            const routePrice = route.price * route.discount
                            if (flightPrice < routePrice) {
                                route.price = parseFloat(flight.price)
                                route.discount = parseFloat(flight.discount)
                            }
                        }
                    })

                    // 限制为6个热门航线
                    this.popularRoutes = routes.slice(0, 6)
                } else {
                    // 如果没有数据，使用模拟数据
                    this.setMockRoutes()
                }
            } catch (error) {
                console.error('获取热门航线失败:', error)
                // 如果API请求失败，使用模拟数据
                this.setMockRoutes()
            }
        },
        setMockRoutes() {
            // 备用的模拟数据
            this.popularRoutes = [
                { id: 1, from: '北京', to: '上海', price: 520, discount: 0.9 },
                { id: 2, from: '广州', to: '北京', price: 780, discount: 0.85 },
                { id: 3, from: '深圳', to: '上海', price: 620, discount: 0.95 },
                { id: 4, from: '成都', to: '广州', price: 650, discount: 1 },
                { id: 5, from: '杭州', to: '厦门', price: 450, discount: 0.8 },
                { id: 6, from: '西安', to: '北京', price: 580, discount: 0.9 }
            ]
        },
        selectRoute(route) {
            this.$emit('select-route', { from: route.from, to: route.to })
        }
    }
}
</script>

<style scoped>
.popular-routes {
    margin: 40px 0;
    padding: 0 20px;
}

.route-card {
    margin-bottom: 20px;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
    height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.route-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.route-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
    padding: 10px 15px;
}

.cities {
    display: flex;
    align-items: center;
    gap: 10px;
}

.from,
.to {
    font-weight: bold;
    font-size: 16px;
}

.el-icon {
    color: #1976d2;
}

.price {
    color: #F56C6C;
    font-weight: bold;
}

.price span {
    font-size: 20px;
}

.discount {
    color: white;
    background-color: #F56C6C;
    padding: 2px 8px;
    border-radius: 4px;
    display: inline-block;
    font-size: 12px;
    position: absolute;
    top: 10px;
    right: 10px;
}

:deep(.el-card__body) {
    padding: 15px 0;
    position: relative;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}
</style>