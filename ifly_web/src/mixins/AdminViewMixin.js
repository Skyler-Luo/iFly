/**
 * 管理员视图公共Mixin
 * 提供常用的管理功能：分页、格式化、批量操作等
 */

import { ElMessage, ElMessageBox } from 'element-plus'
// api 模块可在组件中按需导入使用
// import api from '@/services/api'

export default {
  data() {
    return {
      // 通用数据状态
      loading: false,
      tableData: [],
      multipleSelection: [],
      
      // 分页数据
      pagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      
      // 搜索条件
      searchForm: {},
      
      // 对话框状态
      dialogVisible: false,
      dialogTitle: '添加',
      editingItem: null
    }
  },
  
  computed: {
    // 是否有选中项
    hasSelection() {
      return this.multipleSelection.length > 0
    },
    
    // 选中项数量
    selectionCount() {
      return this.multipleSelection.length
    }
  },
  
  methods: {
    // 格式化日期时间
    formatDate(dateString, format = 'YYYY-MM-DD HH:mm:ss') {
      if (!dateString) return '--'
      const date = new Date(dateString)
      if (isNaN(date.getTime())) return '--'
      
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      const seconds = String(date.getSeconds()).padStart(2, '0')
      
      switch (format) {
        case 'YYYY-MM-DD':
          return `${year}-${month}-${day}`
        case 'MM-DD HH:mm':
          return `${month}-${day} ${hours}:${minutes}`
        case 'HH:mm:ss':
          return `${hours}:${minutes}:${seconds}`
        default:
          return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
      }
    },
    
    // 格式化文件大小
    formatFileSize(bytes) {
      if (!bytes || bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    
    // 格式化状态
    formatStatus(status, statusMap = {}) {
      return statusMap[status] || status
    },
    
    // 格式化金额
    formatMoney(amount, currency = '¥') {
      if (!amount && amount !== 0) return '--'
      return currency + Number(amount).toFixed(2)
    },
    
    // 分页处理
    handleSizeChange(newSize) {
      this.pagination.pageSize = newSize
      this.pagination.currentPage = 1
      this.fetchData()
    },
    
    handleCurrentChange(newPage) {
      this.pagination.currentPage = newPage
      this.fetchData()
    },
    
    // 多选处理
    handleSelectionChange(selection) {
      this.multipleSelection = selection
    },
    
    // 搜索
    handleSearch() {
      this.pagination.currentPage = 1
      this.fetchData()
    },
    
    // 重置搜索
    handleResetSearch() {
      this.searchForm = {}
      this.pagination.currentPage = 1
      this.fetchData()
    },
    
    // 添加项目
    handleAdd() {
      this.dialogTitle = '添加'
      this.editingItem = null
      this.dialogVisible = true
    },
    
    // 编辑项目
    handleEdit(row) {
      this.dialogTitle = '编辑'
      this.editingItem = { ...row }
      this.dialogVisible = true
    },
    
    // 删除确认
    async handleDelete(row) {
      try {
        await ElMessageBox.confirm(
          '此操作将永久删除该记录, 是否继续?',
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        await this.deleteItem(row.id)
        ElMessage.success('删除成功')
        this.fetchData()
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('删除失败: ' + (error.message || error))
        }
      }
    },
    
    // 批量删除
    async handleBatchDelete() {
      if (!this.hasSelection) {
        ElMessage.warning('请先选择要删除的记录')
        return
      }
      
      try {
        await ElMessageBox.confirm(
          `确定要删除选中的 ${this.selectionCount} 条记录吗？`,
          '批量删除确认',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )
        
        const ids = this.multipleSelection.map(item => item.id)
        await this.batchDeleteItems(ids)
        ElMessage.success('批量删除成功')
        this.fetchData()
        this.multipleSelection = []
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('批量删除失败: ' + (error.message || error))
        }
      }
    },
    
    // 状态切换
    async handleStatusChange(row, status) {
      try {
        await this.updateItemStatus(row.id, status)
        ElMessage.success('状态更新成功')
        this.fetchData()
      } catch (error) {
        ElMessage.error('状态更新失败: ' + (error.message || error))
        // 恢复原状态
        row.status = !status
      }
    },
    
    // 导出数据
    async handleExport() {
      try {
        this.loading = true
        const response = await this.exportData(this.searchForm)
        
        // 创建下载链接
        const blob = new Blob([response.data])
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `${this.getExportFileName()}_${this.formatDate(new Date(), 'YYYY-MM-DD')}.xlsx`
        link.click()
        window.URL.revokeObjectURL(url)
        
        ElMessage.success('导出成功')
      } catch (error) {
        ElMessage.error('导出失败: ' + (error.message || error))
      } finally {
        this.loading = false
      }
    },
    
    // 刷新数据
    handleRefresh() {
      this.fetchData()
      ElMessage.success('刷新成功')
    },
    
    // ========== 需要在组件中实现的方法 ==========
    
    // 获取数据 - 必须实现
    async fetchData() {
      console.warn('fetchData method should be implemented in component')
    },
    
    // 删除单个项目 - 可选实现
    // eslint-disable-next-line no-unused-vars
    async deleteItem(id) {
      console.warn('deleteItem method should be implemented in component')
      throw new Error('Method not implemented')
    },
    
    // 批量删除 - 可选实现
    // eslint-disable-next-line no-unused-vars
    async batchDeleteItems(ids) {
      console.warn('batchDeleteItems method should be implemented in component')
      throw new Error('Method not implemented')
    },
    
    // 更新状态 - 可选实现
    // eslint-disable-next-line no-unused-vars
    async updateItemStatus(id, status) {
      console.warn('updateItemStatus method should be implemented in component')
      throw new Error('Method not implemented')
    },
    
    // 导出数据 - 可选实现
    // eslint-disable-next-line no-unused-vars
    async exportData(params) {
      console.warn('exportData method should be implemented in component')
      throw new Error('Method not implemented')
    },
    
    // 获取导出文件名 - 可选实现
    getExportFileName() {
      return 'export_data'
    }
  },
  
  // 组件挂载时自动加载数据
  mounted() {
    this.fetchData()
  }
}
