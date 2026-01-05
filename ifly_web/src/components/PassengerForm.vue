<template>
    <div class="passenger-form">
        <el-form :model="passengerData" :rules="passengerRules" label-width="100px" @submit.prevent ref="form">
            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="姓名" prop="name">
                        <el-input v-model="passengerData.name" placeholder="请输入乘客姓名"></el-input>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="性别" prop="gender">
                        <el-radio-group v-model="passengerData.gender">
                            <el-radio value="male">男</el-radio>
                            <el-radio value="female">女</el-radio>
                        </el-radio-group>
                    </el-form-item>
                </el-col>
            </el-row>

            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="证件类型" prop="idType">
                        <el-select v-model="passengerData.idType" placeholder="请选择证件类型" style="width: 100%">
                            <el-option label="身份证" value="idcard"></el-option>
                            <el-option label="护照" value="passport"></el-option>
                            <el-option label="军官证" value="military"></el-option>
                        </el-select>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="证件号码" prop="idNumber">
                        <el-input v-model="passengerData.idNumber" placeholder="请输入证件号码"></el-input>
                    </el-form-item>
                </el-col>
            </el-row>

            <el-row :gutter="20">
                <el-col :span="12">
                    <el-form-item label="出生日期" prop="birthDate">
                        <el-date-picker v-model="passengerData.birthDate" type="date" placeholder="选择出生日期"
                            style="width: 100%" :picker-options="{
                                disabledDate: time => time.getTime() > Date.now()
                            }"></el-date-picker>
                    </el-form-item>
                </el-col>
                <el-col :span="12">
                    <el-form-item label="手机号码" prop="phone">
                        <el-input v-model="passengerData.phone" placeholder="请输入联系电话"></el-input>
                    </el-form-item>
                </el-col>
            </el-row>

            <div class="form-actions">
                <el-button type="primary" @click="savePassenger">
                    保存乘客信息
                </el-button>
                <el-button type="info" plain v-if="hasSavedPassengers" @click="useExisting">
                    使用已保存的乘客
                </el-button>
            </div>
        </el-form>
    </div>
</template>

<script>
export default {
    name: 'PassengerForm',
    props: {
        passenger: {
            type: Object,
            default: () => ({
                name: '',
                gender: '',
                idType: '',
                idNumber: '',
                birthDate: '',
                phone: '',
                isComplete: false
            })
        },
        hasSavedPassengers: {
            type: Boolean,
            default: false
        },
        index: {
            type: Number,
            default: 0
        }
    },
    data() {
        return {
            passengerData: { ...this.passenger },
            passengerRules: {
                name: [
                    { required: true, message: '请输入乘客姓名', trigger: 'blur' },
                    { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
                ],
                gender: [
                    { required: true, message: '请选择性别', trigger: 'change' }
                ],
                idType: [
                    { required: true, message: '请选择证件类型', trigger: 'change' }
                ],
                idNumber: [
                    { required: true, message: '请输入证件号码', trigger: 'blur' },
                    { min: 5, max: 18, message: '长度在 5 到 18 个字符', trigger: 'blur' }
                ],
                birthDate: [
                    { required: true, message: '请选择出生日期', trigger: 'change' },
                    { type: 'date', message: '请选择正确的日期格式', trigger: 'change' }
                ],
                phone: [
                    { required: true, message: '请输入手机号码', trigger: 'blur' },
                    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
                ]
            }
        }
    },
    watch: {
        passenger: {
            handler(newValue) {
                this.passengerData = { ...newValue };
            },
            deep: true
        }
    },
    methods: {
        savePassenger() {
            this.$refs.form.validate(valid => {
                if (valid) {
                    this.$emit('save', { ...this.passengerData, isComplete: true }, this.index);
                }
            });
        },
        useExisting() {
            this.$emit('use-existing', this.index);
        },
        validate() {
            return new Promise((resolve) => {
                this.$refs.form.validate(valid => {
                    resolve(valid);
                });
            });
        },
        resetForm() {
            this.$refs.form.resetFields();
        }
    },
    mounted() {
        this.$emit('mount', this);
    }
}
</script>

<style scoped>
.passenger-form {
    margin-bottom: 20px;
}

.form-actions {
    display: flex;
    justify-content: flex-start;
    margin-top: 20px;
}

.form-actions .el-button {
    margin-right: 15px;
}
</style>