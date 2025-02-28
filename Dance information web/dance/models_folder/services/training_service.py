from django.db import transaction
from django.db.models import F
from django.utils.dateparse import parse_date, parse_time
from dance.models_folder import Training, Artist, TrainingParticipant

class TrainingService:
    @staticmethod
    def get_all_trainings():
        """获取所有训练信息"""
        return Training.objects.all()
    
    @staticmethod
    def get_training(training_id):
        """根据id获取表演信息"""
        return Training.objects.get(training_id=training_id)

    @staticmethod
    def create_training(title, training_date, start_time, end_time, venue, status):
        """创建新的训练记录"""
        try:
            training = Training.objects.create(
                title=title,
                training_date=training_date,
                start_time=start_time,
                end_time=end_time,
                venue=venue,
                participants_number=0,
                status=status
            )
            return training
        except Exception as e:
            raise Exception(f"Failed to create training: {str(e)}")

    @staticmethod
    def delete_training(training_id):
        """删除训练记录"""
        try:
            Training.objects.filter(training_id=training_id).delete()
        except Exception as e:
            raise Exception(f"Deleting training failed: {str(e)}")

    @staticmethod
    def get_training_detail(training_id):
        """获取训练详情"""
        try:
            training = Training.objects.get(training_id=training_id)
            participants = Artist.objects.filter(
                trainings=training
            ).select_related('trainingparticipant').values(
                'artist_id', 'name', 'age', 'gender', 'phone',
                body_status=F('trainingparticipant__body_status')
            )
            
            existing_artist_ids = participants.values_list('artist_id', flat=True)
            available_artists = Artist.objects.exclude(
                artist_id__in=existing_artist_ids
            ).values()
            
            return {
                'training': training,
                'participants': participants,
                'available_artists': available_artists
            }
        except Training.DoesNotExist:
            raise Exception("Training does not exist")
        except Exception as e:
            raise Exception(f"Failed to obtain training details: {str(e)}")

    @staticmethod
    def update_training(training_id, data, new_participant_ids, participants_body_status):
        """更新训练信息及参与者"""
        try:
            with transaction.atomic():
                training = Training.objects.get(training_id=training_id)
                
                # 更新基本信息
                training.title = data.get('title')
                training.training_date = parse_date(data.get('training_date'))
                training.start_time = parse_time(data.get('start_time'))
                training.end_time = parse_time(data.get('end_time'))
                training.venue = data.get('venue')
                training.status = data.get('status')
                training.participants_number = len(new_participant_ids)
                training.save()

                # 更新参与者
                current_participant_ids = list(training.participants.values_list('artist_id', flat=True))
                new_participant_ids = list(map(int, new_participant_ids))

                # 删除不再参与的人员
                to_remove = [id for id in current_participant_ids if id not in new_participant_ids]
                if to_remove:
                    TrainingParticipant.objects.filter(
                        training=training,
                        artist_id__in=to_remove
                    ).delete()

                # 添加新参与者
                to_add = [id for id in new_participant_ids if id not in current_participant_ids]
                if to_add:
                    new_participants = [
                        TrainingParticipant(
                            training=training,
                            artist_id=artist_id,
                            body_status='Healthy'
                        ) for artist_id in to_add
                    ]
                    TrainingParticipant.objects.bulk_create(new_participants)

                # 更新身体状态
                for artist_id, body_status in zip(new_participant_ids, participants_body_status):
                    TrainingParticipant.objects.filter(
                        training=training,
                        artist_id=artist_id
                    ).update(body_status=body_status)

                return training

        except Training.DoesNotExist:
            raise Exception("Training does not exist")
        except Exception as e:
            raise Exception(f"Failed to update training information: {str(e)}")

    @staticmethod
    def get_trainings_by_date(start_date, end_date, artist_id=None):
        """获取日期范围内的训练"""
        try:
            trainings = Training.objects.filter(
                training_date__range=(start_date, end_date)
            ).values()

            if artist_id:
                artist_trainings = TrainingParticipant.objects.filter(
                    artist_id=artist_id,
                    training__training_date__range=(start_date, end_date)
                ).values_list('training_id', flat=True)

                for training in trainings:
                    training['attendance'] = training['training_id'] in artist_trainings

            return trainings
        except Exception as e:
            raise Exception(f"Failed to obtain training information: {str(e)}")