<template>
  <div class="world-map-container">
    <h3>全球航线选择</h3>
    <div class="map-wrapper">
      <div id="world-map" ref="worldMap"></div>

      <!-- 地图加载状态 -->
      <div v-if="mapStatus !== 'loaded' || dataStatus === 'loading'" class="map-loading-overlay">
        <div v-if="mapStatus === 'loading' || dataStatus === 'loading'" class="loading-message">
          <el-icon class="loading"><Loading /></el-icon>
          <span>{{ mapStatus === 'loading' ? '地图加载中...' : '城市数据加载中...' }}</span>
        </div>
        <div v-else-if="mapStatus === 'error'" class="error-message">
          <el-icon class="error"><Close /></el-icon>
          <span>地图加载失败，请刷新页面重试</span>
          <el-button type="primary" size="small" @click="reloadMap">重新加载</el-button>
        </div>
      </div>

      <!-- 数据加载错误提示 -->
      <div v-if="dataStatus === 'error' && mapStatus === 'loaded'" class="data-error-overlay">
        <div class="error-message">
          <el-icon class="error"><WarningFilled /></el-icon>
          <span>{{ dataError || '城市数据加载失败' }}</span>
          <el-button type="primary" size="small" @click="reloadCityData">重新加载</el-button>
        </div>
      </div>

      <!-- 空数据提示 -->
      <div v-if="dataStatus === 'loaded' && Object.keys(cityData).length === 0 && mapStatus === 'loaded'" class="empty-data-overlay">
        <div class="empty-message">
          <el-icon><Location /></el-icon>
          <span>暂无城市数据</span>
        </div>
      </div>

      <!-- 路线信息卡片 -->
      <route-info-card 
        v-if="dataStatus === 'loaded' && Object.keys(cityData).length > 0"
        :selected-route="selectedRoute"
        @select-route="selectThisRoute"
        @reset-route="resetRoute"
      />
    </div>

    <!-- 城市选择器 -->
    <city-selector 
      v-if="dataStatus === 'loaded' && Object.keys(cityData).length > 0"
      :selected-from-city="selectedFromCity"
      :selected-to-city="selectedToCity"
      @city-selected="handleCitySelection"
      ref="citySelector"
    />
  </div>
</template>

<script>
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { Loading, Close, WarningFilled, Location } from '@element-plus/icons-vue'
import RouteInfoCard from '@/components/map/RouteInfoCard.vue'
import CitySelector from '@/components/map/CitySelector.vue'
import { useMapManager } from '@/composables/useMapManager'

// 修复Leaflet默认图标问题
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
})

export default {
  name: 'WorldMapRoutes',
  components: {
    Loading,
    Close,
    WarningFilled,
    Location,
    RouteInfoCard,
    CitySelector
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
  setup() {
    const {
      map,
      mapStatus,
      dataStatus,
      dataError,
      markers,
      cityData,
      initMap,
      addCityMarkers,
      highlightMarker,
      drawRoute,
      resetSelection,
      reloadCityData,
      setOnCityClick
    } = useMapManager()

    return {
      map,
      mapStatus,
      dataStatus,
      dataError,
      markers,
      cityData,
      initMap,
      addCityMarkers,
      highlightMarker,
      drawRoute,
      resetSelection,
      reloadCityData,
      setOnCityClick
    }
  },
  data() {
    return {
      selectedRoute: null,
      selectedFromCity: null,
      selectedToCity: null
    }
  },
  mounted() {
    // 先注册城市点击回调
    this.setOnCityClick(this.handleCityClick)
    
    this.$nextTick(() => {
      const mapContainer = this.$refs.worldMap
      if (mapContainer) {
        mapContainer.style.height = '450px'
        setTimeout(() => {
          this.initMap(mapContainer)
          if (this.initialFrom && this.initialTo) {
            this.selectCities(this.initialFrom, this.initialTo)
          }
        }, 300)
      }
    })
  },
  methods: {
    handleCityClick(cityName) {
      if (!this.selectedFromCity) {
        // 第一次选择
        this.selectedFromCity = cityName;
        this.highlightMarker(cityName, 'from');
      } else if (!this.selectedToCity) {
        // 第二次选择
        if (cityName === this.selectedFromCity) {
          return; // 避免选择相同的城市
        }
        this.selectedToCity = cityName;
        this.highlightMarker(cityName, 'to');
        
        this.drawRouteAndSetSelection();
      } else {
        // 重置并重新选择
        this.resetSelection();
        this.selectedFromCity = cityName;
        this.highlightMarker(cityName, 'from');
      }
    },

    drawRouteAndSetSelection() {
      // 使用 composable 中的 drawRoute 方法
      const distance = this.drawRoute(this.selectedFromCity, this.selectedToCity);
      if (distance) {
        this.selectedRoute = {
          from: this.selectedFromCity,
          to: this.selectedToCity,
          distance: Math.round(distance)
        };
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

    handleCitySelection(city) {
      // 处理来自城市选择器的选择事件
      this.handleCityClick(city.name);
    },

    selectCities(fromCity, toCity) {
      if (this.cityData[fromCity] && this.cityData[toCity]) {
        this.selectedFromCity = fromCity;
        this.selectedToCity = toCity;

        this.highlightMarker(fromCity, 'from');
        this.highlightMarker(toCity, 'to');

        this.drawRouteAndSetSelection();
      }
    },

    reloadMap() {
      const mapContainer = this.$refs.worldMap;
      if (mapContainer) {
        this.initMap(mapContainer);
      }
    },

    resetRoute() {
      this.selectedRoute = null;
      this.selectedFromCity = null;
      this.selectedToCity = null;
      this.resetSelection();
    }
  }
}
</script>


<style scoped>
.world-map-container {
  width: 100%;
  margin: 0;
  display: flex;
  flex-direction: column;
  background: transparent;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
}

.map-wrapper {
  position: relative;
  width: 100%;
  height: 450px;
  margin-bottom: 20px;
  border: 1px solid #eaeaea;
  border-radius: 8px;
  overflow: visible;
}

#world-map {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;
  z-index: 1;
  background-color: #f8f8f8;
}

:deep(.leaflet-layer),
:deep(.leaflet-control-container) {
  z-index: 999 !important;
}

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

:deep(.animated-route) {
  stroke-dasharray: 10 10;
  animation: dash 30s linear infinite;
}

.map-loading-overlay,
.data-error-overlay,
.empty-data-overlay {
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
.error-message,
.empty-message {
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.loading-message .el-icon {
  font-size: 40px;
  color: #1890ff;
  animation: spin 1s linear infinite;
}

.error-message .el-icon {
  font-size: 40px;
  color: #f56c6c;
}

.empty-message .el-icon {
  font-size: 40px;
  color: #909399;
}

.loading-message span,
.error-message span,
.empty-message span {
  font-size: 16px;
  font-weight: bold;
  color: #606266;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

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
