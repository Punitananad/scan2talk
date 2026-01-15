"""
Gateway URL patterns.
"""
from django.urls import path
from . import views
from . import qr_views
from . import qr_download_views
from . import call_masking_views

app_name = 'gateways'

urlpatterns = [
    # QR Code Management (Admin)
    path('gqr/', qr_views.generate_qr_codes, name='generate_qr'),
    path('qr/dashboard/', qr_views.qr_dashboard, name='qr_dashboard'),
    path('qr/batch/<str:batch_number>/preview-page/', qr_views.batch_preview_page, name='batch_preview_page'),
    path('qr/category/<uuid:category_id>/', qr_views.category_users_view, name='category_users'),
    path('qr/registrations/', qr_views.registrations_page, name='registrations'),
    path('qr/<uuid:qr_id>/details/', qr_views.qr_detail, name='qr_detail'),
    path('qr/<uuid:qr_id>/deregister/', qr_views.deregister_qr, name='deregister_qr'),
    path('qr/<uuid:qr_id>/activate-for-user/', qr_views.activate_qr_for_user, name='activate_qr_for_user'),
    path('qr/<uuid:qr_id>/delete/', qr_views.delete_qr, name='delete_qr'),
    path('qr/delete-all/', qr_views.delete_all_qr, name='delete_all_qr'),
    path('qr/batch/<str:batch_number>/delete/', qr_views.delete_batch, name='delete_batch'),
    
    # QR Code Downloads (Admin)
    path('qr/<uuid:qr_id>/download/', qr_download_views.download_qr_image, name='download_qr_image'),
    path('qr/<uuid:qr_id>/view/', qr_download_views.view_qr_image, name='view_qr_image'),
    path('qr/batch/<str:batch_number>/preview/', qr_download_views.preview_batch_sample, name='preview_batch_sample'),
    path('qr/batch/<str:batch_number>/download-pdf/', qr_download_views.download_batch_pdf, name='download_batch_pdf'),
    path('qr/batch/<str:batch_number>/download-zip/', qr_download_views.download_qr_zip, name='download_batch_zip'),
    
    # QR Code Activation (User)
    path('activate/<str:qr_code>/', qr_views.activate_qr_code, name='activate_qr'),
    path('activate/<str:qr_code>/resend-otp/', qr_views.resend_otp_view, name='resend_otp'),
    
    # Public QR Access
    path('g/<str:qr_code>/', qr_views.public_qr_access, name='public_qr_access'),
    
    # Call Masking
    path('call/<str:qr_code>/', call_masking_views.generate_masked_call_url, name='generate_masked_call'),
    path('call/<str:qr_code>/info/', call_masking_views.get_call_info, name='get_call_info'),
    
    # QR API Endpoints
    path('api/qr/generate/', qr_views.api_generate_qr_batch, name='api_generate_qr'),
    path('api/qr/my/', qr_views.api_my_qr_codes, name='api_my_qr_codes'),
    path('api/qr/activate/<str:qr_code>/', qr_views.api_activate_qr, name='api_activate_qr'),
    
    # Web views
    path('', views.GatewayListView.as_view(), name='list'),
    path('<uuid:gateway_id>/', views.GatewayDetailView.as_view(), name='detail'),
    
    # API endpoints
    path('api/', views.GatewayListAPIView.as_view(), name='list_api'),
    path('api/<uuid:pk>/', views.GatewayDetailAPIView.as_view(), name='detail_api'),
    path('api/<uuid:gateway_id>/settings/', views.GatewaySettingsAPIView.as_view(), name='settings_api'),
    path('api/<uuid:gateway_id>/analytics/', views.gateway_analytics, name='analytics_api'),
    
    # Entry point endpoints
    path('api/<uuid:gateway_id>/entry-points/', views.EntryPointListAPIView.as_view(), name='entry_points_api'),
    path('api/entry-points/<uuid:pk>/', views.EntryPointDetailAPIView.as_view(), name='entry_point_detail_api'),
    path('api/entry-points/<uuid:entry_point_id>/regenerate/', views.regenerate_entry_point, name='regenerate_entry_point'),
]