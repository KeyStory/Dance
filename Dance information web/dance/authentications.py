from django.contrib.auth.backends import BaseBackend
from django.db import connection
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password

class XamppDatabaseBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):

        # 连接到数据库并检查凭据
        with connection.cursor() as cursor:
            # 首先确认该用户是否存在
            cursor.execute("""
                SELECT username, password 
                FROM app_users 
                WHERE username = %s
            """, [username])
            
            user = cursor.fetchone()
            
            if user is None:
                # 用户名不存在时
                return None
            
            # 使用 check_password 来验证密码
            stored_password = user[1]  # 数据库中的哈希密码
            if not check_password(password, stored_password): 
                return None
            
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # 创建一个新的Django用户
                user = User(username=username)
                user.save()
            return user
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
