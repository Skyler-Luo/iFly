from django.db.models.signals import post_save
from django.dispatch import receiver
from django.apps import apps
from django.conf import settings
from .models import User


@receiver(post_save, sender=User)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    """
    为新创建的用户自动生成认证令牌
    """
    if created:
        try:
            # 检查rest_framework.authtoken是否在INSTALLED_APPS中
            if 'rest_framework.authtoken' in settings.INSTALLED_APPS:
                # 动态导入Token模型，避免直接依赖
                Token = apps.get_model('authtoken', 'Token')
                # 创建令牌
                Token.objects.create(user=instance)
        except Exception as e:
            # 记录错误但不中断流程
            print(f"创建Token时出错: {str(e)}") 