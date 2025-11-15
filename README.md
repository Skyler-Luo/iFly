# iFly飞机订票系统

## 项目简介
iFly是一个基于Django+Vue.js开发的现代化飞机订票系统。该系统旨在提供用户友好的界面，实现航班信息的录入、查询、修改与管理等核心功能，支持订票、退票、航班余票查询以及客户资料的维护与管理。

## 技术栈
- **后端**：Django 5.x，Django REST Framework
- **前端**：Vue.js 3.x，Element Plus（用户界面和管理后台）
- **数据库**：SQLite（开发环境），PostgreSQL（生产环境推荐）
- **其他工具**：NPM，Webpack，Docker（可选）

## 功能特点
- **航班管理**
  - 航班信息录入、修改、删除
  - 按多种条件（航班号、城市、时间等）查询航班
  - 支持按起飞/到达时间范围筛选
  - 支持按价格、折扣率、总座位数、剩余座位数范围筛选
  - 航班状态管理（正常、已满、已起飞等），支持一键起飞/取消
  - 剩余座位自动管理（预订扣减、退订增加）
  - 支持批量导入/导出航班（CSV）
  - 定时任务自动更新航班状态
  
- **订票系统**
  - 在线购票
  - 退票处理
  - 票务状态查询
  - 价格与折扣管理
  - 支付与结算：集成支付宝、微信支付，支持自动退款与对账
  - **订票系统 API**
    - 创建订单 (可一次生成多张机票)：POST `/api/bookings/orders/`  
      请求示例：  
      ```json
      {
        "payment_method": "credit_card",
        "tickets": [
          {"flight": 1, "passenger": 2, "seat_number": "12A"},
          {"flight": 1, "passenger": 3, "seat_number": "12B"}
        ]
      }
      ```
    - 支付订单：POST `/api/bookings/orders/{order_id}/pay/`
    - 取消订单：POST `/api/bookings/orders/{order_id}/cancel/`
    - 查询订单列表：GET `/api/bookings/orders/`
    - 查询单个订单：GET `/api/bookings/orders/{order_id}/`
    - 查询机票列表：GET `/api/bookings/tickets/`
    - 退票：POST `/api/bookings/tickets/{ticket_id}/refund/`
    - 查询座位布局：GET `/api/flights/{flight_id}/seats/`
  
- **用户管理**
  - 客户信息注册与维护
  - 用户身份验证与授权
  - 个人订单历史查询
  - 常用乘客信息高级筛选与批量导入/导出（CSV）

- **系统特性**
  - 结构化数据存储
  - 高效检索算法
  - 响应式界面设计
  - 安全的用户数据保护
  - 应用内消息中心：系统通知、订单状态、航班变动提醒

- **智能推荐系统**
  - 基于用户历史行为的航班推荐
  - 价格波动预测
  - 个性化旅行方案推荐

- **数据分析与报表**
  - 销售数据可视化
  - 客流量分析
  - 航线热度分析
  - 经营状况报表生成
  - BI 仪表盘与实时监控
  - 自定义报表导出（Excel/CSV/PDF）

- **客户互动与评价**
  - 用户评分与评论
  - 客服聊天与工单系统
  - 应用内即时聊天支持

## 安装步骤

### 环境要求
- Python 3.12+
- Node.js 14+
- NPM 6+

### 后端设置
```bash
# 克隆项目
git clone https://github.com/yourusername/iFly.git
cd iFly

# 创建虚拟环境
python -m venv venv
# Windows激活虚拟环境
venv\Scripts\activate
# Linux/Mac激活虚拟环境
# source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
python manage.py migrate

# 创建管理员账户
python manage.py createsuperuser

# 运行开发服务器
python manage.py runserver
```

### 前端设置
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

## 使用说明

### 管理员操作
1. 访问 `http://localhost:8080/admin` 登录管理后台
2. 添加和管理航班信息
3. 查看系统订单和用户数据

### 用户操作
1. 访问 `http://localhost:8080` 打开用户界面
2. 注册/登录账户
3. 搜索可用航班
4. 预订机票并完成支付流程
5. 查看订单历史和管理个人信息

## 项目结构
```
iFly/
│
├── backend/                # Django后端
│   ├── flight/             # 航班应用
│   ├── booking/            # 订票应用
│   ├── accounts/           # 用户管理应用
│   ├── core/               # 核心功能
│   └── iFly/               # 项目设置
│
├── frontend/               # Vue.js前端
│   ├── public/             # 静态资源
│   ├── src/                # 源代码
│   │   ├── assets/         # 资源文件
│   │   ├── components/     # 组件
│   │   ├── views/          # 视图
│   │   │   ├── admin/      # 管理后台视图
│   │   │   └── client/     # 用户界面视图
│   │   ├── router/         # 路由配置
│   │   ├── store/          # Vuex存储
│   │   ├── services/       # API服务
│   │   └── App.vue         # 主应用组件
│   │
│   ├── package.json        # 依赖配置
│   └── vue.config.js       # Vue配置
│
├── requirements.txt        # 后端依赖
├── manage.py               # Django管理脚本
└── README.md               # 项目说明
```

## 数据库设计

### 核心数据表结构
 
#### 航班信息表 (Flight)
| 字段名          | 类型          | 说明                                 |
| --------------- | ------------- | ------------------------------------ |
| id              | Integer       | 主键，自增                           |
| flight_number   | Varchar(10)   | 航班编号，唯一                       |
| departure_city  | Varchar(50)   | 出发城市                             |
| arrival_city    | Varchar(50)   | 到达城市                             |
| departure_time  | DateTime      | 起飞时间                             |
| arrival_time    | DateTime      | 预计到达时间                         |
| price           | Decimal(10,2) | 标准票价                             |
| discount        | Decimal(3,2)  | 折扣率，如0.85表示85折               |
| capacity        | Integer       | 总座位数                             |
| available_seats | Integer       | 可用座位数                           |
| status          | Varchar(20)   | 航班状态：正常、已满、已起飞、取消等 |
| aircraft_type   | Varchar(50)   | 飞机型号                             |
| created_at      | DateTime      | 记录创建时间                         |
| updated_at      | DateTime      | 记录更新时间                         |

#### 用户信息表 (User)
| 字段名     | 类型         | 说明                         |
| ---------- | ------------ | ---------------------------- |
| id         | Integer      | 主键，自增                   |
| username   | Varchar(50)  | 用户名，唯一                 |
| password   | Varchar(128) | 密码（加密存储）             |
| email      | Varchar(100) | 电子邮箱，唯一               |
| phone      | Varchar(20)  | 联系电话                     |
| role       | Varchar(20)  | 用户角色：普通用户、管理员等 |
| created_at | DateTime     | 账户创建时间                 |
| last_login | DateTime     | 最后登录时间                 |

#### 乘客信息表 (Passenger)
| 字段名          | 类型        | 说明                     |
| --------------- | ----------- | ------------------------ |
| id              | Integer     | 主键，自增               |
| user_id         | Integer     | 外键，关联用户表         |
| name            | Varchar(50) | 乘客姓名                 |
| id_card         | Varchar(18) | 身份证号码，唯一         |
| passport_number | Varchar(20) | 护照号码（国际航班可选） |
| gender          | Varchar(10) | 性别                     |
| birth_date      | Date        | 出生日期                 |
| created_at      | DateTime    | 记录创建时间             |
| updated_at      | DateTime    | 记录更新时间             |

#### 订单表 (Order)
| 字段名         | 类型          | 说明                               |
| -------------- | ------------- | ---------------------------------- |
| id             | Integer       | 主键，自增                         |
| order_number   | Varchar(20)   | 订单编号，唯一                     |
| user_id        | Integer       | 外键，关联用户表                   |
| total_amount   | Decimal(10,2) | 订单总金额                         |
| status         | Varchar(20)   | 订单状态：待付款、已付款、已取消等 |
| payment_method | Varchar(20)   | 支付方式                           |
| created_at     | DateTime      | 订单创建时间                       |
| paid_at        | DateTime      | 支付时间                           |

#### 机票表 (Ticket)
| 字段名        | 类型          | 说明                             |
| ------------- | ------------- | -------------------------------- |
| id            | Integer       | 主键，自增                       |
| ticket_number | Varchar(15)   | 机票编号，唯一                   |
| order_id      | Integer       | 外键，关联订单表                 |
| flight_id     | Integer       | 外键，关联航班表                 |
| passenger_id  | Integer       | 外键，关联乘客表                 |
| seat_number   | Varchar(10)   | 座位号                           |
| price         | Decimal(10,2) | 实际支付价格                     |
| status        | Varchar(20)   | 票务状态：有效、已退票、已使用等 |
| created_at    | DateTime      | 记录创建时间                     |
| updated_at    | DateTime      | 记录更新时间                     |

#### 系统日志表 (SystemLog)
| 字段名     | 类型        | 说明             |
| ---------- | ----------- | ---------------- |
| id         | Integer     | 主键，自增       |
| user_id    | Integer     | 外键，关联用户表 |
| action     | Varchar(50) | 操作类型         |
| detail     | Text        | 操作详情         |
| ip_address | Varchar(50) | IP地址           |
| created_at | DateTime    | 日志创建时间     |

### 表关系
- 一个用户可以有多个乘客信息（一对多）
- 一个用户可以创建多个订单（一对多）
- 一个订单可以包含多张机票（一对多）
- 一张机票对应一个航班和一个乘客（多对一）

## 系统页面设计

### 用户端页面

#### 首页
- 航班搜索模块（出发地、目的地、日期选择器）
- 热门航线推荐
- 最新优惠信息展示
- 快速登录/注册入口

#### 航班搜索结果页
- 航班列表展示（航班号、起降时间、票价、折扣、剩余座位等）
- 多条件筛选功能（价格区间、起飞时间段、航空公司等）
- 排序功能（按价格、时间等）
- 选择航班进入订票流程

#### 航班详情页
- 航班具体信息展示
- 座位选择界面
- 价格明细
- 相关政策说明（退改签规则等）

#### 订单填写页
- 乘客信息填写/选择
- 联系人信息确认
- 附加服务选择（行李、餐食等）
- 价格汇总

#### 支付页面
- 支付方式选择
- 订单信息确认
- 支付流程引导
- 支付结果反馈

#### 用户中心
- **个人资料管理**
  - 基本信息修改
  - 密码修改
  - 联系方式管理
  
- **我的订单**
  - 订单列表展示
  - 订单详情查看
  - 订单状态跟踪
  - 退票/改签申请
  
- **常用乘客管理**
  - 乘客信息列表
  - 添加/编辑/删除乘客
  
- **消息中心**
  - 系统通知
  - 订单状态更新提醒
  - 航班变动提醒

### 管理员端页面

#### 仪表盘
- 系统概览数据
- 近期销售统计
- 订单处理情况
- 重要通知与提醒

#### 航班管理
- 航班列表与搜索
- 添加/编辑航班信息
- 航班状态管理
- 余票情况监控
- 高级筛选（起飞/到达时间范围）
- 预订/退票座位操作
- 一键起飞/取消航班
- 批量导入/导出（CSV）
- 定时任务：自动更新航班状态

#### 订单管理
- 订单列表与搜索
- 订单详情查看
- 订单状态修改
- 退改签处理

#### 用户管理
- 用户列表与搜索
- 用户详情查看
- 用户权限管理
- 账户状态控制
- 常用乘客信息高级筛选与批量导入/导出

#### 系统设置
- 基本参数配置
- 折扣规则设置
- 系统维护选项

#### 数据分析与报表
- 销售数据分析
- 客流量统计
- 航线热度分析
- 自定义报表生成

## 开发计划
- [x] 系统设计与架构规划
- [ ] 数据库模型设计
- [ ] 后端API开发
- [ ] 前端界面实现
- [ ] 用户认证与授权
- [ ] 订票流程实现
- [ ] 系统测试与优化
- [ ] 部署文档编写

## 贡献指南
我们欢迎所有形式的贡献，包括功能请求、bug报告和代码贡献。请遵循以下步骤：

1. Fork项目
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个Pull Request

## 许可证
本项目基于MIT许可证开源 - 详情请参阅 [LICENSE](LICENSE) 文件

## 最新更新

### 用户头像及个人资料功能增强

在最新版本中，我们为系统添加了用户头像和扩展了个人资料功能：

#### 后端更新：

1. 用户模型扩展：
   - 添加了头像字段 (`avatar`)
   - 添加了真实姓名字段 (`real_name`)
   - 添加了身份证号字段 (`id_card`)
   - 添加了性别字段 (`gender`)
   - 添加了地址字段 (`address`)

2. 用户序列化器增强：
   - 添加了头像URL字段，方便前端获取完整的头像URL
   - 增加了表单验证功能，对身份证、手机号等进行格式验证

3. API增强：
   - 支持基于base64的图片上传
   - 支持标准的文件上传（通过multipart/form-data）
   - 登录接口现在返回完整的用户信息

#### 前端更新：

1. 用户个人中心组件优化：
   - 添加了头像上传、预览和删除功能
   - 增加了上传进度条展示
   - 添加了图片验证（类型和大小）

2. API服务增强：
   - 新增专用的文件上传客户端
   - 支持头像上传专用接口

#### 如何使用：

对于前端开发者，可以通过以下方式访问用户头像：

1. 直接访问API返回的`avatar_url`字段
2. 上传头像可以使用两种方式：
   - 使用base64编码，通过`updateProfile` API
   - 使用文件上传，通过`uploadAvatar` API

#### 安装和配置：

1. 确保安装了Pillow包：`pip install Pillow`
2. 创建媒体目录：`mkdir -p media/avatars`

#### 示例代码：

```javascript
// 使用base64方式上传
const reader = new FileReader();
reader.readAsDataURL(imageFile);
reader.onload = async () => {
    const formData = {
        avatar: reader.result,
        // 其他用户信息字段
    };
    await api.auth.updateProfile(formData);
};

// 使用multipart方式上传
const formData = new FormData();
formData.append('avatar', imageFile);
await api.auth.uploadAvatar(formData);
```

#### 后续优化计划：

1. 添加头像裁剪功能
2. 实现头像缓存和CDN支持
3. 实现头像缩略图自动生成
4. 添加更多的个人资料验证和隐私设置
5. 支持社交账号头像引入
