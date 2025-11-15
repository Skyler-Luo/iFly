<template>
    <div class="debug-page">
        <h1>API 调试页面</h1>
        <el-card class="debug-card">
            <template #header>
                <div class="card-header">
                    <h3>航班搜索 API 测试</h3>
                    <el-button @click="testFlightSearch" type="primary" :loading="isLoading">测试航班搜索API</el-button>
                </div>
            </template>
            <div v-if="results" class="results">
                <h4>搜索结果：找到 {{ results.length }} 个航班</h4>
                <pre>{{ JSON.stringify(results[0], null, 2) }}</pre>
            </div>
            <div v-if="error" class="error">
                <h4>错误信息</h4>
                <pre>{{ error }}</pre>
            </div>
        </el-card>
    </div>
</template>

<script>
import { ref } from 'vue'
import api from '@/services/api'

export default {
    name: 'DebugPage',
    setup() {
        const isLoading = ref(false)
        const results = ref(null)
        const error = ref(null)

        const testFlightSearch = async () => {
            isLoading.value = true
            error.value = null
            results.value = null

            try {
                // 构建测试参数
                const params = {
                    departure_city: '北京',
                    arrival_city: '上海',
                    departure_date: new Date().toISOString().split('T')[0],
                }

                console.log('搜索航班，参数：', params)

                // 调用API
                const response = await api.flights.search(params)
                console.log('API返回结果：', response)
                results.value = response
            } catch (err) {
                console.error('API调用错误:', err)
                error.value = err.toString() + '\n\nStack: ' + (err.stack || '')
            } finally {
                isLoading.value = false
            }
        }

        return {
            isLoading,
            results,
            error,
            testFlightSearch
        }
    }
}
</script>

<style scoped>
.debug-page {
    padding: 20px;
}

.debug-card {
    margin: 20px 0;
}

.card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.results {
    margin-top: 10px;
    overflow-x: auto;
}

.error {
    margin-top: 10px;
    color: red;
}

pre {
    background: #f5f5f5;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
}
</style>