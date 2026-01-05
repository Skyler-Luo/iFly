const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')
const TerserPlugin = require('terser-webpack-plugin')

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_OPTIONS_API__: JSON.stringify(true),
        __VUE_PROD_DEVTOOLS__: JSON.stringify(false),
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false)
      })
    ],
    // 生产环境优化配置
    optimization: process.env.NODE_ENV === 'production' ? {
      minimizer: [
        '...',
        // 自动移除console语句和debugger
        new TerserPlugin({
          terserOptions: {
            compress: {
              drop_console: true,
              drop_debugger: true,
              pure_funcs: ['console.log', 'console.warn', 'console.error']
            }
          }
        })
      ]
    } : {}
  },
  // 开发服务器配置
  devServer: {
    port: 8080,
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false
      }
    },
    // 忽略 ResizeObserver 错误的 overlay 显示
    client: {
      overlay: {
        warnings: false,
        errors: true,
        runtimeErrors: (error) => {
          if (error.message && error.message.includes('ResizeObserver loop')) {
            return false
          }
          return true
        }
      }
    }
  }
})
