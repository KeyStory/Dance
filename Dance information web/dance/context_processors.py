def user_info(request):
    if request.user.is_authenticated:
        return {
            # 'user_avatar': request.user.avatar.url if request.user.avatar else '/static/dance/pictures/default_user.jpg',
            'user_name': request.user.username
        }
    return {}