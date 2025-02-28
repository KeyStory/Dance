from django.db import models, connection
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils import timezone
from datetime import date, datetime
from .performance_participant import PerformanceParticipant
from .training_participant import TrainingParticipant


class ArtistManager(models.Manager):
    def get_all_details(self):
        return self.all().values()
    
    def add_new_artist(self, details):
        try:
            new_date_of_birth = details[1]
            today = date.today()
            if not isinstance(new_date_of_birth, date):
                new_date_of_birth = datetime.strptime(new_date_of_birth, "%Y-%m-%d").date()
            
            new_age = today.year - new_date_of_birth.year - (
                (today.month, today.day) < (new_date_of_birth.month, new_date_of_birth.day)
            )
            details.insert(2, new_age)
            with connection.cursor() as cursor:
                sql = """
                    INSERT INTO artists (name, date_of_birth, age, gender, email, phone)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, details)
            
            return JsonResponse({
                'status': 'success',
                'message': 'New artist added successfully!'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Save failed: {str(e)}'
            })

class Artist(models.Model):
    artist_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField()
    age = models.IntegerField()
    gender = models.CharField(
        max_length=10,
        choices=[
            ('M', 'Male'),
            ('F', 'Female'),
            ('O', 'Other')
        ]
    )
    
    # 联系信息
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    class Meta:
        db_table = 'artists'

    # 使用自定义管理器
    objects = ArtistManager()
    def __str__(self):
        return self.name
    
    def clean(self):
        # 验证年龄是否在允许范围内
        if self.date_of_birth:
            age = (date.today() - self.date_of_birth).days // 365
            if age < 7:
                raise ValidationError('artist age must bigger than 6')
            if age > 70:
                raise ValidationError('artist age must smaller than 71')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def artist(name, date_of_birth, gender, email, phone):
        try:
            today = date.today()
            age = today.year - date_of_birth.year - (
                    (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
                )
            Artist.objects.create(name=name, date_of_birth=date_of_birth, age=age, gender=gender, email=email, phone=phone)
            return True
        except Exception as e:
            return False
