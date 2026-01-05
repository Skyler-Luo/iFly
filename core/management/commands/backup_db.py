import os
import shutil
import datetime
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = '备份数据库'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            default='json',
            help='指定输出格式 (json 或 sql)',
        )

    def handle(self, *args, **options):
        # 创建备份文件夹
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 选择备份格式
        backup_format = options['format'].lower()
        
        if backup_format == 'json':
            # 使用 dumpdata 命令备份为 JSON
            filename = f'backup_{timestamp}.json'
            backup_file = os.path.join(backup_dir, filename)
            self.stdout.write(f'正在创建数据库备份: {backup_file}')
            
            with open(backup_file, 'w') as f:
                call_command('dumpdata', '--indent=4', stdout=f)
                
        elif backup_format == 'sql' or backup_format == 'file':
            # 直接复制 SQLite 文件
            db_file = settings.DATABASES['default']['NAME']
            filename = f'db_backup_{timestamp}.sqlite3'
            backup_file = os.path.join(backup_dir, filename)
            self.stdout.write(f'正在创建数据库文件备份: {backup_file}')
            
            shutil.copy2(db_file, backup_file)
        
        self.stdout.write(self.style.SUCCESS(f'备份完成: {backup_file}')) 