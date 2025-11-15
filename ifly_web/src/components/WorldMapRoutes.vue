<template>
    <div class="world-map-container">
        <h3>全球航线选择</h3>
        <div class="map-wrapper">
            <div id="world-map" ref="worldMap"></div>

            <!-- 地图加载状态 -->
            <div v-if="mapStatus !== 'loaded'" class="map-loading-overlay">
                <div v-if="mapStatus === 'loading'" class="loading-message">
                    <el-icon class="loading"><svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M512 1024c-69.1 0-136.2-13.5-199.3-40.2C251.7 958 197 921 150 874c-47-47-84-101.7-109.8-162.7C13.5 648.2 0 581.1 0 512c0-19.9 16.1-36 36-36s36 16.1 36 36c0 59.4 11.6 117 34.6 171.3 22.2 52.4 53.9 99.5 94.3 139.9 40.4 40.4 87.5 72.2 139.9 94.3C395 940.4 452.6 952 512 952c59.4 0 117-11.6 171.3-34.6 52.4-22.2 99.5-53.9 139.9-94.3 40.4-40.4 72.2-87.5 94.3-139.9C940.4 629 952 571.4 952 512c0-59.4-11.6-117-34.6-171.3a440.45 440.45 0 00-94.3-139.9 437.71 437.71 0 00-139.9-94.3C629 83.6 571.4 72 512 72c-19.9 0-36-16.1-36-36s16.1-36 36-36c69.1 0 136.2 13.5 199.3 40.2C772.3 66 827 103 874 150c47 47 83.9 101.8 109.7 162.7 26.7 63.1 40.2 130.2 40.2 199.3s-13.5 136.2-40.2 199.3C958 772.3 921 827 874 874c-47 47-101.8 83.9-162.7 109.7-63.1 26.8-130.2 40.3-199.3 40.3z">
                            </path>
                        </svg></el-icon>
                    <span>地图加载中...</span>
                </div>
                <div v-else-if="mapStatus === 'error'" class="error-message">
                    <el-icon class="error"><svg viewBox="0 0 1024 1024" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M512 64a448 448 0 1 1 0 896 448 448 0 0 1 0-896zm0 393.664L407.936 353.6a38.4 38.4 0 1 0-54.336 54.336L457.664 512 353.6 616.064a38.4 38.4 0 1 0 54.336 54.336L512 566.336 616.064 670.4a38.4 38.4 0 1 0 54.336-54.336L566.336 512 670.4 407.936a38.4 38.4 0 1 0-54.336-54.336L512 457.664z">
                            </path>
                        </svg></el-icon>
                    <span>地图加载失败，请刷新页面重试</span>
                    <el-button type="primary" size="small" @click="reloadMap">重新加载</el-button>
                </div>
            </div>

            <!-- 天气信息窗口 -->
            <div id="weather-popup" class="weather-popup" v-if="showWeather">
                <div class="weather-popup-header">
                    <span>{{ selectedWeatherCity }} 天气</span>
                    <button class="close-btn" @click="closeWeather">×</button>
                </div>
                <div class="weather-popup-content">
                    <city-weather-info :city="selectedWeatherCity" />
                </div>
            </div>

            <div class="route-info" v-if="selectedRoute">
                <div class="route-card">
                    <h4>已选择航线</h4>
                    <div class="route-details">
                        <p><strong>出发城市:</strong> {{ selectedRoute.from }}
                            <el-button size="small" type="text" @click="showCityWeather(selectedRoute.from)">
                                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
                                        <path fill="currentColor"
                                            d="M512 704a192 192 0 1 0 0-384 192 192 0 0 0 0 384zm0 64a256 256 0 1 1 0-512 256 256 0 0 1 0 512zm0-704a32 32 0 0 1 32 32v64a32 32 0 0 1-64 0V96a32 32 0 0 1 32-32zm0 768a32 32 0 0 1 32 32v64a32 32 0 1 1-64 0v-64a32 32 0 0 1 32-32zM195.2 195.2a32 32 0 0 1 45.3 0l45.3 45.3a32 32 0 0 1-45.3 45.3l-45.3-45.3a32 32 0 0 1 0-45.3zm543 543a32 32 0 0 1 45.3 0l45.3 45.3a32 32 0 0 1-45.3 45.3l-45.3-45.3a32 32 0 0 1 0-45.3zM64 512a32 32 0 0 1 32-32h64a32 32 0 0 1 0 64H96a32 32 0 0 1-32-32zm768 0a32 32 0 0 1 32-32h64a32 32 0 1 1 0 64h-64a32 32 0 0 1-32-32zM195.2 828.8a32 32 0 0 1 0-45.3l45.3-45.3a32 32 0 0 1 45.3 45.3l-45.3 45.3a32 32 0 0 1-45.3 0zm543-543a32 32 0 0 1 0-45.3l45.3-45.3a32 32 0 0 1 45.3 45.3l-45.3 45.3a32 32 0 0 1-45.3 0z">
                                        </path>
                                    </svg></el-icon>
                            </el-button>
                        </p>
                        <p><strong>目的城市:</strong> {{ selectedRoute.to }}
                            <el-button size="small" type="text" @click="showCityWeather(selectedRoute.to)">
                                <el-icon><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">
                                        <path fill="currentColor"
                                            d="M512 704a192 192 0 1 0 0-384 192 192 0 0 0 0 384zm0 64a256 256 0 1 1 0-512 256 256 0 0 1 0 512zm0-704a32 32 0 0 1 32 32v64a32 32 0 0 1-64 0V96a32 32 0 0 1 32-32zm0 768a32 32 0 0 1 32 32v64a32 32 0 1 1-64 0v-64a32 32 0 0 1 32-32zM195.2 195.2a32 32 0 0 1 45.3 0l45.3 45.3a32 32 0 0 1-45.3 45.3l-45.3-45.3a32 32 0 0 1 0-45.3zm543 543a32 32 0 0 1 45.3 0l45.3 45.3a32 32 0 0 1-45.3 45.3l-45.3-45.3a32 32 0 0 1 0-45.3zM64 512a32 32 0 0 1 32-32h64a32 32 0 0 1 0 64H96a32 32 0 0 1-32-32zm768 0a32 32 0 0 1 32-32h64a32 32 0 1 1 0 64h-64a32 32 0 0 1-32-32zM195.2 828.8a32 32 0 0 1 0-45.3l45.3-45.3a32 32 0 0 1 45.3 45.3l-45.3 45.3a32 32 0 0 1-45.3 0zm543-543a32 32 0 0 1 0-45.3l45.3-45.3a32 32 0 0 1 45.3 45.3l-45.3 45.3a32 32 0 0 1-45.3 0z">
                                        </path>
                                    </svg></el-icon>
                            </el-button>
                        </p>
                        <p><strong>距离:</strong> {{ selectedRoute.distance }}公里</p>
                        <p><strong>预计飞行时间:</strong> {{ calculateFlightTime(selectedRoute.distance) }}</p>
                    </div>
                    <div class="route-actions">
                        <el-button type="primary" size="small" @click="selectThisRoute">选择此航线</el-button>
                        <el-button type="danger" size="small" @click="resetRoute">重置选择</el-button>
                    </div>
                </div>
            </div>
        </div>

        <div class="popular-cities">
            <h4>热门城市</h4>
            <div class="city-chips">
                <el-tag v-for="city in popularCities" :key="city.name" @click="highlightCity(city)" class="city-tag"
                    :effect="city.selected ? 'dark' : 'plain'">
                    {{ city.name }}
                </el-tag>
            </div>
        </div>
    </div>
</template>

<script>
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import CityWeatherInfo from '@/components/CityWeatherInfo.vue';
import api from '@/services/api';

// 检查组件是否正确导入
console.log('导入的天气组件:', CityWeatherInfo);

// 修复Leaflet默认图标问题
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
    iconUrl: require('leaflet/dist/images/marker-icon.png'),
    shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

export default {
    name: 'WorldMapRoutes',
    components: {
        CityWeatherInfo: CityWeatherInfo // 明确注册组件
    },
    props: {
        initialFrom: {
            type: String,
            default: ''
        },
        initialTo: {
            type: String,
            default: ''
        }
    },
    data() {
        return {
            map: null,
            markers: {},
            routeLine: null,
            planeMarker: null,
            fromPointMarker: null,
            toPointMarker: null,
            selectedRoute: null,
            selectedFromCity: null,
            selectedToCity: null,
            mapStatus: 'loading', // 'loading', 'loaded', 'error'
            showWeather: false,
            selectedWeatherCity: '',
            popularCities: [
                { name: '北京', coords: [39.9042, 116.4074], selected: false },
                { name: '上海', coords: [31.2304, 121.4737], selected: false },
                { name: '广州', coords: [23.1291, 113.2644], selected: false },
                { name: '成都', coords: [30.5728, 104.0668], selected: false },
                { name: '深圳', coords: [22.5431, 114.0579], selected: false },
                { name: '杭州', coords: [30.2741, 120.1551], selected: false },
                { name: '西安', coords: [34.3416, 108.9398], selected: false },
                { name: '重庆', coords: [29.5630, 106.5500], selected: false },
                { name: '南京', coords: [32.0603, 118.7969], selected: false },
                { name: '武汉', coords: [30.5928, 114.3055], selected: false },
                { name: '厦门', coords: [24.4798, 118.0819], selected: false },
                { name: '长沙', coords: [28.2282, 112.9388], selected: false },
                { name: '青岛', coords: [36.0671, 120.3826], selected: false },
                { name: '大连', coords: [38.9140, 121.6147], selected: false },
                { name: '沈阳', coords: [41.8057, 123.4315], selected: false },
                { name: '哈尔滨', coords: [45.7656, 126.6250], selected: false },
                { name: '纽约', coords: [40.7128, -74.0060], selected: false },
                { name: '东京', coords: [35.6762, 139.6503], selected: false },
                { name: '伦敦', coords: [51.5074, -0.1278], selected: false },
                { name: '巴黎', coords: [48.8566, 2.3522], selected: false },
                { name: '悉尼', coords: [-33.8688, 151.2093], selected: false },
                { name: '迪拜', coords: [25.2048, 55.2708], selected: false },
                { name: '新加坡', coords: [1.3521, 103.8198], selected: false },
                { name: '曼谷', coords: [13.7563, 100.5018], selected: false }
            ],
            cityData: {
                '北京': { code: 'PEK', coords: [39.9042, 116.4074] },
                '上海': { code: 'SHA', coords: [31.2304, 121.4737] },
                '广州': { code: 'CAN', coords: [23.1291, 113.2644] },
                '成都': { code: 'CTU', coords: [30.5728, 104.0668] },
                '深圳': { code: 'SZX', coords: [22.5431, 114.0579] },
                '杭州': { code: 'HGH', coords: [30.2741, 120.1551] },
                '西安': { code: 'XIY', coords: [34.3416, 108.9398] },
                '重庆': { code: 'CKG', coords: [29.5630, 106.5500] },
                '南京': { code: 'NKG', coords: [32.0603, 118.7969] },
                '武汉': { code: 'WUH', coords: [30.5928, 114.3055] },
                '厦门': { code: 'XMN', coords: [24.4798, 118.0819] },
                '长沙': { code: 'CSX', coords: [28.2282, 112.9388] },
                '青岛': { code: 'TAO', coords: [36.0671, 120.3826] },
                '大连': { code: 'DLC', coords: [38.9140, 121.6147] },
                '沈阳': { code: 'SHE', coords: [41.8057, 123.4315] },
                '哈尔滨': { code: 'HRB', coords: [45.7656, 126.6250] },
                '纽约': { code: 'JFK', coords: [40.7128, -74.0060] },
                '东京': { code: 'HND', coords: [35.6762, 139.6503] },
                '伦敦': { code: 'LHR', coords: [51.5074, -0.1278] },
                '巴黎': { code: 'CDG', coords: [48.8566, 2.3522] },
                '悉尼': { code: 'SYD', coords: [-33.8688, 151.2093] },
                '新加坡': { code: 'SIN', coords: [1.3521, 103.8198] },
                '曼谷': { code: 'BKK', coords: [13.7563, 100.5018] },
                '迪拜': { code: 'DXB', coords: [25.2048, 55.2708] }
            }
        };
    },
    created() {
        console.log('WorldMapRoutes组件已创建');
        console.log('注册的组件:', this.$options.components);
    },
    mounted() {
        console.log('WorldMapRoutes组件已挂载，准备初始化地图');
        // 确保DOM完全渲染后再初始化地图
        this.$nextTick(() => {
            const mapContainer = this.$refs.worldMap;
            console.log('地图容器元素:', mapContainer);

            if (mapContainer) {
                console.log('地图容器尺寸:', mapContainer.clientWidth, 'x', mapContainer.clientHeight);
                // 给容器一个明确的高度，确保可见
                mapContainer.style.height = '450px';

                // 使用setTimeout给足够时间让DOM渲染
                setTimeout(() => {
                    this.initMap();

                    // 如果有初始城市，设置它们
                    if (this.initialFrom && this.initialTo) {
                        this.selectCities(this.initialFrom, this.initialTo);
                    }
                }, 300); // 增加延迟时间
            } else {
                console.error('严重错误: 地图容器元素不存在');
            }
        });
    },
    beforeUnmount() {
        // 组件销毁前清理地图资源
        console.log('清理地图资源');
        try {
            if (this.map) {
                // 清除路线和标记
                if (this.routeLine) {
                    this.map.removeLayer(this.routeLine);
                }
                if (this.planeMarker) {
                    this.map.removeLayer(this.planeMarker);
                }
                if (this.fromPointMarker) {
                    this.map.removeLayer(this.fromPointMarker);
                }
                if (this.toPointMarker) {
                    this.map.removeLayer(this.toPointMarker);
                }

                // 移除所有图层
                this.map.eachLayer(layer => {
                    this.map.removeLayer(layer);
                });

                // 移除所有事件监听器
                this.map.off();

                // 移除地图
                this.map.remove();
                this.map = null;
            }
        } catch (error) {
            console.error('清理地图资源失败:', error);
        }
    },
    methods: {
        initMap() {
            try {
                console.log('初始化地图...');
                this.mapStatus = 'loading';

                // 检查DOM元素是否存在且有尺寸
                const mapContainer = this.$refs.worldMap;
                if (!mapContainer) {
                    console.error('地图容器元素不存在');
                    this.mapStatus = 'error';
                    return;
                }

                console.log('地图容器尺寸检查:', mapContainer.clientWidth, 'x', mapContainer.clientHeight);
                if (mapContainer.clientWidth === 0 || mapContainer.clientHeight === 0) {
                    console.error('地图容器尺寸为0');
                    // 尝试强制设置容器尺寸
                    mapContainer.style.width = '100%';
                    mapContainer.style.height = '450px';
                    console.log('已强制设置地图容器尺寸');
                }

                // 创建地图实例
                console.log('开始创建地图实例...');
                this.map = L.map(mapContainer, {
                    center: [30, 105], // 将中国置于中心
                    zoom: 3,
                    minZoom: 2,
                    maxBounds: [
                        [-90, -180], // 南极洲到最西边
                        [90, 180]    // 北极到最东边
                    ],
                    zoomControl: false, // 禁用默认缩放控件，后面手动添加
                    attributionControl: false // 禁用默认归因控件，后面手动添加
                });

                // 手动添加缩放和归因控件
                L.control.zoom({
                    position: 'topright'
                }).addTo(this.map);

                L.control.attribution({
                    position: 'bottomright'
                }).addTo(this.map);

                console.log('地图实例创建成功，添加底图...');

                // 简化地图源配置，避免同时加载多个图层
                // 按优先级尝试加载不同的地图源
                const loadMapSource = (sourceIndex = 0) => {
                    // 定义地图源列表，按优先级排序
                    const mapSources = [
                        {
                            name: '简洁风格',
                            url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                            options: {
                                attribution: '&copy; <a href="https://carto.com/attributions">CARTO</a>',
                                subdomains: 'abcd',
                                maxZoom: 20
                            }
                        },
                        {
                            name: '全球卫星影像',
                            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                            options: {
                                attribution: '&copy; Esri'
                            }
                        },
                        {
                            name: '高德地图',
                            url: 'https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
                            options: {
                                attribution: '&copy; 高德地图'
                            }
                        }
                    ];

                    // 如果已尝试所有地图源仍失败，则显示错误
                    if (sourceIndex >= mapSources.length) {
                        console.error('所有地图源加载失败');
                        this.mapStatus = 'error';
                        return;
                    }

                    const source = mapSources[sourceIndex];
                    console.log(`尝试加载地图源: ${source.name}`);

                    // 创建图层
                    const tileLayer = L.tileLayer(source.url, source.options);

                    // 监听事件
                    let tileLoadCount = 0;
                    let tileErrorCount = 0;
                    let hasSuccessfulLoad = false;

                    tileLayer.on('tileload', () => {
                        tileLoadCount++;
                        // 一旦有瓦片成功加载，标记地图加载成功
                        if (!hasSuccessfulLoad && tileLoadCount > 0) {
                            hasSuccessfulLoad = true;
                            this.mapStatus = 'loaded';
                            console.log(`地图源 ${source.name} 加载成功`);

                            // 地图成功加载后添加城市标记
                            this.addCityMarkers();
                        }
                    });

                    tileLayer.on('tileerror', () => {
                        tileErrorCount++;
                        // 如果有超过3个瓦片加载失败，且没有一个成功，则尝试下一个地图源
                        if (!hasSuccessfulLoad && tileErrorCount > 3) {
                            console.log(`地图源 ${source.name} 加载失败，尝试下一个地图源`);
                            tileLayer.remove();
                            loadMapSource(sourceIndex + 1);
                        }
                    });

                    // 添加图层到地图
                    tileLayer.addTo(this.map);

                    // 设置超时
                    setTimeout(() => {
                        if (!hasSuccessfulLoad) {
                            console.log(`地图源 ${source.name} 加载超时，尝试下一个地图源`);
                            tileLayer.remove();
                            loadMapSource(sourceIndex + 1);
                        }
                    }, 5000);
                };

                // 开始加载第一个地图源
                loadMapSource();

                console.log('地图初始化完成');
            } catch (error) {
                console.error('地图初始化失败:', error);
                this.mapStatus = 'error';
            }
        },

        addCityMarkers() {
            try {
                console.log('添加城市标记...');
                
                // 首先清理现有的标记
                for (const cityName in this.markers) {
                    if (this.markers[cityName] && this.map && this.map.hasLayer(this.markers[cityName])) {
                        this.map.removeLayer(this.markers[cityName]);
                    }
                }
                this.markers = {};
                
                // 创建新的标记
                Object.entries(this.cityData).forEach(([cityName, data]) => {
                    const icon = L.divIcon({
                        className: 'city-marker',
                        html: `<div class="marker-dot"></div><div class="city-label">${cityName}</div>`,
                        iconSize: [60, 30],
                        iconAnchor: [15, 15]
                    });

                    const marker = L.marker(data.coords, { icon })
                        .addTo(this.map)
                        .on('click', () => this.handleCityClick(cityName));

                    this.markers[cityName] = marker;
                });
            } catch (error) {
                console.error('添加城市标记失败:', error);
            }
        },

        handleCityClick(cityName) {
            console.log('点击了城市:', cityName);
            
            if (!this.selectedFromCity) {
                // 第一次选择
                this.selectedFromCity = cityName;
                this.highlightMarker(cityName, 'from');
                
                // 更新热门城市标签状态
                this.popularCities.forEach(city => {
                    if (city.name === cityName) {
                        city.selected = true;
                    }
                });
            } else if (!this.selectedToCity) {
                // 第二次选择
                if (cityName === this.selectedFromCity) {
                    return; // 避免选择相同的城市
                }
                this.selectedToCity = cityName;
                this.highlightMarker(cityName, 'to');
                
                // 更新热门城市标签状态
                this.popularCities.forEach(city => {
                    if (city.name === cityName) {
                        city.selected = true;
                    }
                });
                
                this.drawRoute();
            } else {
                // 重置并重新选择
                this.resetSelection();
                this.selectedFromCity = cityName;
                this.highlightMarker(cityName, 'from');
                
                // 更新热门城市标签状态
                this.popularCities.forEach(city => {
                    if (city.name === cityName) {
                        city.selected = true;
                    }
                });
            }
        },

        highlightMarker(cityName, type) {
            // 更新标记样式
            const marker = this.markers[cityName];
            const cityCoords = this.cityData[cityName].coords;

            // 移除之前的标记
            if (marker) {
                this.map.removeLayer(marker);
            }

            // 如果是起点，清除之前的fromPointMarker
            if (type === 'from' && this.fromPointMarker) {
                this.map.removeLayer(this.fromPointMarker);
                this.fromPointMarker = null;
            }

            // 如果是终点，清除之前的toPointMarker
            if (type === 'to' && this.toPointMarker) {
                this.map.removeLayer(this.toPointMarker);
                this.toPointMarker = null;
            }

            // 创建高亮标记
            const highlightClass = type === 'from' ? 'from-city' : 'to-city';
            const highlightIcon = L.divIcon({
                className: `city-marker ${highlightClass}`,
                html: `<div class="marker-dot ${highlightClass}"></div><div class="city-label">${cityName}</div>`,
                iconSize: [60, 30],
                iconAnchor: [15, 15]
            });

            const newMarker = L.marker(cityCoords, { icon: highlightIcon }).addTo(this.map);

            newMarker.on('click', () => {
                this.handleCityClick(cityName);
            });

            this.markers[cityName] = newMarker;

            // 同时保存为起点或终点标记引用
            if (type === 'from') {
                this.fromPointMarker = newMarker;
            } else if (type === 'to') {
                this.toPointMarker = newMarker;
            }
        },

        drawRoute() {
            if (!this.selectedFromCity || !this.selectedToCity || !this.map) return;

            try {
                const fromCoords = this.cityData[this.selectedFromCity].coords;
                const toCoords = this.cityData[this.selectedToCity].coords;

                // 计算距离（简化版，直线距离）
                const distance = this.calculateDistance(fromCoords[0], fromCoords[1], toCoords[0], toCoords[1]);

                // 如果已有路线，移除它
                if (this.routeLine) {
                    this.map.removeLayer(this.routeLine);
                }

                // 如果已有飞机标记，移除它
                if (this.planeMarker) {
                    this.map.removeLayer(this.planeMarker);
                    this.planeMarker = null;
                }

                // 使用插件创建动画航线
                this.routeLine = L.polyline([fromCoords, toCoords], {
                    color: '#1890ff',
                    weight: 4,
                    opacity: 0.8,
                    dashArray: '10, 10',
                    dashOffset: '0',
                    lineCap: 'round',
                    lineJoin: 'round',
                    className: 'animated-route' // 添加一个CSS类用于动画
                }).addTo(this.map);

                // 不再创建额外的起点和终点标记，使用highlightMarker创建的标记
                // 确保调用highlightMarker已经创建了标记
                if (!this.fromPointMarker) {
                    this.highlightMarker(this.selectedFromCity, 'from');
                }

                if (!this.toPointMarker) {
                    this.highlightMarker(this.selectedToCity, 'to');
                }

                // 设置选择的路线信息
                this.selectedRoute = {
                    from: this.selectedFromCity,
                    to: this.selectedToCity,
                    distance: Math.round(distance)
                };

                // 确保地图可以看到整个路线，使用平滑的动画
                try {
                    this.map.fitBounds([fromCoords, toCoords], {
                        padding: [50, 50],
                        animate: true,
                        duration: 0.5
                    });
                } catch (error) {
                    console.error('设置地图视图范围失败:', error);
                    // 使用更简单的方式缩放地图
                    this.map.setView(
                        [(fromCoords[0] + toCoords[0]) / 2, (fromCoords[1] + toCoords[1]) / 2],
                        3
                    );
                }
            } catch (error) {
                console.error('绘制航线失败:', error);
            }
        },

        calculateDistance(lat1, lon1, lat2, lon2) {
            // 使用Haversine公式计算两点之间的距离
            const R = 6371; // 地球半径，单位公里
            const dLat = this.deg2rad(lat2 - lat1);
            const dLon = this.deg2rad(lon2 - lon1);
            const a =
                Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                Math.cos(this.deg2rad(lat1)) * Math.cos(this.deg2rad(lat2)) *
                Math.sin(dLon / 2) * Math.sin(dLon / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            const distance = R * c;
            return distance;
        },

        deg2rad(deg) {
            return deg * (Math.PI / 180);
        },

        calculateAngle(lat1, lon1, lat2, lon2) {
            // 计算两点之间的角度，用于旋转飞机图标
            const dy = lat2 - lat1;
            const dx = Math.cos(Math.PI / 180 * lat1) * (lon2 - lon1);
            const angle = Math.atan2(dy, dx) * 180 / Math.PI;
            return angle;
        },

        resetSelection() {
            console.log('重置路线选择');
            
            try {
                // 清除路线
                if (this.routeLine && this.map) {
                    this.map.removeLayer(this.routeLine);
                    this.routeLine = null;
                }
                
                // 清除飞机标记
                if (this.planeMarker && this.map) {
                    this.map.removeLayer(this.planeMarker);
                    this.planeMarker = null;
                }
                
                // 清除起点和终点标记
                if (this.fromPointMarker && this.map) {
                    this.map.removeLayer(this.fromPointMarker);
                    this.fromPointMarker = null;
                }
                
                if (this.toPointMarker && this.map) {
                    this.map.removeLayer(this.toPointMarker);
                    this.toPointMarker = null;
                }
                
                // 重置城市选择状态
                this.selectedFromCity = null;
                this.selectedToCity = null;
                this.selectedRoute = null;
                
                // 重置热门城市选择状态
                this.popularCities.forEach(city => {
                    city.selected = false;
                });
                
                // 发送事件通知父组件
                this.$emit('route-selected', { from: '', to: '' });
                
                // 重新添加所有城市标记
                this.addCityMarkers();
                
                // 提示用户
                this.$message.success('已重置航线选择');
            } catch (error) {
                console.error('重置路线失败:', error);
                // 如果发生错误，仍然尝试添加标记
                setTimeout(() => {
                    if (this.map && this.mapStatus === 'loaded') {
                        this.addCityMarkers();
                    }
                }, 100);
            }
        },

        selectThisRoute() {
            if (this.selectedRoute) {
                this.$emit('route-selected', {
                    from: this.selectedRoute.from,
                    to: this.selectedRoute.to
                });
            }
        },

        highlightCity(city) {
            // 点击热门城市标签
            if (!this.selectedFromCity) {
                // 第一次选择
                this.selectedFromCity = city.name;
                city.selected = true;
                this.highlightMarker(city.name, 'from');
            } else if (!this.selectedToCity) {
                // 第二次选择
                if (city.name === this.selectedFromCity) {
                    return;
                }
                this.selectedToCity = city.name;
                city.selected = true;
                this.highlightMarker(city.name, 'to');
                this.drawRoute();
            } else {
                // 重置并重新选择
                this.resetSelection();
                this.selectedFromCity = city.name;
                city.selected = true;
                this.highlightMarker(city.name, 'from');
            }
        },

        selectCities(fromCity, toCity) {
            if (this.cityData[fromCity] && this.cityData[toCity]) {
                this.selectedFromCity = fromCity;
                this.selectedToCity = toCity;

                this.highlightMarker(fromCity, 'from');
                this.highlightMarker(toCity, 'to');

                // 更新热门城市标签状态
                this.popularCities.forEach(city => {
                    if (city.name === fromCity || city.name === toCity) {
                        city.selected = true;
                    }
                });

                this.drawRoute();
            }
        },

        reloadMap() {
            this.mapStatus = 'loading';
            this.initMap();
        },

        // 计算预估飞行时间
        calculateFlightTime(distance) {
            // 假设平均飞行速度为800公里/小时
            const hours = distance / 800;
            const fullHours = Math.floor(hours);
            const minutes = Math.round((hours - fullHours) * 60);

            if (fullHours === 0) {
                return `${minutes}分钟`;
            } else if (minutes === 0) {
                return `${fullHours}小时`;
            } else {
                return `${fullHours}小时${minutes}分钟`;
            }
        },

        // 显示城市天气
        showCityWeather(cityName) {
            console.log('---------------------------------------');
            console.log('开始显示城市天气:', cityName);
            this.selectedWeatherCity = cityName;

            try {
                // 直接创建DOM元素实现天气弹窗
                console.log('创建原生DOM天气弹窗...');

                // 移除可能已存在的弹窗
                const existingPopup = document.getElementById('weather-popup-container');
                if (existingPopup) {
                    document.body.removeChild(existingPopup);
                    console.log('已移除旧弹窗');
                }

                // 创建新弹窗容器
                const container = document.createElement('div');
                container.id = 'weather-popup-container';
                container.style.position = 'fixed';
                container.style.zIndex = '99999';
                container.style.top = '120px';
                container.style.left = '120px';
                container.style.backgroundColor = 'white';
                container.style.width = '350px';
                container.style.borderRadius = '8px';
                container.style.boxShadow = '0 0 20px rgba(0,0,0,0.3)';
                container.style.overflow = 'hidden';

                // 创建弹窗头部
                const header = document.createElement('div');
                header.style.backgroundColor = '#1890ff';
                header.style.color = 'white';
                header.style.padding = '12px 16px';
                header.style.display = 'flex';
                header.style.justifyContent = 'space-between';
                header.style.alignItems = 'center';
                header.style.fontWeight = 'bold';
                header.style.cursor = 'move'; // 指示可拖动

                // 添加标题
                const title = document.createElement('div');
                title.textContent = `${cityName} 天气信息`;
                header.appendChild(title);

                // 添加关闭按钮
                const closeBtn = document.createElement('button');
                closeBtn.textContent = '×';
                closeBtn.style.background = 'none';
                closeBtn.style.border = 'none';
                closeBtn.style.color = 'white';
                closeBtn.style.fontSize = '24px';
                closeBtn.style.cursor = 'pointer';
                closeBtn.style.lineHeight = '24px';
                closeBtn.style.padding = '0';
                closeBtn.style.width = '24px';
                closeBtn.style.height = '24px';
                closeBtn.style.display = 'flex';
                closeBtn.style.justifyContent = 'center';
                closeBtn.style.alignItems = 'center';
                closeBtn.onclick = () => {
                    document.body.removeChild(container);
                    console.log('弹窗已关闭');
                };
                header.appendChild(closeBtn);

                // 添加头部到容器
                container.appendChild(header);

                // 创建内容区域
                const content = document.createElement('div');
                content.style.padding = '16px';

                // 手动创建天气内容
                const weatherContent = document.createElement('div');
                weatherContent.style.fontFamily = 'Arial, sans-serif';

                // 添加加载指示器
                const loadingDiv = document.createElement('div');
                loadingDiv.style.display = 'flex';
                loadingDiv.style.flexDirection = 'column';
                loadingDiv.style.alignItems = 'center';
                loadingDiv.style.justifyContent = 'center';
                loadingDiv.style.padding = '20px';

                const spinner = document.createElement('div');
                spinner.style.width = '40px';
                spinner.style.height = '40px';
                spinner.style.border = '4px solid rgba(0,0,0,0.1)';
                spinner.style.borderRadius = '50%';
                spinner.style.borderTopColor = '#1890ff';
                spinner.style.animation = 'spin 1s linear infinite';

                const style = document.createElement('style');
                style.textContent = `
                    @keyframes spin {
                        to { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);

                const loadingText = document.createElement('div');
                loadingText.textContent = '加载天气数据中...';
                loadingText.style.marginTop = '10px';
                loadingText.style.color = '#666';

                loadingDiv.appendChild(spinner);
                loadingDiv.appendChild(loadingText);
                weatherContent.appendChild(loadingDiv);

                content.appendChild(weatherContent);
                container.appendChild(content);

                // 添加到body
                document.body.appendChild(container);
                console.log('天气弹窗已添加到DOM');

                // 实现拖拽功能
                let isDragging = false;
                let offsetX, offsetY;

                header.onmousedown = (e) => {
                    isDragging = true;
                    offsetX = e.clientX - container.getBoundingClientRect().left;
                    offsetY = e.clientY - container.getBoundingClientRect().top;
                    header.style.cursor = 'grabbing';
                };

                document.onmousemove = (e) => {
                    if (isDragging) {
                        container.style.left = (e.clientX - offsetX) + 'px';
                        container.style.top = (e.clientY - offsetY) + 'px';
                    }
                };

                document.onmouseup = () => {
                    if (isDragging) {
                        isDragging = false;
                        header.style.cursor = 'move';
                    }
                };

                // 获取天气数据并更新内容
                setTimeout(() => {
                    this.fetchWeatherData(cityName).then(weatherData => {
                        // 清除加载指示器
                        weatherContent.innerHTML = '';

                        // 创建天气内容
                        const mainInfo = document.createElement('div');
                        mainInfo.style.display = 'flex';
                        mainInfo.style.justifyContent = 'space-between';
                        mainInfo.style.alignItems = 'center';
                        mainInfo.style.marginBottom = '15px';

                        const temperature = document.createElement('div');
                        temperature.style.fontSize = '36px';
                        temperature.style.fontWeight = 'bold';
                        temperature.style.color = '#1890ff';
                        temperature.textContent = `${weatherData.temperature}°C`;

                        const weatherIcon = document.createElement('img');
                        weatherIcon.src = `http://openweathermap.org/img/wn/${weatherData.icon}@2x.png`;
                        weatherIcon.style.width = '64px';
                        weatherIcon.style.height = '64px';

                        mainInfo.appendChild(temperature);
                        mainInfo.appendChild(weatherIcon);

                        const description = document.createElement('div');
                        description.style.fontSize = '18px';
                        description.style.marginBottom = '15px';
                        description.style.color = '#555';
                        description.textContent = weatherData.description;

                        const details = document.createElement('div');
                        details.style.display = 'flex';
                        details.style.justifyContent = 'space-between';
                        details.style.padding = '10px';
                        details.style.backgroundColor = '#f5f5f5';
                        details.style.borderRadius = '8px';
                        details.style.marginBottom = '10px';

                        // 创建湿度
                        const humidity = this.createDetailItem('湿度', `${weatherData.humidity}%`);
                        // 创建风速
                        const windSpeed = this.createDetailItem('风速', `${weatherData.windSpeed} m/s`);
                        // 创建气压
                        const pressure = this.createDetailItem('气压', `${weatherData.pressure} hPa`);

                        details.appendChild(humidity);
                        details.appendChild(windSpeed);
                        details.appendChild(pressure);

                        const updateTime = document.createElement('div');
                        updateTime.style.fontSize = '12px';
                        updateTime.style.color = '#999';
                        updateTime.style.textAlign = 'center';
                        updateTime.style.marginTop = '15px';
                        updateTime.innerHTML = `更新时间: ${weatherData.updateTime}`;
                        
                        // 添加数据来源标识
                        if (weatherData.is_mock) {
                            const mockIndicator = document.createElement('span');
                            mockIndicator.style.color = '#ff7875';
                            mockIndicator.style.marginLeft = '5px';
                            mockIndicator.textContent = '(模拟数据)';
                            updateTime.appendChild(mockIndicator);
                        } else if (weatherData.is_real) {
                            const realIndicator = document.createElement('span');
                            realIndicator.style.color = '#52c41a';
                            realIndicator.style.marginLeft = '5px';
                            realIndicator.textContent = '(真实数据)';
                            updateTime.appendChild(realIndicator);
                        }

                        weatherContent.appendChild(mainInfo);
                        weatherContent.appendChild(description);
                        weatherContent.appendChild(details);
                        weatherContent.appendChild(updateTime);

                        console.log('天气数据已更新到弹窗');
                    }).catch(error => {
                        console.error('获取天气数据失败:', error);

                        // 显示错误信息
                        weatherContent.innerHTML = '';

                        const errorDiv = document.createElement('div');
                        errorDiv.style.display = 'flex';
                        errorDiv.style.alignItems = 'center';
                        errorDiv.style.padding = '15px';
                        errorDiv.style.backgroundColor = '#fff2f0';
                        errorDiv.style.border = '1px solid #ffccc7';
                        errorDiv.style.borderRadius = '4px';

                        const errorIcon = document.createElement('div');
                        errorIcon.textContent = '!';
                        errorIcon.style.width = '24px';
                        errorIcon.style.height = '24px';
                        errorIcon.style.backgroundColor = '#ff4d4f';
                        errorIcon.style.color = 'white';
                        errorIcon.style.borderRadius = '50%';
                        errorIcon.style.display = 'flex';
                        errorIcon.style.alignItems = 'center';
                        errorIcon.style.justifyContent = 'center';
                        errorIcon.style.fontWeight = 'bold';
                        errorIcon.style.marginRight = '10px';

                        const errorMsg = document.createElement('div');
                        errorMsg.innerHTML = `<p>抱歉，无法获取天气数据</p><small>${error.message}</small>`;

                        errorDiv.appendChild(errorIcon);
                        errorDiv.appendChild(errorMsg);
                        weatherContent.appendChild(errorDiv);
                    });
                }, 300);

            } catch (error) {
                console.error('创建天气弹窗失败:', error);
            }
        },

        // 创建天气详情项
        createDetailItem(label, value) {
            const item = document.createElement('div');
            item.style.textAlign = 'center';
            item.style.flex = '1';

            const labelDiv = document.createElement('div');
            labelDiv.style.fontSize = '12px';
            labelDiv.style.color = '#888';
            labelDiv.style.marginBottom = '5px';
            labelDiv.textContent = label;

            const valueDiv = document.createElement('div');
            valueDiv.style.fontSize = '16px';
            valueDiv.style.fontWeight = '500';
            valueDiv.textContent = value;

            item.appendChild(labelDiv);
            item.appendChild(valueDiv);

            return item;
        },

        // 获取天气数据
        async fetchWeatherData(cityName) {
            console.log('获取城市天气数据:', cityName);

            try {
                // 使用API获取真实天气数据
                const response = await api.weather.getByCity(cityName);
                console.log('API返回的天气数据:', response);
                
                // 安全地获取更新时间
                let formattedUpdateTime = '未知';
                try {
                    if (response.updated_at) {
                        formattedUpdateTime = this.formatTime(new Date(response.updated_at));
                    } else {
                        formattedUpdateTime = this.formatTime(new Date());
                    }
                } catch (timeError) {
                    console.warn('日期格式化失败:', timeError);
                    formattedUpdateTime = '未知';
                }
                
                // 格式化返回的天气数据
                return {
                    temperature: response.temperature || response.temp,
                    humidity: response.humidity,
                    windSpeed: response.wind_speed || (response.wind && response.wind.speed),
                    pressure: response.pressure || 1013,
                    description: response.description,
                    icon: response.icon,
                    updateTime: formattedUpdateTime,
                    is_mock: response.is_mock,
                    is_real: response.is_real
                };
            } catch (error) {
                console.error('API获取天气数据失败:', error);
                throw error;
            }
        },

        // 格式化时间
        formatTime(date) {
            try {
                if (!(date instanceof Date) || isNaN(date.getTime())) {
                    return '未知时间';
                }
                
                const options = {
                    year: 'numeric',
                    month: 'numeric',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                };
                return new Intl.DateTimeFormat('zh-CN', options).format(date);
            } catch (e) {
                console.error('日期格式化错误:', e);
                return '未知时间';
            }
        },

        // 关闭天气窗口
        closeWeather() {
            console.log('关闭天气窗口');

            // 移除天气弹窗
            const popup = document.getElementById('weather-popup-container');
            if (popup) {
                document.body.removeChild(popup);
                console.log('已移除天气弹窗');
            }
        },

        // 恢复城市标记为普通状态
        restoreCityMarker(cityName) {
            if (!this.cityData[cityName] || !this.map) return;

            const cityCoords = this.cityData[cityName].coords;

            // 如果存在当前标记，先移除
            if (this.markers[cityName]) {
                this.map.removeLayer(this.markers[cityName]);
            }

            // 创建普通标记
            const icon = L.divIcon({
                className: 'city-marker',
                html: `<div class="marker-dot"></div><div class="city-label">${cityName}</div>`,
                iconSize: [60, 30],
                iconAnchor: [15, 15]
            });

            const marker = L.marker(cityCoords, { icon }).addTo(this.map);

            marker.on('click', () => {
                this.handleCityClick(cityName);
            });

            this.markers[cityName] = marker;
        },
        
        resetRoute() {
            this.resetSelection();
        }
    }
}
</script>

<style scoped>
.world-map-container {
    width: 100%;
    margin: 20px 0;
    display: flex;
    flex-direction: column;
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.map-wrapper {
    position: relative;
    width: 100%;
    height: 450px;
    margin-bottom: 20px;
    border: 1px solid #eaeaea;
    border-radius: 8px;
    overflow: visible;
    /* 改为visible允许子元素溢出 */
}

#world-map {
    width: 100%;
    height: 100%;
    border-radius: 8px;
    overflow: hidden;
    z-index: 1;
    /* 确保地图层级正确 */
    background-color: #f8f8f8;
    /* 给地图一个背景色，以便识别容器 */
}

/* 让地图图层可见 */
:deep(.leaflet-layer),
:deep(.leaflet-control-container) {
    z-index: 999 !important;
}

/* 让地图瓦片和控件可见 */
:deep(.leaflet-tile-pane),
:deep(.leaflet-control-container) {
    z-index: 400 !important;
}

.route-info {
    position: absolute;
    bottom: 20px;
    right: 20px;
    z-index: 1000;
}

.route-card {
    background: rgba(255, 255, 255, 0.85);
    padding: 15px;
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    backdrop-filter: blur(4px);
    border: 1px solid rgba(255, 255, 255, 0.5);
}

.route-card h4 {
    margin-top: 0;
    color: #1890ff;
    border-bottom: 1px solid #f0f0f0;
    padding-bottom: 8px;
}

.route-details p {
    margin: 8px 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.popular-cities {
    margin-top: 10px;
}

.city-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 10px;
}

.city-tag {
    cursor: pointer;
    transition: all 0.3s;
}

.city-tag:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

/* 地图标记样式 */
:deep(.city-marker) {
    text-align: center;
    transform: translateY(-15px);
}

:deep(.marker-dot) {
    width: 12px;
    height: 12px;
    background-color: #5e5e5e;
    border-radius: 50%;
    margin: 0 auto 5px;
    box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.8), 0 0 10px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
    animation: pulse 2s infinite;
}

:deep(.city-label) {
    background-color: rgba(255, 255, 255, 0.8);
    padding: 3px 6px;
    border-radius: 4px;
    font-size: 12px;
    color: #333;
    font-weight: bold;
    white-space: nowrap;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    transition: all 0.3s;
}

:deep(.city-marker:hover .city-label) {
    transform: translateY(-3px);
    background-color: rgba(255, 255, 255, 0.9);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

:deep(.city-marker:hover .marker-dot) {
    transform: scale(1.2);
}

:deep(.from-city .marker-dot) {
    background-color: #1890ff;
    width: 16px;
    height: 16px;
    animation: pulse-blue 1.5s infinite;
}

:deep(.to-city .marker-dot) {
    background-color: #f5222d;
    width: 16px;
    height: 16px;
    box-shadow: 0 0 0 4px rgba(245, 34, 45, 0.3), 0 0 10px rgba(245, 34, 45, 0.5);
    animation: pulse-red 1.5s infinite;
}

@keyframes pulse {
    0% {
        box-shadow: 0 0 0 0 rgba(94, 94, 94, 0.4);
    }
    70% {
        box-shadow: 0 0 0 6px rgba(94, 94, 94, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(94, 94, 94, 0);
    }
}

/* 飞机标记样式 */
:deep(.plane-marker) {
    background: transparent;
}

:deep(.plane-icon) {
    font-size: 20px;
    color: #1890ff;
    filter: drop-shadow(0 0 2px rgba(0, 0, 0, 0.5));
    animation: float 3s ease-in-out infinite;
}

:deep(.el-icon-airplane) {
    display: inline-block;
}

/* 动画航线样式 */
:deep(.animated-route) {
    stroke-dasharray: 10 10;
    animation: dash 30s linear infinite;
}

.map-loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(255, 255, 255, 0.8);
    z-index: 1000;
    display: flex;
    justify-content: center;
    align-items: center;
}

.loading-message,
.error-message {
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    background-color: #fff;
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.loading-message {
    flex-direction: column;
}

.loading-message .el-icon {
    font-size: 40px;
    margin-bottom: 10px;
}

.loading-message span {
    font-size: 16px;
    font-weight: bold;
}

.error-message {
    flex-direction: column;
}

.error-message .el-icon {
    font-size: 40px;
    margin-bottom: 10px;
}

.error-message span {
    font-size: 16px;
    font-weight: bold;
}

.error-message .el-button {
    margin-top: 10px;
}

/* 天气弹窗 */
.weather-popup {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 9999;
    /* 增加z-index确保在所有地图层上方 */
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    width: 320px;
    /* 加宽弹窗 */
    max-width: 90%;
    overflow: hidden;
    animation: fadeIn 0.3s ease-in-out;
    display: flex;
    /* 确保使用flex布局 */
    flex-direction: column;
    pointer-events: auto;
    /* 确保弹窗可以接收鼠标事件 */
}

.weather-popup.active {
    transform: scale(1);
    opacity: 1;
}

.weather-popup.fade-out {
    animation: fadeOut 0.3s ease-in-out;
}

@keyframes fadeOut {
    from {
        opacity: 1;
        transform: translateY(0);
    }

    to {
        opacity: 0;
        transform: translateY(-10px);
    }
}

.weather-popup-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 15px;
    background-color: #1890ff;
    color: white;
    font-weight: bold;
    width: 100%;
}

.close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
    padding: 0;
    line-height: 1;
}

.weather-popup-content {
    padding: 15px;
    width: 100%;
    max-height: 350px;
    overflow-y: auto;
    background-color: white;
}

/* 确保地图容器中的事件正确传递 */
.map-wrapper {
    position: relative;
    width: 100%;
    height: 450px;
    margin-bottom: 20px;
    border: 1px solid #eaeaea;
    border-radius: 8px;
    overflow: visible;
    /* 改为visible允许子元素溢出 */
}

/* 提升地图弹窗层级 */
#weather-popup {
    position: fixed;
    /* 改为fixed定位，确保在整个视口中定位 */
    top: 50px;
    left: 50px;
    z-index: 10000 !important;
    /* 更高的z-index */
}

/* 让地图图层和控件正确显示 */
:deep(.leaflet-pane),
:deep(.leaflet-control-container) {
    z-index: 900 !important;
}

/* 天气组件内部样式，确保内部元素显示正确 */
:deep(.city-weather-info) {
    width: 100%;
    background-color: white;
    color: #333;
}

/* 动画定义 */
@keyframes pulse-blue {
    0% {
        box-shadow: 0 0 0 0 rgba(24, 144, 255, 0.6);
    }

    70% {
        box-shadow: 0 0 0 10px rgba(24, 144, 255, 0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(24, 144, 255, 0);
    }
}

@keyframes pulse-red {
    0% {
        box-shadow: 0 0 0 0 rgba(245, 34, 45, 0.6);
    }

    70% {
        box-shadow: 0 0 0 10px rgba(245, 34, 45, 0);
    }

    100% {
        box-shadow: 0 0 0 0 rgba(245, 34, 45, 0);
    }
}

@keyframes float {
    0% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-5px);
    }

    100% {
        transform: translateY(0px);
    }
}

@keyframes dash {
    to {
        stroke-dashoffset: 1000;
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* 添加新的起点终点标记样式 */
:deep(.city-point-marker) {
    background: transparent;
}

:deep(.city-point) {
    width: 100%;
    height: 100%;
    border-radius: 50%;
}

:deep(.from-point) {
    background-color: #1890ff;
    box-shadow: 0 0 0 4px rgba(24, 144, 255, 0.3), 0 0 10px rgba(24, 144, 255, 0.5);
    animation: pulse-blue 1.5s infinite;
}

:deep(.to-point) {
    background-color: #f5222d;
    box-shadow: 0 0 0 4px rgba(245, 34, 45, 0.3), 0 0 10px rgba(245, 34, 45, 0.5);
    animation: pulse-red 1.5s infinite;
}

/* 强化航线动画 */
:deep(.animated-route) {
    stroke-dasharray: 10 10;
    animation: dash 15s linear infinite;
    filter: drop-shadow(0 0 2px rgba(24, 144, 255, 0.5));
}

.route-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
}

:deep(.el-button--danger) {
    background-color: #ff4d4f;
    border-color: #ff4d4f;
    color: white;
}

:deep(.el-button--danger:hover) {
    background-color: #ff7875;
    border-color: #ff7875;
}
</style>