<template>
  <div class="home">
    <!-- 动态背景横幅 -->
    <div class="banner">
      <div class="banner-overlay"></div>
      <div class="flying-plane"></div>
      <div class="clouds">
        <div class="cloud cloud-1"></div>
        <div class="cloud cloud-2"></div>
        <div class="cloud cloud-3"></div>
      </div>

      <div class="search-container">
        <div class="banner-content">
          <h1>iFly <span class="highlight">飞行体验</span></h1>
          <p>便捷、快速、安全的在线订票平台</p>
          <div class="banner-badges">
            <div class="badge">
              <i class="el-icon-time"></i>
              <span>快速预订</span>
            </div>
            <div class="badge">
              <i class="el-icon-star-on"></i>
              <span>优质服务</span>
            </div>
            <div class="badge">
              <i class="el-icon-discount"></i>
              <span>超值优惠</span>
            </div>
          </div>
        </div>

        <search-form @search="handleSearchFlights" ref="searchForm" />
      </div>
    </div>

    <!-- 世界地图航线选择 -->
    <div class="section map-section">
      <h2 class="section-title">世界地图航线选择</h2>
      <p class="section-subtitle">在地图上点击出发地和目的地，或从热门城市中选择</p>
      <world-map-routes @route-selected="handleRouteSelected" :initialFrom="selectedRoute.from"
        :initialTo="selectedRoute.to" ref="worldMap" />
    </div>

    <!-- 服务特点 -->
    <feature-section />

    <!-- 热门航线推荐 -->
    <div class="section">
      <popular-routes @select-route="handleSelectRoute" />
    </div>

    <!-- 优惠信息 -->
    <div class="section promo-section">
      <promotion-carousel />
    </div>

    <!-- 目的地推荐 -->
    <div class="section destinations-section">
      <destinations-grid :destinations="popularDestinations" @select-destination="handleDestinationClick" />
    </div>

    <!-- 客户评价 -->
    <div class="section testimonials-section">
      <testimonial-section :testimonials="testimonials" />
    </div>

    <!-- 常见问题 -->
    <div class="section faq-section">
      <FaqSection :faqs="faqs" />
    </div>

    <!-- 移动应用下载 -->
    <app-download />

    <!-- 页脚 -->
    <site-footer />
  </div>
</template>

<script>
import SearchForm from '@/components/SearchForm.vue'
import PopularRoutes from '@/components/PopularRoutes.vue'
import PromotionCarousel from '@/components/PromotionCarousel.vue'
import FeatureSection from '@/components/FeatureSection.vue'
import DestinationsGrid from '@/components/DestinationsGrid.vue'
import TestimonialSection from '@/components/TestimonialSection.vue'
import FaqSection from '@/components/FAQSection.vue'
import AppDownload from '@/components/AppDownload.vue'
import SiteFooter from '@/components/SiteFooter.vue'
import WorldMapRoutes from '@/components/WorldMapRoutes.vue'

export default {
  name: 'HomeView',
  components: {
    SearchForm,
    PopularRoutes,
    PromotionCarousel,
    FeatureSection,
    DestinationsGrid,
    TestimonialSection,
    FaqSection,
    AppDownload,
    SiteFooter,
    WorldMapRoutes
  },
  data() {
    return {
      selectedRoute: {
        from: '',
        to: ''
      },
      popularDestinations: [
        {
          name: '巴黎',
          image: 'https://picsum.photos/id/1067/300/200',
          price: '2999'
        },
        {
          name: '东京',
          image: 'https://picsum.photos/id/1036/300/200',
          price: '1999'
        },
        {
          name: '曼谷',
          image: 'https://picsum.photos/id/164/300/200',
          price: '1599'
        },
        {
          name: '悉尼',
          image: 'https://picsum.photos/id/1037/300/200',
          price: '3999'
        },
        {
          name: '纽约',
          image: 'https://picsum.photos/id/1016/300/200',
          price: '4999'
        },
        {
          name: '新加坡',
          image: 'https://picsum.photos/id/1039/300/200',
          price: '1899'
        }
      ],
      testimonials: [
        {
          author: '张小明',
          avatar: 'https://picsum.photos/id/1062/60/60',
          rating: 5,
          text: '第一次在iFly预订机票，整个过程非常流畅，价格也很实惠。航班准点，服务一流，下次还会选择iFly！',
          trip: '北京 - 上海'
        },
        {
          author: '李华',
          avatar: 'https://picsum.photos/id/1066/60/60',
          rating: 4,
          text: '退改签流程简单明了，客服响应迅速，解决了我的所有问题。虽然有小插曲，但总体体验还是很好的。',
          trip: '成都 - 广州'
        },
        {
          author: '王丽',
          avatar: 'https://picsum.photos/id/1074/60/60',
          rating: 5,
          text: '作为常旅客，我尝试过很多订票平台，但iFly的用户体验是最好的，尤其是座位选择和在线值机功能非常实用！',
          trip: '上海 - 纽约'
        }
      ],
      faqs: [
        {
          question: '如何取消或更改我的预订？',
          answer: '您可以在"我的订单"中找到您想要取消或更改的预订，然后点击相应的按钮进行操作。请注意，根据航空公司的政策，可能会收取一定的手续费。'
        },
        {
          question: '我可以提前多久预订航班？',
          answer: '大多数航班可以提前11个月预订。建议您尽早预订以获得最优惠的价格。'
        },
        {
          question: '如何选择座位？',
          answer: '在完成订票后，您可以在"我的订单"中找到您的订单，点击"选择座位"按钮进行座位选择。部分航班可能需要支付额外费用。'
        },
        {
          question: '儿童和婴儿的预订政策是什么？',
          answer: '2岁以上的儿童需要购买全价机票，2岁以下的婴儿可以享受婴儿票价（通常是成人票价的10%）。不同航空公司可能有不同规定，请在预订时查看具体政策。'
        },
        {
          question: '行李限额是多少？',
          answer: '行李限额取决于您预订的航班和舱位。经济舱通常允许一件随身行李和一件托运行李（不超过23kg）。您可以在订单详情中查看具体的行李限额。'
        }
      ]
    };
  },
  methods: {
    handleSearchFlights(searchParams) {
      // 记录传入的搜索参数
      console.log('HomeView收到搜索参数:', searchParams);
      
      // 将搜索参数添加到查询参数中
      this.$router.push({
        path: '/flights',
        query: {
          from: searchParams.departureCity,
          to: searchParams.arrivalCity,
          date: searchParams.departureDate,
          returnDate: searchParams.returnDate,
          passengers: searchParams.passengerCount,
          cabin: searchParams.cabinClass
        }
      });
    },
    handleSelectRoute(route) {
      if (this.$refs.searchForm) {
        this.$refs.searchForm.setRoute(route);
      }
    },
    handleDestinationClick(destination) {
      // 处理目的地点击，默认设置为单程前往该城市
      if (this.$refs.searchForm) {
        this.$refs.searchForm.setDestination(destination.name);
      }
      // 滚动到页面顶部的搜索表单
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    },
    handleRouteSelected(route) {
      this.selectedRoute = route;
      if (this.$refs.searchForm) {
        this.$refs.searchForm.setRoute(route);
      }
    }
  }
}
</script>

<style>
.home {
  width: 100%;
  margin: 0 auto;
  background: linear-gradient(135deg, #f0f8ff, #e8f4ff, #f5faff);
  position: relative;
}

.home::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm32-22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%230076c6' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
  opacity: 0.5;
}

.home::after {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle at 10% 10%, rgba(255, 255, 255, 0.03) 0%, transparent 60%),
    radial-gradient(circle at 90% 90%, rgba(230, 240, 255, 0.03) 0%, transparent 40%);
  z-index: -2;
  pointer-events: none;
}

.home {
  width: 100%;
  margin: 0 auto;
  padding-bottom: 60px;
  position: relative;
  overflow-x: hidden;
}

/* 目的地部分 */
.destinations-section {
  margin-bottom: 60px;
  text-align: center;
}

.destinations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 25px;
  margin: 0 auto;
  max-width: 1300px;
  padding: 20px 0;
}

.destination-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  height: 250px;
  position: relative;
  border: none;
  transform: translateY(0);
}

.destination-card:hover {
  transform: translateY(-8px) scale(1.02);
  box-shadow: 0 15px 30px rgba(0, 70, 139, 0.2);
  z-index: 2;
}

.destination-image {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  position: relative;
}

.destination-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: linear-gradient(to top, rgba(0, 45, 98, 0.85), rgba(0, 70, 139, 0.2), transparent);
  color: white;
  padding: 25px;
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  height: 50%;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  backdrop-filter: blur(0px);
}

.destination-card:hover .destination-overlay {
  height: 100%;
  background: linear-gradient(to top, rgba(0, 45, 98, 0.9), rgba(0, 70, 139, 0.7));
  justify-content: center;
  align-items: center;
  backdrop-filter: blur(2px);
}

.destination-overlay h3 {
  margin: 0;
  font-size: 2em;
  margin-bottom: 8px;
  font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  position: relative;
  transition: all 0.3s ease;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

.destination-overlay p {
  margin: 0;
  font-size: 1.3em;
  margin-bottom: 15px;
  color: #42a5f5;
  font-weight: 600;
  transform: translateY(0);
  opacity: 0;
  transition: all 0.3s ease 0.1s;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 评价部分 */
.testimonials-section {
  margin-bottom: 60px;
  text-align: center;
  background: linear-gradient(135deg, #f9f9ff, #f0f7ff);
  padding: 40px 0;
  border-radius: 8px;
}

.testimonial-card {
  background: linear-gradient(135deg, #ffffff, #f9fbff);
  border-radius: 16px;
  padding: 35px;
  height: 100%;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.06);
  display: flex;
  flex-direction: column;
  align-items: center;
  border: 1px solid rgba(230, 242, 255, 0.7);
  transform: translateY(0);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.testimonial-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 35px rgba(0, 70, 139, 0.1);
  border-color: rgba(230, 242, 255, 0.9);
}

.testimonial-avatar {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background-size: cover;
  background-position: center;
  border: none;
  margin-bottom: 20px;
  position: relative;
  box-shadow: 0 8px 25px rgba(0, 118, 198, 0.2);
}

.testimonial-avatar::before {
  content: '';
  position: absolute;
  top: -6px;
  left: -6px;
  right: -6px;
  bottom: -6px;
  border-radius: 50%;
  background: linear-gradient(135deg, #0076c6, #42a5f5);
  z-index: -1;
}

.testimonial-avatar::after {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  border-radius: 50%;
  border: 2px dashed rgba(255, 255, 255, 0.6);
  z-index: 1;
}

.testimonial-content {
  text-align: center;
}

.testimonial-stars {
  color: #FFC107;
  margin-bottom: 10px;
}

.testimonial-text {
  font-style: italic;
  margin-bottom: 15px;
  line-height: 1.6;
  color: #555;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  word-wrap: break-word;
  padding: 0 5px;
}

.testimonial-author {
  font-weight: bold;
  font-size: 1.1em;
  margin-bottom: 5px;
  color: #333;
}

.testimonial-trip {
  color: #777;
  font-size: 0.9em;
}

/* FAQ部分 */
.faq-section {
  margin-bottom: 60px;
  text-align: center;
  background: linear-gradient(135deg, #f8fcff, #eef6ff);
  padding: 40px 0;
  border-radius: 8px;
}

/* 应用下载部分 */
.app-section {
  background: linear-gradient(135deg, #00468c, #0076c6);
  color: white;
  border-radius: 0;
  padding: 40px;
  margin-bottom: 60px;
}

.app-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-text {
  flex: 1;
}

.app-text h2 {
  font-size: 2.5em;
  margin-bottom: 20px;
}

.app-text p {
  font-size: 1.2em;
  margin-bottom: 30px;
  opacity: 0.9;
}

.app-buttons {
  display: flex;
  gap: 20px;
}

.app-button {
  display: block;
  max-width: 170px;
}

.app-button img {
  width: 100%;
}

.app-image {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.app-image img {
  max-height: 400px;
  filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3));
}

/* 页脚 */
.site-footer {
  background: linear-gradient(135deg, #003366, #001f3f);
  color: #eee;
  border-radius: 0;
  padding: 60px 40px 20px;
  margin-top: 40px;
  position: relative;
  overflow: hidden;
}

.footer-content {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  margin-bottom: 40px;
}

.footer-section {
  flex: 1;
  min-width: 250px;
  margin-bottom: 30px;
}

.footer-section h3 {
  position: relative;
  padding-bottom: 15px;
  margin-bottom: 15px;
  font-size: 1.4em;
  color: white;
}

.footer-section h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 40px;
  height: 2px;
  background: #2b98f0;
}

.footer-section p {
  margin-bottom: 10px;
  color: #bbb;
  line-height: 1.6;
}

.footer-section ul {
  list-style: none;
  padding: 0;
}

.footer-section ul li {
  margin-bottom: 10px;
}

.footer-section a {
  color: #bbb;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-section a:hover {
  color: #42A5F5;
}

.social-icons {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.social-icons a {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.1);
  transition: background-color 0.3s;
}

.social-icons a:hover {
  background-color: #42A5F5;
}

.social-icons i {
  font-size: 20px;
  color: white;
}

.footer-bottom {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

/* 横幅样式 */
.banner {
  position: relative;
  background-image: url('https://images.unsplash.com/photo-1464037866556-6812c9d1c72e?q=80&w=1920&auto=format&fit=crop');
  background-size: cover;
  background-position: center 30%;
  height: 680px;
  border-radius: 0;
  margin-bottom: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;
  overflow: hidden;
  box-shadow: none;
  margin-left: -50vw;
  margin-right: -50vw;
  width: 100vw;
  left: 50%;
  right: 50%;
  position: relative;
}

.banner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 70, 139, 0.6) 0%, rgba(0, 28, 85, 0.75) 100%);
  z-index: 1;
  animation: pulseOverlay 8s infinite alternate;
}

@keyframes pulseOverlay {
  0% {
    opacity: 0.6;
  }

  100% {
    opacity: 0.75;
  }
}

/* 飞机动画 */
.flying-plane {
  position: absolute;
  top: 180px;
  left: -120px;
  width: 120px;
  height: 50px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 576 512'%3E%3Cpath fill='white' d='M482.3 192C516.5 192 576 221 576 256C576 292 516.5 320 482.3 320H365.7L265.2 495.9C259.5 505.8 248.9 512 237.4 512H181.2C170.6 512 162.9 501.8 165.8 491.6L214.9 320H112L68.8 377.6C65.78 381.6 61.04 384 56 384H14.03C6.284 384 0 377.7 0 369.1C0 368.7 .1818 367.4 .5398 366.1L32 256L.5398 145.9C.1818 144.6 0 143.3 0 142C0 134.3 6.284 128 14.03 128H56C61.04 128 65.78 130.4 68.8 134.4L112 192H214.9L165.8 20.4C162.9 10.17 170.6 0 181.2 0H237.4C248.9 0 259.5 6.153 265.2 16.12L365.7 192H482.3z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  z-index: 5;
  animation: flyPlane 22s linear infinite;
  filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.9));
}

@keyframes flyPlane {
  0% {
    transform: translateX(0) translateY(0) rotate(10deg);
    opacity: 0;
  }

  8% {
    opacity: 1;
  }

  40% {
    transform: translateX(40vw) translateY(-100px) rotate(0deg);
  }

  85% {
    opacity: 1;
  }

  100% {
    transform: translateX(calc(100vw + 180px)) translateY(80px) rotate(-8deg);
    opacity: 0;
  }
}

/* 云朵动画 */
.clouds {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  z-index: 2;
  pointer-events: none;
}

.cloud {
  position: absolute;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  opacity: 0.7;
  box-shadow: 0 0 30px rgba(255, 255, 255, 0.4);
  filter: blur(2px);
}

.cloud::before,
.cloud::after {
  content: '';
  position: absolute;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
}

.cloud-1 {
  width: 80px;
  height: 30px;
  top: 20%;
  right: -80px;
  animation: cloudMove1 30s linear infinite;
}

.cloud-1::before {
  width: 50px;
  height: 50px;
  top: -25px;
  left: 15px;
}

.cloud-1::after {
  width: 40px;
  height: 40px;
  top: -20px;
  left: 35px;
}

.cloud-2 {
  width: 100px;
  height: 40px;
  top: 50%;
  right: -100px;
  animation: cloudMove2 40s linear infinite;
  animation-delay: 5s;
}

.cloud-2::before {
  width: 60px;
  height: 60px;
  top: -30px;
  left: 20px;
}

.cloud-2::after {
  width: 50px;
  height: 50px;
  top: -25px;
  left: 45px;
}

.cloud-3 {
  width: 70px;
  height: 30px;
  top: 75%;
  right: -70px;
  animation: cloudMove3 35s linear infinite;
  animation-delay: 13s;
}

.cloud-3::before {
  width: 45px;
  height: 45px;
  top: -22px;
  left: 12px;
}

.cloud-3::after {
  width: 35px;
  height: 35px;
  top: -17px;
  left: 30px;
}

@keyframes cloudMove1 {
  0% {
    transform: translateX(0);
    opacity: 0.6;
  }

  100% {
    transform: translateX(-120vw);
    opacity: 0.4;
  }
}

@keyframes cloudMove2 {
  0% {
    transform: translateX(0);
    opacity: 0.7;
  }

  100% {
    transform: translateX(-120vw);
    opacity: 0.5;
  }
}

@keyframes cloudMove3 {
  0% {
    transform: translateX(0);
    opacity: 0.8;
  }

  100% {
    transform: translateX(-120vw);
    opacity: 0.6;
  }
}

.search-container {
  width: 85%;
  max-width: 1050px;
  position: relative;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(15px);
  border-radius: 14px;
  padding: 40px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.15);
  animation: glow 3s infinite alternate;
  margin-top: 40px;
}

.banner-content {
  margin-bottom: 35px;
  transform: translateY(-15px);
}

.banner-content h1 {
  font-size: 4.5em;
  margin-bottom: 18px;
  text-shadow: 0 2px 15px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 70, 139, 0.4);
  letter-spacing: 3px;
  font-weight: 800;
  font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  position: relative;
  display: inline-block;
  background: linear-gradient(to bottom, #ffffff, #e8f4ff);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  padding: 0 15px;
  transform: perspective(500px) translateZ(0);
  animation: titleGlow 3s ease-in-out infinite alternate;
  max-width: 100%;
  white-space: nowrap;
}

@keyframes titleGlow {
  0% {
    text-shadow: 0 2px 15px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 70, 139, 0.3);
    transform: perspective(500px) translateZ(0);
  }

  100% {
    text-shadow: 0 4px 20px rgba(0, 0, 0, 0.7), 0 0 40px rgba(30, 136, 229, 0.4);
    transform: perspective(500px) translateZ(10px);
  }
}

.banner-content p {
  font-size: 1.7em;
  margin-bottom: 30px;
  text-shadow: 0 2px 5px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 70, 139, 0.3);
  letter-spacing: 1.5px;
  font-weight: 400;
  position: relative;
  opacity: 0;
  animation: fadeInUp 0.8s ease-out 0.3s forwards;
  max-width: 100%;
  white-space: nowrap;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.highlight {
  position: relative;
  display: inline-block;
  background: linear-gradient(to bottom, #2196f3, #0d47a1);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  text-shadow: none;
  font-weight: 900;
  animation: highlightPulse 3s ease-in-out infinite alternate;
  white-space: nowrap;
}

@keyframes highlightPulse {
  0% {
    filter: drop-shadow(0 0 12px rgba(30, 136, 229, 0.8));
  }

  100% {
    filter: drop-shadow(0 0 18px rgba(33, 150, 243, 0.9));
  }
}

.highlight:after {
  content: '';
  position: absolute;
  width: 100%;
  height: 3px;
  bottom: 5px;
  left: 0;
  background: linear-gradient(to right, #2196f3, #0d47a1);
  box-shadow: 0 0 15px rgba(30, 136, 229, 0.9);
  border-radius: 3px;
  animation: underlineGlow 3s ease-in-out infinite alternate;
}

@keyframes underlineGlow {
  0% {
    width: 0;
    left: 0;
    opacity: 0.7;
  }

  40% {
    width: 100%;
    left: 0;
    opacity: 1;
  }

  60% {
    width: 100%;
    left: 0;
    opacity: 1;
  }

  100% {
    width: 95%;
    left: 2.5%;
    opacity: 0.9;
  }
}

.banner-badges {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 45px;
  margin-top: 20px;
  opacity: 0;
  animation: fadeInUp 0.8s ease-out 0.6s forwards;
  flex-wrap: wrap;
  padding: 0 10px;
}

.badge {
  display: flex;
  align-items: center;
  background-color: rgba(0, 51, 102, 0.6);
  backdrop-filter: blur(12px);
  padding: 14px 24px;
  border-radius: 6px;
  font-size: 1.05em;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.22);
  border-left: 3px solid #1e88e5;
  transition: all 0.3s ease;
}

.badge:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  background-color: rgba(0, 51, 102, 0.85);
  border-left: 3px solid #fff;
}

.badge i {
  margin-right: 8px;
  color: #1e88e5;
  font-size: 1.2em;
  text-shadow: 0 0 8px rgba(30, 136, 229, 0.6);
}

/* 特点部分 */
.section {
  margin-bottom: 75px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23e6f2ff' fill-opacity='0.4'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.2;
  z-index: -1;
  pointer-events: none;
}

.section-title {
  text-align: center;
  margin-bottom: 35px;
  font-size: 2.2em;
  color: #003b7a;
  position: relative;
  padding-bottom: 28px;
  font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  letter-spacing: 0.5px;
  font-weight: 600;
  width: 100%;
  padding-left: 15px;
  padding-right: 15px;
  box-sizing: border-box;
  display: inline-block;
}

.section-title::before {
  content: '';
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 120px;
  height: 2px;
  background-color: rgba(0, 76, 148, 0.1);
  border-radius: 2px;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 70px;
  height: 3px;
  background: linear-gradient(to right, #0057a9, #0076c6, #42a5f5);
  border-radius: 3px;
  animation: gradientShift 3s infinite alternate;
}

@keyframes gradientShift {
  0% {
    background-position: 0% 50%;
    width: 70px;
  }

  100% {
    background-position: 100% 50%;
    width: 80px;
  }
}

.features-section {
  margin-bottom: 60px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5faff, #edf7ff);
  border-radius: 8px;
  max-width: 100%;
  position: relative;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.features-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='152' height='152' viewBox='0 0 152 152'%3E%3Cg fill-rule='evenodd'%3E%3Cg id='temple' fill='%230076c6' fill-opacity='0.03'%3E%3Cpath d='M152 150v2H0v-2h28v-8H8v-20H0v-2h8V80h42v20h20v42H30v8h90v-8H80v-42h20V80h42v40h8V30h-8v40h-42V50H80V8h40V0h2v8h20v20h8V0h2v150zm-2 0v-28h-8v20h-20v8h28zM82 30v18h18V30H82zm20 18h20v20h18V30h-20V10H82v18h20v20zm0 2v18h18V50h-18zm20-22h18V10h-18v18zm-54 92v-18H50v18h18zm-20-18H28V82H10v38h20v20h38v-18H48v-20zm0-2V82H30v18h18zm-20 22H10v18h18v-18zm54 0v18h38v-20h20V82h-18v20h-20v20H82zm18-20H82v18h18v-18zm2-2h18V82h-18v18zm20 40v-18h18v18h-18zM30 0h-2v8H8v20H0v2h8v40h42V50h20V8H30V0zm20 48h18V30H50v18zm18-20H48v20H28v20H10V30h20V10h38v18zM30 50h18v18H30V50zm-2-40H10v18h18V10z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.4;
}

.features-container {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 20px;
}

.feature-card {
  flex: 1;
  min-width: 320px;
  background: linear-gradient(135deg, #ffffff, #f7fafd);
  padding: 35px 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 8px 25px rgba(0, 70, 139, 0.07);
  transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
  border: 1px solid rgba(230, 242, 255, 0.6);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: linear-gradient(to right, #0057a9, #0076c6, #42a5f5);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.4s ease-out;
  z-index: 2;
}

.feature-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(0, 70, 139, 0.15);
  border-color: rgba(230, 242, 255, 0.9);
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 25px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  padding: 10px;
  border-radius: 50%;
  background-color: rgba(0, 70, 139, 0.05);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.feature-icon::after {
  content: '';
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px dashed rgba(0, 118, 198, 0.2);
  top: 0;
  left: 0;
  animation: spin 15s linear infinite;
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

.flight-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 576 512'%3E%3Cpath fill='%2300468c' d='M482.3 192C516.5 192 576 221 576 256C576 292 516.5 320 482.3 320H365.7L265.2 495.9C259.5 505.8 248.9 512 237.4 512H181.2C170.6 512 162.9 501.8 165.8 491.6L214.9 320H112L68.8 377.6C65.78 381.6 61.04 384 56 384H14.03C6.284 384 0 377.7 0 369.1C0 368.7 .1818 367.4 .5398 366.1L32 256L.5398 145.9C.1818 144.6 0 143.3 0 142C0 134.3 6.284 128 14.03 128H56C61.04 128 65.78 130.4 68.8 134.4L112 192H214.9L165.8 20.4C162.9 10.17 170.6 0 181.2 0H237.4C248.9 0 259.5 6.153 265.2 16.12L365.7 192H482.3z'/%3E%3C/svg%3E");
}

.price-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Cpath fill='%2300468c' d='M320 96H192L144.6 24.88C137.5 14.24 145.1 0 157.9 0H354.1C366.9 0 374.5 14.24 367.4 24.88L320 96zM192 128H320C323.8 130.5 328.1 133.3 332.8 136.5L393.7 174.8C405.9 183.1 417.1 193.4 425.6 205.8L456.1 248.8C466.1 263.2 480 284.5 480 298.7V448C480 483.3 451.3 512 416 512H96C60.65 512 32 483.3 32 448V298.7C32 284.5 45.05 263.2 56.94 248.8L87.4 205.8C95.03 193.4 107.1 183.1 119.3 174.8L180.2 136.5C184.9 133.3 189.2 130.5 192 128V128zM96 192C87.16 192 80 199.2 80 208V272C80 280.8 87.16 288 96 288H128C136.8 288 144 280.8 144 272V208C144 199.2 136.8 192 128 192H96zM368 192C359.2 192 352 199.2 352 208V272C352 280.8 359.2 288 368 288H400C408.8 288 416 280.8 416 272V208C416 199.2 408.8 192 400 192H368z'/%3E%3C/svg%3E");
}

.service-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 640 512'%3E%3Cpath fill='%2300468c' d='M488 191.1h-152l.0001 51.86c.0001 37.66-27.08 72-64.55 75.77c-43.09 4.333-79.45-29.42-79.45-71.63V126.4l-24.51 14.73C123.2 167.8 96.04 215.7 96.04 267.5L16.04 313.8c-15.25 8.751-20.63 28.38-11.75 43.63l80 138.6c8.875 15.25 28.5 20.5 43.75 11.75l103.4-59.75h136.6c35.25 0 64-28.75 64-64c26.51 0 48-21.49 48-48V288h8c13.25 0 24-10.75 24-24l.0001-48C512 202.7 501.3 191.1 488 191.1zM635.7 154.5l-79.95-138.6c-8.875-15.25-28.5-20.5-43.75-11.75l-103.4 59.75h-62.57c-37.85 0-74.93 10.61-107.1 30.63C229.7 100.4 224 110.6 224 121.6l-.0004 126.4c0 22.13 17.88 40 40 40c22.13 0 40-17.88 40-40V159.1h184c30.93 0 56 25.07 56 56v28.5l80-46.25C639.3 189.4 644.5 169.8 635.7 154.5z'/%3E%3C/svg%3E");
}

.feature-card h3 {
  margin: 15px 0;
  color: #00468c;
  font-size: 1.4em;
  font-family: 'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
}

.feature-card p {
  color: #555;
  line-height: 1.6;
}

/* 优惠部分 */
.promo-section {
  padding: 40px 20px;
  background: linear-gradient(135deg, #e8f4ff, #d4ebff);
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0, 70, 139, 0.08);
  position: relative;
  overflow: hidden;
}

.promo-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M11 18c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm48 25c3.866 0 7-3.134 7-7s-3.134-7-7-7-7 3.134-7 7 3.134 7 7 7zm-43-7c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm63 31c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM34 90c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zm56-76c1.657 0 3-1.343 3-3s-1.343-3-3-3-3 1.343-3 3 1.343 3 3 3zM12 86c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm28-65c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm23-11c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-6 60c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm29 22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm32-22c2.76 0 5-2.24 5-5s-2.24-5-5-5-5 2.24-5 5 2.24 5 5 5zm-9-21c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM60 91c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM35 41c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2zM12 60c1.105 0 2-.895 2-2s-.895-2-2-2-2 .895-2 2 .895 2 2 2z' fill='%230076c6' fill-opacity='0.05' fill-rule='evenodd'/%3E%3C/svg%3E");
  opacity: 0.5;
}

.map-section {
  padding: 50px 25px;
  margin: 40px auto;
  max-width: 1200px;
  background: linear-gradient(135deg, #f9f9f9, #e6f0ff, #e8f2ff);
  border-radius: 16px;
  box-shadow: 0 15px 35px rgba(0, 70, 139, 0.08);
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(0, 118, 198, 0.1);
}

.map-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='84' height='48' viewBox='0 0 84 48' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 0h12v6H0V0zm28 8h12v6H28V8zm14-8h12v6H42V0zm14 0h12v6H56V0zm0 8h12v6H56V8zM42 8h12v6H42V8zm0 16h12v6H42v-6zm14-8h12v6H56v-6zm14 0h12v6H70v-6zm0-16h12v6H70V0zM28 32h12v6H28v-6zM14 16h12v6H14v-6zM0 24h12v6H0v-6zm0 8h12v6H0v-6zm14 0h12v6H14v-6zm14 8h12v6H28v-6zm-14 0h12v6H14v-6zm28 0h12v6H42v-6zm14-8h12v6H56v-6zm0-8h12v6H56v-6zm14 8h12v6H70v-6zm0 8h12v6H70v-6zM14 24h12v6H14v-6zm14-8h12v6H28v-6zM14 8h12v6H14V8zM0 8h12v6H0V8z' fill='%230076c6' fill-opacity='0.04' fill-rule='evenodd'/%3E%3C/svg%3E");
  opacity: 0.7;
}

.map-section::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'%3E%3Cpath fill='%230076c6' fill-opacity='0.03' d='M326.1 160l127.4-127.4C451.7 32.39 449.9 32 448 32h-86.06l-128 128H326.1zM224 288h86.06l128-128H352L224 288zM17.39 128l159.7 159.7C180.3 290.8 184.2 292.4 188.6 293L68.27 173.3c2.87-17 10.4-33.4 21.9-45.3l105.4-105.4C208.3 34.61 204.1 40.8 201.7 48H34.08C33.06 54.56 32 61.72 32 68.4C32 87.55 35.5 105.4 41.36 122.2C33.11 123.2 24.94 124.8 17.39 128zM512 136c0-16.18-1.89-30.75-4.7-44.04c-32.64 0-48.28 1.765-71.8 11.21c-10.02 4.173-19.6 9.874-28.9 16.5l126.3 126.3c.6201-3.533 .3645-5.361 1.13-9.96C511.1 195.3 512 177.2 512 136zM0 304.6c0 18.56 2.395 35.82 6.555 52.6c35.33 0 49.8-.2324 73.51-9.777c9.537-4.005 18.71-9.477 27.63-16L0 223.7V304.6zM114.7 352.7c16.09 10.38 30.96 20.55 49.89 27.39c41.97 15.3 89.73 18.11 134.8 4.898l-184-184C55.62 265.1 48.98 311.1 114.7 352.7zM295.2 444.1c-42.55 15.27-90.62 18.5-136.2 4.983c-18.91-6.824-33.78-16.99-49.89-27.39l200.7 200.7c20.78-10.14 38.31-24.74 51.82-43.23L295.2 444.1zM173.3 446.2c-23.77 9.52-38.3 9.731-73.8 9.731c-4.281 13.83-6.489 28-6.489 43.05C93.06 500.4 94.12 502.3 95.13 504h173.7C234.8 482.7 204.7 458.9 173.3 446.2zM493.4 128c-17.34 0-25.53-1.564-49.45 9.957c-11.53 5.894-19.13 10.34-27.47 16.61l147.7 147.7C487.3 190.8 480.1 135.7 493.4 128zM320 504h82.29c10.68-9.5 18.30-22.29 24.35-38.34l-146.4-146.4c-4.655 .6255-9.413 2.381-12.7 3.936l122.7 122.7C369.6 462.2 348.3 483.2 320 504z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: top right;
  opacity: 0.4;
  transform: rotate(15deg) scale(1.5);
}

/* 响应式设计 */
@media (max-width: 992px) {
  .app-content {
    flex-direction: column;
    text-align: center;
  }

  .app-text {
    margin-bottom: 40px;
  }

  .app-buttons {
    justify-content: center;
  }

  .footer-section {
    min-width: 45%;
  }
}

@media (max-width: 768px) {
  .banner-content h1 {
    font-size: 2.5em;
    white-space: normal;
  }

  .banner-content p {
    font-size: 1.2em;
    white-space: normal;
  }

  .highlight {
    white-space: normal;
  }

  .banner {
    height: auto;
    padding: 70px 20px;
  }

  .banner-badges {
    flex-direction: column;
    align-items: center;
    gap: 15px;
    margin-bottom: 30px;
  }

  .search-container {
    padding: 25px;
    width: 95%;
  }

  .features-container {
    flex-direction: column;
    align-items: center;
  }

  .feature-card {
    min-width: 100%;
    margin-bottom: 20px;
  }

  .destinations-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .destination-card {
    height: 220px;
  }

  .map-section {
    padding: 30px 15px;
    margin: 30px auto;
  }

  .footer-section {
    min-width: 100%;
  }

  .section-title {
    font-size: 1.9em;
  }

  .testimonial-card {
    padding: 25px 15px;
  }
}

/* 添加动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section {
  animation: fadeIn 1s ease-out;
}

/* 增强滚动效果 */
html {
  scroll-behavior: smooth;
}

/* 世界地图部分 */
.map-section {
  padding: 40px 20px;
  margin: 20px auto;
  max-width: 1200px;
  background-color: #f9f9f9;
  border-radius: 10px;
}

.section-subtitle {
  text-align: center;
  font-size: 17px;
  color: #555;
  margin-bottom: 40px;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
  line-height: 1.6;
  position: relative;
  opacity: 0;
  animation: fadeIn 0.8s ease-out 0.2s forwards;
  padding-left: 15px;
  padding-right: 15px;
  box-sizing: border-box;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 确保地图容器响应式显示 */
@media (max-width: 768px) {
  .map-section {
    padding: 20px 10px;
  }

  .section-title {
    font-size: 24px;
  }

  .section-subtitle {
    font-size: 14px;
  }
}

/* 添加新的装饰元素 */
.section::after {
  content: '';
  position: absolute;
  top: 20px;
  right: 20px;
  width: 80px;
  height: 40px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 800'%3E%3Cpath fill='%230076c6' fill-opacity='0.05' d='M659.5,400c0,143.1-116.4,259.5-259.5,259.5S140.5,543.1,140.5,400S256.9,140.5,400,140.5S659.5,256.9,659.5,400z M400,0C179.1,0,0,179.1,0,400s179.1,400,400,400s400-179.1,400-400S620.9,0,400,0z M400,650c-138.1,0-250-111.9-250-250s111.9-250,250-250s250,111.9,250,250S538.1,650,400,650z'/%3E%3Cpath fill='%230076c6' fill-opacity='0.05' d='M400,150c-7.2,0-14.3,0.3-21.3,0.9C290.5,159.4,218.7,231.2,210.1,320H150v40h60.1c8.6,88.8,80.4,160.6,168.6,168.1c7,0.6,14.1,0.9,21.3,0.9c137.8,0,250-112.2,250-250S537.8,150,400,150z M400,228.6c65.8,0,119.8,50.7,124.5,115.3l0.5,6.1h-25v-40h-40v40h-40v-40h-40v40h-40v-40h-40v40h-25l0.5-6.1C280.2,279.3,334.2,228.6,400,228.6z M400,531.4c-68.8,0-125-56.2-125-125c0-2.1,0.1-4.2,0.2-6.3c0.1-1.1,0.2-2.2,0.3-3.2H525c0.1,1.1,0.2,2.2,0.3,3.2c0.1,2.1,0.2,4.2,0.2,6.3C525,475.2,468.8,531.4,400,531.4z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  opacity: 0.3;
  z-index: 0;
  pointer-events: none;
  transform: rotate(15deg);
}

/* 调整各部分的背景样式 */
.features-section {
  margin-bottom: 60px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #f5faff, #edf7ff);
  border-radius: 8px;
  max-width: 100%;
  position: relative;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.promo-section {
  padding: 40px 20px;
  background: linear-gradient(135deg, #e8f4ff, #d4ebff);
  border-radius: 8px;
  box-shadow: 0 5px 20px rgba(0, 70, 139, 0.08);
  position: relative;
  overflow: hidden;
}

.map-section {
  padding: 40px 20px;
  margin: 20px auto;
  max-width: 1200px;
  background: linear-gradient(to bottom, #f9f9f9, #e8f2ff);
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 70, 139, 0.06);
  position: relative;
  overflow: hidden;
}

/* 搜索容器增强效果 */
.search-container {
  width: 90%;
  max-width: 1100px;
  position: relative;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(15px);
  border-radius: 12px;
  padding: 35px;
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.2);
  animation: glow 3s infinite alternate;
}

@keyframes glow {
  0% {
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
  }

  100% {
    box-shadow: 0 15px 35px rgba(31, 107, 184, 0.4);
  }
}

/* 改进页脚效果 */
.site-footer {
  background: linear-gradient(135deg, #003366, #001f3f);
  color: #eee;
  border-radius: 0;
  padding: 60px 40px 20px;
  margin-top: 40px;
  position: relative;
  overflow: hidden;
}
</style>
