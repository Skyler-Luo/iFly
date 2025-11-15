# iFly航空订票系统

一个基于Vue的航空订票系统前端项目。

## 项目说明

iFly是一个航空订票平台的前端应用，提供航班查询、预订、支付、行程管理等功能。

## 功能特点

- 航班搜索和筛选
- 航班预订流程
- 乘客信息管理
- 座位选择
- 订单管理
- 用户账户管理
- 在线支付

## 项目结构

```
ifly_web/
├── public/               # 静态资源
├── src/                  # 源代码
│   ├── assets/           # 项目资源文件
│   ├── components/       # 公共组件
│   │   ├── common/       # 通用组件
│   │   ├── flight/       # 航班相关组件
│   │   ├── booking/      # 预订相关组件
│   │   ├── profile/      # 用户相关组件
│   │   └── ...
│   ├── views/            # 页面视图
│   ├── router/           # 路由配置
│   ├── store/            # Vuex状态管理
│   ├── services/         # API服务
│   ├── utils/            # 工具函数
│   ├── App.vue           # 根组件
│   └── main.js           # 入口文件
├── package.json          # 项目依赖
└── README.md             # 项目说明
```

## 组件化重构

本项目进行了组件化重构，提取了以下复用组件：

### 通用组件
- `AuthBackground.vue` - 登录/注册背景动画组件
- `SocialLogin.vue` - 社交登录组件
- `SiteFooter.vue` - 页脚组件

### 首页组件
- `FeatureSection.vue` - 服务特点展示组件
- `TestimonialSection.vue` - 用户评价组件
- `DestinationsGrid.vue` - 热门目的地展示组件
- `FAQSection.vue` - 常见问题组件
- `AppDownload.vue` - 应用下载组件

### 预订相关组件
- `BookingSteps.vue` - 预订步骤指示器组件
- `FlightDetailCard.vue` - 航班详情卡片组件
- `PassengerForm.vue` - 乘客信息表单组件
- `ContactForm.vue` - 联系人信息表单组件
- `SeatMap.vue` - 座位选择组件

## 如何运行

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run serve

# 构建生产版本
npm run build
```

## 浏览器支持

支持所有主流的现代浏览器。

## 技术栈

- Vue 3
- Vuex
- Vue Router
- Element Plus
- Axios
