<template>
    <div class="testimonials-section">
        <h2 class="section-title">乘客的<span class="highlight">真实评价</span></h2>
        <p class="section-subtitle">来自我们客户的真实反馈，让您了解我们的服务水平</p>
        <el-carousel :interval="4000" type="card" height="250px">
            <el-carousel-item v-for="(testimonial, index) in testimonials" :key="index">
                <div class="testimonial-card">
                    <div class="testimonial-avatar" :style="{ backgroundImage: `url(${testimonial.avatar})` }"></div>
                    <div class="testimonial-content">
                        <div class="testimonial-stars">
                            <i class="el-icon-star-on" v-for="n in testimonial.rating" :key="n"></i>
                        </div>
                        <p class="testimonial-text">"{{ testimonial.text }}"</p>
                        <p class="testimonial-author">{{ testimonial.author }}</p>
                        <p class="testimonial-trip">{{ testimonial.trip }}</p>
                    </div>
                </div>
            </el-carousel-item>
        </el-carousel>
    </div>
</template>

<script>
export default {
    name: 'TestimonialSection',
    props: {
        testimonials: {
            type: Array,
            default: () => [
                {
                    author: '张小明',
                    avatar: 'https://picsum.photos/id/1062/60/60',
                    rating: 5,
                    text: '第一次在iFly预订机票，整个过程非常流畅，价格也很实惠。航班准点，服务一流，下次还会选择iFly！',
                    trip: '北京 - 上海'
                },
                {
                    author: '李华',
                    avatar: 'https://picsum.photos/id/1066/60/60',
                    rating: 4,
                    text: '退改签流程简单明了，客服响应迅速，解决了我的所有问题。虽然有小插曲，但总体体验还是很好的。',
                    trip: '成都 - 广州'
                },
                {
                    author: '王丽',
                    avatar: 'https://picsum.photos/id/1074/60/60',
                    rating: 5,
                    text: '作为常旅客，我尝试过很多订票平台，但iFly的用户体验是最好的，尤其是座位选择和在线值机功能非常实用！',
                    trip: '上海 - 纽约'
                }
            ]
        }
    }
}
</script>

<style scoped>
.testimonials-section {
    margin: 50px 0;
}

.section-title {
    text-align: center;
    margin-bottom: 30px;
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

.el-carousel {
    padding: 20px 0;
}

.testimonial-card {
    background: white;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    padding: 20px;
    height: 90%;
    display: flex;
    flex-direction: column;
    align-items: center;
}

.testimonial-avatar {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-size: cover;
    background-position: center;
    border: 3px solid #1976d2;
    margin-bottom: 15px;
}

.testimonial-content {
    text-align: center;
}

.testimonial-stars {
    color: #ffc107;
    margin-bottom: 10px;
}

.testimonial-text {
    font-style: italic;
    margin-bottom: 15px;
    line-height: 1.5;
    font-size: 14px;
}

.testimonial-author {
    font-weight: bold;
    margin-bottom: 5px;
}

.testimonial-trip {
    color: #666;
    font-size: 12px;
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
</style>