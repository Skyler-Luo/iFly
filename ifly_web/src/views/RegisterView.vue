<template>
    <div class="register-container">
        <div class="earth-background">
            <div class="earth">
                <div class="earth-clouds"></div>
            </div>
            <div class="moon-orbit">
                <div class="moon"></div>
            </div>
            <div class="orbit">
                <div class="airplane airplane-1">✈</div>
                <div class="airplane airplane-2">✈</div>
                <div class="airplane airplane-3">✈</div>
            </div>
            <div class="stars"></div>
        </div>
        <div class="register-card">
            <div class="register-header">
                <div class="icon-wrapper">
                    <svg class="register-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                </div>
                <h2 class="title-animation">注册 iFly</h2>
                <p class="sub-title">创建您的账号，加入我们的航空社区</p>
            </div>

            <el-form :model="registerForm" :rules="rules" ref="registerFormRef" class="register-form">
                <el-form-item prop="username" class="fade-in-item" style="animation-delay: 0.1s">
                    <el-input v-model="registerForm.username" placeholder="用户名" class="custom-input">
                        <template #prefix>
                            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                                <circle cx="12" cy="7" r="4"></circle>
                            </svg>
                        </template>
                    </el-input>
                </el-form-item>

                <el-form-item prop="email" class="fade-in-item" style="animation-delay: 0.2s">
                    <el-input v-model="registerForm.email" placeholder="电子邮箱" class="custom-input">
                        <template #prefix>
                            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z">
                                </path>
                                <polyline points="22,6 12,14.01 2,6"></polyline>
                            </svg>
                        </template>
                    </el-input>
                </el-form-item>

                <el-form-item prop="phone" class="fade-in-item" style="animation-delay: 0.3s">
                    <el-input v-model="registerForm.phone" placeholder="手机号码" class="custom-input">
                        <template #prefix>
                            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z">
                                </path>
                                <polyline points="22,6 12,14.01 2,6"></polyline>
                            </svg>
                        </template>
                    </el-input>
                </el-form-item>

                <el-form-item prop="password" class="fade-in-item" style="animation-delay: 0.4s">
                    <el-input v-model="registerForm.password" type="password" placeholder="密码" show-password
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

                <el-form-item prop="confirmPassword" class="fade-in-item" style="animation-delay: 0.5s">
                    <el-input v-model="registerForm.confirmPassword" type="password" placeholder="确认密码" show-password
                        class="custom-input">
                        <template #prefix>
                            <svg class="input-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                                stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="8" cy="15" r="4"></circle>
                                <line x1="10.85" y1="12.15" x2="19" y2="4"></line>
                                <line x1="18" y1="5" x2="20" y2="7"></line>
                                <line x1="15" y1="8" x2="17" y2="10"></line>
                            </svg>
                        </template>
                    </el-input>
                </el-form-item>

                <el-form-item class="fade-in-item" style="animation-delay: 0.6s">
                    <el-checkbox v-model="registerForm.agreement" required>
                        <div class="checkbox-content">
                            <span>我已阅读并同意</span>
                            <a href="#" @click.prevent="showTerms" class="terms-link">
                                <svg class="link-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                                    <polyline points="14 2 14 8 20 8"></polyline>
                                    <line x1="16" y1="13" x2="8" y2="13"></line>
                                    <line x1="16" y1="17" x2="8" y2="17"></line>
                                    <polyline points="10 9 9 9 8 9"></polyline>
                                </svg>
                                服务条款
                            </a>
                            <span>和</span>
                            <a href="#" @click.prevent="showPrivacy" class="terms-link">
                                <svg class="link-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round">
                                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                                </svg>
                                隐私政策
                            </a>
                        </div>
                    </el-checkbox>
                </el-form-item>

                <el-form-item class="fade-in-item" style="animation-delay: 0.7s">
                    <el-button type="primary" class="register-button pulse-animation" @click="submitForm"
                        :loading="loading">
                        <svg v-if="!loading" class="button-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
                            fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                            stroke-linejoin="round">
                            <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                            <circle cx="8.5" cy="7" r="4"></circle>
                            <line x1="20" y1="8" x2="20" y2="14"></line>
                            <line x1="23" y1="11" x2="17" y2="11"></line>
                        </svg>
                        <span v-if="!loading">注 册</span>
                        <span v-else>注册中...</span>
                    </el-button>
                </el-form-item>

                <div class="login-link fade-in-item" style="animation-delay: 0.8s">
                    <svg class="login-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="9 18 15 12 9 6"></polyline>
                    </svg>
                    <span>已有账号？</span>
                    <router-link to="/login" class="highlight-link">
                        <svg class="login-link-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
                            <polyline points="10 17 15 12 10 7"></polyline>
                            <line x1="15" y1="12" x2="3" y2="12"></line>
                        </svg>
                        立即登录
                    </router-link>
                </div>
            </el-form>
        </div>

        <!-- 使用拆分的组件 -->
        <TermsOfService v-model:visible="termsDialogVisible" />
        <PrivacyPolicy v-model:visible="privacyDialogVisible" />
    </div>
</template>

<script>
import { ElMessage } from 'element-plus';
import TermsOfService from '@/components/TermsOfService.vue';
import PrivacyPolicy from '@/components/PrivacyPolicy.vue';
import api from '@/services/api';

export default {
    name: 'RegisterView',
    components: {
        TermsOfService,
        PrivacyPolicy
    },
    data() {
        const validatePass = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请输入密码'));
            } else {
                if (this.registerForm.confirmPassword !== '') {
                    if (this.$refs.registerFormRef) {
                        this.$refs.registerFormRef.validateField('confirmPassword');
                    }
                }
                callback();
            }
        };
        const validatePass2 = (rule, value, callback) => {
            if (value === '') {
                callback(new Error('请再次输入密码'));
            } else if (value !== this.registerForm.password) {
                callback(new Error('两次输入密码不一致!'));
            } else {
                callback();
            }
        };

        return {
            loading: false,
            termsDialogVisible: false,
            privacyDialogVisible: false,
            registerForm: {
                username: '',
                email: '',
                phone: '',
                password: '',
                confirmPassword: '',
                agreement: false
            },
            rules: {
                username: [
                    { required: true, message: '请输入用户名', trigger: 'blur' },
                    { min: 3, max: 20, message: '长度在 3 到 20 个字符', trigger: 'blur' }
                ],
                email: [
                    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
                    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
                ],
                phone: [
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号码', trigger: 'blur' }
                ],
                password: [
                    { required: true, message: '请输入密码', trigger: 'blur' },
                    { min: 6, max: 20, message: '长度在 6 到 20 个字符', trigger: 'blur' },
                    { validator: validatePass, trigger: 'blur' }
                ],
                confirmPassword: [
                    { required: true, message: '请确认密码', trigger: 'blur' },
                    { validator: validatePass2, trigger: 'blur' }
                ]
            }
        }
    },
    methods: {
        showTerms() {
            this.termsDialogVisible = true;
        },
        showPrivacy() {
            this.privacyDialogVisible = true;
        },
        submitForm() {
            this.$refs.registerFormRef.validate((valid) => {
                if (valid) {
                    if (!this.registerForm.agreement) {
                        ElMessage.warning('请阅读并同意服务条款和隐私政策');
                        return false;
                    }

                    this.loading = true;

                    // 构建API需要的数据格式
                    const userData = {
                        username: this.registerForm.username,
                        email: this.registerForm.email,
                        phone: this.registerForm.phone,
                        password: this.registerForm.password,
                        password2: this.registerForm.confirmPassword
                    };

                    // 调用注册API
                    api.auth.register(userData)
                        .then(() => {
                            ElMessage.success('注册成功，请登录');
                            this.$router.push('/login');
                        })
                        .catch(error => {
                            let errorMsg = '注册失败';
                            // 处理后端返回的具体错误信息
                            if (error.response && error.response.data) {
                                const errors = error.response.data;
                                if (errors.username) {
                                    errorMsg = `用户名错误: ${errors.username[0]}`;
                                } else if (errors.email) {
                                    errorMsg = `邮箱错误: ${errors.email[0]}`;
                                } else if (errors.password) {
                                    errorMsg = `密码错误: ${errors.password[0]}`;
                                } else if (errors.non_field_errors) {
                                    errorMsg = errors.non_field_errors[0];
                                }
                            }
                            ElMessage.error(errorMsg);
                            console.error('注册错误:', error);
                        })
                        .finally(() => {
                            this.loading = false;
                        });
                } else {
                    return false;
                }
            });
        }
    }
}
</script>

<style scoped>
.register-container {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    min-height: calc(100vh - 60px);
    background: linear-gradient(135deg, #0a192f 0%, #112240 100%);
    padding: 40px;
    padding-right: 8%;
    position: relative;
    overflow: hidden;
}

@keyframes rotate {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

@keyframes planeMove1 {

    0%,
    100% {
        transform: translateY(-5px) rotate(30deg);
    }

    50% {
        transform: translateY(5px) rotate(30deg) scale(1.1);
    }
}

@keyframes planeMove2 {

    0%,
    100% {
        transform: translateY(-5px) rotate(150deg);
    }

    50% {
        transform: translateY(5px) rotate(150deg) scale(1.1);
    }
}

@keyframes planeMove3 {

    0%,
    100% {
        transform: translateY(-5px) rotate(270deg);
    }

    50% {
        transform: translateY(5px) rotate(270deg) scale(1.1);
    }
}

@keyframes twinkle {

    0%,
    100% {
        opacity: 0.3;
    }

    50% {
        opacity: 1;
    }
}

@keyframes moonGlow {

    0%,
    100% {
        box-shadow: 0 0 20px 2px rgba(255, 255, 255, 0.8);
    }

    50% {
        box-shadow: 0 0 30px 5px rgba(255, 255, 255, 0.9);
    }
}

@keyframes moonRotate {
    0% {
        transform: rotate(0deg) translateX(-50%);
    }

    100% {
        transform: rotate(360deg) translateX(-50%);
    }
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

.earth-background {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: 0;
}

.earth {
    position: absolute;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle at 120px 120px, #5fb8ff 0%, #429fdd 40%, #1e5799 70%, #06214b 100%);
    border-radius: 50%;
    box-shadow: 0 0 80px rgba(66, 159, 221, 0.7);
    left: 15%;
    top: calc(50% - 200px);
    overflow: hidden;
    z-index: 1;
}

.earth::before {
    content: '';
    position: absolute;
    width: 500px;
    height: 400px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='400' viewBox='0 0 500 400'%3E%3Cpath fill='%2332CD32' d='M40,80 C60,70 80,90 100,80 C120,70 140,90 160,80 C180,70 200,90 220,80 C240,70 260,90 280,80 C300,70 320,90 340,80 C360,70 380,90 400,80 C420,70 440,90 460,80 L460,180 C440,170 420,190 400,180 C380,170 360,190 340,180 C320,170 300,190 280,180 C260,170 240,190 220,180 C200,170 180,190 160,180 C140,170 120,190 100,180 C80,170 60,190 40,180 Z'/%3E%3Cpath fill='%2332CD32' d='M120,220 C140,210 160,230 180,220 C200,210 220,230 240,220 C260,210 280,230 300,220 C320,210 340,230 360,220 C380,210 400,230 420,220 L420,320 C400,310 380,330 360,320 C340,310 320,330 300,320 C280,310 260,330 240,320 C220,310 200,330 180,320 C160,310 140,330 120,320 Z'/%3E%3C/svg%3E");
    background-repeat: repeat-x;
    left: -50px;
    top: 130px;
    opacity: 0.75;
    animation: rotate 60s linear infinite;
}

.earth::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background:
        radial-gradient(circle at 180px 120px, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0) 60%),
        radial-gradient(circle at 300px 250px, rgba(201, 234, 255, 0.3) 0%, rgba(201, 234, 255, 0) 50%);
    left: 0;
    top: 0;
    z-index: 2;
}

/* 添加云层效果 */
.earth::before {
    content: '';
    position: absolute;
    width: 500px;
    height: 400px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='400' viewBox='0 0 500 400'%3E%3Cpath fill='%2332CD32' d='M40,80 C60,70 80,90 100,80 C120,70 140,90 160,80 C180,70 200,90 220,80 C240,70 260,90 280,80 C300,70 320,90 340,80 C360,70 380,90 400,80 C420,70 440,90 460,80 L460,180 C440,170 420,190 400,180 C380,170 360,190 340,180 C320,170 300,190 280,180 C260,170 240,190 220,180 C200,170 180,190 160,180 C140,170 120,190 100,180 C80,170 60,190 40,180 Z'/%3E%3Cpath fill='%2332CD32' d='M120,220 C140,210 160,230 180,220 C200,210 220,230 240,220 C260,210 280,230 300,220 C320,210 340,230 360,220 C380,210 400,230 420,220 L420,320 C400,310 380,330 360,320 C340,310 320,330 300,320 C280,310 260,330 240,320 C220,310 200,330 180,320 C160,310 140,330 120,320 Z'/%3E%3C/svg%3E");
    background-repeat: repeat-x;
    left: -50px;
    top: 130px;
    opacity: 0.75;
    animation: rotate 60s linear infinite;
}

.earth-clouds {
    content: '';
    position: absolute;
    width: 500px;
    height: 400px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='500' height='400' viewBox='0 0 500 400'%3E%3Cpath fill='%23FFFFFF' fill-opacity='0.2' d='M50,50 C70,40 90,60 110,50 L110,60 C90,70 70,50 50,60 Z M150,80 C170,70 190,90 210,80 L210,90 C190,100 170,80 150,90 Z M250,40 C270,30 290,50 310,40 L310,50 C290,60 270,40 250,50 Z M350,70 C370,60 390,80 410,70 L410,80 C390,90 370,70 350,80 Z M80,150 C100,140 120,160 140,150 L140,160 C120,170 100,150 80,160 Z M180,120 C200,110 220,130 240,120 L240,130 C220,140 200,120 180,130 Z M280,160 C300,150 320,170 340,160 L340,170 C320,180 300,160 280,170 Z M380,130 C400,120 420,140 440,130 L440,140 C420,150 400,130 380,140 Z'/%3E%3C/svg%3E");
    background-repeat: repeat;
    left: -50px;
    top: 0;
    opacity: 0.8;
    animation: rotate 40s linear infinite;
    z-index: 3;
}

.orbit {
    position: absolute;
    width: 550px;
    height: 550px;
    border: 2px dashed rgba(255, 255, 255, 0.2);
    border-radius: 50%;
    left: calc(15% - 75px);
    top: calc(50% - 275px);
    animation: rotate 60s linear infinite;
    z-index: 0;
}

.airplane {
    position: absolute;
    color: white;
    font-size: 22px;
    text-shadow: 0 0 10px rgba(78, 196, 255, 0.8);
    filter: drop-shadow(0 0 5px rgba(78, 196, 255, 0.5));
    transform-origin: center;
}

.airplane-1 {
    top: 15%;
    right: 15%;
    transform: rotate(30deg);
    animation: planeMove1 8s ease-in-out infinite;
    font-size: 24px;
}

.airplane-2 {
    bottom: 15%;
    right: 15%;
    transform: rotate(150deg);
    animation: planeMove2 7s ease-in-out infinite 2s;
    font-size: 20px;
}

.airplane-3 {
    bottom: 15%;
    left: 15%;
    transform: rotate(270deg);
    animation: planeMove3 9s ease-in-out infinite 1s;
    font-size: 22px;
}

.stars {
    position: absolute;
    width: 100%;
    height: 100%;
    top: 0;
    left: 0;
    z-index: -1;
}

.stars::before,
.stars::after {
    content: "";
    position: absolute;
    width: 100%;
    height: 100%;
    background-image:
        radial-gradient(1px 1px at 10% 10%, rgba(255, 255, 255, 0.8) 50%, transparent 100%),
        radial-gradient(1.5px 1.5px at 20% 20%, rgba(255, 255, 255, 0.7) 50%, transparent 100%),
        radial-gradient(1px 1px at 30% 30%, rgba(255, 255, 255, 0.9) 50%, transparent 100%),
        radial-gradient(2px 2px at 40% 40%, rgba(255, 255, 255, 0.6) 50%, transparent 100%),
        radial-gradient(1px 1px at 50% 50%, rgba(255, 255, 255, 0.8) 50%, transparent 100%),
        radial-gradient(1.5px 1.5px at 60% 60%, rgba(255, 255, 255, 0.7) 50%, transparent 100%),
        radial-gradient(1px 1px at 70% 70%, rgba(255, 255, 255, 0.9) 50%, transparent 100%),
        radial-gradient(2px 2px at 80% 80%, rgba(255, 255, 255, 0.6) 50%, transparent 100%),
        radial-gradient(1px 1px at 90% 90%, rgba(255, 255, 255, 0.8) 50%, transparent 100%);
    background-repeat: repeat;
    background-size: 200px 200px;
}

.stars::before {
    animation: twinkle 3s ease-in-out infinite;
}

.stars::after {
    background-size: 250px 250px;
    background-position: 50px 50px;
    animation: twinkle 4s ease-in-out 1s infinite;
}

.register-card {
    background: rgba(7, 19, 41, 0.85);
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
    padding: 40px;
    width: 100%;
    max-width: 400px;
    text-align: center;
    position: relative;
    z-index: 2;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(78, 160, 220, 0.2);
    overflow: hidden;
}

.register-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg,
            rgba(255, 255, 255, 0.1) 0%,
            rgba(255, 255, 255, 0.05) 50%,
            rgba(255, 255, 255, 0.02) 100%);
    z-index: -1;
}

.register-header {
    margin-bottom: 30px;
}

h2.title-animation {
    color: #ffffff;
    margin-bottom: 10px;
    font-size: 32px;
    font-weight: 600;
    text-shadow: 0 2px 10px rgba(78, 196, 255, 0.4);
    background: linear-gradient(135deg, #ffffff 0%, #7eb6ff 100%);
    background-clip: text;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
    animation: fadeInUp 0.8s ease-out forwards;
}

.sub-title {
    color: #a0d4ff;
    margin-bottom: 30px;
    font-size: 16px;
    text-shadow: 0 1px 5px rgba(0, 0, 0, 0.5);
    animation: fadeInUp 0.8s ease-out 0.2s forwards;
    opacity: 0;
}

.register-form {
    text-align: left;
}

.fade-in-item {
    opacity: 0;
    animation: fadeInUp 0.5s ease-out forwards;
}

.custom-input {
    margin-bottom: 10px;
    border-radius: 8px;
    overflow: hidden;
}

.custom-input :deep(.el-input__inner) {
    background: rgba(255, 255, 255, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #a0d4ff;
    border-radius: 8px;
    padding-left: 48px;
    height: 48px;
    font-size: 16px;
    transition: all 0.3s ease;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    font-weight: 600;
    letter-spacing: 0.5px;
}

.custom-input :deep(.el-input__inner:focus) {
    border-color: rgba(78, 196, 255, 0.8);
    box-shadow: 0 0 10px rgba(78, 196, 255, 0.5);
    background: rgba(255, 255, 255, 0.35);
}

.custom-input :deep(.el-input__inner::placeholder) {
    color: rgba(120, 192, 255, 0.7);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    font-weight: 500;
}

.custom-input :deep(.el-input__prefix) {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    left: 0;
    background-color: rgba(255, 255, 255, 0.6);
    height: 100%;
    border-radius: 8px 0 0 8px;
    border-right: 1px solid rgba(255, 255, 255, 0.4);
}

.el-input {
    margin-bottom: 10px;
}

.el-input :deep(.el-input__inner) {
    background: rgba(255, 255, 255, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: #a0d4ff;
    border-radius: 8px;
    padding-left: 48px;
    height: 48px;
    font-size: 16px;
    transition: all 0.3s ease;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    font-weight: 600;
    letter-spacing: 0.5px;
}

.el-input :deep(.el-input__inner:focus) {
    border-color: rgba(78, 196, 255, 0.8);
    box-shadow: 0 0 10px rgba(78, 196, 255, 0.5);
    background: rgba(255, 255, 255, 0.35);
}

.el-input :deep(.el-input__inner::placeholder) {
    color: rgba(120, 192, 255, 0.7);
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
    font-weight: 500;
}

.el-input :deep(.el-input__prefix) {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    left: 0;
    background-color: rgba(255, 255, 255, 0.6);
    height: 100%;
    border-radius: 8px 0 0 8px;
    border-right: 1px solid rgba(255, 255, 255, 0.4);
}

.el-checkbox :deep(.el-checkbox__label) {
    color: #a0d4ff;
    font-size: 15px;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    font-weight: 500;
    letter-spacing: 0.3px;
}

.el-checkbox :deep(.el-checkbox__inner) {
    background: rgba(255, 255, 255, 0.15);
    border: 2px solid rgba(255, 255, 255, 0.6);
    width: 18px;
    height: 18px;
}

.el-checkbox :deep(.el-checkbox__inner::after) {
    border-color: #429fdd;
    height: 9px;
    width: 4px;
    left: 5px;
    top: 1px;
}

.el-form-item.is-error :deep(.el-form-item__error) {
    color: #ff9ebf;
    font-size: 13px;
    font-weight: 500;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    padding-top: 4px;
}

.register-button {
    width: 100%;
    padding: 14px 0;
    font-size: 16px;
    background: linear-gradient(135deg, #429fdd 0%, #06214b 100%);
    border: none;
    border-radius: 8px;
    letter-spacing: 1px;
    font-weight: 500;
    transition: all 0.3s ease;
    box-shadow: 0 5px 15px rgba(6, 33, 75, 0.4);
}

.pulse-animation {
    animation: pulse 2s infinite;
}

.register-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(6, 33, 75, 0.6);
    background: linear-gradient(135deg, #5aafef 0%, #073063 100%);
}

.login-link {
    margin-top: 20px;
    font-size: 15px;
    color: rgba(255, 255, 255, 0.7);
    text-align: center;
}

.login-link a,
.highlight-link {
    color: #7eb6ff;
    text-decoration: none;
    font-weight: 500;
    transition: all 0.3s;
    position: relative;
    padding-bottom: 2px;
}

.login-link a:after,
.highlight-link:after {
    content: '';
    position: absolute;
    width: 0;
    height: 2px;
    bottom: 0;
    left: 0;
    background: linear-gradient(90deg, #7eb6ff, transparent);
    transition: width 0.3s ease;
}

.login-link a:hover,
.highlight-link:hover {
    color: #a0d4ff;
    text-decoration: none;
}

.login-link a:hover:after,
.highlight-link:hover:after {
    width: 100%;
}

a {
    color: #7eb6ff;
    text-decoration: none;
    transition: all 0.3s;
    font-weight: 600;
}

a:hover {
    color: #a0d4ff;
    text-shadow: 0 0 8px rgba(126, 182, 255, 0.7);
}

.moon-orbit {
    position: absolute;
    width: 700px;
    height: 300px;
    left: calc(15% - 150px);
    top: calc(50% - 150px);
    border-radius: 50%;
    transform: rotate(-15deg);
    z-index: 3;
    animation: rotate 120s linear infinite reverse;
    border: 2px dashed rgba(255, 255, 255, 0.15);
    pointer-events: none;
}

.moon {
    position: absolute;
    width: 70px;
    height: 70px;
    background: radial-gradient(circle at 25px 25px, #f8f8f8, #d0d0d0);
    border-radius: 50%;
    top: -35px;
    /* 调整位置使月亮在轨道上 */
    left: 50%;
    transform: translateX(-50%);
    box-shadow: 0 0 35px 5px rgba(255, 255, 255, 0.9);
    z-index: 4;
    animation: moonGlow 8s infinite ease-in-out;
    overflow: hidden;
}

.moon::before {
    content: '';
    position: absolute;
    width: 70px;
    height: 70px;
    background-image: radial-gradient(circle at 7px 10px, rgba(0, 0, 0, 0.15) 5px, transparent 6px),
        radial-gradient(circle at 21px 17px, rgba(0, 0, 0, 0.15) 10px, transparent 10px),
        radial-gradient(circle at 45px 28px, rgba(0, 0, 0, 0.15) 7px, transparent 7px),
        radial-gradient(circle at 42px 49px, rgba(0, 0, 0, 0.15) 14px, transparent 14px),
        radial-gradient(circle at 14px 42px, rgba(0, 0, 0, 0.15) 8px, transparent 8px);
    opacity: 0.8;
}

.register-icon {
    width: 50px;
    height: 50px;
    margin-bottom: 15px;
    color: #78c0ff;
    filter: drop-shadow(0 0 8px rgba(120, 192, 255, 0.4));
}

.icon-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-bottom: 10px;
}

.input-icon {
    width: 22px;
    height: 22px;
    color: #78c0ff;
    stroke-width: 2.5;
    filter: none;
}

.custom-input :deep(.el-input__prefix) {
    display: flex;
    align-items: center;
}

.checkbox-content {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
}

.checkbox-icon {
    width: 16px;
    height: 16px;
    margin-right: 5px;
    color: #78c0ff;
}

.terms-link {
    display: inline-flex;
    align-items: center;
    margin: 0 3px;
}

.link-icon {
    width: 14px;
    height: 14px;
    margin-right: 3px;
    color: #78c0ff;
}

.button-icon {
    width: 20px;
    height: 20px;
    margin-right: 8px;
    color: #ffffff;
}

.login-icon {
    width: 16px;
    height: 16px;
    margin-right: 5px;
    color: #78c0ff;
    vertical-align: middle;
}

.login-link-icon {
    width: 16px;
    height: 16px;
    margin-right: 4px;
    color: #78c0ff;
    vertical-align: middle;
}

.login-link {
    display: flex;
    align-items: center;
    justify-content: center;
}

.highlight-link {
    display: inline-flex;
    align-items: center;
}
</style>