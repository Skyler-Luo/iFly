import os
import requests
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# 使用 OpenWeatherMap API
API_KEY = getattr(settings, 'OPENWEATHER_API_KEY', os.environ.get('OPENWEATHER_API_KEY', 'f7979f2a78a5e1534dccb5918e1c3dbd'))
BASE_URL = 'https://api.openweathermap.org/data/2.5'

def get_weather_data(city_name, country='CN'):
    """
    从OpenWeatherMap API获取城市天气数据
    
    Args:
        city_name (str): 城市名称
        country (str, optional): 国家代码，默认为"CN"(中国)
        
    Returns:
        dict: 包含天气数据的字典，如果出错返回None
    """
    try:
        # 构建API请求URL
        url = f"{BASE_URL}/weather"
        
        # 构建请求参数
        params = {
            'q': f"{city_name},{country}",
            'appid': API_KEY,
            'units': 'metric',  # 使用摄氏度
            'lang': 'zh_cn'     # 使用中文
        }
        
        logger.info(f"请求OpenWeatherMap天气API: {url}，城市: {city_name}")
        
        # 发送API请求
        response = requests.get(url, params=params, timeout=10)
        
        # 详细记录API响应信息
        if response.status_code != 200:
            logger.error(f"API状态码错误: {response.status_code}, 响应: {response.text}")
            raise requests.exceptions.HTTPError(f"API返回状态码 {response.status_code}")
            
        logger.info(f"API响应状态码: {response.status_code}")
        
        # 处理API响应
        data = response.json()
        
        # 获取当前时间并转换为ISO格式字符串
        current_time = timezone.now().isoformat()
        
        # 解析天气数据
        weather_data = {
            'temperature': int(data['main']['temp']),
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': float(data['wind']['speed']),
            'icon': data['weather'][0]['icon'],
            'updated_at': current_time,
            'is_real': True  # 标记这是真实数据
        }
        
        logger.info(f"成功获取 {city_name} 实时天气数据: {weather_data}")
        return weather_data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"天气API请求失败: {str(e)}")
        # 记录更多上下文信息以帮助调试
        if 'response' in locals():
            logger.error(f"API响应: {getattr(response, 'text', '无响应内容')}")
        # 尝试再次调用API，更换URL或参数
        try:
            # 使用城市名直接请求，不包括国家代码
            params = {
                'q': city_name,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            logger.info(f"第二次尝试请求天气API: {url}, 仅使用城市名: {city_name}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 获取当前时间并转换为ISO格式字符串
            current_time = timezone.now().isoformat()
            
            weather_data = {
                'temperature': int(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': float(data['wind']['speed']),
                'icon': data['weather'][0]['icon'],
                'updated_at': current_time,
                'is_real': True
            }
            
            logger.info(f"成功获取 {city_name} 实时天气数据(第二次尝试)")
            return weather_data
            
        except Exception as retry_e:
            logger.error(f"第二次尝试请求天气API失败: {str(retry_e)}")
            # 最后才使用模拟数据
            logger.warning(f"所有API请求尝试均失败，将使用模拟数据")
            return get_mock_weather_data(city_name)
            
    except (KeyError, ValueError) as e:
        logger.error(f"天气数据解析失败: {e}")
        if 'data' in locals():
            logger.error(f"API返回的数据: {data}")
        return get_mock_weather_data(city_name)
    except Exception as e:
        logger.error(f"获取天气数据时发生未知错误: {e}")
        return get_mock_weather_data(city_name)

def get_forecast_data(city_name, country='CN'):
    """
    获取5天天气预报数据
    
    Args:
        city_name (str): 城市名称
        country (str, optional): 国家代码，默认为"CN"(中国)
        
    Returns:
        dict: 包含天气预报数据的字典，如果出错返回None
    """
    try:
        # 构建API请求URL
        url = f"{BASE_URL}/forecast"
        
        # 构建请求参数
        params = {
            'q': f"{city_name},{country}",
            'appid': API_KEY,
            'units': 'metric',  # 使用摄氏度
            'lang': 'zh_cn'     # 使用中文
        }
        
        logger.info(f"请求OpenWeatherMap天气预报API: {url}，城市: {city_name}")
        
        # 发送API请求
        response = requests.get(url, params=params, timeout=10)
        
        # 详细记录API响应信息
        if response.status_code != 200:
            logger.error(f"API状态码错误: {response.status_code}, 响应: {response.text}")
            raise requests.exceptions.HTTPError(f"API返回状态码 {response.status_code}")
            
        logger.info(f"API响应状态码: {response.status_code}")
        
        # 处理API响应
        data = response.json()
        
        # 当前时间的ISO格式字符串
        current_time = timezone.now().isoformat()
        
        # 解析天气预报数据
        forecast = {
            'city': city_name,
            'country': country,
            'forecast': [],
            'is_real': True,  # 标记这是真实数据
            'updated_at': current_time
        }
        
        # 获取未来5天的天气预报（每3小时一个数据点，取每天的中午数据）
        today = timezone.now().date()
        
        for item in data['list']:
            forecast_time = datetime.fromtimestamp(item['dt'])
            forecast_date = forecast_time.date()
            
            # 如果是新的一天且是在中午附近（11:00-14:00之间）
            if forecast_date > today and 11 <= forecast_time.hour <= 14:
                forecast_item = {
                    'date': forecast_time.strftime('%Y-%m-%d'),
                    'time': forecast_time.strftime('%H:%M'),
                    'temperature': int(item['main']['temp']),
                    'description': item['weather'][0]['description'],
                    'icon': item['weather'][0]['icon'],
                    'humidity': item['main']['humidity'],
                    'wind_speed': float(item['wind']['speed']),
                }
                forecast['forecast'].append(forecast_item)
                
                # 一旦收集到足够的天数，就停止
                if len(forecast['forecast']) >= 5:
                    break
        
        logger.info(f"成功获取 {city_name} 天气预报数据，共 {len(forecast['forecast'])} 天")
        return forecast
        
    except requests.exceptions.RequestException as e:
        logger.error(f"天气预报API请求失败: {str(e)}")
        # 记录更多上下文信息以帮助调试
        if 'response' in locals():
            logger.error(f"API响应: {getattr(response, 'text', '无响应内容')}")
            
        # 尝试再次调用API，更换URL或参数
        try:
            # 使用城市名直接请求，不包括国家代码
            params = {
                'q': city_name,
                'appid': API_KEY,
                'units': 'metric',
                'lang': 'zh_cn'
            }
            logger.info(f"第二次尝试请求天气预报API: {url}, 仅使用城市名: {city_name}")
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 获取当前时间的ISO格式字符串
            current_time = timezone.now().isoformat()
            
            # 解析天气预报数据
            forecast = {
                'city': city_name,
                'country': country,
                'forecast': [],
                'is_real': True,
                'updated_at': current_time
            }
            
            # 获取未来5天的天气预报
            today = timezone.now().date()
            
            for item in data['list']:
                forecast_time = datetime.fromtimestamp(item['dt'])
                forecast_date = forecast_time.date()
                
                # 如果是新的一天且是在中午附近（11:00-14:00之间）
                if forecast_date > today and 11 <= forecast_time.hour <= 14:
                    forecast_item = {
                        'date': forecast_time.strftime('%Y-%m-%d'),
                        'time': forecast_time.strftime('%H:%M'),
                        'temperature': int(item['main']['temp']),
                        'description': item['weather'][0]['description'],
                        'icon': item['weather'][0]['icon'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': float(item['wind']['speed']),
                    }
                    forecast['forecast'].append(forecast_item)
                    
                    # 一旦收集到足够的天数，就停止
                    if len(forecast['forecast']) >= 5:
                        break
            
            logger.info(f"成功获取 {city_name} 天气预报数据(第二次尝试)，共 {len(forecast['forecast'])} 天")
            return forecast
            
        except Exception as retry_e:
            logger.error(f"第二次尝试请求天气预报API失败: {str(retry_e)}")
            # 最后才使用模拟数据
            logger.warning(f"所有API请求尝试均失败，将使用模拟数据")
            return get_mock_forecast_data(city_name)
            
    except (KeyError, ValueError) as e:
        logger.error(f"天气预报数据解析失败: {e}")
        if 'data' in locals():
            logger.error(f"API返回的数据: {data}")
        return get_mock_forecast_data(city_name)
    except Exception as e:
        logger.error(f"获取天气预报时发生未知错误: {e}")
        return get_mock_forecast_data(city_name)

# 保留模拟数据函数，以便在API调用失败时作为备用
def get_mock_weather_data(city_name):
    """提供模拟的天气数据作为备用"""
    logger.info(f"使用模拟数据代替 {city_name} 的天气信息")
    # 使用ISO格式的时间字符串
    
    # 获取当前的季节
    now = timezone.now()
    month = now.month
    
    # 根据季节调整温度
    if 3 <= month <= 5:  # 春季
        base_temp = 20
        temp_range = 5
    elif 6 <= month <= 8:  # 夏季
        base_temp = 30
        temp_range = 5
    elif 9 <= month <= 11:  # 秋季
        base_temp = 15
        temp_range = 5
    else:  # 冬季
        base_temp = 5
        temp_range = 10
        
    # 城市温度调整
    city_temp_adjust = {
        '北京': 0,
        '上海': 2,
        '广州': 5,
        '深圳': 6,
        '杭州': 1,
        '成都': 0,
        '南京': 1,
        '武汉': 2,
        '西安': -1,
        '重庆': 3,
        '厦门': 4,
        '长沙': 2,
        '青岛': -1,
        '大连': -2,
        '三亚': 8
    }
    
    # 调整基础温度
    temp_adjust = city_temp_adjust.get(city_name, 0)
    adjusted_temp = base_temp + temp_adjust
    
    # 添加一些随机变化
    import random
    temp_variation = random.randint(-temp_range, temp_range)
    final_temp = adjusted_temp + temp_variation
    
    # 根据温度和季节决定天气描述
    weather_types = []
    if final_temp > 30:
        weather_types = ['晴', '晴间多云', '多云']
    elif 20 <= final_temp <= 30:
        weather_types = ['晴', '晴间多云', '多云', '阴']
    elif 10 <= final_temp < 20:
        weather_types = ['晴', '多云', '阴', '小雨']
    elif 0 <= final_temp < 10:
        weather_types = ['晴', '阴', '小雨', '小雪']
    else:
        weather_types = ['阴', '小雪', '中雪']
        
    description = random.choice(weather_types)
    
    # 根据描述选择图标
    icon = map_weather_to_icon(description)
    
    # 生成湿度和风速
    humidity = random.randint(40, 90)
    wind_speed = round(random.uniform(1.0, 6.0), 1)
    
    # 创建天气数据
    weather_data = {
        'temperature': final_temp,
        'description': description,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'icon': icon,
        'updated_at': timezone.now().isoformat(),
        'is_mock': True  # 标记这是模拟数据
    }
    
    return weather_data

def get_mock_forecast_data(city_name):
    """提供模拟的天气预报数据作为备用"""
    logger.info(f"使用模拟数据代替 {city_name} 的天气预报")
    
    # 获取当前天气作为基础
    current_weather = get_mock_weather_data(city_name)
    base_temp = current_weather['temperature']
    
    forecast = {
        'city': city_name,
        'country': 'CN',
        'forecast': [],
        'is_mock': True,  # 标记这是模拟数据
        'updated_at': timezone.now().isoformat()  # 添加ISO格式的时间戳
    }
    
    # 天气类型、图标和概率表
    weather_types = ['晴', '多云', '晴间多云', '阴', '小雨', '中雨', '大雨', '阵雨', '雷阵雨', '小雪', '中雪']
    weather_icons = {
        '晴': '01d', 
        '多云': '02d', 
        '晴间多云': '03d', 
        '阴': '04d',
        '小雨': '10d', 
        '中雨': '10d', 
        '大雨': '10d', 
        '阵雨': '09d', 
        '雷阵雨': '11d',
        '小雪': '13d', 
        '中雪': '13d'
    }
    
    import random
    
    # 生成未来5天的模拟预报
    today = timezone.now()
    current_temp = base_temp
    current_weather_type = current_weather['description']
    
    for i in range(1, 6):
        forecast_date = today + timedelta(days=i)
        
        # 温度变化（有一定连续性）
        temp_change = random.randint(-3, 3)
        new_temp = current_temp + temp_change
        # 限制温度范围
        new_temp = max(-10, min(40, new_temp))
        current_temp = new_temp
        
        # 天气变化（有一定连续性）
        # 如果当前天气是降水，有较高概率继续降水
        if current_weather_type in ['小雨', '中雨', '大雨', '阵雨', '雷阵雨', '小雪', '中雪']:
            if random.random() < 0.6:  # 60%概率保持类似天气
                weather_options = ['小雨', '中雨', '阵雨', '雷阵雨'] if new_temp > 0 else ['小雪', '中雪']
                new_weather = random.choice(weather_options)
            else:
                new_weather = '阴'  # 降水后通常转阴
        else:
            # 随机选择天气，但考虑温度
            if new_temp > 30:
                weather_options = ['晴', '多云', '晴间多云']
            elif 20 <= new_temp <= 30:
                weather_options = ['晴', '多云', '晴间多云', '阴', '阵雨']
            elif 5 <= new_temp < 20:
                weather_options = ['晴', '多云', '阴', '小雨', '阵雨']
            elif 0 <= new_temp < 5:
                weather_options = ['多云', '阴', '小雨', '小雪']
            else:  # 温度 < 0
                weather_options = ['晴', '阴', '小雪', '中雪']
                
            new_weather = random.choice(weather_options)
        
        current_weather_type = new_weather
        
        # 选择图标
        icon = weather_icons.get(new_weather, '01d')
        
        # 生成湿度和风速
        if new_weather in ['小雨', '中雨', '大雨', '阵雨', '雷阵雨', '小雪', '中雪']:
            humidity = random.randint(70, 95)  # 下雨/雪天湿度高
        else:
            humidity = random.randint(40, 75)
            
        wind_speed = round(random.uniform(1.0, 6.0), 1)
        
        forecast_item = {
            'date': forecast_date.strftime('%Y-%m-%d'),
            'time': '12:00',
            'temperature': int(new_temp),
            'description': new_weather,
            'icon': icon,
            'humidity': humidity,
            'wind_speed': wind_speed,
        }
        
        forecast['forecast'].append(forecast_item)
    
    return forecast

def map_weather_to_icon(weather_type):
    """
    将中文天气现象映射为OpenWeatherMap图标代码
    """
    weather_icon_map = {
        '晴': '01d',
        '多云': '02d',
        '阴': '03d',
        '阵雨': '09d',
        '雷阵雨': '11d',
        '小雨': '10d',
        '中雨': '10d',
        '大雨': '10d',
        '暴雨': '10d',
        '雨夹雪': '13d',
        '小雪': '13d',
        '中雪': '13d',
        '大雪': '13d',
        '暴雪': '13d',
        '雾': '50d',
        '霾': '50d'
    }
    
    # 默认图标
    default_icon = '01d'
    
    # 搜索最匹配的天气类型
    for key in weather_icon_map:
        if key in weather_type:
            return weather_icon_map[key]
            
    return default_icon 