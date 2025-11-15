<template>
  <div class="social-login-container">
    <div class="divider">
      <span>或</span>
    </div>

    <div class="social-login">
      <p>其他登录方式</p>
      <div class="social-icons">
        <div class="social-icon"><el-icon>
            <Message />
          </el-icon></div>
        <div class="social-icon"><el-icon>
            <Service />
          </el-icon></div>
        <div class="social-icon"><el-icon>
            <Phone />
          </el-icon></div>
      </div>
    </div>
  </div>
</template>

<script>
import { Message, Service, Phone } from '@element-plus/icons-vue'

export default {
  name: 'SocialLogin',
  components: {
    Message,
    Service,
    Phone
  },
  emits: ['social-login']
}
</script>

<style scoped>
.social-login-container {
  margin-top: 20px;
}

.divider {
  display: flex;
  align-items: center;
  margin: 20px 0;
}

.divider::before,
.divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.2);
}

.divider span {
  padding: 0 15px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.social-login {
  text-align: center;
}

.social-login p {
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 15px;
  font-size: 14px;
}

.social-icons {
  display: flex;
  justify-content: center;
  gap: 15px;
}

.social-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.social-icon:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateY(-3px);
}

.social-icon .el-icon {
  font-size: 20px;
  color: white;
}
</style> 