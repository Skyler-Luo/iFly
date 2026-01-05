import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 忽略 ResizeObserver 循环错误（ECharts 图表调整大小时的常见警告）
const resizeObserverErr = window.onerror
window.onerror = (message, ...args) => {
  if (typeof message === 'string' && message.includes('ResizeObserver loop')) {
    return true
  }
  return resizeObserverErr ? resizeObserverErr(message, ...args) : false
}

// 导入全局错误处理器
import errorHandler from './utils/errorHandler'

// 导入 Leaflet 样式
import './assets/main.css'
import './styles/responsive.css'
import './styles/animations.css'
import 'leaflet/dist/leaflet.css'

// 导入 ECharts 和 Vue-ECharts
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'

// 导入 ECharts 组件
import {
    CanvasRenderer
} from 'echarts/renderers'
import {
    BarChart,
    LineChart,
    PieChart,
    GaugeChart,
    RadarChart,
    ScatterChart,
    HeatmapChart,
    TreemapChart
} from 'echarts/charts'
import {
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    DataZoomComponent,
    ToolboxComponent,
    MarkLineComponent,
    MarkPointComponent
} from 'echarts/components'

// 全局注册必要的组件
use([
    CanvasRenderer,
    BarChart,
    LineChart,
    PieChart,
    GaugeChart,
    RadarChart,
    ScatterChart,
    HeatmapChart,
    TreemapChart,
    TitleComponent,
    TooltipComponent,
    LegendComponent,
    GridComponent,
    DataZoomComponent,
    ToolboxComponent,
    MarkLineComponent,
    MarkPointComponent
])

const app = createApp(App)

// 初始化全局错误处理器
errorHandler.init(app)

app.use(store)
app.use(router)
app.use(ElementPlus)

// 全局注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
    app.component(key, component)
}

// 全局注册 ECharts 组件
app.component('v-chart', ECharts)

app.mount('#app')
