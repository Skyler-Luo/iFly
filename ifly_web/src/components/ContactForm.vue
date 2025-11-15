<template>
    <div class="contact-info-section">
        <h3>联系人信息</h3>
        <p class="section-desc">用于接收航班信息和订单状态变更通知</p>

        <el-form :model="contactData" :rules="contactRules" ref="contactForm" label-width="100px">
            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="联系人" prop="name">
                        <el-input v-model="contactData.name" placeholder="请输入联系人姓名"></el-input>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="手机号码" prop="phone">
                        <el-input v-model="contactData.phone" placeholder="请输入联系电话"></el-input>
                    </el-form-item>
                </el-col>
            </el-row>
            <el-form-item label="电子邮箱" prop="email">
                <el-input v-model="contactData.email" placeholder="请输入电子邮箱"></el-input>
            </el-form-item>
        </el-form>
    </div>
</template>

<script>
export default {
    name: 'ContactForm',
    props: {
        contact: {
            type: Object,
            default: () => ({
                name: '',
                phone: '',
                email: ''
            })
        }
    },
    data() {
        return {
            contactData: { ...this.contact },
            contactRules: {
                name: [
                    { required: true, message: '请输入联系人姓名', trigger: 'blur' },
                    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
                ],
                phone: [
                    { required: true, message: '请输入联系电话', trigger: 'blur' },
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
                ],
                email: [
                    { required: true, message: '请输入电子邮箱', trigger: 'blur' },
                    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
                ]
            }
        };
    },
    watch: {
        contact: {
            handler(newValue) {
                this.contactData = { ...newValue };
            },
            deep: true
        }
    },
    methods: {
        validate() {
            return new Promise((resolve, reject) => {
                this.$refs.contactForm.validate(valid => {
                    if (valid) {
                        resolve(this.contactData);
                    } else {
                        reject('联系人信息验证失败');
                    }
                });
            });
        },
        getData() {
            return this.contactData;
        }
    }
}
</script>

<style scoped>
.contact-info-section {
    background-color: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    margin-top: 30px;
}

.section-desc {
    color: #666;
    margin-bottom: 20px;
    font-size: 14px;
}
</style>