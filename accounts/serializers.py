from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Passenger


class PassengerSerializer(serializers.ModelSerializer):
    """乘客信息序列化器"""
    class Meta:
        model = Passenger
        fields = ['id', 'name', 'id_card', 'passport_number', 'gender', 'birth_date']
        read_only_fields = ['id']


class UserSerializer(serializers.ModelSerializer):
    """用户信息序列化器"""
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'role', 'date_joined', 'last_login', 
                 'avatar', 'avatar_url', 'real_name', 'id_card', 'gender', 'address']
        read_only_fields = ['id', 'date_joined', 'last_login']
        
    def get_avatar_url(self, obj):
        if obj.avatar and hasattr(obj.avatar, 'url'):
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
            return obj.avatar.url
        return None


class UserRegistrationSerializer(serializers.ModelSerializer):
    """用户注册序列化器"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2', 'email', 'phone']

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password2'):
            raise serializers.ValidationError({"password": "两次输入的密码不匹配"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data.get('phone', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户信息更新序列化器"""
    class Meta:
        model = User
        fields = ['email', 'phone', 'avatar', 'real_name', 'id_card', 'gender', 'address']
    
    def validate_id_card(self, value):
        """验证身份证号码格式"""
        import re
        if value and not re.match(r'(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)', value):
            raise serializers.ValidationError("无效的身份证号码格式")
        return value
    
    def validate_phone(self, value):
        """验证手机号码格式"""
        import re
        if value and not re.match(r'^1[3456789]\d{9}$', value):
            raise serializers.ValidationError("无效的手机号码格式")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """密码修改序列化器"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "两次输入的新密码不匹配"})
        return attrs
