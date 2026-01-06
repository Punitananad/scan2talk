"""
Interaction URL patterns.
"""
from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    # Interaction logs
    path('api/<uuid:gateway_id>/logs/', views.InteractionLogListAPIView.as_view(), name='logs_api'),
    path('api/logs/<uuid:pk>/', views.InteractionLogDetailAPIView.as_view(), name='log_detail_api'),
    
    # Interaction sessions
    path('api/<uuid:gateway_id>/sessions/', views.InteractionSessionListAPIView.as_view(), name='sessions_api'),
    
    # Feedback
    path('api/logs/<uuid:interaction_id>/feedback/', views.InteractionFeedbackAPIView.as_view(), name='feedback_api'),
    
    # Analytics and stats
    path('api/<uuid:gateway_id>/stats/', views.interaction_stats, name='stats_api'),
    path('api/<uuid:gateway_id>/analytics/', views.interaction_analytics, name='analytics_api'),
    path('api/<uuid:gateway_id>/recent/', views.recent_interactions, name='recent_api'),
    
    # Actions
    path('api/logs/<uuid:interaction_id>/block-source/', views.block_interaction_source, name='block_source_api'),
    path('api/cleanup-sessions/', views.cleanup_expired_sessions, name='cleanup_sessions_api'),
]