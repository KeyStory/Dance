from datetime import date
from django.db import transaction
from django.db.models import F, Count
from dance.models_folder import Artist, Performance, Training, PerformanceParticipant, TrainingParticipant

class ArtistService:
    @staticmethod
    def get_all_artists():
        """获取所有艺人信息"""
        return Artist.objects.all().values()
    
    @staticmethod
    def create_artist(name, date_of_birth, gender, email='', phone=''):
        try:
            today = date.today()
            age = today.year - date_of_birth.year - (
                    (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
                )
            
            artist = Artist.objects.create(
                name=name,
                date_of_birth=date_of_birth,
                gender=gender,
                age = age,
                email=email,
                phone=phone
            )
            return artist
        except Exception as e:
            raise Exception(f"Failed to create artist: {str(e)}")

    @staticmethod 
    def delete_artist(artist_id):
        """删除艺人"""
        try:
            Artist.objects.filter(artist_id=artist_id).delete()
        except Exception as e:
            raise Exception(f"Failed to delete artist: {str(e)}")

    @staticmethod
    def get_artist_detail(artist_id):
        """获取艺人详细信息"""
        artist = Artist.objects.filter(artist_id=artist_id).values().first()
        if not artist:
            raise Exception("Artist does not exist")
        return artist

    @staticmethod
    def update_artist(artist_id, data):
        try:
            artist = Artist.objects.get(artist_id=artist_id)
            artist.name = data.get('name', artist.name)
            date_of_birth = data.get('date_of_birth', artist.date_of_birth)
            today = date.today()
            age = today.year - date_of_birth.year - (
                    (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
                )
            artist.date_of_birth = date_of_birth
            artist.age = age
            artist.gender = data.get('gender', artist.gender)
            artist.email = data.get('email', artist.email)
            artist.phone = data.get('phone', artist.phone)
            artist.save()
            return artist
        except Artist.DoesNotExist:
            raise Exception("Artist does not exist")
        except Exception as e:
            raise Exception(f"Failed to update artist information: {str(e)}")

    @staticmethod
    def get_performance_history(artist_id, start_date, end_date):
        """获取艺人的演出历史"""
        try:
            performances = Performance.objects.filter(
                performanceparticipant__artist_id=artist_id,
                performance_date__range=(start_date, end_date)
            ).values()
            return performances
        except Exception as e:
            raise Exception(f"Failed to obtain performance history: {str(e)}")

    @staticmethod
    def get_training_history(artist_id, start_date, end_date):
        """获取艺人的训练历史"""
        try:
            trainings = Training.objects.filter(
                trainingparticipant__artist_id=artist_id,
                training_date__range=(start_date, end_date)
            ).values()
            return trainings
        except Exception as e:
            raise Exception(f"Failed to obtain training history: {str(e)}")

    @staticmethod
    def update_performance_attendance(artist_id, performance_id, attendance):
        """更新艺人演出出勤状态"""
        try:
            with transaction.atomic():
                performance = Performance.objects.get(performance_id=performance_id)
                if attendance:
                    # 添加出勤记录
                    PerformanceParticipant.objects.get_or_create(
                        performance_id=performance_id,
                        artist_id=artist_id,
                        defaults={
                            'role': 'artist',
                            'attendance': 'Present'
                        }
                    )
                    performance.participants_number = F('participants_number') + 1
                else:
                    # 删除出勤记录
                    PerformanceParticipant.objects.filter(
                        performance_id=performance_id,
                        artist_id=artist_id
                    ).delete()
                    performance.participants_number = F('participants_number') - 1
                performance.save()
        except Performance.DoesNotExist:
            raise Exception("Performance record does not exist")
        except Exception as e:
            raise Exception(f"Update attendance status failed: {str(e)}")

    @staticmethod
    def update_training_attendance(artist_id, training_id, attendance, body_status='Healthy'):
        """更新艺人训练出勤状态"""
        try:
            with transaction.atomic():
                if attendance:
                    TrainingParticipant.objects.get_or_create(
                        training_id=training_id,
                        artist_id=artist_id,
                        defaults={
                            'attendance': 'Present',
                            'body_status': body_status
                        }
                    )
                else:
                    TrainingParticipant.objects.filter(
                        training_id=training_id,
                        artist_id=artist_id
                    ).delete()
        except Exception as e:
            raise Exception(f"Failed to update training attendance status: {str(e)}")

    @staticmethod
    def get_performance_stats(artist_id):
        """获取艺人的演出统计信息"""
        try:
            total_performances = PerformanceParticipant.objects.filter(
                artist_id=artist_id
            ).count()
            return {
                'total_performances': total_performances
            }
        except Exception as e:
            raise Exception(f"Failed to obtain performance statistics: {str(e)}")