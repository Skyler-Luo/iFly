<template>
    <div class="app-section">
        <div class="app-decoration left"></div>
        <div class="app-decoration right"></div>
        <div class="app-content">
            <div class="app-text">
                <h2>随时随地<span class="highlight">预订航班</span></h2>
                <p>下载我们的移动应用，享受更便捷的预订体验和专属优惠</p>
                <ul class="app-features">
                    <li><i class="el-icon-check"></i> 一键预订和管理航班</li>
                    <li><i class="el-icon-check"></i> 手机值机，无需排队</li>
                    <li><i class="el-icon-check"></i> 实时航班动态提醒</li>
                    <li><i class="el-icon-check"></i> 专享折扣和会员特权</li>
                </ul>
                <div class="app-buttons">
                    <a href="#" class="app-button apple">
                        <img src="https://picsum.photos/id/1/170/50" alt="App Store" />
                    </a>
                    <a href="#" class="app-button google">
                        <img src="https://picsum.photos/id/2/170/50" alt="Google Play" />
                    </a>
                </div>
                <div class="qr-code">
                    <div class="qr-image">
                        <img src="https://picsum.photos/id/20/100/100" alt="扫描下载" />
                    </div>
                    <p>扫描二维码下载</p>
                </div>
            </div>
            <div class="app-image">
                <div class="phone-shadow"></div>
                <img src="https://picsum.photos/id/3/300/500" alt="iFly 移动应用" class="phone-image" />
                <div class="phone-highlight"></div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'AppDownload'
}
</script>

<style scoped>
.app-section {
    padding: 80px 0;
    background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
    position: relative;
    overflow: hidden;
}

.app-decoration {
    position: absolute;
    width: 300px;
    height: 300px;
    border-radius: 50%;
    z-index: 0;
}

.app-decoration.left {
    background: radial-gradient(circle, rgba(66, 165, 245, 0.2) 0%, transparent 70%);
    top: -100px;
    left: -100px;
}

.app-decoration.right {
    background: radial-gradient(circle, rgba(25, 118, 210, 0.15) 0%, transparent 70%);
    bottom: -100px;
    right: -100px;
}

.app-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    position: relative;
    z-index: 1;
}

.app-text {
    flex: 1;
    min-width: 300px;
    padding-right: 50px;
}

.app-text h2 {
    font-size: 36px;
    margin-bottom: 20px;
    letter-spacing: 1px;
}

.highlight {
    color: #1976d2;
    position: relative;
}

.highlight::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(to right, #42a5f5, transparent);
}

.app-text p {
    font-size: 18px;
    color: #555;
    margin-bottom: 30px;
    line-height: 1.6;
}

.app-features {
    list-style: none;
    padding: 0;
    margin-bottom: 30px;
}

.app-features li {
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    font-size: 16px;
    color: #444;
}

.app-features i {
    color: #1976d2;
    margin-right: 10px;
    font-size: 18px;
    background-color: rgba(66, 165, 245, 0.1);
    padding: 5px;
    border-radius: 50%;
}

.app-buttons {
    display: flex;
    gap: 15px;
    margin-bottom: 25px;
    flex-wrap: wrap;
}

.app-button {
    transition: all 0.3s ease;
    display: block;
    transform: scale(1);
}

.app-button:hover {
    transform: translateY(-5px) scale(1.05);
}

.app-button img {
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.qr-code {
    display: flex;
    align-items: center;
    margin-top: 20px;
}

.qr-image {
    background-color: white;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    margin-right: 15px;
}

.qr-code p {
    margin: 0;
    font-size: 14px;
    color: #666;
}

.app-image {
    flex: 0 0 auto;
    position: relative;
}

.phone-image {
    display: block;
    max-width: 100%;
    height: auto;
    border-radius: 30px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
    position: relative;
    z-index: 2;
}

.phone-shadow {
    position: absolute;
    width: 90%;
    height: 20px;
    bottom: -10px;
    left: 5%;
    background: radial-gradient(ellipse at center, rgba(0, 0, 0, 0.2) 0%, transparent 70%);
    border-radius: 50%;
    z-index: 1;
}

.phone-highlight {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
    border-radius: 30px;
    z-index: 3;
}

@media (max-width: 768px) {
    .app-section {
        padding: 60px 0;
    }

    .app-content {
        flex-direction: column;
        padding: 0 20px;
    }

    .app-text {
        text-align: center;
        padding-right: 0;
        margin-bottom: 40px;
    }

    .app-text h2 {
        font-size: 28px;
    }

    .app-features {
        display: inline-block;
        text-align: left;
        margin: 0 auto 30px;
    }

    .app-buttons {
        justify-content: center;
    }

    .qr-code {
        justify-content: center;
    }

    .app-image {
        margin-bottom: 30px;
    }
}
</style>