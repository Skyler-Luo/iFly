<template>
    <div class="destinations-section">
        <h2 class="section-title">热门<span class="highlight">目的地</span></h2>
        <p class="section-subtitle">探索世界各地最受欢迎的旅游胜地，开启您的旅行</p>
        <div class="destinations-grid">
            <div class="destination-card" v-for="(destination, index) in destinations" :key="index">
                <div class="destination-image" :style="{ backgroundImage: `url(${destination.image})` }">
                    <div class="destination-overlay">
                        <h3>{{ destination.name }}</h3>
                        <p>¥{{ destination.price }}起</p>
                        <el-button size="small" type="primary" round @click="handleDestinationClick(destination)">
                            查看详情
                        </el-button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'DestinationsGrid',
    props: {
        destinations: {
            type: Array,
            default: () => [
                {
                    name: '巴黎',
                    image: 'https://picsum.photos/id/1067/300/200',
                    price: '2999'
                },
                {
                    name: '东京',
                    image: 'https://picsum.photos/id/1036/300/200',
                    price: '1999'
                },
                {
                    name: '曼谷',
                    image: 'https://picsum.photos/id/164/300/200',
                    price: '1599'
                },
                {
                    name: '悉尼',
                    image: 'https://picsum.photos/id/1037/300/200',
                    price: '3999'
                },
                {
                    name: '纽约',
                    image: 'https://picsum.photos/id/1016/300/200',
                    price: '4999'
                },
                {
                    name: '新加坡',
                    image: 'https://picsum.photos/id/1039/300/200',
                    price: '1899'
                }
            ]
        }
    },
    methods: {
        handleDestinationClick(destination) {
            this.$emit('select-destination', destination);
        }
    }
}
</script>

<style scoped>
.destinations-section {
    padding: 50px 0;
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

.destinations-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 25px;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.destination-card {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    height: 220px;
    position: relative;
    transition: all 0.3s cubic-bezier(0.165, 0.84, 0.44, 1);
}

.destination-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
}

.destination-image {
    width: 100%;
    height: 100%;
    background-size: cover;
    background-position: center;
    transition: transform 0.5s ease;
}

.destination-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: linear-gradient(to top, rgba(0, 0, 0, 0.8) 0%, rgba(0, 0, 0, 0.4) 60%, transparent 100%);
    color: white;
    padding: 25px 20px;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    transform: translateY(0);
    transition: all 0.3s ease;
}

.destination-card:hover .destination-image {
    transform: scale(1.05);
}

.destination-overlay h3 {
    margin: 0 0 10px;
    font-size: 24px;
    font-weight: 700;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

.destination-overlay p {
    margin: 0 0 15px;
    font-size: 18px;
    font-weight: 600;
    color: #ffeb3b;
    text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
    opacity: 1;
    transform: translateY(0);
}

@media (max-width: 768px) {
    .destinations-grid {
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 15px;
    }

    .destination-card {
        height: 180px;
    }

    .destination-overlay h3 {
        font-size: 20px;
    }

    .destination-overlay p {
        font-size: 16px;
    }
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