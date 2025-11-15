from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework import viewsets, generics, status, permissions, filters as drf_filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from .models import User, Passenger
from .serializers import (
    UserSerializer, 
    UserRegistrationSerializer, 
    UserUpdateSerializer,
    PasswordChangeSerializer, 
    PassengerSerializer
)
from .permissions import IsOwnerOrAdmin, IsPassengerOwnerOrAdmin, IsAdminUser
from .filters import PassengerFilter
from django.http import HttpResponse
import base64
from django.core.files.base import ContentFile
import os


class UserRegistrationView(generics.CreateAPIView):
    """用户注册视图"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class UserLoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            serializer = UserSerializer(user, context={'request': request})
            return Response({
                'token': token.key,
                'user': serializer.data
            })
        return Response(
            {"error": "用户名或密码不正确"}, 
            status=status.HTTP_400_BAD_REQUEST
        )


class UserLogoutView(APIView):
    """用户登出视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # 删除用户token
            request.user.auth_token.delete()
            return Response({"success": "成功登出"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """用户个人信息视图"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_object(self):
        return self.request.user
        
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    def handle_exception(self, exc):
        # 优化未授权错误的处理
        if isinstance(exc, permissions.exceptions.NotAuthenticated):
            return Response(
                {"error": "您需要登录才能访问此内容", "code": "not_authenticated"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().handle_exception(exc)


class UserProfileUpdateView(generics.UpdateAPIView):
    """用户信息更新视图"""
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # 处理base64编码的头像
        avatar_data = request.data.get('avatar')
        if avatar_data and isinstance(avatar_data, str) and avatar_data.startswith('data:image'):
            # 从base64字符串中提取文件格式和数据
            format, imgstr = avatar_data.split(';base64,')
            ext = format.split('/')[-1]
            
            # 为头像生成文件名
            avatar_filename = f"avatar_{instance.id}.{ext}"
            
            # 删除旧头像
            if instance.avatar:
                if os.path.isfile(instance.avatar.path):
                    os.remove(instance.avatar.path)
            
            # 创建新头像文件
            data = ContentFile(base64.b64decode(imgstr), name=avatar_filename)
            instance.avatar = data
            instance.save(update_fields=['avatar'])
        
        # 创建一个不包含avatar的数据副本进行序列化，而不是直接修改request.data
        data_for_serializer = {}
        for key, value in request.data.items():
            if key != 'avatar':  # 跳过头像字段
                data_for_serializer[key] = value
        
        serializer = self.get_serializer(instance, data=data_for_serializer, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
            
        return Response(UserSerializer(instance, context={'request': request}).data)


class ChangePasswordView(generics.UpdateAPIView):
    """密码修改视图"""
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
        
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # 检查旧密码
            if not user.check_password(serializer.data.get('old_password')):
                return Response({"old_password": ["旧密码不正确"]}, 
                               status=status.HTTP_400_BAD_REQUEST)
                               
            # 设置新密码
            user.set_password(serializer.data.get('new_password'))
            user.save()
            
            # 更新token
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)
            
            return Response({
                'token': token.key,
                'message': '密码修改成功'
            }, status=status.HTTP_200_OK)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PassengerViewSet(viewsets.ModelViewSet):
    """乘客信息视图集"""
    serializer_class = PassengerSerializer
    permission_classes = [IsAuthenticated, IsPassengerOwnerOrAdmin]
    filter_backends = [drf_filters.SearchFilter]
    filterset_class = PassengerFilter
    search_fields = ['name', 'id_card', 'passport_number']
    
    def get_queryset(self):
        user = self.request.user
        # 管理员可以查看所有乘客信息
        if user.role == 'admin':
            return Passenger.objects.all()
        # 普通用户只能查看自己的乘客信息
        return Passenger.objects.filter(user=user)
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def export_csv(self, request):
        import csv
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="passengers.csv"'
        writer = csv.writer(response)
        writer.writerow(['id','user','name','id_card','passport_number','gender','birth_date','created_at','updated_at'])
        for p in self.get_queryset():
            writer.writerow([p.id, p.user.id, p.name, p.id_card, p.passport_number, p.gender, p.birth_date, p.created_at, p.updated_at])
        return response

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def import_csv(self, request):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': '请上传 CSV 文件'}, status=status.HTTP_400_BAD_REQUEST)
        import csv, io
        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        created = updated = 0
        for row in reader:
            try:
                user = User.objects.get(id=row['user'])
            except:
                continue
            obj, created_flag = Passenger.objects.update_or_create(
                id_card=row['id_card'],
                defaults={
                    'user': user,
                    'name': row['name'],
                    'passport_number': row['passport_number'],
                    'gender': row['gender'],
                    'birth_date': row['birth_date'],
                }
            )
            if created_flag:
                created += 1
            else:
                updated += 1
        return Response({'created': created, 'updated': updated})


class UserManagementViewSet(viewsets.ModelViewSet):
    """用户管理视图集（仅限管理员）"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """用户统计信息"""
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        admin_users = User.objects.filter(role='admin').count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'admin_users': admin_users
        })
