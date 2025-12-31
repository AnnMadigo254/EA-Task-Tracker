# """
# EA Task Tracker - URL Configuration
# """
# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from rest_framework.routers import DefaultRouter
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from drf_yasg.views import get_schema_view
# from drf_yasg import openapi
# from rest_framework import permissions

# from tasks import views  # Fixed: import from tasks app, not from current module

# # API Documentation
# schema_view = get_schema_view(
#     openapi.Info(
#         title="EA Task Tracker API",
#         default_version='v1',
#         description="Enterprise Architecture Task Management System",
#         contact=openapi.Contact(email="ea-team@coopbank.co.ke"),
#     ),
#     public=True,
#     permission_classes=(permissions.AllowAny,),
# )

# # API Router
# router = DefaultRouter()
# router.register(r'users', views.UserViewSet, basename='user')
# router.register(r'boards', views.BoardViewSet, basename='board')
# router.register(r'columns', views.ColumnViewSet, basename='column')
# router.register(r'tasks', views.TaskViewSet, basename='task')
# router.register(r'task-history', views.TaskHistoryViewSet, basename='taskhistory')
# router.register(r'comments', views.CommentViewSet, basename='comment')
# router.register(r'attachments', views.AttachmentViewSet, basename='attachment')
# router.register(r'reports', views.ReportViewSet, basename='report')
# router.register(r'notifications', views.NotificationViewSet, basename='notification')

# urlpatterns = [
#     # Admin
#     path('admin/', admin.site.urls),
    
#     # API Documentation
#     path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
#     path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    
#     # JWT Authentication
#     path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
#     # API Endpoints
#     path('api/', include(router.urls)),
    
#     # DRF browsable API auth (for testing)
#     path('api-auth/', include('rest_framework.urls')),
# ]

# # Serve media files in development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# tasks/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API Router for all viewsets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'boards', views.BoardViewSet, basename='board')
router.register(r'columns', views.ColumnViewSet, basename='column')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'task-history', views.TaskHistoryViewSet, basename='taskhistory')
router.register(r'comments', views.CommentViewSet, basename='comment')
router.register(r'attachments', views.AttachmentViewSet, basename='attachment')
router.register(r'reports', views.ReportViewSet, basename='report')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('', include(router.urls)),
]