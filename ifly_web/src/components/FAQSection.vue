<template>
    <div class="faq-section">
        <h2 class="section-title">常见<span class="highlight">问题</span></h2>
        <p class="section-subtitle">您可能遇到的常见问题和解答，更多问题请联系我们的客服团队</p>
        <el-collapse accordion class="faq-list">
            <el-collapse-item v-for="(faq, index) in faqs" :key="index" :title="faq.question">
                <div class="faq-answer">{{ faq.answer }}</div>
            </el-collapse-item>
        </el-collapse>
        <div class="more-help">
            <p>还有其他问题？</p>
            <el-button type="primary" size="large" round class="contact-btn">联系客服</el-button>
        </div>
    </div>
</template>

<script>
export default {
    name: 'FaqSection',
    props: {
        faqs: {
            type: Array,
            default: () => [
                {
                    question: '如何取消或更改我的预订？',
                    answer: '您可以在"我的订单"中找到您想要取消或更改的预订，然后点击相应的按钮进行操作。请注意，根据航空公司的政策，可能会收取一定的手续费。'
                },
                {
                    question: '我可以提前多久预订航班？',
                    answer: '大多数航班可以提前11个月预订。建议您尽早预订以获得最优惠的价格。'
                },
                {
                    question: '如何选择座位？',
                    answer: '在完成订票后，您可以在"我的订单"中找到您的订单，点击"选择座位"按钮进行座位选择。部分航班可能需要支付额外费用。'
                },
                {
                    question: '儿童和婴儿的预订政策是什么？',
                    answer: '2岁以上的儿童需要购买全价机票，2岁以下的婴儿可以享受婴儿票价（通常是成人票价的10%）。不同航空公司可能有不同规定，请在预订时查看具体政策。'
                },
                {
                    question: '行李限额是多少？',
                    answer: '行李限额取决于您预订的航班和舱位。经济舱通常允许一件随身行李和一件托运行李（不超过23kg）。您可以在订单详情中查看具体的行李限额。'
                }
            ]
        }
    }
}
</script>

<style scoped>
.faq-section {
    padding: 60px 0;
    background-color: #f8f9fa;
    max-width: 1000px;
    margin: 0 auto;
}

.section-title {
    text-align: center;
    margin-bottom: 15px;
    font-size: 28px;
    color: #333;
    position: relative;
    padding-bottom: 25px;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: 10px;
    left: 50%;
    transform: translateX(-50%);
    width: 80px;
    height: 3px;
    background: linear-gradient(to right, #42a5f5, #1976d2);
}

.highlight {
    color: #1976d2;
}

.section-subtitle {
    text-align: center;
    max-width: 600px;
    margin: 0 auto 30px;
    color: #666;
    font-size: 16px;
    line-height: 1.6;
    opacity: 0.9;
}

.faq-list {
    border: none;
    margin: 0 20px;
}

.el-collapse-item {
    margin-bottom: 12px;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
    background-color: white;
}

:deep(.el-collapse-item__header) {
    font-weight: 600;
    font-size: 16px;
    color: #333;
    background-color: white;
    padding: 15px 20px;
    border-bottom: none;
}

:deep(.el-collapse-item__header:hover) {
    color: #1976d2;
}

:deep(.el-collapse-item__arrow) {
    color: #1976d2;
}

:deep(.el-collapse-item__wrap) {
    background-color: #f9f9f9;
    border-top: 1px solid #f0f0f0;
}

.faq-answer {
    padding: 5px 0;
    line-height: 1.7;
    color: #555;
}

.more-help {
    text-align: center;
    margin-top: 40px;
}

.more-help p {
    margin-bottom: 15px;
    font-weight: 500;
    color: #333;
}

.contact-btn {
    padding: 12px 30px;
    font-size: 16px;
    background: linear-gradient(135deg, #42a5f5, #1976d2);
    border: none;
    transition: all 0.3s ease;
}

.contact-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(66, 165, 245, 0.3);
}

@media (max-width: 768px) {
    .faq-section {
        padding: 40px 15px;
    }

    .faq-list {
        margin: 0;
    }

    .section-title {
        font-size: 24px;
    }
}
</style>