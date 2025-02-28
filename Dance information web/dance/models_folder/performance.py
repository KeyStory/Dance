from django.db import models, connection
from django.http import JsonResponse


class PerformanceManager(models.Manager):
    def get_all_details(self):
        sql_select = """
            SELECT performance_id, title, performance_date, start_time, end_time, venue, participants_number, status 
            FROM performances 
            ORDER BY performance_date ASC, start_time DESC
        """
        performances_details = self.raw(sql_select)
        performances = []
        for details in performances_details:
            performances.append({
                'performance_id': details.performance_id,
                'title': details.title,
                'performance_date': details.performance_date,
                'start_time': details.start_time,
                'end_time': details.end_time,
                'venue': details.venue,
                'participants_number': details.participants_number,
                'status': details.status
            })
        return performances

    def update_details(self, details):
        try:
            with connection.cursor() as cursor:
                sql_update = """
                    UPDATE performances
                    SET title = %s, performance_date = %s, start_time = %s, end_time = %s, participants_number = %s
                    WHERE performance_id = %s
                """
                cursor.execute(sql_update, details)
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Save failed: {str(e)}'
            })

class Performance(models.Model):
    performance_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True)
    performance_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=50)
    participants_number = models.IntegerField()
    status = models.CharField(
        max_length=10,
        choices=[
            ('Com', 'Completed'),
            ('Can', 'Cancel'),
            ('Oth', 'Other')
        ]
    )
    participants = models.ManyToManyField(
        'dance.Artist',
        through='PerformanceParticipant',
        related_name='performances'
    )
    
    class Meta:
        db_table = 'performances'

    # 使用自定义管理器
    objects = PerformanceManager()

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def performance(title, performance_date, start_time, end_time, venue, participants_number, status):
        try:
            Performance.objects.create(title=title, performance_date=performance_date, start_time=start_time, end_time=end_time,
                venue=venue, participants_number=participants_number, status=status)
            return True
        except Exception as e:
            return False
        