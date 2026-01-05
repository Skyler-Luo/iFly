     <template>
  <div class="home">
    <!-- 搜索航班区域 -->
    <div class="banner" :style="bannerStyle">
      <div class="search-container">
        <search-form @search="handleSearchFlights" ref="searchForm" />
      </div>
    </div>

    <!-- 世界地图航线选择 -->
    <div class="section map-section">
      <h2 class="section-title">世界地图航线选择</h2>
      <p class="section-subtitle">
        在地图上点击出发地和目的地，或从热门城市中选择
      </p>
      <world-map-routes
        @route-selected="handleRouteSelected"
        :initialFrom="selectedRoute.from"
        :initialTo="selectedRoute.to"
        ref="worldMap"
      />
    </div>

    <!-- 推荐航线区域 -->
    <div class="section recommendations-section">
      <recommended-routes
        :limit="6"
        @route-selected="handleRouteSelected"
        ref="recommendedRoutes"
      />
    </div>

  </div>
</template>

<script>
import SearchForm from '@/components/SearchForm.vue'
import WorldMapRoutes from '@/components/WorldMapRoutes.vue'
import RecommendedRoutes from '@/components/RecommendedRoutes.vue'

export default {
  name: 'HomeView',
  components: {
    SearchForm,
    WorldMapRoutes,
    RecommendedRoutes
  },
  data() {
    return {
      selectedRoute: {
        from: '',
        to: ''
      },
      bannerStyle: {
        backgroundImage: `url(${require('@/assets/wallhaven.jpg')})`
      }
    }
  },
  methods: {
    handleSearchFlights(searchParams) {
      /* debug */ console.log('HomeView收到搜索参数:', searchParams)

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
      })
    },
    handleRouteSelected(route) {
      this.selectedRoute = route
      if (this.$refs.searchForm) {
        this.$refs.searchForm.setRoute(route)
      }
    }
  }
}
</script>

<style>
.home {
  width: 100%;
  margin: 0 auto;
  background: #ffffff;
  position: relative;
  padding-bottom: 60px;
  padding-top: 0;
  overflow-x: hidden;
}

.home::before {
  display: none;
}

.home::after {
  display: none;
}

/* 目的地部分 - 使用设计系统变量 (Requirements: 2.1, 2.3) */
.destinations-section {
  margin-bottom: var(--section-margin-bottom, 75px);
  padding: var(--section-padding-y, 60px) var(--section-padding-x, 20px);
  text-align: center;
  background: var(
    --section-bg-secondary,
    linear-gradient(135deg, #f8fcff 0%, #f0f7ff 100%)
  );
  border-radius: var(--border-radius-lg, 12px);
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
  background: linear-gradient(
    to top,
    rgba(0, 45, 98, 0.85),
    rgba(0, 70, 139, 0.2),
    transparent
  );
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
  background: linear-gradient(
    to top,
    rgba(0, 45, 98, 0.9),
    rgba(0, 70, 139, 0.7)
  );
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

/* 评价部分 - 使用设计系统变量 (Requirements: 2.1, 2.3) */
.testimonials-section {
  margin-bottom: var(--section-margin-bottom, 75px);
  padding: var(--section-padding-y, 60px) var(--section-padding-x, 20px);
  text-align: center;
  background: var(
    --section-bg-tertiary,
    linear-gradient(135deg, #f5faff 0%, #edf7ff 100%)
  );
  border-radius: var(--border-radius-lg, 12px);
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
  color: #ffc107;
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

/* FAQ部分 - 使用设计系统变量 (Requirements: 2.1, 2.3) */
.faq-section {
  margin-bottom: var(--section-margin-bottom, 75px);
  padding: var(--section-padding-y, 60px) var(--section-padding-x, 20px);
  text-align: center;
  background: var(
    --section-bg-accent,
    linear-gradient(135deg, #e8f4ff 0%, #d4ebff 100%)
  );
  border-radius: var(--border-radius-lg, 12px);
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
  color: #42a5f5;
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
  background-color: #42a5f5;
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

/* 横幅样式 - 带背景图片 */
.banner {
  position: relative;
  background-color: #003366;
  background-size: cover;
  background-position: center center;
  background-repeat: no-repeat;
  min-height: 500px;
  border-radius: 12px;
  margin: 20px auto 40px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  text-align: center;
  color: #fff;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 70, 139, 0.2);
  width: calc(100% - 40px);
  max-width: 1200px;
  padding: 60px 20px 40px;
}

.banner::before {
  display: none;
}

/* 平滑渐变背景叠加层 (Requirements: 1.1) */

.banner-overlay {
  display: none;
}

@keyframes pulseOverlay {
  0% {
    opacity: 0.6;
  }

  100% {
    opacity: 0.75;
  }
}



/* 搜索框容器 - 透明背景 */
.search-container {
  width: 100%;
  max-width: 1000px;
  position: relative;
  z-index: 10;
  background: transparent;
  border-radius: 0;
  padding: 0;
  box-shadow: none;
  border: none;
  margin: 0 auto;
  text-align: left;
  color: #fff;
}

.banner-content {
  margin-bottom: 35px;
  transform: translateY(-15px);
}

.banner-content h1 {
  font-size: 3.6em;
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
  font-size: 1.3em;
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

/* 特点部分 - 使用设计系统变量 (Requirements: 2.1, 2.3) */
.section {
  margin-bottom: var(--section-margin-bottom, 75px);
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
  padding: var(--section-padding-y, 60px) var(--section-padding-x, 20px);
  position: relative;
  z-index: 1;
}

.section::before {
  display: none;
}

/* 区块标题统一样式 (Requirements: 2.2, 2.4) */
.section-title {
  text-align: center;
  margin-bottom: var(--section-title-margin-bottom, 35px);
  font-size: var(--section-title-font-size, 2.2em);
  color: var(--section-title-color, #003b7a);
  position: relative;
  padding-bottom: var(--section-title-padding-bottom, 28px);
  font-family: var(
    --font-family-primary,
    'Microsoft YaHei',
    '微软雅黑',
    Arial,
    sans-serif
  );
  letter-spacing: 0.5px;
  font-weight: var(--section-title-font-weight, 600);
  width: 100%;
  padding-left: 15px;
  padding-right: 15px;
  box-sizing: border-box;
  display: block;
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

/* 优惠部分 - 使用设计系统变量 (Requirements: 2.1, 2.3) */
.promo-section {
  margin-bottom: var(--section-margin-bottom, 75px);
  padding: var(--section-padding-y, 60px) var(--section-padding-x, 20px);
  background: var(--section-bg-primary, #ffffff);
  border-radius: var(--border-radius-lg, 12px);
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

/* 地图部分 - 与推荐航线部分保持一致 */
.map-section {
  margin-bottom: var(--section-margin-bottom, 75px);
  padding: var(--section-padding-y, 40px) var(--section-padding-x, 20px);
  margin-left: auto;
  margin-right: auto;
  max-width: 1200px;
  background: #ffffff;
  border-radius: var(--border-radius-lg, 12px);
  box-shadow: 0 8px 30px rgba(0, 70, 139, 0.12);
  position: relative;
  overflow: visible;
}

/* 推荐航线部分 */
.recommendations-section {
  margin-bottom: var(--section-margin-bottom, 75px);
  padding: var(--section-padding-y, 40px) var(--section-padding-x, 20px);
  margin-left: auto;
  margin-right: auto;
  max-width: 1200px;
  background: #ffffff;
  border-radius: var(--border-radius-lg, 12px);
  position: relative;
  box-shadow: 0 8px 30px rgba(0, 70, 139, 0.12);
}

/* ===== 响应式横幅布局适配 ===== */

/* 平板端 (768px - 991px) */
@media (min-width: 768px) and (max-width: 991px) {
  .banner {
    padding: var(--spacing-xl, 32px) 15px;
  }

  .search-container {
    max-width: 680px;
  }
}

/* 移动端 (<768px) */
@media (max-width: 767px) {
  .banner {
    padding: var(--spacing-lg, 24px) 10px;
  }

  .search-container {
    width: 100%;
  }
}

/* 小屏移动端 (<480px) */
@media (max-width: 479px) {
  .banner {
    padding: var(--spacing-md, 16px) 8px;
  }
}

/* 其他响应式设计 */
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

/* 世界地图部分 - 响应式适配 */
@media (max-width: 768px) {
  .map-section {
    padding: 20px 10px;
  }
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

/* 添加新的装饰元素 */
.section::after {
  display: none;
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

/* 注意：promo-section 和 map-section 的主要样式已在上方定义，此处为兼容性覆盖 */



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

.home {
  background: #ffffff;
}

.home::before,
.home::after {
  content: none;
  background: none;
  background-image: none;
  opacity: 0;
}


</style>
