<template>
    <div class="passenger-list-tab">
        <div class="passenger-header">
            <h3>我的常用乘客</h3>
            <el-button type="primary" @click="showAddDialog">添加乘客</el-button>
        </div>

        <el-table :data="passengers" style="width: 100%" v-loading="loading" empty-text="暂无常用乘客，请点击添加乘客按钮添加">
            <el-table-column prop="name" label="姓名" min-width="100" />
            <el-table-column prop="id_card_type_display" label="证件类型" min-width="120" />
            <el-table-column prop="id_card" label="证件号码" min-width="180" />
            <el-table-column prop="phone" label="手机号" min-width="150" />
            <el-table-column label="操作" width="150" fixed="right">
                <template #default="scope">
                    <el-button type="primary" size="small" @click="handleEdit(scope.row)" text>
                        编辑
                    </el-button>
                    <el-button type="danger" size="small" @click="handleDelete(scope.row)" text>
                        删除
                    </el-button>
                </template>
            </el-table-column>
        </el-table>

        <!-- 添加/编辑乘客对话框 -->
        <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑乘客' : '添加乘客'" width="500px">
            <el-form ref="passengerFormRef" :model="passengerForm" :rules="rules" label-width="100px"
                label-position="right">
                <el-form-item label="姓名" prop="name">
                    <el-input v-model="passengerForm.name" placeholder="请输入乘客姓名" />
                </el-form-item>

                <el-form-item label="证件类型" prop="id_card_type">
                    <el-select v-model="passengerForm.id_card_type" placeholder="请选择证件类型" style="width: 100%">
                        <el-option label="身份证" value="IDENTITY_CARD" />
                        <el-option label="护照" value="PASSPORT" />
                        <el-option label="军官证" value="MILITARY_ID" />
                        <el-option label="港澳通行证" value="HK_MACAO_PASS" />
                        <el-option label="台湾通行证" value="TAIWAN_PASS" />
                    </el-select>
                </el-form-item>

                <el-form-item label="证件号码" prop="id_card">
                    <el-input v-model="passengerForm.id_card" placeholder="请输入证件号码" />
                </el-form-item>

                <el-form-item label="手机号码" prop="phone">
                    <el-input v-model="passengerForm.phone" placeholder="请输入手机号码" />
                </el-form-item>

                <el-form-item label="旅客类型" prop="passenger_type">
                    <el-select v-model="passengerForm.passenger_type" placeholder="请选择旅客类型" style="width: 100%">
                        <el-option label="成人" value="ADULT" />
                        <el-option label="儿童" value="CHILD" />
                        <el-option label="婴儿" value="INFANT" />
                    </el-select>
                </el-form-item>
            </el-form>

            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="dialogVisible = false">取消</el-button>
                    <el-button type="primary" @click="submitPassenger" :loading="submitting">
                        {{ isEdit ? '保存' : '添加' }}
                    </el-button>
                </span>
            </template>
        </el-dialog>

        <!-- 删除确认对话框 -->
        <el-dialog v-model="deleteDialogVisible" title="确认删除" width="400px">
            <div>确定要删除乘客 "{{ currentPassenger?.name || '' }}" 吗？</div>
            <template #footer>
                <span class="dialog-footer">
                    <el-button @click="deleteDialogVisible = false">取消</el-button>
                    <el-button type="danger" @click="confirmDelete" :loading="deleting">
                        删除
                    </el-button>
                </span>
            </template>
        </el-dialog>
    </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/services/api'

export default {
    name: 'PassengerListTab',
    setup() {
        const loading = ref(false)
        const submitting = ref(false)
        const deleting = ref(false)
        const passengers = ref([])
        const dialogVisible = ref(false)
        const deleteDialogVisible = ref(false)
        const isEdit = ref(false)
        const currentPassenger = ref(null)
        const passengerFormRef = ref(null)

        // 表单数据
        const passengerForm = reactive({
            id: null,
            name: '',
            id_card_type: 'IDENTITY_CARD',
            id_card: '',
            phone: '',
            passenger_type: 'ADULT'
        })

        // 表单验证规则
        const rules = {
            name: [
                { required: true, message: '请输入乘客姓名', trigger: 'blur' },
                { min: 2, max: 50, message: '姓名长度应为2-50个字符', trigger: 'blur' }
            ],
            id_card_type: [
                { required: true, message: '请选择证件类型', trigger: 'change' }
            ],
            id_card: [
                { required: true, message: '请输入证件号码', trigger: 'blur' }
            ],
            phone: [
                { pattern: /^1[3456789]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
            ],
            passenger_type: [
                { required: true, message: '请选择旅客类型', trigger: 'change' }
            ]
        }

        // 获取乘客列表
        const fetchPassengers = async () => {
            loading.value = true

            try {
                const response = await api.passengers.getAll()
                const data = response.results || response || []
                
                // 证件类型映射
                const idCardTypeMap = {
                    '身份证': '身份证',
                    'IDENTITY_CARD': '身份证',
                    'PASSPORT': '护照',
                    'MILITARY_ID': '军官证',
                    'HK_MACAO_PASS': '港澳通行证',
                    'TAIWAN_PASS': '台湾通行证'
                }
                
                passengers.value = data.map(item => ({
                    id: item.id,
                    name: item.name,
                    id_card_type: item.id_type || item.id_card_type || 'IDENTITY_CARD',
                    id_card_type_display: idCardTypeMap[item.id_type] || idCardTypeMap[item.id_card_type] || item.id_type || '身份证',
                    id_card: item.id_number || item.id_card,
                    phone: item.phone || '',
                    passenger_type: item.passenger_type || 'ADULT'
                }))
            } catch (error) {
                console.error('获取乘客列表失败:', error)
                ElMessage.error('获取乘客列表失败，请稍后重试')
            } finally {
                loading.value = false
            }
        }

        // 显示添加对话框
        const showAddDialog = () => {
            isEdit.value = false
            resetForm()
            dialogVisible.value = true
        }

        // 处理编辑
        const handleEdit = (row) => {
            isEdit.value = true
            currentPassenger.value = row
            Object.keys(passengerForm).forEach(key => {
                if (row[key] !== undefined) {
                    passengerForm[key] = row[key]
                }
            })
            dialogVisible.value = true
        }

        // 重置表单
        const resetForm = () => {
            if (passengerFormRef.value) {
                passengerFormRef.value.resetFields()
            }
            passengerForm.id = null
            passengerForm.name = ''
            passengerForm.id_card_type = 'IDENTITY_CARD'
            passengerForm.id_card = ''
            passengerForm.phone = ''
            passengerForm.passenger_type = 'ADULT'
            currentPassenger.value = null
        }

        // 提交乘客表单
        const submitPassenger = async () => {
            if (!passengerFormRef.value) return

            await passengerFormRef.value.validate(async (valid) => {
                if (valid) {
                    submitting.value = true

                    try {
                        const data = {
                            name: passengerForm.name,
                            id_type: passengerForm.id_card_type,
                            id_number: passengerForm.id_card,
                            phone: passengerForm.phone
                        }

                        if (isEdit.value) {
                            await api.passengers.update(passengerForm.id, data)
                            ElMessage.success('乘客信息更新成功')
                        } else {
                            await api.passengers.create(data)
                            ElMessage.success('乘客添加成功')
                        }
                        dialogVisible.value = false
                        fetchPassengers()
                    } catch (error) {
                        console.error('保存乘客信息失败:', error)
                        ElMessage.error('保存乘客信息失败，请稍后重试')
                    } finally {
                        submitting.value = false
                    }
                }
            })
        }

        // 处理删除
        const handleDelete = (row) => {
            currentPassenger.value = row
            deleteDialogVisible.value = true
        }

        // 确认删除
        const confirmDelete = async () => {
            if (!currentPassenger.value || !currentPassenger.value.id) return

            deleting.value = true

            try {
                await api.passengers.delete(currentPassenger.value.id)
                ElMessage.success('乘客删除成功')
                deleteDialogVisible.value = false
                fetchPassengers()
            } catch (error) {
                console.error('删除乘客失败:', error)
                ElMessage.error('删除乘客失败，请稍后重试')
            } finally {
                deleting.value = false
            }
        }

        onMounted(() => {
            fetchPassengers()
        })

        return {
            loading,
            submitting,
            deleting,
            passengers,
            dialogVisible,
            deleteDialogVisible,
            isEdit,
            currentPassenger,
            passengerFormRef,
            passengerForm,
            rules,
            showAddDialog,
            handleEdit,
            handleDelete,
            submitPassenger,
            confirmDelete
        }
    }
}
</script>

<style scoped>
.passenger-list-tab {
    padding: 10px;
}

.passenger-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.passenger-header h3 {
    margin: 0;
}
</style>