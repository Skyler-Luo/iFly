import axios from 'axios';

// 使用 OpenWeatherMap API
// 通常应该在环境变量中存储API密钥，这里为了示例直接使用
// 注意：这是一个示例密钥，可能不工作，真实项目中请使用自己的密钥
const API_KEY = '5f17e2dc0af5d5f3a1658da51470ee9f';
const BASE_URL = 'https://api.openweathermap.org/data/2.5';

// 创建一个带有错误处理的axios实例
const weatherApi = axios.create({
    timeout: 10000, // 10秒超时
    headers: {
        'Content-Type': 'application/json'
    }
});

// 添加请求拦截器
weatherApi.interceptors.request.use(
    config => {
        console.log('发送天气请求:', config.url);
        return config;
    },
    error => {
        console.error('天气请求错误:', error);
        return Promise.reject(error);
    }
);

// 添加响应拦截器
weatherApi.interceptors.response.use(
    response => {
        console.log('天气响应成功:', response.status);
        return response;
    },
    error => {
        console.error('天气响应错误:', error.message);
        return Promise.reject(error);
    }
);

/**
 * 天气服务类，提供城市天气查询功能
 */
class WeatherService {
    /**
     * 根据城市名称获取当前天气
     * @param {string} city 城市名称
     * @param {string} country 国家代码，如CN, US等
     * @returns {Promise} 天气信息Promise
     */
    async getCurrentWeather(city, country = '') {
        try {
            console.log(`获取城市天气: ${city}, ${country}`);

            // 添加国家代码可以提高准确度
            const query = country ? `${city},${country}` : city;

            const response = await weatherApi.get(`${BASE_URL}/weather`, {
                params: {
                    q: query,
                    appid: API_KEY,
                    units: 'metric', // 使用摄氏度
                    lang: 'zh_cn'    // 中文结果
                }
            });

            return this.formatWeatherData(response.data);
        } catch (error) {
            console.error('获取天气数据失败:', error);
            return {
                error: true,
                message: error.response?.data?.message || '获取天气数据失败'
            };
        }
    }

    /**
     * 获取5天天气预报
     * @param {string} city 城市名称
     * @param {string} country 国家代码，如CN, US等
     * @returns {Promise} 天气预报信息Promise
     */
    async getForecast(city, country = '') {
        try {
            // 添加国家代码可以提高准确度
            const query = country ? `${city},${country}` : city;
            const response = await weatherApi.get(`${BASE_URL}/forecast`, {
                params: {
                    q: query,
                    appid: API_KEY,
                    units: 'metric',
                    lang: 'zh_cn'
                }
            });

            return this.formatForecastData(response.data);
        } catch (error) {
            console.error('获取天气预报失败:', error);
            return {
                error: true,
                city: city,
                country: country || 'Unknown',
                message: error.response?.data?.message || '获取天气预报数据失败'
            };
        }
    }

    /**
     * 格式化天气数据
     * @param {Object} data 原始天气数据
     * @returns {Object} 格式化后的天气数据
     */
    formatWeatherData(data) {
        if (!data) return null;

        return {
            city: data.name,
            country: data.sys.country,
            temp: Math.round(data.main.temp),
            feels_like: Math.round(data.main.feels_like),
            humidity: data.main.humidity,
            pressure: data.main.pressure,
            description: data.weather[0].description,
            icon: this.getWeatherIconUrl(data.weather[0].icon),
            wind: {
                speed: data.wind.speed,
                deg: data.wind.deg
            },
            clouds: data.clouds.all,
            timestamp: data.dt,
            sunrise: data.sys.sunrise,
            sunset: data.sys.sunset
        };
    }

    /**
     * 格式化天气预报数据
     * @param {Object} data 原始天气预报数据
     * @returns {Object} 格式化后的天气预报数据
     */
    formatForecastData(data) {
        if (!data || !data.list) return null;

        const forecast = data.list.map(item => ({
            timestamp: item.dt,
            date: new Date(item.dt * 1000),
            temp: Math.round(item.main.temp),
            feels_like: Math.round(item.main.feels_like),
            humidity: item.main.humidity,
            description: item.weather[0].description,
            icon: this.getWeatherIconUrl(item.weather[0].icon),
            wind: {
                speed: item.wind.speed,
                deg: item.wind.deg
            },
            clouds: item.clouds.all
        }));

        return {
            city: data.city.name,
            country: data.city.country,
            forecast
        };
    }

    /**
     * 获取天气图标URL
     * @param {string} iconCode 图标代码
     * @returns {string} 图标URL
     */
    getWeatherIconUrl(iconCode) {
        return `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
    }
}

export default new WeatherService(); 