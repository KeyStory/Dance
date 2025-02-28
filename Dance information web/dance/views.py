from django.contrib import messages
from django.forms import ValidationError
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import F, Count
from django.utils.dateparse import parse_date, parse_time
from django.conf import settings
from datetime import date
from dance.models_folder import Artist, Performance, Training, PerformanceParticipant, TrainingParticipant
from dance.models_folder.services.artist_service import ArtistService
from dance.models_folder.services.performance_service import PerformanceService
from dance.models_folder.services.training_service import TrainingService
from dance.models_folder.services.user_service import UserService
import json


# 主页
def home(request):
    return render(request, "dance/home.html")

# 注册页面
def sign_up(request):
    context = {
        'recaptcha_site_key': settings.RECAPTCHA_SITE_KEY
    }
    return render(request, "dance/sign_up.html", context)

# 检查注册的用户名有没有重复
@require_http_methods(["GET"])
def check_username(request):
    username = request.GET.get('username', '')
    exists = UserService.check_username(username)
    return JsonResponse({'exists': exists})

# 注册流程
@require_http_methods(["POST"])
def register(request):
    try:
        web_data = json.loads(request.body)

        # 验证 reCAPTCHA
        recaptcha_token = web_data.get('g-recaptcha-response')
        if not recaptcha_token:
            return JsonResponse({
                'success': False,
                'message': 'Please complete the reCAPTCHA verification'
            })
        
        if not UserService.verify_recaptcha(recaptcha_token):
            return JsonResponse({
                'success': False,
                'message': 'reCAPTCHA verification failed'
            })
        
        birth_year = web_data.get('birth_year')
        birth_month = web_data.get('birth_month')
        birth_day = web_data.get('birth_day')
        
        # 检查是否所有生日字段都存在
        if all([birth_year, birth_month, birth_day]):
            try:
                birthday = date(
                    int(birth_year),
                    int(birth_month),
                    int(birth_day)
                )
            except (ValueError, TypeError):
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid date format'
                }, status=400)
        
        # 创建新用户数据
        user_data = {
            'username': web_data.get('username'),
            'password': web_data.get('password'),
            'email': web_data.get('email'),
            'birthday': birthday,
            'job': web_data.get('job')
        }
        UserService.register(user_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful'
        })
        
    except (ValueError, ValidationError, Exception) as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

# 登录页面
def app_users_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember', None)
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if remember_me:
                # 设置会话过期时间为2周
                request.session.set_expiry(1209600)  # 2周的秒数
            else:
                # 浏览器关闭即过期
                request.session.set_expiry(0)

            login(request, user)
            # 直接从用户对象获取job
            request.session['user_job'] = user.job
            return redirect('/')
        else:
            return render(request, 'dance/login_files/login.html', {
                'error_message': 'incorrect username or password'
            })

    return render(request, 'dance/login_files/login.html')

class CustomPasswordResetView(PasswordResetView):
    """自定义密码重置视图"""
    template_name = 'dance/login_files/password_reset_form.html'
    email_template_name = 'dance/login_files/password_reset_email.html'
    subject_template_name = 'dance/login_files/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetDoneView(PasswordResetDoneView):
    """密码重置邮件发送完成视图"""
    template_name = 'dance/login_files/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """密码重置确认视图"""
    template_name = 'dance/login_files/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """密码重置完成视图"""
    template_name = 'dance/login_files/password_reset_complete.html'

# 用户退出登录
def app_users_logout(request):
    logout(request)
    request.session.flush()
    return render(request, 'dance/home.html')

# 用户更改密码
@login_required
@require_http_methods(["POST"])
def change_password(request):
    try:
        data = json.loads(request.body)
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        user = request.user
        
        update_result = UserService.update_password(user=user, current_password=current_password, new_password=new_password)
        
        # 更新会话，避免用户被登出
        update_session_auth_hash(request, user)
        
        return JsonResponse({
            'success': True,
            'message': 'Password updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error updating password: {str(e)}'
        }, status=400)

# 舞蹈团队管理平台
@login_required
def dashboard(request):
    artist_count = Artist.objects.count()
    performance_count = Performance.objects.count()
    training_count = Training.objects.count()
    artists_with_performance_count = Artist.objects.annotate(performance_count=Count('performances')).values('name', 'performance_count')
    artists_with_training_count = Artist.objects.annotate(training_count=Count('trainings')).values('name', 'training_count')

    performances_attendance = []
    for artist in artists_with_performance_count:
        percent = artist['performance_count']/Performance.objects.count()*100
        percent_num = float(f"{percent:.2f}")
        performances_attendance.append({'name': artist['name'], 'percent': percent_num})

    context = {'artist_count': artist_count,
               'performance_count': performance_count,
               'training_count': training_count,
               'artists_with_performance_count': artists_with_performance_count,
               'artists_with_training_count': artists_with_training_count,
               'performances_attendance': performances_attendance}
    return render(request, "dance/dashboard.html", context)

# 用户设置
@login_required
def user_settings(request):
    return render(request, "dance/user_settings.html")

# 更新用户信息
@login_required
@require_http_methods(["POST"])
def update_personal_info(request):
    try:
        data = json.loads(request.body)
        user_data = {
            'new_username': data.get('username'),
            'new_email': data.get('email')
        }
        UserService.update_personal_info(request.user, user_data)

        return JsonResponse({
            'success': True,
            'message': 'Personal information updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

# 展示所有艺人信息的页面
@login_required
def artists_info(request):
    try:
        edit_mode = request.GET.get('edit') == 'true'
        artists = ArtistService.get_all_artists()
        context = {'artists': artists, 
               'edit_mode': edit_mode}
        return render(request, 'dance/artists_info.html', context)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('dashboard')

# 保存新建的艺人信息
@login_required
@require_http_methods(["POST"])
def save_artist(request):
    try:
        data = request.POST
        artist = ArtistService.create_artist(
            name=data.get('name'),
            date_of_birth=parse_date(data.get('date_of_birth')),
            gender=data.get('gender'),
            email=data.get('email', ''),
            phone=data.get('phone', '')
        )
        return JsonResponse({
            'status': 'success',
            'message': 'New artist added successfully!'
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': f'Save failed: {str(e)}'})

# 根据id删除指定艺人记录
@login_required
@require_http_methods(["POST"])
def delete_artist(request, artist_id):
    try:
        ArtistService.delete_artist(artist_id)
        return JsonResponse({
                'status': 'success',
                'message': 'Artist deleted successfully!'
            })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Delete failed: {str(e)}'
        })

# 根据id获取特定艺人的资料
@login_required
def artist_detail(request, artist_id):
    # 获取特定的艺人记录
    artist = ArtistService.get_artist_detail(artist_id)
    
    # 检查是否处于编辑模式
    edit_mode = request.GET.get('edit') == 'true'
    
    # 处理编辑表单的提交
    if request.method == 'POST':
        try:
            data = {
                'name': request.POST.get('name'),
                'date_of_birth': parse_date(request.POST.get('date_of_birth')),
                'gender': request.POST.get('gender'),
                'email': request.POST.get('email'),
                'phone': request.POST.get('phone')
            }

            ArtistService.update_artist(artist_id, data)
            # 重定向到非编辑模式的详情页
            return HttpResponseRedirect(reverse('artist_detail', args=[str(artist_id)]))
        
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Search failed: {str(e)}'
            })
    
    # 渲染模板
    context = {
        'artist': artist,
        'edit_mode': edit_mode,
        'artist_id_json': artist_id
    }
    
    return render(request, 'dance/artist_detail.html', context)

# 获取指定日期范围内所有表演的信息
@login_required
def get_performances_by_date(request, artist_id):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    # 获取所有在日期范围内的演出
    performances = PerformanceService.get_performances_by_date(start_date, end_date)
    
    # 获取艺术家参与的演出ID列表
    artist_performances = PerformanceParticipant.objects.filter(
        artist_id=artist_id,
        performance__performance_date__range=(start_date, end_date)
    ).values_list('performance_id', flat=True)
    
    # 添加出勤信息
    for performance in performances:
        performance['attendance'] = 1 if performance['performance_id'] in artist_performances else 0
    
    return JsonResponse(list(performances), safe=False)

# 根据id获取指定表演的信息
@login_required
def get_performance_detail(request, performance_id):
    performance = PerformanceService.get_performance(performance_id)
    
    if performance:
        # 获取参与者信息
        participants = PerformanceParticipant.objects.filter(
            performance_id=performance_id
        ).values_list('artist_id', flat=True)
        performance['attendance'] = 1 if participants else 0
    
    return JsonResponse(performance, safe=False)

# 更新艺人在指定表演的出勤状态
@login_required
@require_http_methods(["POST"])
def update_performance_attendance(request, performance_id):
    data = json.loads(request.body)
    artist_id = data.get('artist_id')
    attendance = data.get('attendance')
    selected_performance = PerformanceService.get_performance(performance_id)
    
    if attendance:
        # 添加参与者
        PerformanceParticipant.objects.get_or_create(
            performance_id=performance_id,
            artist_id=artist_id,
            role= 'artist',
            attendance= 'Present'
        )
        selected_performance.participants_number += 1
    else:
        # 移除参与者
        PerformanceParticipant.objects.filter(
            performance=selected_performance,
            artist_id=artist_id
        ).delete()
        selected_performance.participants_number -= 1
    
    selected_performance.save()
    return JsonResponse({'success': True})

# 获取指定日期范围内的训练记录
@login_required
def get_trainings_by_date(request, artist_id):
    start_date = request.GET.get('start')
    end_date = request.GET.get('end')
    
    # 获取所有在日期范围内的训练
    trainings = TrainingService.get_trainings_by_date(start_date, end_date)
    
    # 获取艺术家参与的训练ID列表
    artist_trainings = TrainingParticipant.objects.filter(
        artist_id=artist_id,
        training__training_date__range=(start_date, end_date)
    ).values_list('training_id', flat=True)
    
    # 添加出勤信息
    for training in trainings:
        training['attendance'] = 1 if training['training_id'] in artist_trainings else 0
    
    return JsonResponse(list(trainings), safe=False)

# 根据id获取指定训练的信息
@login_required
def get_training_detail(request, training_id):
    training = TrainingService.get_training(training_id)
    
    if training:
        # 获取参与者信息
        participants = TrainingParticipant.objects.filter(
            training_id=training_id
        ).values_list('artist_id', flat=True)
        training['attendance'] = 1 if participants else 0
    
    return JsonResponse(training, safe=False)

# 更新艺人在指定表训练的出勤状态
@login_required
@require_http_methods(["POST"])
def update_training_attendance(request, training_id):
    data = json.loads(request.body)
    artist_id = data.get('artist_id')
    attendance = data.get('attendance')
    selected_training = TrainingService.get_training(training_id)
    
    if attendance:
        # 添加参与者
        TrainingParticipant.objects.get_or_create(
            training_id=training_id,
            artist_id=artist_id,
            defaults={
                'attendance': 'Present',  # 默认出勤状态为Present
                'body_status': 'Healthy'  # 默认身体状态为Healthy
            }
        )
        selected_training.participants_number += 1
    else:
        # 移除参与者
        TrainingParticipant.objects.filter(
            training_id=selected_training,
            artist_id=artist_id
        ).delete()
        selected_training.participants_number -= 1
    selected_training.save()
    return JsonResponse({'success': True})

# 展示所有表演信息的页面
@login_required
def performances(request):
    try:
        edit_mode = request.GET.get('edit') == 'true'
        performances = PerformanceService.get_all_performances()
        context = {'performances': performances, 
                   'edit_mode': edit_mode}
        return render(request, 'dance/performance.html', context)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('dashboard')

# 保存新建表演的信息
@login_required
@require_http_methods(["POST"])
def save_performance(request):
    try:
        title = request.POST.get('title')
        performance_date = parse_date(request.POST.get('performance_date'))
        start_time = parse_time(request.POST.get('start_time'))
        end_time = parse_time(request.POST.get('end_time'))
        venue = request.POST.get('venue')
        status = request.POST.get('status')
        PerformanceService.create_performance(title=title,performance_date=performance_date, 
                                              start_time=start_time, end_time=end_time, venue=venue, status=status)
        
        return JsonResponse({
            'status': 'success',
            'message': 'New performace was added successfully!'
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Save failed: {str(e)}'
        })

# 根据id删除指定表演记录
@login_required
@require_http_methods(["POST"])
def delete_performance(request, performance_id):
    try:
        PerformanceService.delete_performance(performance_id)
        return JsonResponse({
            'status': 'success',
            'message': 'performance deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Delete failed: {str(e)}'
        })

# 根据id获取指定表演信息的页面
@login_required
def performance_detail(request, performance_id):
    try:
        # 获取表演详情及其相关参与者
        performance = Performance.objects.select_related().get(performance_id=performance_id)
        
        # 获取该表演的所有参与者
        participants = Artist.objects.filter(performances=performance).select_related().values()
        
        
        # 获取未参与该表演的艺术家
        existing_artist_ids = participants.values_list('artist_id', flat=True)
        available_artists = Artist.objects.exclude(artist_id__in=existing_artist_ids).values()
        
        # 检查是否处于编辑模式
        edit_mode = request.GET.get('edit') == 'true'
        
        # 处理编辑表单的提交
        if request.method == 'POST':
            try:
                with transaction.atomic():  # 使用事务确保数据一致性
                    # 更新表演信息
                    performance_data = {
                        'title': request.POST.get('title'),
                        'performance_date': request.POST.get('date'),
                        'start_time': request.POST.get('start_time'),
                        'end_time': request.POST.get('end_time'),
                        'venue': request.POST.get('venue'),
                        'status': request.POST.get('status')
                    }
                    new_participant_ids = json.loads(request.POST.get('participants_ids', '[]'))
                    PerformanceService.update_performance(performance_id=performance_id, data=performance_data, new_participant_ids=new_participant_ids)
                    
                return HttpResponseRedirect(reverse('performance_detail', args=[performance_id]))
                
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('performance_detail', args=[performance_id]))
                
        context = {
            'performance': performance,
            'participants': participants,
            'available_artists': available_artists,
            'edit_mode': edit_mode,
        }
        
        return render(request, 'dance/performance_detail.html', context)

    except Exception as e:
        messages.error(request, str(e))
        return HttpResponseRedirect(reverse('performance_detail', args=[performance_id]))

# 展示所有训练信息的页面
@login_required
def trainings(request):
    try:
        edit_mode = request.GET.get('edit') == 'true'
        trainings = TrainingService.get_all_trainings()
        context = {'trainings': trainings, 
                   'edit_mode': edit_mode}
        return render(request, 'dance/trainings.html', context)
    except Exception as e:
        messages.error(request, str(e))
        return redirect('dashboard')

# 保存新建的训练信息
@login_required
@require_http_methods(["POST"])
def save_training(request):
    try:
        title = request.POST.get('title')
        training_date = parse_date(request.POST.get('training_date'))
        start_time = parse_time(request.POST.get('start_time'))
        end_time = parse_time(request.POST.get('end_time'))
        venue = request.POST.get('venue')
        status = request.POST.get('status')
        TrainingService.create_training(title=title, training_date=training_date, start_time=start_time, end_time=end_time, venue=venue, status=status)
        
        return JsonResponse({
            'status': 'success',
            'message': 'New performace was added successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Save failed: {str(e)}'
        })

# 根据id删除指定训练记录
@login_required
@require_http_methods(["POST"])
def delete_training(request, training_id):
    try:
        TrainingService.delete_training(training_id)
        return JsonResponse({
            'status': 'success',
            'message': 'training deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Delete failed: {str(e)}'
        })
    
# 根据id获取特定的训练信息的页面
@login_required
def training_detail(request, training_id):
    try:
        # 获取训练详情
        training = Training.objects.get(training_id=training_id)
        
        # 获取该训练的所有参与者
        participants = Artist.objects.filter(trainings=training).select_related('trainingparticipant').values('artist_id', 'name', 'age', 
                        'gender', 'phone', body_status=F('trainingparticipant__body_status'))
        
        # 获取未参与该训练的艺术家
        existing_artist_ids = participants.values_list('artist_id', flat=True)
        available_artists = Artist.objects.exclude(artist_id__in=existing_artist_ids).values()
        
        # 检查是否处于编辑模式
        edit_mode = request.GET.get('edit') == 'true'
        
        # 处理编辑表单的提交
        if request.method == 'POST':
            try:
                with transaction.atomic():
                    # 更新训练信息
                    training_data = {
                        'title':request.POST.get('title'),
                        'training_date': request.POST.get('date'),
                        'start_time': request.POST.get('start_time'),
                        'end_time': request.POST.get('end_time'),
                        'venue': request.POST.get('venue'),
                        'status': request.POST.get('status')
                    }
                    new_participant_ids = json.loads(request.POST.get('participants_ids', '[]'))
                    participants_body_status = json.loads(request.POST.get('participants_body_status', '[]'))
                    
                    TrainingService.update_training(training_id=training_id, data=training_data, 
                                                    new_participant_ids=new_participant_ids, participants_body_status=participants_body_status)
                
                return HttpResponseRedirect(reverse('training_detail', args=[training_id]))
            
            except Exception as e:
                print(e)
                return HttpResponseRedirect(reverse('training_detail', args=[training_id]))
        
        context = {
            'training': training,
            'participants': participants,
            'available_artists': available_artists,
            'edit_mode': edit_mode,
        }
        
        return render(request, 'dance/training_detail.html', context)
        
    except Exception as e:
        messages.error(request, str(e))
        return HttpResponseRedirect(reverse('training_detail', args=[training_id]))

# 活动页面
@login_required
def activities(request):
    return render(request, 'dance/activities.html')

# 设置页面
@login_required
def settings_page(request):
    return render(request, 'dance/settings.html')