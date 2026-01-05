<template>
    <el-dialog title="iFly 服务条款" v-model="dialogVisible" width="65%" class="policy-dialog" @close="closeDialog">
        <div class="policy-content">
            <h2>iFly 服务条款</h2>
            <p><strong>最后更新日期：2023年11月15日</strong></p>

            <h3>1. 接受条款</h3>
            <p>欢迎使用iFly服务。通过访问或使用我们的网站、移动应用程序或任何相关服务（以下统称为"服务"），您同意受这些服务条款的约束。如果您不同意这些条款，请勿使用我们的服务。</p>

            <h3>2. 服务描述</h3>
            <p>iFly提供一个航空旅行社区平台，用户可以在此获取航班信息、分享旅行经验、参与社区讨论并获取相关资讯。我们保留随时修改、暂停或终止部分或全部服务的权利，恕不另行通知。</p>

            <h3>3. 账户注册与安全</h3>
            <p>为使用我们的某些服务，您可能需要创建一个账户。您须提供准确、完整和最新的注册信息，并维护账户安全。您对通过您的账户进行的所有活动负全责。如发现任何未经授权的使用或安全漏洞，请立即通知我们。</p>

            <h3>4. 用户行为准则</h3>
            <p>使用我们的服务时，您同意：</p>
            <ul>
                <li>遵守所有适用法律和法规</li>
                <li>尊重其他用户的权利和隐私</li>
                <li>不发布虚假、误导、侮辱、诽谤、淫秽或违法内容</li>
                <li>不从事可能损害我们服务运行的行为</li>
                <li>不使用我们的服务进行商业目的，除非经过我们的明确许可</li>
            </ul>

            <h3>5. 知识产权</h3>
            <p>iFly及其许可方拥有与服务相关的所有知识产权。服务内容（包括但不限于文本、图形、徽标、图标和软件）受版权、商标和其他法律的保护。未经我们事先书面同意，您不得复制、修改、出版、传输、分发、展示、执行或以任何方式利用任何服务内容。
            </p>

            <h3>6. 用户内容</h3>
            <p>您在我们的平台上发布的内容（以下称为"用户内容"）仍然归您所有，但您授予iFly非排他性、免费、全球性、可转让、可再许可的权利，可以使用、复制、修改、改编、出版、翻译、创建衍生作品、分发和展示这些用户内容。
            </p>

            <h3>7. 免责声明</h3>
            <p>我们的服务按"现状"和"可用性"提供，不附带任何形式的担保。我们不保证服务将不间断、及时、安全或无错误，也不保证通过使用服务获得的结果准确可靠。</p>

            <h3>8. 责任限制</h3>
            <p>在适用法律允许的最大范围内，iFly及其关联公司、管理人员、员工和代理人不对因使用或无法使用我们的服务而造成的任何直接、间接、附带、特殊、后果性或惩罚性损害负责。</p>

            <h3>9. 条款修改</h3>
            <p>我们保留随时修改这些服务条款的权利。修改后的条款将在网站上发布，并在发布时立即生效。继续使用我们的服务即视为接受修改后的条款。我们建议您定期查看这些条款。</p>

            <h3>10. 适用法律</h3>
            <p>这些条款受中华人民共和国法律管辖，任何争议应提交至有管辖权的中国法院解决。</p>

            <h3>11. 联系我们</h3>
            <p>如果您对这些服务条款有任何疑问，请通过 support@ifly.com 与我们联系。</p>
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
    name: 'TermsOfService',
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