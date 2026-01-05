# 机场和航空公司数据配置
# 此文件用于替换硬编码的机场和航空公司信息

# 机场信息配置
AIRPORT_DATA = {
    '北京': {
        'name': '首都国际机场',
        'code': 'PEK',
        'terminal': 'T2'
    },
    '上海': {
        'name': '浦东国际机场', 
        'code': 'PVG',
        'terminal': 'T1'
    },
    '广州': {
        'name': '白云国际机场',
        'code': 'CAN', 
        'terminal': 'T1'
    },
    '深圳': {
        'name': '宝安国际机场',
        'code': 'SZX',
        'terminal': 'T3'
    },
    '成都': {
        'name': '双流国际机场',
        'code': 'CTU',
        'terminal': 'T1'
    },
    '杭州': {
        'name': '萧山国际机场',
        'code': 'HGH',
        'terminal': 'T3'
    },
    '西安': {
        'name': '咸阳国际机场',
        'code': 'XIY',
        'terminal': 'T2'
    },
    '重庆': {
        'name': '江北国际机场',
        'code': 'CKG',
        'terminal': 'T2'
    },
    '南京': {
        'name': '禄口国际机场',
        'code': 'NKG',
        'terminal': 'T2'
    },
    '武汉': {
        'name': '天河国际机场',
        'code': 'WUH',
        'terminal': 'T2'
    }
}

# 航空公司信息配置
AIRLINE_DATA = {
    '中国国际航空': {
        'code': 'CA',
        'logo_url': 'https://picsum.photos/id/10/200/200'
    },
    '东方航空': {
        'code': 'MU',
        'logo_url': 'https://picsum.photos/id/11/200/200'
    },
    '南方航空': {
        'code': 'CZ',
        'logo_url': 'https://picsum.photos/id/12/200/200'
    },
    '海南航空': {
        'code': 'HU',
        'logo_url': 'https://picsum.photos/id/13/200/200'
    },
    '四川航空': {
        'code': '3U',
        'logo_url': 'https://picsum.photos/id/14/200/200'
    },
    '厦门航空': {
        'code': 'MF',
        'logo_url': 'https://picsum.photos/id/15/200/200'
    }
}

def get_airport_info(city_name):
    """根据城市名获取机场信息"""
    return AIRPORT_DATA.get(city_name, {
        'name': f"{city_name}机场",
        'code': city_name[:3].upper(),
        'terminal': 'T1'
    })

def get_airline_info(airline_name):
    """根据航空公司名获取航空公司信息"""
    return AIRLINE_DATA.get(airline_name, {
        'code': 'XX',
        'logo_url': 'https://picsum.photos/id/10/200/200'
    })
