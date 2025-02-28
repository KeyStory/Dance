import re
import requests
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from dance.models_folder import AppUser
from datetime import date


class UserService:
    @staticmethod
    def check_username(username):
        """检查用户名是否存在"""
        return AppUser.objects.filter(username=username).exists()

    @staticmethod
    def verify_recaptcha(token):
        """验证 reCAPTCHA token"""
        try:
            response = requests.post('https://www.google.com/recaptcha/api/siteverify', {
                'secret': settings.RECAPTCHA_SECRET_KEY,
                'response': token
            })
            result = response.json()
            return result.get('success', False)
        except Exception as e:
            print(f"reCAPTCHA verification error: {e}")
            return False

    @staticmethod
    def register(data):
        """注册新用户"""
        try:
            # 提取所有字段
            username = data.get('username')
            password = data.get('password')
            email = data.get('email')
            birthday = data.get('birthday')
            job = data.get('job')
            
            # 1. 检查必填字段是否存在
            if not all([username, password, email]):
                raise ValueError("Username, password and email are required fields")
                
            # 2. 检查用户名格式和唯一性
            # 用户名格式验证（示例：只允许字母、数字和下划线）
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                raise ValueError("Username can only contain letters, numbers and underscores")
                
            # 检查用户名唯一性
            if AppUser.objects.filter(username=username).exists():
                raise ValueError("Username already exists")
                
            # 3. 密码强度验证 (使用Django内置验证器)
            validate_password(password)
            
            # 4. 邮箱格式和唯一性验证
            # 邮箱格式验证
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, email):
                raise ValueError("Invalid email format")
                
            # 检查邮箱唯一性
            if AppUser.objects.filter(email=email).exists():
                raise ValueError("Email already registered")
                
            # 5. 生日验证
            if birthday:
                # 确保生日不是未来日期
                if birthday > date.today():
                    raise ValueError("Birthday cannot be a future date")
                    
                # 确保年龄在合理范围内
                age = (date.today() - birthday).days // 365
                if age > 70 or age < 7:
                    raise ValueError("Age must be between 7 and 70 years")
            
            if job == "":
                job = "director"

            # 所有验证通过后创建用户
            user = AppUser.objects.create_user(
                username=username,
                password=password,
                email=email,
                birthday=birthday,
                job=job
            )
            return user
            
        except ValidationError as e:
            # 这是密码验证错误
            raise ValueError(f"Password validation failed: {', '.join(e.messages)}")
        except IntegrityError as e:
            # 数据库唯一性约束错误
            raise ValueError(f"Database integrity error: {str(e)}")
        except Exception as e:
            raise Exception(f"User registration failed: {str(e)}")

    @staticmethod
    def update_password(user, current_password, new_password):
        """更新用户密码"""
        try:
            # 验证当前密码
            if not user.check_password(current_password):
                raise Exception("Current password is incorrect")

            # 验证新密码长度
            if len(new_password) < 8:
                raise Exception("Password must be at least 8 characters")

            # 验证密码复杂度
            if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$', new_password):
                raise Exception("Password must contain letters and numbers")

            # 设置新密码
            user.set_password(new_password)
            user.save()

            return True
        except Exception as e:
            raise Exception(f"密码更新失败: {str(e)}")

    @staticmethod
    def update_personal_info(user, data):
        """更新用户个人信息"""
        try:
            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.save()
            return user
        except Exception as e:
            raise Exception(f"Personal information update failed: {str(e)}")