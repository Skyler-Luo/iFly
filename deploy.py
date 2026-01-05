#!/usr/bin/env python3
"""
iFly项目部署脚本
用于自动化部署前后端项目
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """运行系统命令"""
    print(f"执行命令: {command}")
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, check=True, capture_output=True, text=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def deploy_frontend():
    """部署前端项目"""
    print("🚀 开始部署前端项目...")
    
    frontend_dir = Path("ifly_web")
    if not frontend_dir.exists():
        print("❌ 前端目录不存在!")
        return False
    
    # 安装依赖
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    # 构建项目
    if not run_command("npm run build", cwd=frontend_dir):
        return False
    
    print("✅ 前端项目构建完成!")
    return True

def deploy_backend():
    """部署后端项目"""
    print("🚀 开始部署后端项目...")
    
    # 检查requirements.txt文件
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt文件不存在!")
        return False
    
    # 安装Python依赖
    if not run_command("pip install -r requirements.txt"):
        return False
    
    # 数据库迁移
    if not run_command("python manage.py migrate"):
        return False
    
    # 收集静态文件
    if not run_command("python manage.py collectstatic --noinput"):
        return False
    
    print("✅ 后端项目部署完成!")
    return True

def check_environment():
    """检查环境变量"""
    print("🔍 检查环境配置...")
    
    required_env_vars = [
        'SECRET_KEY',
        'ALLOWED_HOSTS',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD',
    ]
    
    missing_vars = []
    for var in required_env_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少环境变量: {', '.join(missing_vars)}")
        print("请设置这些环境变量后再进行部署")
        return False
    
    print("✅ 环境变量检查通过!")
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("🎯 iFly项目自动化部署脚本")
    print("=" * 50)
    
    # 检查环境
    if len(sys.argv) > 1 and sys.argv[1] == '--production':
        print("🏭 生产环境部署模式")
        if not check_environment():
            sys.exit(1)
        os.environ['DJANGO_SETTINGS_MODULE'] = 'iFly.settings_production'
    else:
        print("🧪 开发环境部署模式")
    
    # 部署后端
    if not deploy_backend():
        print("❌ 后端部署失败!")
        sys.exit(1)
    
    # 部署前端
    if not deploy_frontend():
        print("❌ 前端部署失败!")
        sys.exit(1)
    
    print("=" * 50)
    print("🎉 项目部署完成!")
    print("🌐 前端访问地址: http://localhost:8080")
    print("🔧 后端API地址: http://localhost:8000/api/")
    print("📚 API文档地址: http://localhost:8000/api/docs/")
    print("=" * 50)

if __name__ == "__main__":
    main()
