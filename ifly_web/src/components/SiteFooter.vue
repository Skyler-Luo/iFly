<template>
    <footer class="site-footer">
        <div class="footer-content">
            <div class="footer-section about">
                <h3>iFly</h3>
                <p>便捷、快速、安全的在线订票平台，让您的旅程更加轻松愉快。</p>
                <div class="social-icons">
                    <a href="#"><i class="el-icon-s-promotion"></i></a>
                    <a href="#"><i class="el-icon-s-custom"></i></a>
                    <a href="#"><i class="el-icon-s-platform"></i></a>
                </div>
            </div>
            <div class="footer-section links">
                <h3>快速链接</h3>
                <ul>
                    <li><router-link to="/">首页</router-link></li>
                    <li><router-link to="/flights">航班查询</router-link></li>
                    <li><router-link to="/orders">我的订单</router-link></li>
                    <li><router-link to="/about">关于我们</router-link></li>
                </ul>
            </div>
            <div class="footer-section support">
                <h3>支持</h3>
                <ul>
                    <li><a href="#">常见问题</a></li>
                    <li><a href="#">行李规定</a></li>
                    <li><a href="#">退票政策</a></li>
                    <li><a href="#">联系我们</a></li>
                </ul>
            </div>
            <div class="footer-section contact">
                <h3>联系我们</h3>
                <p><i class="el-icon-location"></i> 北京市朝阳区建国路88号</p>
                <p><i class="el-icon-phone"></i> 400-888-8888</p>
                <p><i class="el-icon-message"></i> support@ifly.com</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; {{ currentYear }} iFly 航空. 保留所有权利</p>
        </div>
    </footer>
</template>

<script>
export default {
    name: 'SiteFooter',
    computed: {
        currentYear() {
            return new Date().getFullYear();
        }
    }
}
</script>

<style scoped>
.site-footer {
    background-color: #263238;
    color: #f5f5f5;
    padding-top: 50px;
    margin-top: 30px;
}

.footer-content {
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    padding: 0 20px;
}

.footer-section {
    width: 250px;
    margin-bottom: 30px;
}

.footer-section h3 {
    color: #fff;
    margin-bottom: 20px;
    font-size: 18px;
    position: relative;
    padding-bottom: 10px;
}

.footer-section h3::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 40px;
    height: 2px;
    background-color: #1976d2;
}

.footer-section p {
    line-height: 1.6;
    margin-bottom: 10px;
    color: #b0bec5;
    font-size: 14px;
}

.footer-section i {
    margin-right: 8px;
    color: #1976d2;
}

.social-icons {
    display: flex;
    margin-top: 15px;
}

.social-icons a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: #455a64;
    margin-right: 10px;
    transition: all 0.3s ease;
}

.social-icons a:hover {
    background-color: #1976d2;
    transform: translateY(-3px);
}

.social-icons i {
    color: white;
    margin-right: 0;
}

.footer-section ul {
    list-style: none;
    padding: 0;
}

.footer-section ul li {
    margin-bottom: 10px;
}

.footer-section ul li a {
    color: #b0bec5;
    text-decoration: none;
    transition: color 0.3s ease;
    font-size: 14px;
    display: inline-block;
    position: relative;
    padding-left: 15px;
}

.footer-section ul li a::before {
    content: '›';
    position: absolute;
    left: 0;
    color: #1976d2;
}

.footer-section ul li a:hover {
    color: #42A5F5;
    transform: translateX(5px);
}

.footer-bottom {
    background-color: #1a2327;
    text-align: center;
    padding: 15px 0;
    margin-top: 30px;
}

.footer-bottom p {
    margin: 0;
    font-size: 14px;
    color: #78909c;
}

@media (max-width: 768px) {
    .footer-content {
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    .footer-section {
        width: 100%;
        margin-bottom: 30px;
    }

    .footer-section h3::after {
        left: 50%;
        transform: translateX(-50%);
    }

    .social-icons {
        justify-content: center;
    }

    .footer-section ul li a {
        padding-left: 0;
    }

    .footer-section ul li a::before {
        content: none;
    }
}
</style>