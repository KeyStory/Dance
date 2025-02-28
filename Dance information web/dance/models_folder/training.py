from django.db import models, connection
from django.http import JsonResponse


class TrainingManager(models.Manager):
    def get_all_details(self):
        sql_select = """
            SELECT training_id, title, training_date, start_time, end_time, venue, participants_number, status 
            FROM trainings 
            ORDER BY training_date ASC, start_time DESC
        """
        trainings_details = self.raw(sql_select)
        trainings = []
        for details in trainings_details:
            trainings.append({
                'training_id': details.training_id,
                'title': details.title,
                'training_date': details.training_date,
                'start_time': details.start_time,
                'end_time': details.end_time,
                'venue': details.venue,
                'participants_number': details.participants_number,
                'status': details.status
            })
        return trainings

    def update_details(self, details):
        try:
            with connection.cursor() as cursor:
                sql_update = """
                    UPDATE trainings
                    SET title = %s, training_date = %s, start_time = %s, end_time = %s, participants_number = %s
                    WHERE training_id = %s
                """
                cursor.execute(sql_update, details)
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Save failed: {str(e)}'
            })
        

class Training(models.Model):
    training_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, blank=True)
    training_date = models.DateField()
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
        through='TrainingParticipant',
        related_name='trainings'
    )
    
    class Meta:
        db_table = 'trainings'

    # 使用自定义管理器
    objects = TrainingManager()

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def training(title, training_date, start_time, end_time, venue, participants_number, status):
        try:
            Training.objects.create(title=title, training_date=training_date, start_time=start_time, end_time=end_time,
                venue=venue, participants_number=participants_number, status=status)
            return True
        except Exception as e:
            return False
