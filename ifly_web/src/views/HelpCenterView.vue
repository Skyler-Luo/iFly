<template>
    <div class="help-center">
        <div class="header-banner">
            <div class="banner-content">
                <h1><i class="el-icon-question-filled"></i> 帮助中心</h1>
                <p>找到您需要的所有支持和问题解答</p>
                <div class="banner-actions">
                    <el-button type="primary" size="large" @click="startChat">
                        <i class="el-icon-service"></i> 在线咨询
                    </el-button>
                    <el-button type="default" size="large" plain>
                        <i class="el-icon-document"></i> 浏览指南
                    </el-button>
                </div>
            </div>
            <div class="banner-decoration">
                <div class="decoration-circle circle-1"></div>
                <div class="decoration-circle circle-2"></div>
                <div class="decoration-circle circle-3"></div>
                <div class="decoration-line line-1"></div>
                <div class="decoration-line line-2"></div>
            </div>
        </div>

        <!-- AI客服悬浮窗按钮 -->
        <div class="ai-chat-trigger" @click="toggleAiChat" v-if="!showAiChat">
            <i class="el-icon-chat-dot-round"></i>
            <span>智能客服</span>
        </div>

        <!-- AI客服聊天窗口 -->
        <transition name="slide-up">
            <div class="ai-chat-window" v-if="showAiChat">
                <div class="ai-chat-header">
                    <div class="ai-chat-title">
                        <i class="el-icon-service"></i>
                        <span>iFly智能助手</span>
                    </div>
                    <div class="ai-chat-actions">
                        <i class="el-icon-minus" @click="minimizeAiChat"></i>
                        <i class="el-icon-close" @click="toggleAiChat"></i>
                    </div>
                </div>
                <div class="ai-chat-body" ref="chatBody">
                    <div class="ai-chat-messages">
                        <div class="message bot-message">
                            <div class="message-avatar">
                                <i class="el-icon-service"></i>
                            </div>
                            <div class="message-content">
                                <p>您好！我是iFly智能助手，请问有什么可以帮您？</p>
                                <span class="message-time">{{ getCurrentTime() }}</span>
                            </div>
                        </div>
                        <div v-for="(message, index) in chatMessages" :key="index"
                            :class="['message', message.isBot ? 'bot-message' : 'user-message']">
                            <div class="message-avatar" v-if="message.isBot">
                                <i class="el-icon-service"></i>
                            </div>
                            <div class="message-content">
                                <p>{{ message.text }}</p>
                                <span class="message-time">{{ message.time }}</span>
                            </div>
                            <div class="message-avatar" v-if="!message.isBot">
                                <i class="el-icon-user"></i>
                            </div>
                        </div>
                        <div class="typing-indicator" v-if="isTyping">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                    </div>
                </div>
                <div class="ai-chat-suggestions" v-if="chatSuggestions.length > 0">
                    <div v-for="(suggestion, index) in chatSuggestions" :key="index" class="suggestion-chip"
                        @click="selectSuggestion(suggestion)">
                        {{ suggestion }}
                    </div>
                </div>
                <div class="ai-chat-footer">
                    <el-input v-model="chatInput" placeholder="输入您的问题..." @keyup.enter="sendMessage">
                        <template #append>
                            <el-button icon="el-icon-s-promotion" @click="sendMessage"></el-button>
                        </template>
                    </el-input>
                </div>
            </div>
        </transition>

        <div class="help-categories">
            <el-row :gutter="20">
                <el-col :xs="24" :sm="12" :md="8" v-for="(category, index) in helpCategories" :key="index">
                    <el-card class="help-category-card" @click="showCategoryContent(category)">
                        <div class="category-icon">
                            <i :class="category.icon"></i>
                        </div>
                        <h3>{{ category.title }}</h3>
                        <p>{{ category.description }}</p>
                    </el-card>
                </el-col>
            </el-row>
        </div>

        <!-- 分类内容弹窗 -->
        <el-dialog :title="selectedCategory ? selectedCategory.title : ''" v-model="showCategoryDialog"
            width="70%" class="category-dialog">
            <div class="category-content" v-if="selectedCategory">
                <div class="category-header">
                    <div class="category-icon large">
                        <i :class="selectedCategory.icon"></i>
                    </div>
                    <p>{{ selectedCategory.description }}</p>
                </div>

                <div class="category-questions">
                    <el-collapse v-model="activeCategoryQuestions">
                        <el-collapse-item v-for="(question, index) in filteredQuestions" :key="index"
                            :name="index.toString()">
                            <template #title>
                                <div class="question-title">
                                    <i class="el-icon-question"></i>
                                    <span>{{ question.title }}</span>
                                </div>
                            </template>
                            <div class="question-answer" v-html="question.answer"></div>
                        </el-collapse-item>
                    </el-collapse>
                </div>
            </div>
        </el-dialog>

        <div class="popular-questions">
            <h2>热门问题</h2>
            <el-collapse v-model="activeNames">
                <el-collapse-item v-for="(question, index) in popularQuestions" :key="index" :name="index.toString()">
                    <template #title>
                        <div class="question-title">
                            <i class="el-icon-question"></i>
                            <span>{{ question.title }}</span>
                        </div>
                    </template>
                    <div class="question-answer" v-html="question.answer"></div>
                </el-collapse-item>
            </el-collapse>
        </div>

        <div class="contact-section">
            <h2>联系我们</h2>
            <el-row :gutter="20">
                <el-col :xs="24" :sm="8">
                    <div class="contact-method">
                        <i class="el-icon-phone"></i>
                        <h3>客服热线</h3>
                        <p>400-123-4567</p>
                        <p class="note">8:00-22:00 (周一至周日)</p>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="8">
                    <div class="contact-method">
                        <i class="el-icon-message"></i>
                        <h3>邮箱</h3>
                        <p>support@ifly.com</p>
                        <p class="note">通常在24小时内回复</p>
                    </div>
                </el-col>
                <el-col :xs="24" :sm="8">
                    <div class="contact-method">
                        <i class="el-icon-chat-dot-round"></i>
                        <h3>在线客服</h3>
                        <el-button type="primary" size="small" @click="startChat">开始对话</el-button>
                        <p class="note">立即获得帮助</p>
                    </div>
                </el-col>
            </el-row>
        </div>
    </div>
</template>

<script>
export default {
    name: 'HelpCenterView',
    data() {
        return {
            activeNames: ['0', '1', '2'], // 默认打开前三个问题
            showAiChat: false,
            isTyping: false,
            chatInput: '',
            chatMessages: [],
            minimized: false,
            showCategoryDialog: false,
            selectedCategory: null,
            activeCategoryQuestions: ['0'], // 默认打开分类中的第一个问题
            chatSuggestions: [
                "如何更改机票?",
                "行李限额是多少?",
                "怎样申请退票?"
            ],
            helpCategories: [
                {
                    id: 'booking',
                    icon: 'el-icon-tickets',
                    title: '订票服务',
                    description: '了解如何预订、修改和取消您的机票'
                },
                {
                    id: 'payment',
                    icon: 'el-icon-wallet',
                    title: '支付问题',
                    description: '付款方式、退款流程、发票开具等问题'
                },
                {
                    id: 'checkin',
                    icon: 'el-icon-place',
                    title: '值机与登机',
                    description: '在线值机、座位选择、登机程序等'
                },
                {
                    id: 'baggage',
                    icon: 'el-icon-suitcase',
                    title: '行李信息',
                    description: '行李限额、托运规定、特殊行李处理'
                },
                {
                    id: 'account',
                    icon: 'el-icon-user',
                    title: '账户管理',
                    description: '账户注册、个人信息维护、密码修改等'
                },
                {
                    id: 'service',
                    icon: 'el-icon-service',
                    title: '特殊服务',
                    description: '轮椅服务、儿童陪护、特殊餐食等'
                }
            ],
            popularQuestions: [
                {
                    title: '如何更改或取消已预订的机票？',
                    answer: '<div class="answer-content"><p class="highlight-text">您可以通过以下步骤更改或取消机票：</p><ol class="step-list"><li>登录您的iFly账户</li><li>在"我的订单"中找到对应订单</li><li>点击"更改行程"或"取消订单"按钮</li><li>按照提示完成操作</li></ol><p class="note-text"><i class="el-icon-info"></i> 请注意，根据您购买的机票类型和航空公司规定，可能会收取一定的变更或退票手续费。具体费用会在您操作时显示。</p></div>'
                },
                {
                    title: '航班延误或取消时我该怎么办？',
                    answer: '<div class="answer-content"><p class="highlight-text">当您的航班发生延误或取消时：</p><ol class="step-list"><li>请关注iFly应用中的航班状态通知</li><li>可直接在航班详情页选择免费改签或申请退款</li><li>如需更多帮助，请联系我们的客服热线400-123-4567获取最新信息和解决方案</li></ol><p class="note-text"><i class="el-icon-info"></i> 根据《航空旅客权益保护条例》，在某些情况下，您可能有权获得航空公司提供的餐食、住宿或补偿。</p></div>'
                },
                {
                    title: '如何选择座位和办理在线值机？',
                    answer: '<div class="answer-content"><p class="highlight-text">您可以在航班起飞前24小时至2小时内办理在线值机：</p><ol class="step-list"><li>登录您的iFly账户</li><li>在"我的订单"中找到即将出行的航班</li><li>点击"在线值机"按钮</li><li>按照提示选择座位并完成值机</li><li>下载登机牌或保存到手机钱包</li></ol><p class="note-text"><i class="el-icon-info"></i> 办理值机后，您可以直接前往机场安检，无需在柜台排队办理登机牌。部分机场支持电子登机牌直接登机。</p></div>'
                },
                {
                    title: '行李额度和超重行李费用怎么计算？',
                    answer: '<div class="answer-content"><p class="highlight-text">行李额度根据航线和舱位有所不同：</p><ul class="info-list"><li><i class="el-icon-suitcase"></i> 国内航线：经济舱通常为20kg，商务舱30kg，头等舱40kg</li><li><i class="el-icon-suitcase"></i> 国际航线：根据航空公司和目的地不同，一般为23-32kg/件</li></ul><p>超重行李费用按照超出部分的重量计算，国内航线一般为每公斤30元起，国际航线根据航线不同可能为每公斤150-300元不等。</p><p class="tip-text"><i class="el-icon-star-on"></i> <strong>省钱提示：</strong>建议提前在iFly上购买额外行李额，可享受更优惠的价格。</p></div>'
                },
                {
                    title: '如何申请发票？',
                    answer: '<div class="answer-content"><p class="highlight-text">您可以通过以下方式申请电子发票：</p><ol class="step-list"><li>登录您的iFly账户</li><li>在"我的订单"中找到需要开具发票的订单</li><li>点击"申请发票"按钮</li><li>填写开票信息（普通发票或增值税专用发票）</li><li>提交申请后系统会生成电子发票并发送到您的邮箱</li></ol><p class="note-text"><i class="el-icon-info"></i> 请注意，发票申请需在订单完成后的12个月内提交。如需纸质发票，请联系客服处理。</p></div>'
                },
                {
                    title: '如何使用会员积分和享受会员权益？',
                    answer: '<div class="answer-content"><p class="highlight-text">iFly会员积分使用指南：</p><ul class="info-list"><li><i class="el-icon-medal"></i> <strong>积分累积：</strong>乘坐航班、购买机票或使用iFly合作伙伴服务均可累积积分</li><li><i class="el-icon-medal"></i> <strong>积分使用：</strong>可用于兑换机票、升舱、购买额外行李额或兑换合作伙伴礼品</li><li><i class="el-icon-medal"></i> <strong>会员等级：</strong>根据年度积累的积分提升会员等级，享受优先值机、额外行李额等特权</li></ul><p class="tip-text"><i class="el-icon-star-on"></i> <strong>会员提示：</strong>积分有效期一般为3年，可在"会员中心"查看积分明细和到期时间。</p></div>'
                },
                {
                    title: '特殊旅客服务如何申请？（老人、儿童、孕妇等）',
                    answer: '<div class="answer-content"><p class="highlight-text">iFly为特殊旅客提供贴心服务：</p><div class="service-card"><h4><i class="el-icon-user"></i> 老年旅客</h4><p>70岁以上老人可享受优先登机、轮椅服务，请在预订时或通过"我的订单"页面提前申请。</p></div><div class="service-card"><h4><i class="el-icon-user"></i> 孕妇旅客</h4><p>怀孕28周以内无需医疗证明，28-36周需提供医疗证明，36周以上建议不乘坐飞机。</p></div><div class="service-card"><h4><i class="el-icon-user"></i> 儿童旅客</h4><p>2-12岁儿童可购买儿童票（约75%成人票价），不满2岁婴儿可购买婴儿票（约10%成人票价）。</p></div><div class="service-card"><h4><i class="el-icon-user"></i> 无人陪伴儿童</h4><p>5-12岁无人陪伴儿童需提前申请特殊服务，机场有专人护送登机。</p></div><p class="note-text"><i class="el-icon-info"></i> 各项特殊服务需至少在航班起飞48小时前申请，部分服务可能收取额外费用。</p></div>'
                },
                {
                    title: '航班延误或取消可以获得什么补偿？',
                    answer: '<div class="answer-content"><p class="highlight-text">根据《航空旅客权益保护条例》规定的补偿标准：</p><div class="compensation-table"><table><thead><tr><th>延误情况</th><th>补偿标准</th></tr></thead><tbody><tr><td>延误4小时以上</td><td>免费餐食和饮料</td></tr><tr><td>航班取消或延误8小时以上且当日无法安排替代航班</td><td>免费住宿和交通</td></tr><tr><td>因航空公司原因造成的航班取消</td><td>可选择全额退票或免费改签</td></tr></tbody></table></div><p class="tip-text"><i class="el-icon-star-on"></i> <strong>索赔提示：</strong>如遇航班问题，请保留登机牌、行李牌等凭证，并在iFly应用中的"我的订单"页面申请补偿。</p><p class="note-text"><i class="el-icon-info"></i> 因不可抗力（如恶劣天气、突发安全事件等）造成的航班延误或取消，航空公司可能不提供额外补偿。</p></div>'
                },
                {
                    title: '如何处理行李丢失或损坏问题？',
                    answer: '<div class="answer-content"><p class="highlight-text">如果您的行李在旅行中丢失或损坏，请按以下步骤处理：</p><ol class="step-list"><li>在机场行李提取区发现问题后，立即前往航空公司行李服务柜台报告</li><li>填写行李不正常运输记录(PIR)表格，详细描述行李外观特征及内部物品</li><li>保留一份PIR记录副本和行李牌</li><li>后续通过iFly应用"我的订单"->"行李问题"提交索赔申请</li></ol><div class="time-limit-notice"><i class="el-icon-time"></i> <strong>时效提醒：</strong><ul><li>行李延误：机场发现后21天内提出索赔</li><li>行李损坏：发现后7天内提出索赔</li><li>行李丢失：通常航空公司会在21天内寻找，之后可申请赔偿</li></ul></div><p class="tip-text"><i class="el-icon-star-on"></i> <strong>贴心提示：</strong>贵重物品、易碎品和重要文件建议随身携带，不要托运。考虑购买额外的旅行保险以获得更全面的保障。</p></div>'
                },
                {
                    title: '如何预订特殊餐食？',
                    answer: '<div class="answer-content"><p class="highlight-text">iFly提供多种特殊餐食选择，满足不同旅客的需求：</p><div class="meal-options"><div class="meal-option"><h4><i class="el-icon-food"></i> 宗教餐食</h4><p>包括清真餐、印度素食餐、犹太餐等</p></div><div class="meal-option"><h4><i class="el-icon-food"></i> 健康餐食</h4><p>包括低热量餐、低盐餐、糖尿病餐、低脂餐等</p></div><div class="meal-option"><h4><i class="el-icon-food"></i> 素食餐食</h4><p>包括纯素食、奶蛋素食等多种选择</p></div><div class="meal-option"><h4><i class="el-icon-food"></i> 儿童餐食</h4><p>为2-12岁儿童提供的特别设计餐食</p></div></div><p class="highlight-text">预订步骤：</p><ol class="step-list"><li>在预订机票时在"餐食偏好"中选择</li><li>或在航班起飞前24小时通过"我的订单"页面添加</li><li>部分特殊餐食可能需要支付额外费用</li></ol><p class="note-text"><i class="el-icon-info"></i> 特殊餐食需至少在航班起飞24小时前申请，短途国内航班可能不提供特殊餐食服务。</p></div>'
                }
            ]
        };
    },
    computed: {
        filteredQuestions() {
            if (!this.selectedCategory) return [];

            // 根据分类ID筛选相关问题
            const categoryMap = {
                'booking': ['如何更改或取消已预订的机票？', '航班延误或取消时我该怎么办？'],
                'payment': ['如何申请发票？', '航班延误或取消可以获得什么补偿？'],
                'checkin': ['如何选择座位和办理在线值机？'],
                'baggage': ['行李额度和超重行李费用怎么计算？', '如何处理行李丢失或损坏问题？'],
                'account': ['如何使用会员积分和享受会员权益？'],
                'service': ['特殊旅客服务如何申请？（老人、儿童、孕妇等）', '如何预订特殊餐食？']
            };

            // 获取当前分类对应的问题标题
            const questionTitles = categoryMap[this.selectedCategory.id] || [];

            // 从popularQuestions中筛选匹配的问题
            return this.popularQuestions.filter(q => questionTitles.includes(q.title));
        }
    },
    methods: {
        showCategoryContent(category) {
            this.selectedCategory = category;
            this.showCategoryDialog = true;
            this.activeCategoryQuestions = ['0']; // 默认打开第一个问题
        },

        showCategory(categoryId) {
            // 查找对应的分类并显示内容
            const category = this.helpCategories.find(c => c.id === categoryId);
            if (category) {
                this.showCategoryContent(category);
            }
        },
        startChat() {
            // 打开AI客服窗口
            this.showAiChat = true;
        },
        toggleAiChat() {
            this.showAiChat = !this.showAiChat;
            if (this.showAiChat) {
                this.minimized = false;
                this.$nextTick(() => {
                    this.scrollToBottom();
                });
            }
        },
        minimizeAiChat() {
            this.minimized = !this.minimized;
        },
        sendMessage() {
            if (!this.chatInput.trim()) return;

            const userMessage = {
                text: this.chatInput.trim(),
                isBot: false,
                time: this.getCurrentTime()
            };

            this.chatMessages.push(userMessage);
            this.chatInput = '';
            this.chatSuggestions = [];

            // 显示输入中的状态
            this.isTyping = true;
            this.$nextTick(() => {
                this.scrollToBottom();
            });

            // 模拟AI回复延迟
            setTimeout(() => {
                this.isTyping = false;

                // 根据用户消息生成AI回复
                const botResponse = this.generateBotResponse(userMessage.text);

                this.chatMessages.push({
                    text: botResponse.text,
                    isBot: true,
                    time: this.getCurrentTime()
                });

                // 更新建议问题
                this.chatSuggestions = botResponse.suggestions || [];

                this.$nextTick(() => {
                    this.scrollToBottom();
                });
            }, 1000);
        },
        getCurrentTime() {
            const now = new Date();
            const hours = String(now.getHours()).padStart(2, '0');
            const minutes = String(now.getMinutes()).padStart(2, '0');
            return `${hours}:${minutes}`;
        },
        scrollToBottom() {
            if (this.$refs.chatBody) {
                this.$refs.chatBody.scrollTop = this.$refs.chatBody.scrollHeight;
            }
        },
        selectSuggestion(suggestion) {
            this.chatInput = suggestion;
            this.sendMessage();
        },
        generateBotResponse(userMessage) {
            // 这里可以实现更复杂的规则或接入真实的AI API
            const lowercaseMsg = userMessage.toLowerCase();

            // 简单的关键词匹配规则
            if (lowercaseMsg.includes('退票') || lowercaseMsg.includes('取消')) {
                return {
                    text: '您可以在订单详情页找到"申请退票"按钮，根据您的机票类型，可能会有不同的退票手续费。经济舱全价票一般可全额退款，特价票可能会收取5%-50%不等的退票手续费。',
                    suggestions: ['退票要多长时间到账?', '如何查看退票进度?', '特价票可以退吗?']
                };
            } else if (lowercaseMsg.includes('改签') || lowercaseMsg.includes('更改') || lowercaseMsg.includes('改期')) {
                return {
                    text: '改签需要在"我的订单"页面找到对应航班，点击"申请改签"，选择新的航班后支付差价即可完成。请注意，根据舱位不同，可能收取改签手续费。',
                    suggestions: ['改签有手续费吗?', '可以改签多少次?', '如何选择新航班?']
                };
            } else if (lowercaseMsg.includes('行李') || lowercaseMsg.includes('托运') || lowercaseMsg.includes('限额')) {
                return {
                    text: '国内航线经济舱一般可免费托运20kg行李，商务舱30kg，头等舱40kg。国际航线根据目的地不同有所差异，一般为23-32kg/件。超出部分需支付超重费用。',
                    suggestions: ['如何购买额外行李额?', '特殊行李如何托运?', '行李延误怎么办?']
                };
            } else if (lowercaseMsg.includes('值机') || lowercaseMsg.includes('登机牌')) {
                return {
                    text: '您可以在航班起飞前24小时至2小时内办理在线值机：登录账户→"我的订单"→找到航班→点击"在线值机"→选择座位→生成登机牌。您可以保存电子登机牌或打印纸质登机牌。',
                    suggestions: ['可以为同行人值机吗?', '选座有什么规则?', '值机后可以更换座位吗?']
                };
            } else if (lowercaseMsg.includes('支付') || lowercaseMsg.includes('付款') || lowercaseMsg.includes('付钱')) {
                return {
                    text: 'iFly支持多种支付方式，包括支付宝、微信支付、银联卡、信用卡等。付款成功后，您会立即收到订单确认邮件和短信。如遇支付问题，请保存订单号并联系客服。',
                    suggestions: ['支付失败怎么办?', '可以分期付款吗?', '如何使用优惠券?']
                };
            } else if (lowercaseMsg.includes('发票') || lowercaseMsg.includes('报销')) {
                return {
                    text: '您可以在"我的订单"中找到对应订单，点击"申请发票"，选择发票类型（普通发票或增值税专用发票）并填写相关信息，提交后系统会生成电子发票并发送到您的邮箱。',
                    suggestions: ['发票什么时候开具?', '可以修改发票抬头吗?', '需要纸质发票怎么办?']
                };
            } else if (lowercaseMsg.includes('餐食') || lowercaseMsg.includes('吃')) {
                return {
                    text: '大部分国际航班及3小时以上的国内航班会提供免费餐食。您可以在预订时或航班起飞前24小时通过"我的订单"页面选择特殊餐食（如素食、清真餐等）。',
                    suggestions: ['如何预订特殊餐食?', '航班上有儿童餐吗?', '餐食过敏怎么办?']
                };
            } else if (lowercaseMsg.includes('积分') || lowercaseMsg.includes('里程')) {
                return {
                    text: 'iFly会员可通过乘坐航班累积积分，1元消费通常可获得1积分。积分可用于兑换机票、升舱、购买额外行李额等。积分有效期一般为3年，可在"会员中心"查看积分明细。',
                    suggestions: ['如何查看积分余额?', '积分兑换比例是多少?', '积分快到期怎么办?']
                };
            }

            // 默认回复
            return {
                text: '感谢您的咨询。您的问题可能需要更多细节，请问您需要了解关于预订、退改签、值机还是其他方面的信息？您也可以直接致电客服热线400-123-4567获取更详细的帮助。',
                suggestions: ['如何预订机票?', '退改签规则是什么?', '怎样选择座位?']
            };
        }
    }
};
</script>

<style scoped>
.help-center {
    padding: 20px;
    background-color: #f5f7fa;
    min-height: 100vh;
}

.header-banner {
    background: linear-gradient(135deg, #00468c, #0076c6);
    color: white;
    padding: 50px 30px;
    border-radius: 12px;
    text-align: center;
    margin-bottom: 40px;
    box-shadow: 0 10px 30px rgba(0, 71, 140, 0.2);
    position: relative;
    overflow: hidden;
}

.banner-content {
    position: relative;
    z-index: 1;
    animation: fadeIn 1s ease-out;
}

.banner-content h1 {
    margin: 0 0 15px;
    font-size: 36px;
    font-weight: 600;
    letter-spacing: 1px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    display: inline-flex;
    align-items: center;
}

.banner-content h1 i {
    margin-right: 10px;
    font-size: 32px;
}

.banner-content p {
    margin: 0 0 20px;
    font-size: 18px;
    opacity: 0.9;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
}

.banner-actions {
    margin-top: 30px;
    animation: slideUp 0.8s ease-out 0.3s both;
}

.banner-actions .el-button {
    margin: 0 10px;
    padding: 12px 24px;
    font-size: 16px;
    transition: all 0.3s ease;
}

.banner-actions .el-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
}

.banner-decoration {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 0;
}

.decoration-circle {
    position: absolute;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.1);
    animation: pulse 5s infinite alternate ease-in-out;
}

.decoration-circle.circle-1 {
    width: 150px;
    height: 150px;
    top: -30px;
    left: -30px;
    animation-delay: 0s;
}

.decoration-circle.circle-2 {
    width: 200px;
    height: 200px;
    top: 50%;
    right: -50px;
    transform: translateY(-50%);
    animation-delay: 1s;
}

.decoration-circle.circle-3 {
    width: 120px;
    height: 120px;
    bottom: -30px;
    left: 30%;
    animation-delay: 2s;
}

.decoration-line {
    position: absolute;
    background-color: rgba(255, 255, 255, 0.1);
}

.decoration-line.line-1 {
    width: 100%;
    height: 1px;
    top: 50%;
    animation: expandWidth 3s infinite alternate ease-in-out;
}

.decoration-line.line-2 {
    width: 1px;
    height: 100%;
    top: 0;
    left: 50%;
    animation: expandHeight 3s infinite alternate ease-in-out 1.5s;
}

@keyframes pulse {
    0% {
        transform: scale(1);
        opacity: 0.1;
    }

    100% {
        transform: scale(1.2);
        opacity: 0.2;
    }
}

@keyframes expandWidth {
    0% {
        width: 0%;
        left: 50%;
    }

    100% {
        width: 100%;
        left: 0%;
    }
}

@keyframes expandHeight {
    0% {
        height: 0%;
        top: 50%;
    }

    100% {
        height: 100%;
        top: 0%;
    }
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.search-section {
    max-width: 700px;
    margin: 0 auto 40px;
}

.search-input {
    width: 100%;
}

.help-categories {
    margin-bottom: 40px;
}

/* 帮助分类卡片样式 */
.help-category-card {
    cursor: pointer;
    transition: all 0.3s;
    height: 200px;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    padding: 20px;
    text-align: center;
}

.help-category-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 10px 25px rgba(0, 118, 198, 0.2);
}

.help-category-card .category-icon {
    margin-bottom: 20px;
    font-size: 42px;
    color: #0076c6;
    transition: all 0.3s;
}

.help-category-card:hover .category-icon {
    transform: scale(1.1);
}

.help-category-card h3 {
    margin: 0 0 10px;
    font-size: 18px;
}

.help-category-card p {
    margin: 0;
    font-size: 14px;
    color: #666;
    text-align: center;
}

.popular-questions {
    margin-bottom: 40px;
    background-color: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.popular-questions h2 {
    font-size: 24px;
    margin-bottom: 25px;
    color: #333;
    position: relative;
    padding-bottom: 15px;
    text-align: center;
}

.popular-questions h2:after {
    content: '';
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 0;
    width: 60px;
    height: 3px;
    background-color: #0076c6;
}

.question-title {
    display: flex;
    align-items: center;
    font-weight: 500;
}

.question-title i {
    margin-right: 10px;
    color: #0076c6;
    font-size: 18px;
}

.el-collapse-item {
    margin-bottom: 10px;
    border-radius: 8px;
    overflow: hidden;
}

.question-answer {
    padding: 10px;
    color: #666;
    line-height: 1.6;
}

.contact-section {
    background-color: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
}

.contact-section h2 {
    font-size: 22px;
    margin-bottom: 20px;
    color: #333;
    position: relative;
    padding-bottom: 10px;
    text-align: center;
}

.contact-section h2:after {
    content: '';
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    bottom: 0;
    width: 50px;
    height: 3px;
    background-color: #0076c6;
}

.contact-method {
    text-align: center;
    padding: 20px;
    border-radius: 8px;
    background-color: #f9f9f9;
    height: 100%;
    margin-bottom: 20px;
}

.contact-method i {
    font-size: 36px;
    color: #0076c6;
    margin-bottom: 15px;
}

.contact-method h3 {
    margin: 0 0 10px;
    font-size: 18px;
}

.contact-method p {
    margin: 5px 0;
    font-size: 16px;
    font-weight: 500;
}

.contact-method .note {
    font-size: 14px;
    color: #999;
    font-weight: normal;
    margin-top: 10px;
}

/* AI聊天窗口样式 */
.ai-chat-trigger {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background-color: #0076c6;
    color: white;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    cursor: pointer;
    box-shadow: 0 4px 12px rgba(0, 71, 140, 0.3);
    transition: all 0.3s ease;
    z-index: 1000;
}

.ai-chat-trigger:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 16px rgba(0, 71, 140, 0.4);
}

.ai-chat-trigger i {
    font-size: 24px;
    margin-bottom: 4px;
}

.ai-chat-trigger span {
    font-size: 12px;
}

.ai-chat-window {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 360px;
    height: 500px;
    background-color: white;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
    z-index: 1001;
    overflow: hidden;
}

.ai-chat-header {
    padding: 15px 20px;
    background: linear-gradient(135deg, #0076c6, #003b63);
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.ai-chat-title {
    display: flex;
    align-items: center;
}

.ai-chat-title i {
    font-size: 20px;
    margin-right: 10px;
}

.ai-chat-title span {
    font-weight: 600;
    font-size: 16px;
}

.ai-chat-actions i {
    margin-left: 15px;
    cursor: pointer;
    font-size: 16px;
    opacity: 0.8;
    transition: opacity 0.2s;
}

.ai-chat-actions i:hover {
    opacity: 1;
}

.ai-chat-body {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
    background-color: #f5f7fa;
}

.ai-chat-messages {
    display: flex;
    flex-direction: column;
}

.message {
    margin-bottom: 15px;
    display: flex;
    align-items: flex-start;
    max-width: 80%;
}

.bot-message {
    align-self: flex-start;
}

.user-message {
    align-self: flex-end;
    flex-direction: row-reverse;
}

.message-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    justify-content: center;
    align-items: center;
    margin-right: 10px;
    flex-shrink: 0;
}

.user-message .message-avatar {
    margin-right: 0;
    margin-left: 10px;
    background-color: #42A5F5;
    color: white;
}

.bot-message .message-avatar {
    background-color: #0076c6;
    color: white;
}

.message-content {
    background-color: white;
    padding: 12px;
    border-radius: 12px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    position: relative;
}

.user-message .message-content {
    background-color: #E3F2FD;
    text-align: right;
}

.message-content p {
    margin: 0 0 5px;
    line-height: 1.5;
}

.message-time {
    font-size: 10px;
    color: #999;
    margin-top: 4px;
    display: inline-block;
}

.ai-chat-footer {
    padding: 10px 15px;
    border-top: 1px solid #eee;
}

.typing-indicator {
    display: inline-flex;
    align-items: center;
    padding: 8px 15px;
    background-color: white;
    border-radius: 12px;
    margin-bottom: 15px;
}

.typing-indicator span {
    display: inline-block;
    width: 8px;
    height: 8px;
    margin-right: 5px;
    background-color: #0076c6;
    border-radius: 50%;
    opacity: 0.6;
    animation: typing 1s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
    animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
    animation-delay: 0.3s;
}

.typing-indicator span:nth-child(3) {
    animation-delay: 0.6s;
    margin-right: 0;
}

@keyframes typing {

    0%,
    100% {
        transform: scale(1);
        opacity: 0.6;
    }

    50% {
        transform: scale(1.3);
        opacity: 1;
    }
}

.ai-chat-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px 15px;
    border-top: 1px solid #eee;
}

.suggestion-chip {
    background-color: #f0f9ff;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid #d4e9f7;
}

.suggestion-chip:hover {
    background-color: #e3f2fd;
    border-color: #0076c6;
}

.slide-up-enter-active,
.slide-up-leave-active {
    transition: all 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
    transform: translateY(20px);
    opacity: 0;
}

/* 新增帮助中心内容美化样式 */
.answer-content {
    background-color: #f9fbfd;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);
    margin-top: 10px;
}

.highlight-text {
    font-size: 16px;
    color: #0076c6;
    font-weight: 500;
    margin-bottom: 15px;
    border-left: 4px solid #0076c6;
    padding-left: 12px;
}

.note-text {
    background-color: #f0f7ff;
    padding: 10px 15px;
    border-radius: 8px;
    border-left: 4px solid #a3cfff;
    font-size: 14px;
    color: #333;
    margin-top: 15px;
    display: flex;
    align-items: flex-start;
}

.note-text i {
    margin-right: 8px;
    color: #0076c6;
    font-size: 16px;
    margin-top: 2px;
}

.tip-text {
    background-color: #f0fff4;
    padding: 10px 15px;
    border-radius: 8px;
    border-left: 4px solid #67c23a;
    font-size: 14px;
    color: #333;
    margin-top: 15px;
    display: flex;
    align-items: flex-start;
}

.tip-text i {
    margin-right: 8px;
    color: #67c23a;
    font-size: 16px;
    margin-top: 2px;
}

.step-list {
    padding-left: 20px;
    margin-bottom: 15px;
}

.step-list li {
    margin-bottom: 10px;
    position: relative;
    padding-left: 5px;
}

.info-list {
    list-style: none;
    padding-left: 0;
    margin-bottom: 15px;
}

.info-list li {
    margin-bottom: 10px;
    padding-left: 25px;
    position: relative;
}

.info-list li i {
    position: absolute;
    left: 0;
    top: 2px;
    color: #0076c6;
}

.service-card {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    transition: all 0.3s ease;
}

.service-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}

.service-card h4 {
    display: flex;
    align-items: center;
    color: #0076c6;
    margin-top: 0;
    margin-bottom: 10px;
}

.service-card h4 i {
    margin-right: 8px;
}

.service-card p {
    margin: 0;
    color: #666;
}

.compensation-table {
    margin: 15px 0;
    overflow-x: auto;
}

.compensation-table table {
    width: 100%;
    border-collapse: collapse;
}

.compensation-table th {
    background-color: #e6f2ff;
    color: #0076c6;
    text-align: left;
    padding: 12px 15px;
}

.compensation-table td {
    padding: 10px 15px;
    border-bottom: 1px solid #eee;
}

.compensation-table tr:hover {
    background-color: #f5f9ff;
}

.time-limit-notice {
    background-color: #fff8e6;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
    border-left: 4px solid #e6a23c;
}

.time-limit-notice i {
    color: #e6a23c;
    margin-right: 8px;
}

.time-limit-notice ul {
    margin-top: 10px;
    margin-bottom: 0;
    padding-left: 25px;
}

.time-limit-notice li {
    margin-bottom: 5px;
}

.meal-options {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin: 15px 0;
}

.meal-option {
    background-color: white;
    border-radius: 8px;
    padding: 15px;
    flex: 1;
    min-width: 180px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.meal-option h4 {
    display: flex;
    align-items: center;
    color: #0076c6;
    margin-top: 0;
    margin-bottom: 10px;
    font-size: 15px;
}

.meal-option h4 i {
    margin-right: 8px;
}

.meal-option p {
    margin: 0;
    color: #666;
    font-size: 13px;
}

/* 分类对话框样式 */
.category-dialog>>>.el-dialog__header {
    background-color: #0076c6;
    color: white;
    padding: 15px 20px;
    border-radius: 8px 8px 0 0;
}

.category-dialog>>>.el-dialog__title {
    color: white;
    font-size: 20px;
    font-weight: 600;
}

.category-dialog>>>.el-dialog__headerbtn .el-dialog__close {
    color: white;
    font-size: 20px;
}

.category-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 30px;
    text-align: center;
}

.category-icon.large {
    width: 80px;
    height: 80px;
    background-color: #e6f2ff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 15px;
    font-size: 36px;
    color: #0076c6;
}

.category-header p {
    max-width: 600px;
    color: #666;
    font-size: 16px;
    line-height: 1.6;
}

.category-questions {
    margin-top: 20px;
}
</style>