<template>
    <div class="user-info-tab">
        <el-skeleton :loading="loading" animated>
            <template #template>
                <div style="padding: 20px">
                    <el-skeleton-item variant="image" style="width: 100px; height: 100px; border-radius: 50%" />
                    <div style="margin-top: 20px">
                        <el-skeleton-item variant="p" style="width: 50%" />
                        <el-skeleton-item variant="p" style="width: 70%" />
                        <el-skeleton-item variant="p" style="width: 80%" />
                    </div>
                </div>
            </template>

            <template #default>
                <el-form ref="formRef" :model="form" :rules="rules" label-position="top" class="user-form"
                    v-loading="submitting">
                    <div class="form-header">
                        <div class="avatar-container">
                            <el-avatar :size="100" :src="avatarPreview" class="user-avatar">
                                {{ form.username ? form.username.substring(0, 1).toUpperCase() : 'U' }}
                            </el-avatar>
                            <div class="avatar-actions">
                                <el-upload class="avatar-uploader" action="#" :auto-upload="false"
                                    :show-file-list="false" :on-change="handleAvatarChange"
                                    accept="image/jpeg,image/png,image/gif">
                                    <el-button size="small" type="primary">上传头像</el-button>
                                </el-upload>
                                <el-button v-if="form.avatar" size="small" type="danger" @click="removeAvatar">
                                    删除头像
                                </el-button>
                            </div>
                        </div>
                        <div v-if="avatarUploading" class="avatar-uploading">
                            <el-progress :percentage="uploadPercentage" type="circle" :width="60" />
                        </div>
                    </div>

                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="用户名" prop="username">
                                <el-input v-model="form.username" disabled />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="邮箱" prop="email">
                                <el-input v-model="form.email" disabled />
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="真实姓名" prop="real_name">
                                <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="手机号码" prop="phone">
                                <el-input v-model="form.phone" placeholder="请输入手机号码" />
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-row :gutter="20">
                        <el-col :span="12">
                            <el-form-item label="身份证号" prop="id_card">
                                <el-input v-model="form.id_card" placeholder="请输入身份证号" />
                            </el-form-item>
                        </el-col>
                        <el-col :span="12">
                            <el-form-item label="性别" prop="gender">
                                <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%">
                                    <el-option label="男" value="male" />
                                    <el-option label="女" value="female" />
                                    <el-option label="其他" value="other" />
                                </el-select>
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-row :gutter="20">
                        <el-col :span="24">
                            <el-form-item label="地址" prop="address">
                                <el-input v-model="form.address" placeholder="请输入地址" />
                            </el-form-item>
                        </el-col>
                    </el-row>

                    <el-form-item>
                        <el-button type="primary" @click="submitForm" :loading="submitting">保存信息</el-button>
                        <el-button @click="resetForm">重置</el-button>
                    </el-form-item>
                </el-form>
            </template>
        </el-skeleton>
    </div>
</template>

<script>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/services/api'

export default {
    name: 'UserInfoTab',
    props: {
        user: {
            type: Object,
            default: () => ({})
        }
    },
    emits: ['update-success'],
    setup(props, { emit }) {
        const formRef = ref(null)
        const loading = ref(false)
        const submitting = ref(false)
        const avatarUploading = ref(false)
        const uploadPercentage = ref(0)
        const avatarFile = ref(null)

        // 表单数据
        const form = reactive({
            username: '',
            email: '',
            real_name: '',
            phone: '',
            id_card: '',
            gender: '',
            address: '',
            avatar: ''
        })

        // 头像预览
        const avatarPreview = computed(() => {
            if (avatarFile.value) {
                return URL.createObjectURL(avatarFile.value)
            }
            if (form.avatar) {
                return form.avatar
            }
            return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
        })

        // 表单验证规则
        const rules = {
            phone: [
                { pattern: /^1[3456789]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
            ],
            id_card: [
                { pattern: /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/, message: '请输入正确的身份证号', trigger: 'blur' }
            ]
        }

        // 监听用户数据变化，更新表单
        const updateFormWithUserData = () => {
            if (props.user) {
                Object.keys(form).forEach(key => {
                    if (props.user[key] !== undefined) {
                        form[key] = props.user[key]
                    }
                })

                // 处理头像URL
                if (props.user.avatar_url) {
                    form.avatar = props.user.avatar_url
                }
            }
        }

        // 处理头像上传
        const handleAvatarChange = (file) => {
            const isImage = file.raw.type.startsWith('image/')
            if (!isImage) {
                ElMessage.error('只能上传图片文件！')
                return
            }

            const isLt2M = file.size / 1024 / 1024 < 2
            if (!isLt2M) {
                ElMessage.error('头像图片不能超过2MB！')
                return
            }

            avatarFile.value = file.raw
        }

        // 删除头像
        const removeAvatar = () => {
            avatarFile.value = null
            form.avatar = ''
        }

        // 提交表单
        const submitForm = async () => {
            if (!formRef.value) return

            try {
                await formRef.value.validate()

                submitting.value = true

                // 处理头像上传
                if (avatarFile.value) {
                    avatarUploading.value = true
                    uploadPercentage.value = 0

                    try {
                        // 模拟上传进度
                        const progressInterval = setInterval(() => {
                            if (uploadPercentage.value < 90) {
                                uploadPercentage.value += 10
                            }
                        }, 200)

                        // 使用Base64方式上传
                        const reader = new FileReader()
                        reader.readAsDataURL(avatarFile.value)

                        const base64Avatar = await new Promise((resolve, reject) => {
                            reader.onload = () => resolve(reader.result)
                            reader.onerror = (error) => reject(error)
                        })

                        // 上传头像
                        const avatarResponse = await api.auth.updateProfile({ avatar: base64Avatar })

                        clearInterval(progressInterval)
                        uploadPercentage.value = 100

                        // 更新表单中的头像URL
                        if (avatarResponse && avatarResponse.avatar_url) {
                            form.avatar = avatarResponse.avatar_url
                        }

                        setTimeout(() => {
                            avatarUploading.value = false
                            avatarFile.value = null
                        }, 500)
                    } catch (error) {
                        console.error('头像上传失败:', error)
                        ElMessage.error('头像上传失败')
                        avatarUploading.value = false
                    }
                }

                // 更新个人资料
                const response = await api.auth.updateProfile({
                    real_name: form.real_name,
                    phone: form.phone,
                    id_card: form.id_card,
                    gender: form.gender,
                    address: form.address
                })

                if (response) {
                    ElMessage.success('个人信息更新成功')
                    emit('update-success')
                }
            } catch (error) {
                console.error('表单验证或提交失败:', error)
                ElMessage.error('请检查表单填写是否正确')
            } finally {
                submitting.value = false
            }
        }

        // 重置表单
        const resetForm = () => {
            avatarFile.value = null
            updateFormWithUserData()
        }

        onMounted(() => {
            updateFormWithUserData()
        })

        return {
            formRef,
            form,
            rules,
            loading,
            submitting,
            avatarUploading,
            uploadPercentage,
            avatarPreview,
            handleAvatarChange,
            removeAvatar,
            submitForm,
            resetForm
        }
    }
}
</script>

<style scoped>
.user-info-tab {
    padding: 10px;
}

.user-form {
    max-width: 800px;
    margin: 0 auto;
}

.form-header {
    display: flex;
    align-items: center;
    margin-bottom: 30px;
    position: relative;
}

.avatar-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-right: 20px;
}

.user-avatar {
    border: 2px solid var(--el-color-primary);
    box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.avatar-actions {
    margin-top: 10px;
    display: flex;
    gap: 10px;
}

.avatar-uploading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(255, 255, 255, 0.8);
    border-radius: 50%;
    padding: 20px;
    z-index: 2;
}
</style>