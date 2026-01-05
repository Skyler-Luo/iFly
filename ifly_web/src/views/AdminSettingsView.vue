<template>
  <div class="admin-settings">
    <h1 class="title">系统设置</h1>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange" class="settings-tabs">
      <!-- 站点信息标签页 - Requirements 6.1, 1.1-1.5 -->
      <el-tab-pane label="站点信息" name="site">
        <el-form
          ref="siteFormRef"
          :model="siteSettings"
          :rules="siteRules"
          label-width="120px"
          v-loading="loading"
        >
          <el-form-item label="站点名称" prop="site_name">
            <el-input v-model="siteSettings.site_name" placeholder="请输入站点名称" />
          </el-form-item>

          <el-form-item label="Logo URL" prop="logo_url">
            <el-input v-model="siteSettings.logo_url" placeholder="请输入 Logo 图片地址">
              <template #prepend>https://</template>
            </el-input>
            <div class="form-tip">支持 http://, https:// 或相对路径 /</div>
          </el-form-item>

          <el-form-item label="Favicon URL" prop="favicon_url">
            <el-input v-model="siteSettings.favicon_url" placeholder="请输入 Favicon 图片地址">
              <template #prepend>https://</template>
            </el-input>
            <div class="form-tip">支持 http://, https:// 或相对路径 /</div>
          </el-form-item>

          <el-form-item label="联系邮箱" prop="contact_email">
            <el-input v-model="siteSettings.contact_email" placeholder="请输入联系邮箱" />
          </el-form-item>

          <el-form-item label="联系电话" prop="contact_phone">
            <el-input v-model="siteSettings.contact_phone" placeholder="请输入联系电话" />
          </el-form-item>

          <el-form-item label="联系地址" prop="contact_address">
            <el-input
              v-model="siteSettings.contact_address"
              type="textarea"
              :rows="2"
              placeholder="请输入联系地址"
            />
          </el-form-item>

          <el-form-item label="版权信息" prop="copyright_text">
            <el-input v-model="siteSettings.copyright_text" placeholder="请输入版权信息" />
          </el-form-item>

          <el-form-item label="ICP备案号" prop="icp_number">
            <el-input v-model="siteSettings.icp_number" placeholder="请输入ICP备案号" />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveSiteSettings" :loading="saving">
              保存设置
            </el-button>
            <el-button @click="resetSiteSettings">重置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 业务规则标签页 - Requirements 6.1, 2.1-2.4 -->
      <el-tab-pane label="业务规则" name="business">
        <el-form
          ref="businessFormRef"
          :model="businessRules"
          :rules="businessRulesValidation"
          label-width="140px"
          v-loading="loading"
        >
          <el-form-item label="支付超时时间" prop="payment_timeout_minutes">
            <el-input-number
              v-model="businessRules.payment_timeout_minutes"
              :min="5"
              :max="120"
              :step="5"
            />
            <span class="unit-label">分钟</span>
            <div class="form-tip">订单创建后未支付的超时时间，默认30分钟</div>
          </el-form-item>

          <el-form-item label="退款费率" prop="refund_fee_rate">
            <el-input-number
              v-model="businessRules.refund_fee_rate"
              :min="0"
              :max="1"
              :step="0.01"
              :precision="2"
            />
            <span class="unit-label">（0-1之间的小数）</span>
            <div class="form-tip">退票时收取的手续费比例，如0.05表示5%</div>
          </el-form-item>

          <el-form-item label="改签费率" prop="reschedule_fee_rate">
            <el-input-number
              v-model="businessRules.reschedule_fee_rate"
              :min="0"
              :max="1"
              :step="0.01"
              :precision="2"
            />
            <span class="unit-label">（0-1之间的小数）</span>
            <div class="form-tip">改签时收取的手续费比例，如0.1表示10%</div>
          </el-form-item>

          <el-form-item label="值机开放时间" prop="checkin_hours_before">
            <el-input-number
              v-model="businessRules.checkin_hours_before"
              :min="1"
              :max="72"
              :step="1"
            />
            <span class="unit-label">小时（起飞前）</span>
            <div class="form-tip">航班起飞前多少小时开放在线值机，默认24小时</div>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="saveBusinessRules" :loading="saving">
              保存设置
            </el-button>
            <el-button @click="resetBusinessRules">重置</el-button>
          </el-form-item>
        </el-form>
      </el-tab-pane>

      <!-- 变更历史标签页 - Requirements 2.5 -->
      <el-tab-pane label="变更历史" name="history">
        <div class="history-filters">
          <el-select v-model="historyFilter.category" placeholder="选择分类" clearable>
            <el-option label="站点信息" value="site" />
            <el-option label="业务规则" value="business" />
          </el-select>
          <el-button type="primary" @click="loadSettingsHistory">查询</el-button>
        </div>

        <el-table :data="settingsHistory" v-loading="historyLoading" stripe>
          <el-table-column prop="changed_at" label="变更时间" width="180">
            <template #default="{ row }">
              {{ formatDateTime(row.changed_at) }}
            </template>
          </el-table-column>
          <el-table-column prop="setting_category" label="分类" width="100">
            <template #default="{ row }">
              <el-tag :type="row.setting_category === 'site' ? 'primary' : 'success'">
                {{ row.setting_category === 'site' ? '站点信息' : '业务规则' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="setting_key" label="配置项" width="150" />
          <el-table-column prop="old_value" label="旧值" min-width="150" show-overflow-tooltip />
          <el-table-column prop="new_value" label="新值" min-width="150" show-overflow-tooltip />
          <el-table-column prop="changed_by" label="修改人" width="120" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import api from '@/services/api'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'AdminSettingsView',
  data() {
    // URL 验证器 - Requirements 1.5, 6.4
    const validateUrl = (rule, value, callback) => {
      if (!value) {
        callback()
        return
      }
      const urlPattern = /^(https?:\/\/|\/)[^\s]*$/
      if (!urlPattern.test(value)) {
        callback(new Error('URL 格式不正确，支持 http://, https:// 或相对路径 /'))
      } else {
        callback()
      }
    }

    return {
      activeTab: 'site',
      loading: false,
      saving: false,
      historyLoading: false,

      // 站点设置 - Requirements 1.1-1.4
      siteSettings: {
        site_name: '',
        logo_url: '',
        favicon_url: '',
        contact_email: '',
        contact_phone: '',
        contact_address: '',
        copyright_text: '',
        icp_number: ''
      },
      originalSiteSettings: null,

      // 站点设置验证规则 - Requirements 1.5, 6.4
      siteRules: {
        site_name: [
          { required: true, message: '请输入站点名称', trigger: 'blur' }
        ],
        logo_url: [
          { validator: validateUrl, trigger: 'blur' }
        ],
        favicon_url: [
          { validator: validateUrl, trigger: 'blur' }
        ],
        contact_email: [
          { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
        ]
      },

      // 业务规则 - Requirements 2.1-2.4
      businessRules: {
        payment_timeout_minutes: 30,
        refund_fee_rate: 0.05,
        reschedule_fee_rate: 0.1,
        checkin_hours_before: 24
      },
      originalBusinessRules: null,

      // 业务规则验证
      businessRulesValidation: {
        payment_timeout_minutes: [
          { required: true, message: '请输入支付超时时间', trigger: 'blur' }
        ],
        refund_fee_rate: [
          { required: true, message: '请输入退款费率', trigger: 'blur' }
        ],
        reschedule_fee_rate: [
          { required: true, message: '请输入改签费率', trigger: 'blur' }
        ],
        checkin_hours_before: [
          { required: true, message: '请输入值机开放时间', trigger: 'blur' }
        ]
      },

      // 变更历史
      historyFilter: {
        category: ''
      },
      settingsHistory: []
    }
  },

  async created() {
    await this.loadSiteSettings()
  },

  methods: {
    // 标签页切换处理 - Requirements 6.2
    async handleTabChange(tabName) {
      if (tabName === 'site') {
        await this.loadSiteSettings()
      } else if (tabName === 'business') {
        await this.loadBusinessRules()
      } else if (tabName === 'history') {
        await this.loadSettingsHistory()
      }
    },

    // 加载站点设置 - Requirements 6.2
    async loadSiteSettings() {
      this.loading = true
      try {
        const response = await api.admin.settings.getSiteSettings()
        this.siteSettings = { ...this.siteSettings, ...response }
        this.originalSiteSettings = JSON.parse(JSON.stringify(this.siteSettings))
      } catch (error) {
        console.error('加载站点设置失败:', error)
        ElMessage.error('加载站点设置失败')
      } finally {
        this.loading = false
      }
    },

    // 加载业务规则 - Requirements 6.2
    async loadBusinessRules() {
      this.loading = true
      try {
        const response = await api.admin.settings.getBusinessRules()
        this.businessRules = { ...this.businessRules, ...response }
        this.originalBusinessRules = JSON.parse(JSON.stringify(this.businessRules))
      } catch (error) {
        console.error('加载业务规则失败:', error)
        ElMessage.error('加载业务规则失败')
      } finally {
        this.loading = false
      }
    },

    // 保存站点设置 - Requirements 6.3, 6.4
    async saveSiteSettings() {
      try {
        await this.$refs.siteFormRef.validate()
      } catch {
        ElMessage.warning('请检查表单填写是否正确')
        return
      }

      this.saving = true
      try {
        await api.admin.settings.updateSiteSettings(this.siteSettings)
        ElMessage.success('站点设置已保存')
        this.originalSiteSettings = JSON.parse(JSON.stringify(this.siteSettings))
      } catch (error) {
        console.error('保存站点设置失败:', error)
        ElMessage.error(error.message || '保存站点设置失败')
      } finally {
        this.saving = false
      }
    },

    // 保存业务规则 - Requirements 6.3, 6.5
    async saveBusinessRules() {
      try {
        await this.$refs.businessFormRef.validate()
      } catch {
        ElMessage.warning('请检查表单填写是否正确')
        return
      }

      // 确认对话框 - Requirements 6.5
      try {
        await ElMessageBox.confirm(
          '业务规则的修改将立即生效，确定要保存吗？',
          '确认保存',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
      } catch {
        return
      }

      this.saving = true
      try {
        await api.admin.settings.updateBusinessRules(this.businessRules)
        ElMessage.success('业务规则已保存')
        this.originalBusinessRules = JSON.parse(JSON.stringify(this.businessRules))
      } catch (error) {
        console.error('保存业务规则失败:', error)
        ElMessage.error(error.message || '保存业务规则失败')
      } finally {
        this.saving = false
      }
    },

    // 重置站点设置
    resetSiteSettings() {
      if (this.originalSiteSettings) {
        this.siteSettings = JSON.parse(JSON.stringify(this.originalSiteSettings))
      }
    },

    // 重置业务规则
    resetBusinessRules() {
      if (this.originalBusinessRules) {
        this.businessRules = JSON.parse(JSON.stringify(this.originalBusinessRules))
      }
    },

    // 加载变更历史 - Requirements 2.5
    async loadSettingsHistory() {
      this.historyLoading = true
      try {
        const params = {}
        if (this.historyFilter.category) {
          params.category = this.historyFilter.category
        }
        const response = await api.admin.settings.getSettingsHistory(params)
        this.settingsHistory = Array.isArray(response) ? response : []
      } catch (error) {
        console.error('加载变更历史失败:', error)
        ElMessage.error('加载变更历史失败')
        this.settingsHistory = []
      } finally {
        this.historyLoading = false
      }
    },

    // 格式化日期时间
    formatDateTime(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }
  }
}
</script>

<style scoped>
.admin-settings {
  padding: 20px 40px;
  width: 100%;
  box-sizing: border-box;
}

.title {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  border-bottom: 2px solid #409eff;
  padding-bottom: 10px;
}

.settings-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.settings-tabs :deep(.el-tabs__content) {
  padding: 20px 0;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.unit-label {
  margin-left: 10px;
  color: #606266;
}

.history-filters {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.history-filters .el-select {
  width: 200px;
}

@media (max-width: 768px) {
  .admin-settings {
    padding: 15px;
  }

  .settings-tabs {
    padding: 10px;
  }

  .history-filters {
    flex-direction: column;
  }

  .history-filters .el-select {
    width: 100%;
  }
}
</style>
