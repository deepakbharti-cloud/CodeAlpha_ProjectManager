from django.contrib import admin
from django.urls import path, include
from pm import views as v
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('register/', v.register, name='register'),
    path('', v.dashboard, name='dashboard'),
    path('project/<int:pk>/', v.board, name='board'),
    path('project/<int:pk>/member/', v.add_member, name='add_member'),
    path('project/<int:pk>/task/', v.add_task, name='add_task'),
    path('task/<int:pk>/', v.task, name='task'),
    path('notifications/', v.notifications, name='notifications'),
]
