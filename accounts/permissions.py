from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    仅允许管理员用户访问
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    仅允许对象的所有者或管理员访问
    """
    def has_object_permission(self, request, view, obj):
        # 管理员具有完全访问权限
        if request.user.role == 'admin':
            return True
            
        # 检查对象的所有者
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user


class IsPassengerOwnerOrAdmin(permissions.BasePermission):
    """
    仅允许乘客信息的所有者或管理员访问
    """
    def has_object_permission(self, request, view, obj):
        # 管理员具有完全访问权限
        if request.user.role == 'admin':
            return True
            
        # 检查乘客信息的所有者
        return obj.user == request.user
