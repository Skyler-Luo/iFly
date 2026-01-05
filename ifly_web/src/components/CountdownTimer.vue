<template>
  <span :class="timerClass">
    <el-icon v-if="showIcon" class="timer-icon">
      <Clock />
    </el-icon>
    <span class="timer-text">{{ displayText }}</span>
  </span>
</template>

<script>
import { Clock } from '@element-plus/icons-vue'
import { formatCountdown } from '@/utils/countdownFormatter'

export default {
  name: 'CountdownTimer',
  components: {
    Clock
  },
  props: {
    // 剩余秒数
    remainingSeconds: {
      type: Number,
      required: true
    },
    // 警告阈值（秒），默认5分钟
    warningThreshold: {
      type: Number,
      default: 300
    },
    // 是否显示图标
    showIcon: {
      type: Boolean,
      default: true
    },
    // 是否自动倒计时
    autoCountdown: {
      type: Boolean,
      default: true
    },
    // 超时显示文本
    expiredText: {
      type: String,
      default: '已超时'
    }
  },
  emits: ['timeout', 'update:remainingSeconds'],
  data() {
    return {
      currentSeconds: this.remainingSeconds,
      timerId: null
    }
  },
  computed: {
    // 是否已超时
    isExpired() {
      return this.currentSeconds <= 0
    },
    // 是否处于警告状态
    isWarning() {
      return !this.isExpired && this.currentSeconds <= this.warningThreshold
    },
    // 格式化显示时间
    formattedTime() {
      return formatCountdown(this.currentSeconds)
    },
    // 显示文本
    displayText() {
      if (this.isExpired) {
        return this.expiredText
      }
      return this.formattedTime
    },
    // 计时器样式类
    timerClass() {
      return {
        'countdown-timer': true,
        'countdown-timer--warning': this.isWarning,
        'countdown-timer--expired': this.isExpired
      }
    }
  },
  watch: {
    remainingSeconds: {
      immediate: true,
      handler(newVal) {
        this.currentSeconds = newVal
        if (this.autoCountdown) {
          this.startCountdown()
        }
      }
    }
  },
  mounted() {
    if (this.autoCountdown && this.currentSeconds > 0) {
      this.startCountdown()
    }
  },
  beforeUnmount() {
    this.stopCountdown()
  },
  methods: {
    // 启动倒计时
    startCountdown() {
      this.stopCountdown()
      if (this.currentSeconds <= 0) {
        return
      }
      this.timerId = setInterval(() => {
        this.currentSeconds--
        this.$emit('update:remainingSeconds', this.currentSeconds)
        if (this.currentSeconds <= 0) {
          this.stopCountdown()
          this.$emit('timeout')
        }
      }, 1000)
    },
    // 停止倒计时
    stopCountdown() {
      if (this.timerId) {
        clearInterval(this.timerId)
        this.timerId = null
      }
    }
  }
}
</script>

<style scoped>
.countdown-timer {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: #606266;
}

.countdown-timer--warning {
  color: #e6a23c;
  font-weight: 500;
}

.countdown-timer--expired {
  color: #f56c6c;
  font-weight: 500;
}

.timer-icon {
  font-size: 16px;
}

.timer-text {
  font-family: 'Courier New', monospace;
}
</style>
