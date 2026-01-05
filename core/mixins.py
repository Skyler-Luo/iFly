"""
通用混入类，用于消除重复代码
"""
from rest_framework import permissions


class AdminOrOwnerQuerySetMixin:
    """
    混入类：根据用户角色过滤查询集
    管理员可以查看所有数据，普通用户只能查看自己的数据
    """
    
    def get_queryset(self):
        user = self.request.user
        queryset = super().get_queryset()
        
        # 管理员可以查看所有数据
        if hasattr(user, 'role') and user.role == 'admin':
            return queryset
            
        # 普通用户根据具体模型的用户字段过滤
        return self.filter_user_queryset(queryset, user)
    
    def filter_user_queryset(self, queryset, user):
        """
        子类需要重写此方法来定义用户过滤逻辑
        """
        raise NotImplementedError("子类必须实现 filter_user_queryset 方法")


class UserOwnedQuerySetMixin(AdminOrOwnerQuerySetMixin):
    """
    混入类：用于直接关联到用户的模型
    """
    
    def filter_user_queryset(self, queryset, user):
        return queryset.filter(user=user)


class OrderOwnedQuerySetMixin(AdminOrOwnerQuerySetMixin):
    """
    混入类：用于通过订单关联到用户的模型
    """
    
    def filter_user_queryset(self, queryset, user):
        return queryset.filter(order__user=user)


class TicketOwnedQuerySetMixin(AdminOrOwnerQuerySetMixin):
    """
    混入类：用于通过工单关联到用户的模型
    """
    
    def filter_user_queryset(self, queryset, user):
        return queryset.filter(ticket__user=user)


class AccountOwnedQuerySetMixin(AdminOrOwnerQuerySetMixin):
    """
    混入类：用于通过账户关联到用户的模型
    """
    
    def filter_user_queryset(self, queryset, user):
        return queryset.filter(account__user=user)


class RoleBasedPermissionMixin:
    """
    混入类：基于角色的权限控制
    """
    
    def get_permissions(self):
        """
        根据操作设置权限
        可以在子类中重写 get_action_permissions 方法来自定义权限
        """
        action_permissions = self.get_action_permissions()
        
        if self.action in action_permissions:
            permission_classes = action_permissions[self.action]
        else:
            permission_classes = getattr(self, 'permission_classes', [permissions.IsAuthenticated])
            
        return [permission() for permission in permission_classes]
    
    def get_action_permissions(self):
        """
        子类可以重写此方法来定义不同操作的权限
        返回格式: {'action_name': [permission_class1, permission_class2]}
        """
        return {}


class StandardListMixin:
    """
    混入类：标准化list方法，确保返回格式正确
    """
    
    def list(self, request, *args, **kwargs):
        """重写list方法，确保返回格式正确的数据"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class BulkActionMixin:
    """
    混入类：批量操作功能
    """
    
    def get_bulk_queryset(self, ids):
        """获取批量操作的查询集"""
        return self.get_queryset().filter(id__in=ids)
    
    def perform_bulk_delete(self, queryset):
        """执行批量删除"""
        count = queryset.count()
        queryset.delete()
        return count
    
    def perform_bulk_update(self, queryset, validated_data):
        """执行批量更新"""
        return queryset.update(**validated_data)
