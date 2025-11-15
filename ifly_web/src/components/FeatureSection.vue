<template>
    <div class="features-section">
        <h2 class="section-title">为什么选择 <span class="highlight">iFly</span></h2>
        <p class="section-subtitle">我们致力于为您提供最优质的飞行体验和最贴心的服务</p>
        <div class="features-container">
            <div class="feature-card">
                <div class="feature-icon flight-icon"></div>
                <h3>全球航线覆盖</h3>
                <p>连接全球200+城市，满足您的各种出行需求</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon price-icon"></div>
                <h3>价格透明保障</h3>
                <p>无隐藏费用，价格实时更新，确保您获得最优惠的价格</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon service-icon"></div>
                <h3>7×24小时服务</h3>
                <p>全天候客服团队，随时为您解决出行中的问题</p>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'FeatureSection'
}
</script>

<style scoped>
.features-section {
    padding: 60px 0;
    background-color: #f8f9fa;
}

/* 使用全局标题样式 */

.highlight {
    color: #1976d2;
}

.features-container {
    display: flex;
    justify-content: space-around;
    flex-wrap: wrap;
    max-width: 1200px;
    margin: 0 auto;
}

.feature-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    padding: 25px;
    width: 300px;
    margin: 15px;
    text-align: center;
    transition: transform 0.3s ease;
}

.feature-card:hover {
    transform: translateY(-10px);
}

.feature-icon {
    width: 70px;
    height: 70px;
    margin: 0 auto 20px;
    background-position: center;
    background-repeat: no-repeat;
    background-size: contain;
}

.flight-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%231976d2" d="M21,16V14L13,9V3.5A1.5,1.5,0,0,0,11.5,2A1.5,1.5,0,0,0,10,3.5V9L2,14V16L10,13.5V19L8,20.5V22L11.5,21L15,22V20.5L13,19V13.5L21,16Z"/></svg>');
}

.price-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%231976d2" d="M7,15H9C9,16.08 10.37,17 12,17C13.63,17 15,16.08 15,15C15,13.9 13.96,13.5 11.76,12.97C9.64,12.44 7,11.78 7,9C7,7.21 8.47,5.69 10.5,5.18V3H13.5V5.18C15.53,5.69 17,7.21 17,9H15C15,7.92 13.63,7 12,7C10.37,7 9,7.92 9,9C9,10.1 10.04,10.5 12.24,11.03C14.36,11.56 17,12.22 17,15C17,16.79 15.53,18.31 13.5,18.82V21H10.5V18.82C8.47,18.31 7,16.79 7,15Z"/></svg>');
}

.service-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%231976d2" d="M12,3C7.03,3 3,7.03 3,12H0L4,16L8,12H5C5,8.13 8.13,5 12,5C15.87,5 19,8.13 19,12C19,15.87 15.87,19 12,19C10.5,19 9.09,18.5 7.94,17.7L6.5,19.14C8.04,20.3 9.94,21 12,21C16.97,21 21,16.97 21,12C21,7.03 16.97,3 12,3M14,12C14,10.9 13.1,10 12,10C10.9,10 10,10.9 10,12C10,13.1 10.9,14 12,14C13.1,14 14,13.1 14,12Z"/></svg>');
}

.feature-card h3 {
    margin-bottom: 15px;
    font-size: 18px;
    color: #1976d2;
}

.feature-card p {
    color: #666;
    font-size: 14px;
    line-height: 1.6;
}
</style>