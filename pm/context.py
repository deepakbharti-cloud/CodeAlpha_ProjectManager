def unread(request):
    return {'unread': request.user.notifications.filter(read=False).count() if request.user.is_authenticated else 0}
