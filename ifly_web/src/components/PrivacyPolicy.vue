<template>
    <el-dialog title="iFly 隐私政策" v-model="dialogVisible" width="65%" class="policy-dialog" @close="closeDialog">
        <div class="policy-content">
            <h2>iFly 隐私政策</h2>
            <p><strong>最后更新日期：2023年11月15日</strong></p>

            <h3>1. 引言</h3>
            <p>iFly（"我们"、"我们的"或"本公司"）尊重并保护用户（"您"）的隐私。本隐私政策说明我们如何收集、使用、披露、处理和保护您在使用我们的服务时提供的信息。请仔细阅读本政策，以了解我们的数据处理实践。</p>

            <h3>2. 信息收集</h3>
            <p><strong>我们收集的信息可能包括：</strong></p>
            <ul>
                <li><strong>个人识别信息</strong>：如姓名、电子邮件地址、电话号码、出生日期等。</li>
                <li><strong>账户信息</strong>：登录凭证、密码、账户设置和偏好。</li>
                <li><strong>旅行信息</strong>：航班预订、旅行偏好、常旅客计划信息等。</li>
                <li><strong>设备和使用数据</strong>：IP地址、浏览器类型、操作系统、设备标识符、访问时间、引用/退出页面、点击流数据等。</li>
                <li><strong>位置信息</strong>：基于GPS、WiFi或蜂窝网络的地理位置信息。</li>
            </ul>

            <h3>3. 信息使用</h3>
            <p><strong>我们使用收集的信息用于：</strong></p>
            <ul>
                <li>提供、维护和改进我们的服务</li>
                <li>处理和完成交易</li>
                <li>发送与服务相关的通知和更新</li>
                <li>根据您的偏好提供个性化内容和推荐</li>
                <li>分析使用模式以改进用户体验</li>
                <li>检测、预防和解决欺诈、安全或技术问题</li>
                <li>响应您的请求、问题和关注点</li>
            </ul>

            <h3>4. 信息共享</h3>
            <p>我们不会出售、出租或交易您的个人信息给第三方。然而，在以下情况下，我们可能会共享您的信息：</p>
            <ul>
                <li>经您同意或按您的指示</li>
                <li>与我们的关联公司、服务提供商和业务合作伙伴共享，他们帮助我们提供服务</li>
                <li>为遵守适用法律、法规或法律程序</li>
                <li>保护iFly、我们的用户或公众的权利、财产或安全</li>
                <li>与潜在的合并、收购、融资或业务转让相关</li>
            </ul>

            <h3>5. 数据安全</h3>
            <p>我们实施适当的技术和组织措施来保护您的个人信息不受未经授权的访问、使用、修改和披露。然而，互联网传输不能保证100%的安全性，我们无法确保您传输给我们的信息的安全性。</p>

            <h3>6. 您的权利和选择</h3>
            <p>根据适用的隐私法律，您可能拥有以下权利：</p>
            <ul>
                <li>访问、更正或删除您的个人信息</li>
                <li>限制或反对我们处理您的信息</li>
                <li>获取您的个人信息的便携式副本</li>
                <li>撤回之前的同意</li>
            </ul>
            <p>要行使这些权利，请通过下面提供的联系方式与我们联系。</p>

            <h3>7. Cookie和类似技术</h3>
            <p>我们使用cookie和类似技术来收集和存储有关您设备的信息，以提供更好的用户体验、分析趋势和管理网站。您可以通过浏览器设置控制cookie，但这可能会影响某些服务功能。</p>

            <h3>8. 儿童隐私</h3>
            <p>我们的服务不面向13岁以下儿童。如果我们发现我们收集了13岁以下儿童的个人信息，我们会采取措施删除该信息。</p>

            <h3>9. 国际数据传输</h3>
            <p>我们可能将您的信息传输并存储在中国境内外的设施中。通过使用我们的服务，您同意将您的信息传输至您居住国以外的国家或地区。</p>

            <h3>10. 隐私政策更新</h3>
            <p>我们可能会不时更新本隐私政策。更新后的政策将在我们的网站上发布，并在发布时立即生效。我们建议您定期查看本政策以了解任何变更。</p>

            <h3>11. 联系我们</h3>
            <p>如果您对本隐私政策或我们的隐私实践有任何疑问，请通过 privacy@ifly.com 与我们联系。</p>
        </div>
        <template #footer>
            <span class="dialog-footer">
                <el-button type="primary" @click="closeDialog">我已阅读并理解</el-button>
            </span>
        </template>
    </el-dialog>
</template>

<script>
export default {
    name: 'PrivacyPolicy',
    props: {
        visible: {
            type: Boolean,
            default: false
        }
    },
    computed: {
        dialogVisible: {
            get() {
                return this.visible;
            },
            set(value) {
                if (!value) {
                    this.$emit('update:visible', false);
                }
            }
        }
    },
    methods: {
        closeDialog() {
            this.$emit('update:visible', false);
        }
    }
}
</script>

<style scoped>
/* 对话框样式 */
.policy-dialog :deep(.el-dialog__body) {
    max-height: 60vh;
    overflow-y: auto;
    padding: 20px 25px;
    scrollbar-width: thin;
    scrollbar-color: rgba(66, 159, 221, 0.5) rgba(255, 255, 255, 0.1);
}

.policy-dialog :deep(.el-dialog__body)::-webkit-scrollbar {
    width: 8px;
}

.policy-dialog :deep(.el-dialog__body)::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

.policy-dialog :deep(.el-dialog__body)::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #429fdd 0%, #06214b 100%);
    border-radius: 4px;
}

.policy-dialog :deep(.el-dialog__body)::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #5aafef 0%, #073063 100%);
}

.policy-content {
    text-align: left;
    color: #333;
    padding-right: 5px;
}

.policy-content h2 {
    color: #06214b;
    margin-bottom: 20px;
    font-size: 24px;
}

.policy-content h3 {
    color: #429fdd;
    margin-top: 20px;
    margin-bottom: 10px;
    font-size: 18px;
}

.policy-content p,
.policy-content li {
    line-height: 1.6;
    margin-bottom: 10px;
    font-size: 15px;
}

.policy-content ul {
    padding-left: 20px;
    margin-bottom: 15px;
}

.policy-dialog :deep(.el-dialog__header) {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #429fdd 0%, #06214b 100%);
}

.policy-dialog :deep(.el-dialog__title) {
    color: white;
    font-weight: bold;
}

.policy-dialog :deep(.el-dialog__footer) {
    padding: 15px 20px;
    text-align: center;
}

.policy-dialog :deep(.el-button--primary) {
    background: linear-gradient(135deg, #429fdd 0%, #06214b 100%);
    border: none;
    padding: 12px 25px;
    font-size: 16px;
}

.policy-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
    color: white;
}
</style>