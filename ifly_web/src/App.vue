<template>
  <div class="common-layout">
    <app-header class="full-width" />

    <el-container class="main-container">
      <router-view />
    </el-container>

    <site-footer class="full-width" />

    <!-- 回到顶部按钮 -->
    <el-backtop :right="20" :bottom="100" />
  </div>
</template>

<script>
import AppHeader from '@/components/AppHeader.vue'
import SiteFooter from '@/components/SiteFooter.vue'

export default {
  name: 'App',
  components: {
    AppHeader,
    SiteFooter
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html,
body {
  width: 100%;
  overflow-x: hidden;
}

body {
  font-family: 'Microsoft YaHei', Arial, sans-serif;
  color: #333;
  background-color: #ffffff;
}

.common-layout {
  width: 100%;
  overflow-x: hidden;
}

.main-container {
  width: 100%;
  min-height: calc(100vh - 60px);
  display: flex;
  flex-direction: column;
  margin-top: 60px;
  padding: 0;
  background: #ffffff;
}

.full-width {
  width: 100%;
  max-width: 100%;
  padding: 0;
  margin: 0;
  overflow-x: hidden;
  box-sizing: border-box;
}

.el-header {
  padding: 0;
  height: auto !important;
}

 

.el-footer {
  padding: 0;
  height: auto !important;
}
</style>
