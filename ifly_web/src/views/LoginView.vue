<template>
    <auth-background>
        <div class="login-card">
            <div class="login-header">
                <div class="icon-wrapper">
                    <svg class="login-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                </div>
                <h2 class="title-animation">登录 iFly</h2>
                <p class="sub-title">欢迎回来，开启您的航空之旅</p>
            </div>

            <el-form :model="loginForm" :rules="rules" ref="loginFormRef" class="login-form">
                <el-form-item prop="username" class="fade-in-item" style="animation-delay: 0.1s">
                    <el-input v-model="loginForm.username" placeholder="用户名/邮箱" class="custom-input">
                        <template #prefix>
                            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                        </template>
                    </el-input>
                </el-form-item>

                <el-form-item prop="password" class="fade-in-item" style="animation-delay: 0.2s">
                    <el-input v-model="loginForm.password" type="password" placeholder="密码" show-password
                        class="custom-input">
                        <template #prefix>
                            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                            </svg>
                        </template>
                    </el-input>
                </el-form-item>

                <div class="remember-forgot fade-in-item" style="animation-delay: 0.3s">
                    <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
                    <a href="#" class="forgot-link">忘记密码?</a>
                </div>

                <el-form-item class="fade-in-item" style="animation-delay: 0.4s">
                    <el-button type="primary" class="login-button pulse-animation" @click="submitForm"
                        :loading="loading">
                        <svg v-if="!loading" class="button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                            stroke-linejoin="round">
                            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                            <polyline points="10 17 15 12 10 7"></polyline>
                            <line x1="15" y1="12" x2="3" y2="12"></line>
                        </svg>
                        <span v-if="!loading">登 录</span>
                        <span v-else>登录中...</span>
                    </el-button>
                </el-form-item>

                <div class="register-link fade-in-item" style="animation-delay: 0.5s">
                    还没有账号? <router-link to="/register" class="highlight-link">立即注册</router-link>
                </div>
            </el-form>

        </div>
    </auth-background>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// eslint-disable-next-line no-unused-vars
import { User, Lock } from '@element-plus/icons-vue'
import AuthBackground from '@/components/AuthBackground.vue'
import { createValidationRules } from '@/utils/validators'
import tokenManager from '@/utils/tokenManager'
import api from '@/services/api'

export default {
    name: 'LoginView',
    components: {
        AuthBackground
    },
    setup() {
        const route = useRoute()
        const router = useRouter()
        const loginFormRef = ref(null)
        const loading = ref(false)

        const loginForm = reactive({
            username: '',
            password: '',
            remember: false
        })

        const rules = {
            username: createValidationRules.length(3, 50),  // 支持邮箱，放宽长度限制
            password: createValidationRules.length(6, 30)
        }

        const submitForm = async () => {
            if (!loginFormRef.value) return

            await loginFormRef.value.validate(async (valid) => {
                if (valid) {
                    loading.value = true

                    try {
                        const response = await api.auth.login({
                            username: loginForm.username,
                            password: loginForm.password
                        });

                        if (!response.token || !response.user) {
                            throw new Error('服务器响应格式不正确')
                        }

                        // 使用安全的token管理器
                        // 记住我：30天，否则：关闭浏览器后失效（使用 sessionStorage）
                        if (loginForm.remember) {
                            tokenManager.setToken(response.token, response.user, 30 * 24 * 60 * 60 * 1000) // 30天
                        } else {
                            tokenManager.setToken(response.token, response.user, 24 * 60 * 60 * 1000, true) // 24小时，使用 session
                        }

                        window.dispatchEvent(new CustomEvent('user-login', {
                            detail: {
                                username: response.user.username,
                                userId: response.user.id
                            }
                        }))

                        const redirectPath = route.query.redirect || '/'
                        ElMessage.success('登录成功')

                        router.push(redirectPath)
                    } catch (error) {
                        console.error('登录失败:', error)
                        // 错误消息已在 api.js 拦截器中显示，这里不再重复
                    } finally {
                        loading.value = false
                    }
                }
            })
        }

        return {
            loginFormRef,
            loginForm,
            loading,
            rules,
            submitForm
        }
    }
}
</script>

<style scoped>
@keyframes pulse {
    0% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.05);
    }

    100% {
        transform: scale(1);
    }
}

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

@keyframes floating {
    0% {
        transform: translateY(0px);
    }

    50% {
        transform: translateY(-10px);
    }

    100% {
        transform: translateY(0px);
    }
}

@keyframes shimmer {
    0% {
        background-position: -200% 0;
    }

    100% {
        background-position: 200% 0;
    }
}

.login-card {
    background-color: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(15px);
    border-radius: 20px;
    padding: 35px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3),
        0 0 0 1px rgba(255, 255, 255, 0.1) inset,
        0 5px 15px rgba(120, 192, 255, 0.2);
    max-width: 400px;
    width: 90%;
    overflow: hidden;
    border: 1px solid rgba(255, 255, 255, 0.2);
    transform: translateZ(0);
    transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.login-card:hover {
    box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4),
        0 0 0 1px rgba(255, 255, 255, 0.15) inset,
        0 8px 20px rgba(120, 192, 255, 0.3);
    transform: translateY(-5px) translateZ(0);
}

.login-header {
    text-align: center;
    margin-bottom: 35px;
}

.icon-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 15px;
    animation: floating 3s ease-in-out infinite;
}

.login-icon {
    width: 60px;
    height: 60px;
    margin-bottom: 15px;
    color: #78c0ff;
    filter: drop-shadow(0 0 12px rgba(120, 192, 255, 0.6));
    transition: all 0.3s ease;
}

.login-icon:hover {
    color: #a0d4ff;
    filter: drop-shadow(0 0 15px rgba(120, 192, 255, 0.8));
    transform: scale(1.1) rotate(5deg);
}

.title-animation {
    color: #ffffff;
    font-size: 32px;
    font-weight: 700;
    margin-bottom: 12px;
    animation: fadeIn 0.8s ease-out;
    background: linear-gradient(135deg, #ffffff 0%, #7eb6ff 50%, #42A5F5 100%);
    background-size: 200% auto;
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 2px 10px rgba(78, 196, 255, 0.4);
    animation: shimmer 3s linear infinite;
    letter-spacing: 1px;
}

.sub-title {
    color: #a0d4ff;
    font-size: 16px;
    animation: fadeIn 0.8s ease-out 0.2s both;
    text-shadow: 0 1px 5px rgba(0, 0, 0, 0.5);
    margin-bottom: 10px;
    letter-spacing: 0.5px;
}

.login-form {
    margin-bottom: 25px;
}

.fade-in-item {
    animation: fadeIn 0.8s ease-out both;
}

.custom-input {
    margin-bottom: 15px;
    border-radius: 12px;
    overflow: hidden;
    transition: all 0.3s ease;
}

.custom-input:hover {
    transform: translateY(-2px);
}

.input-icon {
    width: 22px;
    height: 22px;
    color: #78c0ff;
    stroke-width: 2.5;
    filter: drop-shadow(0 0 3px rgba(120, 192, 255, 0.5));
    transition: all 0.3s ease;
}

.custom-input:hover .input-icon {
    color: #42A5F5;
    transform: scale(1.1);
}

.custom-input :deep(.el-input__inner) {
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #78c0ff;
    border-radius: 12px;
    padding-left: 48px;
    height: 50px;
    font-size: 16px;
    transition: all 0.3s ease;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    font-weight: 600;
    letter-spacing: 0.5px;
}

.custom-input :deep(.el-input__inner:focus) {
    border-color: rgba(78, 196, 255, 0.8);
    box-shadow: 0 0 15px rgba(78, 196, 255, 0.5),
        0 0 0 2px rgba(78, 196, 255, 0.2);
    background: rgba(255, 255, 255, 0.25);
    transform: translateY(-1px);
}

.custom-input :deep(.el-input__inner::placeholder) {
    color: rgba(160, 212, 255, 0.7);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    font-weight: 500;
}

.custom-input :deep(.el-input__prefix) {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 45px;
    left: 0;
    background-color: rgba(255, 255, 255, 0.2);
    height: 100%;
    border-radius: 12px 0 0 12px;
    border-right: 1px solid rgba(255, 255, 255, 0.2);
    transition: all 0.3s ease;
}

.custom-input:hover :deep(.el-input__prefix) {
    background-color: rgba(255, 255, 255, 0.3);
}

.remember-forgot {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
    padding: 0 5px;
}

.el-checkbox :deep(.el-checkbox__label) {
    color: rgba(255, 255, 255, 0.8);
    transition: all 0.3s ease;
}

.el-checkbox:hover :deep(.el-checkbox__label) {
    color: #ffffff;
    text-shadow: 0 0 5px rgba(255, 255, 255, 0.5);
}

.forgot-link {
    color: #78c0ff;
    text-decoration: none;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.3s ease;
    position: relative;
    padding: 5px;
}

.forgot-link:hover {
    color: #ffffff;
    text-shadow: 0 0 8px rgba(120, 192, 255, 0.8);
}

.forgot-link::after {
    content: '';
    position: absolute;
    width: 0;
    height: 2px;
    bottom: 0;
    left: 0;
    background-color: #78c0ff;
    transition: width 0.3s ease;
}

.forgot-link:hover::after {
    width: 100%;
}

.login-button {
    width: 100%;
    height: 50px;
    font-size: 18px;
    background-image: linear-gradient(135deg, #42A5F5 0%, #1976D2 100%);
    border: none;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    letter-spacing: 1px;
    box-shadow: 0 10px 20px rgba(25, 118, 210, 0.4);
    transition: all 0.3s ease;
    overflow: hidden;
    position: relative;
}

.login-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
    transition: all 0.5s ease;
}

.login-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 25px rgba(25, 118, 210, 0.5);
    background-image: linear-gradient(135deg, #42A5F5 20%, #1976D2 100%);
}

.login-button:hover::before {
    left: 100%;
}

.button-icon {
    width: 22px;
    height: 22px;
    margin-right: 10px;
    color: #ffffff;
    filter: drop-shadow(0 0 3px rgba(255, 255, 255, 0.5));
}

.pulse-animation:hover {
    animation: pulse 1.5s infinite;
}

.register-link {
    text-align: center;
    margin-top: 20px;
    font-size: 15px;
    color: rgba(255, 255, 255, 0.8);
}

.highlight-link {
    color: #78c0ff;
    text-decoration: none;
    font-weight: bold;
    position: relative;
    padding: 0 3px;
    transition: all 0.3s ease;
}

.highlight-link:after {
    content: '';
    position: absolute;
    width: 0;
    height: 2px;
    bottom: -2px;
    left: 0;
    background: linear-gradient(90deg, #78c0ff, transparent);
    transition: width 0.3s ease;
}

.highlight-link:hover {
    color: #ffffff;
    text-shadow: 0 0 8px rgba(126, 182, 255, 0.7);
}

.highlight-link:hover:after {
    width: 100%;
}

@media (max-width: 480px) {
    .login-card {
        padding: 25px 20px;
        width: 95%;
    }

    .title-animation {
        font-size: 28px;
    }

    .custom-input :deep(.el-input__inner) {
        height: 45px;
    }

    .login-button {
        height: 45px;
    }
}
</style>