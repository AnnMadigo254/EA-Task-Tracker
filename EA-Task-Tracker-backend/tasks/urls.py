"""
EA Task Tracker - URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

# API Router
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'boards', views.BoardViewSet)
router.register(r'columns', views.ColumnViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'task-history', views.TaskHistoryViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'attachments', views.AttachmentViewSet)
router.register(r'reports', views.ReportViewSet)
router.register(r'notifications', views.NotificationViewSet)


urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # JWT Authentication
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API
    path('api/', include(router.urls)),
    
    # DRF browsable API auth
    path('api-auth/', include('rest_framework.urls')),
]