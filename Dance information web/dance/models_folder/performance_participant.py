from django.db import models, connection
from django.http import JsonResponse


class PerformanceParticipant(models.Model):
    performance = models.ForeignKey(
        'dance.Performance', 
        on_delete=models.CASCADE,
        db_column='performance_id'
    )
    artist = models.ForeignKey(
        'dance.Artist', 
        on_delete=models.CASCADE,
        db_column='artist_id'
    )
    role = models.CharField(max_length=50)
    attendance = models.CharField(
        max_length=10,
        choices=[
            ('P', 'Present'),
            ('A', 'Absent'),
            ('L', 'Late')
        ],
        default='Present'
    )

    class Meta:
        db_table = 'performance_participants'
        unique_together = ('performance', 'artist')

    def performanceParticipant(performance, artist, role, attendence="Present"):
        performance=performance
        artist=artist
        role = role
        attendence = attendence
