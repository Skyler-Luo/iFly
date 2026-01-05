<template>
    <div class="steps-container">
        <el-steps :active="currentStep" finish-status="success" simple>
            <el-step title="确认航班" icon="el-icon-plane"></el-step>
            <el-step title="乘客信息" icon="el-icon-user"></el-step>
            <el-step title="选择座位" icon="el-icon-tickets"></el-step>
            <el-step title="支付订单" icon="el-icon-wallet"></el-step>
        </el-steps>
    </div>
</template>

<script>
export default {
    name: 'BookingSteps',
    props: {
        currentStep: {
            type: Number,
            default: 0
        }
    }
}
</script>

<style scoped>
.steps-container {
    margin: 20px 0;
    width: 100%;
}
</style>