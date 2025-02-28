from django.db import models

class TrainingParticipant(models.Model):
    training = models.ForeignKey(
        'dance.Training', 
        on_delete=models.CASCADE,
        db_column='training_id'
    )
    artist = models.ForeignKey(
        'dance.Artist', 
        on_delete=models.CASCADE,
        db_column='artist_id'
    )
    attendance = models.CharField(
        max_length=10,
        choices=[
            ('P', 'Present'),
            ('A', 'Absent'),
            ('L', 'Late')
        ],
        default='P'
    )
    body_status = models.CharField(
        max_length=10,
        choices=[
            ('H', 'Healthy'),
            ('I', 'Injured'),
            ('S', 'Sick'),
            ('O', 'Other')
        ],
        default='H'
    )

    class Meta:
        db_table = 'training_participants'
        unique_together = ('training', 'artist')