<template>
  <div class="route-info" v-if="selectedRoute">
    <div class="route-card">
      <h4>已选择航线</h4>
      <div class="route-details">
        <p>
          <strong>出发城市:</strong> {{ selectedRoute.from }}
        </p>
        <p>
          <strong>目的城市:</strong> {{ selectedRoute.to }}
        </p>
      </div>
      <div class="route-actions">
        <el-button type="primary" size="small" @click="$emit('select-route')">选择此航线</el-button>
        <el-button type="danger" size="small" @click="$emit('reset-route')">重置选择</el-button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RouteInfoCard',
  props: {
    selectedRoute: {
      type: Object,
      default: null
    }
  }
}
</script>

<style scoped>
.route-info {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 1000;
}

.route-card {
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  min-width: 280px;
}

.route-card h4 {
  margin: 0 0 12px 0;
  color: #1890ff;
  font-size: 16px;
}

.route-details p {
  margin: 8px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.route-details strong {
  margin-right: 8px;
}

.route-actions {
  margin-top: 16px;
  display: flex;
  gap: 8px;
}

.route-actions .el-button {
  flex: 1;
}
</style>
