<template>
  <div class="security-tab">
    <el-card class="security-card">
      <template #header>
        <div class="security-header">
          <h3>密码修改</h3>
        </div>
      </template>

      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="120px"
        v-loading="submitting"
      >
        <el-form-item label="当前密码" prop="old_password">
          <el-input
            v-model="passwordForm.old_password"
            type="password"
            placeholder="请输入当前密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="新密码" prop="new_password">
          <el-input
            v-model="passwordForm.new_password"
            type="password"
            placeholder="请输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item label="确认新密码" prop="new_password2">
          <el-input
            v-model="passwordForm.new_password2"
            type="password"
            placeholder="请再次输入新密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="changePassword">修改密码</el-button>
          <el-button @click="resetPasswordForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="security-card">
      <template #header>
        <div class="security-header">
          <h3>账户绑定</h3>
        </div>
      </template>

      <div class="binding-list" v-loading="loadingProfile">
        <div class="binding-item">
          <div class="binding-info">
            <el-icon class="binding-icon">
              <Cellphone />
            </el-icon>
            <div class="binding-detail">
              <div class="binding-title">手机绑定</div>
              <div class="binding-desc" v-if="userInfo.phone">
                已绑定手机: {{ formatPhone(userInfo.phone) }}
              </div>
              <div class="binding-desc" v-else>未绑定手机号</div>
            </div>
          </div>

          <el-button
            type="primary"
            size="small"
            @click="showBindPhoneDialog"
            plain
          >
            {{ userInfo.phone ? '修改' : '绑定' }}
          </el-button>
        </div>

        <div class="binding-item">
          <div class="binding-info">
            <el-icon class="binding-icon">
              <Message />
            </el-icon>
            <div class="binding-detail">
              <div class="binding-title">邮箱绑定</div>
              <div class="binding-desc" v-if="userInfo.email">
                已绑定邮箱: {{ formatEmail(userInfo.email) }}
              </div>
              <div class="binding-desc" v-else>未绑定邮箱</div>
            </div>
          </div>

          <el-button
            type="primary"
            size="small"
            @click="showBindEmailDialog"
            plain
          >
            {{ userInfo.email ? '修改' : '绑定' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card class="security-card">
      <template #header>
        <div class="security-header">
          <h3>账户安全</h3>
        </div>
      </template>

      <div class="security-options">
        <!-- 设备管理 - 敬请期待 -->
        <div class="security-item coming-soon-item">
          <div class="security-info">
            <el-icon class="security-icon">
              <Lock />
            </el-icon>
            <div class="security-detail">
              <div class="security-title">
                登录设备管理
                <el-tag size="small" type="info" class="coming-soon-tag"
                  >敬请期待</el-tag
                >
              </div>
              <div class="security-desc">查看和管理您当前登录的设备</div>
            </div>
          </div>

          <el-button type="primary" size="small" disabled plain>
            查看
          </el-button>
        </div>

        <div class="security-item">
          <div class="security-info">
            <el-icon class="security-icon">
              <Delete />
            </el-icon>
            <div class="security-detail">
              <div class="security-title">注销账户</div>
              <div class="security-desc">永久删除您的账户和所有相关数据</div>
            </div>
          </div>

          <el-button
            type="danger"
            size="small"
            @click="showDeleteAccountDialog"
            plain
          >
            注销
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 手机绑定对话框 -->
    <el-dialog
      v-model="phoneDialogVisible"
      :title="userInfo.phone ? '修改手机绑定' : '绑定手机'"
      width="400px"
    >
      <el-form
        ref="phoneFormRef"
        :model="phoneForm"
        :rules="phoneRules"
        label-width="100px"
      >
        <el-form-item label="手机号码" prop="phone">
          <el-input v-model="phoneForm.phone" placeholder="请输入手机号码" />
        </el-form-item>

        <el-form-item label="验证码" prop="code">
          <div class="verify-code-input">
            <el-input v-model="phoneForm.code" placeholder="请输入验证码" />
            <el-button
              type="primary"
              :disabled="codeSending || countdown > 0"
              @click="sendVerifyCode"
            >
              {{ countdown > 0 ? `${countdown}秒后重新获取` : '获取验证码' }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="phoneDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="bindPhone" :loading="binding">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 邮箱绑定对话框 -->
    <el-dialog
      v-model="emailDialogVisible"
      :title="userInfo.email ? '修改邮箱绑定' : '绑定邮箱'"
      width="400px"
    >
      <el-form
        ref="emailFormRef"
        :model="emailForm"
        :rules="emailRules"
        label-width="100px"
      >
        <el-form-item label="邮箱地址" prop="email">
          <el-input v-model="emailForm.email" placeholder="请输入邮箱地址" />
        </el-form-item>

        <el-form-item label="验证码" prop="code">
          <div class="verify-code-input">
            <el-input v-model="emailForm.code" placeholder="请输入验证码" />
            <el-button
              type="primary"
              :disabled="codeSending || emailCountdown > 0"
              @click="sendEmailVerifyCode"
            >
              {{
                emailCountdown > 0
                  ? `${emailCountdown}秒后重新获取`
                  : '获取验证码'
              }}
            </el-button>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="emailDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="bindEmail" :loading="binding">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 账户注销确认对话框 -->
    <el-dialog
      v-model="deleteAccountDialogVisible"
      title="账户注销确认"
      width="400px"
    >
      <div class="delete-account-warning">
        <el-alert
          title="注销账户将会导致以下结果："
          type="warning"
          :closable="false"
          show-icon
        />
        <ul class="warning-list">
          <li>您的个人资料将被永久删除</li>
          <li>您的订单历史将被匿名化处理</li>
          <li>您的常用乘客信息将被删除</li>
          <li>账户注销后无法恢复</li>
        </ul>
      </div>

      <el-form
        ref="deleteAccountFormRef"
        :model="deleteAccountForm"
        :rules="deleteAccountRules"
        label-width="100px"
      >
        <el-form-item label="账户密码" prop="password">
          <el-input
            v-model="deleteAccountForm.password"
            type="password"
            placeholder="请输入当前账户密码"
            show-password
          />
        </el-form-item>

        <el-form-item prop="confirm">
          <el-checkbox v-model="deleteAccountForm.confirm">
            我已知晓并理解账户注销的后果
          </el-checkbox>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="deleteAccountDialogVisible = false"
            >取消</el-button
          >
          <el-button
            type="danger"
            @click="confirmDeleteAccount"
            :loading="deleting"
          >
            确认注销
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Cellphone, Message, Lock, Delete } from '@element-plus/icons-vue'
import api from '@/services/api'
import tokenManager from '@/utils/tokenManager'

export default {
  name: 'SecurityTab',
  components: {
    Cellphone,
    Message,
    Lock,
    Delete
  },
  setup() {
    const router = useRouter()
    const passwordFormRef = ref(null)
    const phoneFormRef = ref(null)
    const emailFormRef = ref(null)
    const deleteAccountFormRef = ref(null)

    const submitting = ref(false)
    const binding = ref(false)
    const codeSending = ref(false)
    const loadingProfile = ref(false)
    const deleting = ref(false)

    const userInfo = ref({})

    // 对话框显示状态
    const phoneDialogVisible = ref(false)
    const emailDialogVisible = ref(false)
    const deleteAccountDialogVisible = ref(false)

    // 倒计时
    const countdown = ref(0)
    const emailCountdown = ref(0)
    const countdownTimer = ref(null)
    const emailCountdownTimer = ref(null)

    // 密码表单 - 字段名与后端 API 保持一致
    const passwordForm = reactive({
      old_password: '',
      new_password: '',
      new_password2: ''
    })

    // 手机表单
    const phoneForm = reactive({
      phone: '',
      code: ''
    })

    // 邮箱表单
    const emailForm = reactive({
      email: '',
      code: ''
    })

    // 注销账户表单
    const deleteAccountForm = reactive({
      password: '',
      confirm: false
    })

    // 密码表单验证规则
    const passwordRules = {
      old_password: [
        { required: true, message: '请输入当前密码', trigger: 'blur' }
      ],
      new_password: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 8, message: '密码长度不能小于8个字符', trigger: 'blur' }
      ],
      new_password2: [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.new_password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    // 手机表单验证规则
    const phoneRules = {
      phone: [
        { required: true, message: '请输入手机号码', trigger: 'blur' },
        {
          pattern: /^1[3456789]\d{9}$/,
          message: '请输入正确的手机号码',
          trigger: 'blur'
        }
      ],
      code: [
        { required: true, message: '请输入验证码', trigger: 'blur' },
        { len: 6, message: '验证码长度应为6位', trigger: 'blur' }
      ]
    }

    // 邮箱表单验证规则
    const emailRules = {
      email: [
        { required: true, message: '请输入邮箱地址', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
      ],
      code: [
        { required: true, message: '请输入验证码', trigger: 'blur' },
        { len: 6, message: '验证码长度应为6位', trigger: 'blur' }
      ]
    }

    // 注销账户表单验证规则
    const deleteAccountRules = {
      password: [
        { required: true, message: '请输入账户密码', trigger: 'blur' }
      ],
      confirm: [
        {
          validator: (rule, value, callback) => {
            if (value !== true) {
              callback(new Error('请确认您已知晓账户注销的后果'))
            } else {
              callback()
            }
          },
          trigger: 'change'
        }
      ]
    }

    // 获取用户信息 - 调用真实 API
    const fetchUserInfo = async () => {
      loadingProfile.value = true
      try {
        const response = await api.auth.getProfile()
        userInfo.value = response
        // 预填写手机和邮箱表单
        if (response.phone) {
          phoneForm.phone = response.phone
        }
        if (response.email) {
          emailForm.email = response.email
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 错误消息已由 API 拦截器处理
      } finally {
        loadingProfile.value = false
      }
    }

    // 修改密码 - 调用真实 API
    const changePassword = async () => {
      if (!passwordFormRef.value) return

      await passwordFormRef.value.validate(async valid => {
        if (valid) {
          submitting.value = true
          try {
            await api.auth.changePassword({
              old_password: passwordForm.old_password,
              new_password: passwordForm.new_password,
              new_password2: passwordForm.new_password2
            })
            ElMessage.success('密码修改成功，请重新登录')
            // 清空表单
            resetPasswordForm()
            // 清除 token 并跳转到登录页
            tokenManager.clearToken()
            router.push('/login')
          } catch (error) {
            console.error('密码修改失败:', error)
            // 显示 API 返回的具体错误信息
            if (error.data) {
              if (error.data.old_password) {
                ElMessage.error(error.data.old_password[0] || '当前密码不正确')
              } else if (error.data.new_password) {
                ElMessage.error(
                  error.data.new_password[0] || '新密码格式不正确'
                )
              } else if (error.data.new_password2) {
                ElMessage.error(error.data.new_password2[0] || '确认密码不匹配')
              } else if (error.data.detail) {
                ElMessage.error(error.data.detail)
              }
            }
            // 其他错误已由 API 拦截器处理
          } finally {
            submitting.value = false
          }
        }
      })
    }

    // 重置密码表单
    const resetPasswordForm = () => {
      if (passwordFormRef.value) {
        passwordFormRef.value.resetFields()
      }
    }

    // 显示绑定手机对话框
    const showBindPhoneDialog = () => {
      phoneDialogVisible.value = true
      if (userInfo.value.phone) {
        phoneForm.phone = userInfo.value.phone
      }
    }

    // 显示绑定邮箱对话框
    const showBindEmailDialog = () => {
      emailDialogVisible.value = true
      if (userInfo.value.email) {
        emailForm.email = userInfo.value.email
      }
    }

    // 发送手机验证码
    const sendVerifyCode = async () => {
      if (!phoneForm.phone) {
        ElMessage.warning('请先输入手机号码')
        return
      }

      if (!/^1[3456789]\d{9}$/.test(phoneForm.phone)) {
        ElMessage.warning('请输入正确的手机号码')
        return
      }

      codeSending.value = true
      try {
        // 验证码功能暂未实现
        ElMessage.info('验证码功能暂未开放')

        // 开始倒计时
        countdown.value = 60
        countdownTimer.value = setInterval(() => {
          countdown.value--
          if (countdown.value <= 0) {
            clearInterval(countdownTimer.value)
            countdownTimer.value = null
          }
        }, 1000)
      } catch (error) {
        console.error('发送验证码失败:', error)
      } finally {
        codeSending.value = false
      }
    }

    // 发送邮箱验证码
    const sendEmailVerifyCode = async () => {
      if (!emailForm.email) {
        ElMessage.warning('请先输入邮箱地址')
        return
      }

      if (
        !/^[\w-]+(\.[\w-]+)*@([\w-]+\.)+[a-zA-Z]{2,7}$/.test(emailForm.email)
      ) {
        ElMessage.warning('请输入正确的邮箱地址')
        return
      }

      codeSending.value = true
      try {
        // 验证码功能暂未实现
        ElMessage.info('验证码功能暂未开放')

        // 开始倒计时
        emailCountdown.value = 60
        emailCountdownTimer.value = setInterval(() => {
          emailCountdown.value--
          if (emailCountdown.value <= 0) {
            clearInterval(emailCountdownTimer.value)
            emailCountdownTimer.value = null
          }
        }, 1000)
      } catch (error) {
        console.error('发送验证码失败:', error)
      } finally {
        codeSending.value = false
      }
    }

    // 绑定手机
    const bindPhone = async () => {
      if (!phoneFormRef.value) return

      await phoneFormRef.value.validate(async valid => {
        if (valid) {
          binding.value = true
          try {
            // 绑定功能暂未实现
            ElMessage.info('手机绑定功能暂未开放')
            phoneDialogVisible.value = false
            phoneForm.code = ''
          } catch (error) {
            console.error('手机绑定失败:', error)
          } finally {
            binding.value = false
          }
        }
      })
    }

    // 绑定邮箱
    const bindEmail = async () => {
      if (!emailFormRef.value) return

      await emailFormRef.value.validate(async valid => {
        if (valid) {
          binding.value = true
          try {
            // 绑定功能暂未实现
            ElMessage.info('邮箱绑定功能暂未开放')
            emailDialogVisible.value = false
            emailForm.code = ''
          } catch (error) {
            console.error('邮箱绑定失败:', error)
          } finally {
            binding.value = false
          }
        }
      })
    }

    // 显示注销账户对话框
    const showDeleteAccountDialog = () => {
      deleteAccountDialogVisible.value = true
    }

    // 确认注销账户
    const confirmDeleteAccount = async () => {
      if (!deleteAccountFormRef.value) return

      await deleteAccountFormRef.value.validate(async valid => {
        if (valid) {
          // 二次确认
          try {
            await ElMessageBox.confirm(
              '注销账户操作不可逆，您确定要永久删除您的账户吗？',
              '危险操作确认',
              {
                confirmButtonText: '确认注销',
                cancelButtonText: '取消',
                type: 'warning',
                distinguishCancelAndClose: true
              }
            )

            deleting.value = true
            try {
              // 注销功能暂未实现
              ElMessage.info('账户注销功能暂未开放')
              deleteAccountDialogVisible.value = false
            } catch (error) {
              console.error('注销账户失败:', error)
            } finally {
              deleting.value = false
            }
          } catch {
            // 用户取消操作
          }
        }
      })
    }

    // 格式化手机号
    const formatPhone = phone => {
      if (!phone) return ''
      return phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2')
    }

    // 格式化邮箱
    const formatEmail = email => {
      if (!email) return ''
      const parts = email.split('@')
      if (parts.length !== 2) return email

      let username = parts[0]
      const domain = parts[1]

      if (username.length <= 3) {
        username = username.charAt(0) + '*'.repeat(username.length - 1)
      } else {
        username = username.charAt(0) + '*'.repeat(3) + username.substring(4)
      }

      return `${username}@${domain}`
    }

    onMounted(() => {
      fetchUserInfo()
    })

    onBeforeUnmount(() => {
      // 清除定时器
      if (countdownTimer.value) {
        clearInterval(countdownTimer.value)
      }
      if (emailCountdownTimer.value) {
        clearInterval(emailCountdownTimer.value)
      }
    })

    return {
      passwordFormRef,
      phoneFormRef,
      emailFormRef,
      deleteAccountFormRef,
      submitting,
      binding,
      codeSending,
      loadingProfile,
      deleting,
      userInfo,
      phoneDialogVisible,
      emailDialogVisible,
      deleteAccountDialogVisible,
      countdown,
      emailCountdown,
      passwordForm,
      phoneForm,
      emailForm,
      deleteAccountForm,
      passwordRules,
      phoneRules,
      emailRules,
      deleteAccountRules,
      changePassword,
      resetPasswordForm,
      showBindPhoneDialog,
      showBindEmailDialog,
      sendVerifyCode,
      sendEmailVerifyCode,
      bindPhone,
      bindEmail,
      showDeleteAccountDialog,
      confirmDeleteAccount,
      formatPhone,
      formatEmail
    }
  }
}
</script>

<style scoped>
.security-tab {
  padding: 10px;
}

.security-card {
  margin-bottom: 20px;
  border-radius: 8px;
}

.security-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.security-header h3 {
  margin: 0;
}

.binding-list,
.security-options {
  padding: 10px 0;
}

.binding-item,
.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.binding-item:last-child,
.security-item:last-child {
  border-bottom: none;
}

.binding-info,
.security-info {
  display: flex;
  align-items: center;
}

.binding-icon,
.security-icon {
  font-size: 24px;
  margin-right: 15px;
  color: #409eff;
}

.binding-title,
.security-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.binding-desc,
.security-desc {
  font-size: 13px;
  color: #909399;
}

.verify-code-input {
  display: flex;
  gap: 10px;
}

.coming-soon-item {
  opacity: 0.7;
}

.coming-soon-tag {
  font-size: 12px;
}

.delete-account-warning {
  margin-bottom: 20px;
}

.warning-list {
  margin-top: 15px;
  padding-left: 20px;
  color: #e6a23c;
}

.warning-list li {
  margin-bottom: 8px;
}
</style>
