from django.db import models
from django.contrib.auth.models import AbstractUser

class AppUser(AbstractUser):
    avatar = models.ImageField(
        upload_to='avatars/',  # 会上传到 MEDIA_ROOT/avatars/ 目录
        null=True,
        blank=True,
        default='media/avatars/default_user.jpg'  # 默认头像
    )
    phone = models.CharField(max_length=20, null=True, blank=True)
    birthday = models.DateField(null=True, blank=True, verbose_name='birthday')
    job = models.CharField(max_length=100, blank=True, verbose_name='job')

    class Meta:
        db_table = 'app_users'
        verbose_name = 'app_user'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username