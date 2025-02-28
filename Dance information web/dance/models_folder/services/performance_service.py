from django.db import transaction
from django.db.models import F
from django.utils.dateparse import parse_date, parse_time
from dance.models_folder import Performance, Artist, PerformanceParticipant

class PerformanceService:
    @staticmethod
    def get_all_performances():
        """获取所有表演信息"""
        return Performance.objects.all().values()
    
    @staticmethod
    def get_performance(performance_id):
        """根据id获取表演信息"""
        return Performance.objects.get(performance_id=performance_id)

    @staticmethod
    def create_performance(title, performance_date, start_time, end_time, venue, status):
        """创建新的表演记录"""
        try:
            performance = Performance.objects.create(
                title=title,
                performance_date=performance_date,
                start_time=start_time,
                end_time=end_time,
                venue=venue,
                participants_number=0,
                status=status
            )
            return performance
        except Exception as e:
            raise Exception(f"Failed to create show: {str(e)}")

    @staticmethod
    def delete_performance(performance_id):
        """删除表演记录"""
        try:
            Performance.objects.filter(performance_id=performance_id).delete()
        except Exception as e:
            raise Exception(f"Failed to delete show: {str(e)}")

    @staticmethod
    def get_performance_detail(performance_id):
        """获取表演详情"""
        try:
            performance = Performance.objects.select_related().get(performance_id=performance_id)
            participants = Artist.objects.filter(performances=performance).select_related().values()
            existing_artist_ids = participants.values_list('artist_id', flat=True)
            available_artists = Artist.objects.exclude(artist_id__in=existing_artist_ids).values()
            
            return {
                'performance': performance,
                'participants': participants,
                'available_artists': available_artists
            }
        except Performance.DoesNotExist:
            raise Exception("The show doesn't exist")
        except Exception as e:
            raise Exception(f"Failed to obtain performance details: {str(e)}")

    @staticmethod
    def update_performance(performance_id, data, new_participant_ids):
        """更新表演信息及参与者"""
        try:
            with transaction.atomic():
                performance = Performance.objects.get(performance_id=performance_id)
                
                # 更新基本信息
                performance.title = data.get('title')
                performance.performance_date = parse_date(data.get('performance_date'))
                performance.start_time = parse_time(data.get('start_time'))
                performance.end_time = parse_time(data.get('end_time'))
                performance.venue = data.get('venue')
                performance.status = data.get('status')
                performance.participants_number = len(new_participant_ids)
                performance.save()

                # 更新参与者
                current_participant_ids = list(performance.participants.values_list('artist_id', flat=True))
                new_participant_ids = list(map(int, new_participant_ids))

                # 删除不再参与的人员
                to_remove = [id for id in current_participant_ids if id not in new_participant_ids]
                if to_remove:
                    PerformanceParticipant.objects.filter(
                        performance=performance, 
                        artist_id__in=to_remove
                    ).delete()

                # 添加新参与者
                to_add = [id for id in new_participant_ids if id not in current_participant_ids]
                if to_add:
                    new_participants = [
                        PerformanceParticipant(
                            performance=performance,
                            artist_id=artist_id,
                            role='artist'
                        ) for artist_id in to_add
                    ]
                    PerformanceParticipant.objects.bulk_create(new_participants)

                return performance

        except Performance.DoesNotExist:
            raise Exception("The show doesn't exist")
        except Exception as e:
            raise Exception(f"Failed to update performance information: {str(e)}")

    @staticmethod
    def get_performances_by_date(start_date, end_date, artist_id=None):
        """获取日期范围内的表演"""
        try:
            performances = Performance.objects.filter(
                performance_date__range=(start_date, end_date)
            ).values()

            if artist_id:
                artist_performances = PerformanceParticipant.objects.filter(
                    artist_id=artist_id,
                    performance__performance_date__range=(start_date, end_date)
                ).values_list('performance_id', flat=True)

                for performance in performances:
                    performance['attendance'] = performance['performance_id'] in artist_performances

            return performances
        except Exception as e:
            raise Exception(f"Failed to obtain the performance list: {str(e)}")