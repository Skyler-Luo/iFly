"""
accounts 模块 - 用户认证与乘客管理

本模块包含用户认证相关的数据模型，包括自定义用户模型和乘客信息模型。
"""
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


# 身份证号码验证器
id_card_validator = RegexValidator(
    regex=(
        r'^[1-9]\d{5}'
        r'(18|19|20)\d{2}'
        r'((0[1-9])|(1[0-2]))'
        r'(([0-2][1-9])|10|20|30|31)'
        r'\d{3}[0-9Xx]$'
    ),
    message='身份证号码格式不正确'
)


class User(AbstractUser):
    """
    自定义用户模型，扩展 Django 默认用户模型。

    扩展字段包括：手机号、角色、头像、真实姓名、身份证号、性别、地址等。
    """

    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="accounts_user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="accounts_user_set",
        related_query_name="user",
    )

    phone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="联系电话"
    )
    role = models.CharField(
        max_length=20,
        default="user",
        choices=[
            ("user", "普通用户"),
            ("admin", "管理员"),
        ],
        verbose_name="用户角色"
    )
    created_at = models.DateTimeField(
        default=timezone.now, verbose_name="账户创建时间"
    )
    avatar = models.ImageField(
        upload_to='avatars/', null=True, blank=True, verbose_name="用户头像"
    )
    real_name = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="真实姓名"
    )
    id_card = models.CharField(
        max_length=18,
        blank=True,
        null=True,
        unique=True,
        validators=[id_card_validator],
        verbose_name="身份证号码"
    )
    gender = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=[
            ("male", "男"),
            ("female", "女"),
            ("other", "其他"),
        ],
        verbose_name="性别"
    )
    address = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="地址"
    )

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = "用户"

    def __str__(self):
        return self.username


class Passenger(models.Model):
    """
    乘客信息模型。

    存储用户关联的乘客信息，包括姓名、身份证号、护照号、性别、出生日期等。
    一个用户可以关联多个乘客（如家人、朋友）。
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="passengers",
        verbose_name="关联用户"
    )
    name = models.CharField(max_length=50, verbose_name="乘客姓名")
    id_card = models.CharField(
        max_length=18,
        unique=True,
        validators=[id_card_validator],
        verbose_name="身份证号码"
    )
    passport_number = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="护照号码"
    )
    gender = models.CharField(
        max_length=10,
        choices=[
            ("male", "男"),
            ("female", "女"),
            ("other", "其他"),
        ],
        verbose_name="性别"
    )
    birth_date = models.DateField(verbose_name="出生日期")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "乘客"
        verbose_name_plural = "乘客"

    def __str__(self):
        return f"{self.name} ({self.id_card[-4:]})"
