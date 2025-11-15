from .models import SystemLog
from django.urls import is_valid_path
from django.utils import timezone
import json
import logging
from django.http import JsonResponse
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

class SystemLogMiddleware:
    """中间件：记录用户的关键操作日志"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 在请求到达视图前，先保存一份请求体数据的副本
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # 跳过admin路径的日志记录，避免与admin视图冲突
            if request.path.startswith('/admin/'):
                return self.get_response(request)

            try:
                # 安全地获取请求体，可能会抛出异常
                request._body_copy = request.body
            except Exception:
                request._body_copy = b''

        # 继续处理请求
        response = self.get_response(request)

        # 仅记录已登录用户的写操作
        if (hasattr(request, 'user') and request.user.is_authenticated and 
                request.method in ['POST', 'PUT', 'PATCH', 'DELETE'] and
                not request.path.startswith('/admin/')):
            try:
                action = f"{request.method} {request.path}"
                detail = ''
                if hasattr(request, '_body_copy'):
                    detail = request._body_copy.decode('utf-8', errors='replace')
                ip = request.META.get('REMOTE_ADDR') or ''
                SystemLog.objects.create(
                    user=request.user,
                    action=action,
                    detail=detail,
                    ip_address=ip
                )
            except Exception as e:
                # 记录日志时发生错误不应阻止正常响应
                print(f"日志记录失败: {str(e)}")
                
        return response 

class CORSMiddleware:
    """
    处理跨域请求的中间件
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 处理预检请求
        if request.method == 'OPTIONS':
            response = JsonResponse({})
            # 允许的HTTP方法
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            # 允许的请求头
            response["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization, Cache-Control, Pragma"
            # 允许凭证
            response["Access-Control-Allow-Credentials"] = "true"
            # 允许所有来源
            response["Access-Control-Allow-Origin"] = request.headers.get('Origin', '*')
            # 预检请求的有效期（秒）
            response["Access-Control-Max-Age"] = "3600"
            return response
            
        response = self.get_response(request)
        
        # 为所有响应添加CORS头
        origin = request.headers.get('Origin')
        if origin:
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, PATCH, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization, Cache-Control, Pragma"
        
        return response 