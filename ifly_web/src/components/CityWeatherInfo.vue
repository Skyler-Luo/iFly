<template>
    <div class="city-weather-info">
        <div v-if="loading" class="loading-container">
            <div class="loading-spinner"></div>
            <span>加载天气数据中...</span>
        </div>
        <div v-else-if="error" class="error-container">
            <div class="error-icon">!</div>
            <div>
                <p>抱歉，无法获取天气数据</p>
                <small>{{ error }}</small>
            </div>
        </div>
        <div v-else class="weather-data">
            <div class="weather-main">
                <div class="temperature">{{ weatherData.temperature }}°C</div>
                <div class="weather-icon">
                    <img :src="getWeatherIconUrl(weatherData.icon)" alt="天气图标">
                </div>
            </div>
            <div class="weather-description">{{ weatherData.description }}</div>
            <div class="weather-details">
                <div class="detail-item">
                    <div class="detail-label">湿度</div>
                    <div class="detail-value">{{ weatherData.humidity }}%</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">风速</div>
                    <div class="detail-value">{{ weatherData.wind_speed }} m/s</div>
                </div>
                <div class="detail-item">
                    <div class="detail-label">气压</div>
                    <div class="detail-value">{{ weatherData.pressure || 1013 }} hPa</div>
                </div>
            </div>
            <div class="update-time">
                更新时间: {{ formatUpdateTime(weatherData.updated_at) }}
                <span v-if="weatherData.is_mock" class="mock-data-indicator">(模拟数据)</span>
                <span v-else-if="weatherData.is_real" class="real-data-indicator">(真实数据)</span>
            </div>
        </div>
    </div>
</template>

<script>
import api from '@/services/api';

export default {
    name: 'CityWeatherInfo',
    props: {
        city: {
            type: String,
            required: true
        }
    },
    data() {
        return {
            loading: true,
            error: null,
            weatherData: null
        };
    },
    mounted() {
        this.fetchWeatherData();
    },
    watch: {
        city() {
            this.loading = true;
            this.error = null;
            this.fetchWeatherData();
        }
    },
    methods: {
        async fetchWeatherData() {
            console.log('获取城市天气数据:', this.city);
            
            if (!this.city) {
                this.error = '未提供城市名称';
                this.loading = false;
                return;
            }
            
            try {
                this.loading = true;
                
                // 从后端API获取天气数据
                const response = await api.weather.getByCity(this.city);
                console.log('API返回的天气数据:', response);
                
                // 格式化天气数据
                this.weatherData = {
                    temperature: response.temperature || response.temp,
                    description: response.description,
                    humidity: response.humidity,
                    wind_speed: response.wind_speed || (response.wind && response.wind.speed),
                    pressure: response.pressure || 1013,
                    icon: response.icon,
                    updated_at: response.updated_at,
                    is_mock: response.is_mock || false,
                    is_real: response.is_real || false
                };
                
                this.loading = false;
                this.error = null;
            } catch (err) {
                console.error('获取天气数据失败:', err);
                this.error = `获取天气数据失败: ${err.message || '未知错误'}`;                
                this.loading = false;
            }
        },

        getWeatherIconUrl(iconCode) {
            // 使用OpenWeatherMap图标URL
            return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
        },

        formatUpdateTime(dateString) {
            if (!dateString) return '未知';
            
            try {
                const date = new Date(dateString);
                return date.toLocaleString('zh-CN', {
                    year: 'numeric',
                    month: '2-digit',
                    day: '2-digit',
                    hour: '2-digit',
                    minute: '2-digit'
                });
            } catch (e) {
                console.error('日期格式化错误:', e);
                return dateString;
            }
        }
    }
};
</script>

<style scoped>
.city-weather-info {
    font-family: Arial, sans-serif;
    color: #333;
    width: 100%;
    min-height: 200px;
    box-sizing: border-box;
}

.loading-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: #666;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top-color: #1890ff;
    animation: spin 1s ease-in-out infinite;
    margin-bottom: 15px;
}

@keyframes spin {
    to {
        transform: rotate(360deg);
    }
}

.error-container {
    display: flex;
    align-items: center;
    background-color: #fff2f0;
    border: 1px solid #ffccc7;
    padding: 15px;
    border-radius: 4px;
    margin: 10px 0;
}

.error-icon {
    width: 24px;
    height: 24px;
    background-color: #ff4d4f;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin-right: 10px;
}

.weather-data {
    padding: 5px;
}

.weather-main {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}

.temperature {
    font-size: 36px;
    font-weight: bold;
    color: #1890ff;
}

.weather-icon img {
    width: 64px;
    height: 64px;
}

.weather-description {
    text-align: center;
    font-size: 16px;
    margin-bottom: 15px;
}

.weather-details {
    display: flex;
    justify-content: space-around;
    margin-bottom: 15px;
}

.detail-item {
    text-align: center;
}

.detail-label {
    font-size: 12px;
    color: #666;
    margin-bottom: 5px;
}

.detail-value {
    font-size: 16px;
    font-weight: 500;
}

.update-time {
    text-align: center;
    font-size: 12px;
    color: #999;
}

.mock-data-indicator {
    color: #ff7875;
    margin-left: 5px;
}

.real-data-indicator {
    color: #52c41a;
    margin-left: 5px;
}
</style>