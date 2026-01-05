import { ref, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import api from '@/services/api'

export function useMapManager() {
  const map = ref(null)
  const mapStatus = ref('loading') // 'loading', 'loaded', 'error'
  const dataStatus = ref('idle') // 'idle', 'loading', 'loaded', 'error'
  const dataError = ref(null)
  const markers = ref({})
  const routeLine = ref(null)
  const fromPointMarker = ref(null)
  const toPointMarker = ref(null)

  // 城市数据 - 从 API 获取
  const cityData = ref({})

  // 从 API 获取城市数据
  const fetchCityData = async () => {
    dataStatus.value = 'loading'
    dataError.value = null
    
    try {
      const response = await api.core.getCities()
      const cities = response.results || response || []
      
      // 转换为地图需要的格式
      const cityMap = {}
      cities.forEach(city => {
        if (city.latitude && city.longitude) {
          cityMap[city.name] = {
            code: city.code || '',
            coords: [parseFloat(city.latitude), parseFloat(city.longitude)]
          }
        }
      })
      
      cityData.value = cityMap
      dataStatus.value = 'loaded'
      return cityMap
    } catch (error) {
      console.error('获取城市数据失败:', error)
      dataStatus.value = 'error'
      dataError.value = error.message || '获取城市数据失败'
      return {}
    }
  }

  const initMap = async (mapContainer) => {
    try {
      mapStatus.value = 'loading'

      if (!mapContainer) {
        console.error('地图容器元素不存在')
        mapStatus.value = 'error'
        return
      }

      // 确保容器有尺寸
      if (mapContainer.clientWidth === 0 || mapContainer.clientHeight === 0) {
        mapContainer.style.width = '100%'
        mapContainer.style.height = '450px'
      }

      // 等待 DOM 更新
      await new Promise(resolve => setTimeout(resolve, 50))

      // 再次检查容器是否仍然存在于 DOM 中
      if (!document.body.contains(mapContainer)) {
        console.error('地图容器已从 DOM 中移除')
        mapStatus.value = 'error'
        return
      }

      // 创建地图实例
      map.value = L.map(mapContainer, {
        center: [30, 105],
        zoom: 3,
        minZoom: 2,
        maxBounds: [[-90, -180], [90, 180]],
        zoomControl: false,
        attributionControl: false
      })

      // 确保地图实例创建成功
      if (!map.value) {
        console.error('地图实例创建失败')
        mapStatus.value = 'error'
        return
      }

      // 添加控件
      L.control.zoom({ position: 'topright' }).addTo(map.value)
      L.control.attribution({ position: 'bottomright' }).addTo(map.value)

      // 加载地图图层
      loadMapSource()

    } catch (error) {
      console.error('地图初始化失败:', error)
      mapStatus.value = 'error'
      map.value = null
    }
  }

  const loadMapSource = (sourceIndex = 0) => {
    // 确保地图实例存在
    if (!map.value) {
      console.error('地图实例不存在，无法加载图层')
      mapStatus.value = 'error'
      return
    }

    const mapSources = [
      {
        name: '高德地图',
        url: 'https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
        options: {
          attribution: '&copy; 高德地图',
          maxZoom: 18
        }
      },
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
      }
    ]

    if (sourceIndex >= mapSources.length) {
      mapStatus.value = 'error'
      return
    }

    const source = mapSources[sourceIndex]
    const tileLayer = L.tileLayer(source.url, source.options)

    let hasSuccessfulLoad = false

    tileLayer.on('tileload', async () => {
      if (!hasSuccessfulLoad) {
        hasSuccessfulLoad = true
        mapStatus.value = 'loaded'
        // 地图加载成功后获取城市数据并添加标记
        await fetchCityData()
        if (dataStatus.value === 'loaded' && map.value) {
          addCityMarkers()
        }
      }
    })

    tileLayer.on('tileerror', () => {
      if (!hasSuccessfulLoad && map.value) {
        tileLayer.remove()
        loadMapSource(sourceIndex + 1)
      }
    })

    tileLayer.addTo(map.value)

    setTimeout(() => {
      if (!hasSuccessfulLoad && map.value) {
        tileLayer.remove()
        loadMapSource(sourceIndex + 1)
      }
    }, 5000)
  }

  // 城市点击回调函数
  const onCityClickCallback = ref(null)

  const setOnCityClick = (callback) => {
    onCityClickCallback.value = callback
  }

  const addCityMarkers = () => {
    try {
      // 清理现有标记
      Object.values(markers.value).forEach(marker => {
        if (map.value?.hasLayer(marker)) {
          marker.off('click') // 移除旧的点击事件
          map.value.removeLayer(marker)
        }
      })
      markers.value = {}

      // 创建新标记
      Object.entries(cityData.value).forEach(([cityName, data]) => {
        const icon = L.divIcon({
          className: 'city-marker',
          html: `<div class="marker-dot"></div><div class="city-label">${cityName}</div>`,
          iconSize: [60, 30],
          iconAnchor: [15, 15]
        })

        const marker = L.marker(data.coords, { icon }).addTo(map.value)
        
        // 绑定点击事件
        marker.on('click', () => {
          if (onCityClickCallback.value) {
            onCityClickCallback.value(cityName)
          }
        })
        
        markers.value[cityName] = marker
      })
    } catch (error) {
      console.error('添加城市标记失败:', error)
    }
  }

  const highlightMarker = (cityName, type) => {
    const marker = markers.value[cityName]
    const city = cityData.value[cityName]
    if (!city) return null
    
    const cityCoords = city.coords

    if (marker) {
      map.value.removeLayer(marker)
    }

    // 清除之前的标记
    if (type === 'from' && fromPointMarker.value) {
      map.value.removeLayer(fromPointMarker.value)
      fromPointMarker.value = null
    }

    if (type === 'to' && toPointMarker.value) {
      map.value.removeLayer(toPointMarker.value)
      toPointMarker.value = null
    }

    // 创建高亮标记
    const highlightClass = type === 'from' ? 'from-city' : 'to-city'
    const highlightIcon = L.divIcon({
      className: `city-marker ${highlightClass}`,
      html: `<div class="marker-dot ${highlightClass}"></div><div class="city-label">${cityName}</div>`,
      iconSize: [60, 30],
      iconAnchor: [15, 15]
    })

    const newMarker = L.marker(cityCoords, { icon: highlightIcon }).addTo(map.value)
    markers.value[cityName] = newMarker

    if (type === 'from') {
      fromPointMarker.value = newMarker
    } else if (type === 'to') {
      toPointMarker.value = newMarker
    }

    return newMarker
  }

  const drawRoute = (fromCity, toCity) => {
    if (!fromCity || !toCity || !map.value) return null

    try {
      const fromCityData = cityData.value[fromCity]
      const toCityData = cityData.value[toCity]
      
      if (!fromCityData || !toCityData) return null
      
      const fromCoords = fromCityData.coords
      const toCoords = toCityData.coords

      // 移除已有路线
      if (routeLine.value) {
        map.value.removeLayer(routeLine.value)
      }

      // 创建新路线
      routeLine.value = L.polyline([fromCoords, toCoords], {
        color: '#1890ff',
        weight: 4,
        opacity: 0.8,
        dashArray: '10, 10',
        dashOffset: '0',
        lineCap: 'round',
        lineJoin: 'round',
        className: 'animated-route'
      }).addTo(map.value)

      // 调整视图
      try {
        map.value.fitBounds([fromCoords, toCoords], {
          padding: [50, 50],
          animate: true,
          duration: 0.5
        })
      } catch (error) {
        map.value.setView(
          [(fromCoords[0] + toCoords[0]) / 2, (fromCoords[1] + toCoords[1]) / 2],
          3
        )
      }

      return calculateDistance(fromCoords[0], fromCoords[1], toCoords[0], toCoords[1])
    } catch (error) {
      console.error('绘制航线失败:', error)
      return null
    }
  }

  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371 // 地球半径，单位公里
    const dLat = deg2rad(lat2 - lat1)
    const dLon = deg2rad(lon2 - lon1)
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(deg2rad(lat1)) *
        Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  const deg2rad = deg => {
    return deg * (Math.PI / 180)
  }

  const resetSelection = () => {
    try {
      if (routeLine.value && map.value) {
        map.value.removeLayer(routeLine.value)
        routeLine.value = null
      }

      if (fromPointMarker.value && map.value) {
        map.value.removeLayer(fromPointMarker.value)
        fromPointMarker.value = null
      }

      if (toPointMarker.value && map.value) {
        map.value.removeLayer(toPointMarker.value)
        toPointMarker.value = null
      }

      addCityMarkers()
    } catch (error) {
      console.error('重置选择失败:', error)
      setTimeout(() => {
        if (map.value && mapStatus.value === 'loaded') {
          addCityMarkers()
        }
      }, 100)
    }
  }

  const cleanup = () => {
    try {
      if (map.value) {
        if (routeLine.value) {
          map.value.removeLayer(routeLine.value)
        }
        if (fromPointMarker.value) {
          map.value.removeLayer(fromPointMarker.value)
        }
        if (toPointMarker.value) {
          map.value.removeLayer(toPointMarker.value)
        }

        map.value.eachLayer(layer => {
          map.value.removeLayer(layer)
        })

        map.value.off()
        map.value.remove()
        map.value = null
      }
    } catch (error) {
      console.error('清理地图资源失败:', error)
    }
  }

  // 重新加载城市数据
  const reloadCityData = async () => {
    await fetchCityData()
    if (dataStatus.value === 'loaded' && map.value) {
      addCityMarkers()
    }
  }

  onBeforeUnmount(() => {
    cleanup()
  })

  return {
    map,
    mapStatus,
    dataStatus,
    dataError,
    markers,
    cityData,
    initMap,
    fetchCityData,
    addCityMarkers,
    highlightMarker,
    drawRoute,
    calculateDistance,
    resetSelection,
    reloadCityData,
    setOnCityClick,
    cleanup
  }
}
