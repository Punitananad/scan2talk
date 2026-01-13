"""
Account URL patterns.
"""
from django.urls import path
from . import views
from . import wallet_views
from . import admin_views

app_name = 'accounts'

urlpatterns = [
    # ===== WEB VIEWS =====
    # Authentication
    path('login/', views.phone_login, name='phone_login'),
    path('logout/', views.logout_web, name='logout'),
    
    # User pages
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    
    # Wallet web views
    path('wallet/', wallet_views.wallet_dashboard, name='wallet_dashboard'),
    path('wallet/recharge/', wallet_views.recharge_wallet, name='recharge_wallet'),
    path('wallet/recharge/success/', wallet_views.recharge_success, name='recharge_success'),
    path('wallet/recharge/cancel/', wallet_views.recharge_cancel, name='recharge_cancel'),
    path('wallet/phonepe/callback/', wallet_views.phonepe_callback, name='phonepe_callback'),
    path('wallet/test-payment/<str:order_id>/', wallet_views.test_payment_page, name='test_payment_page'),
    path('wallet/test-payment/<str:order_id>/complete/', wallet_views.test_payment_complete, name='test_payment_complete'),
    
    # Visitor payment routes (for prepaid QR codes)
    path('wallet/visitor-pay/<str:identifier>/', wallet_views.initiate_visitor_payment, name='initiate_visitor_payment'),
    path('wallet/visitor-pay/callback/', wallet_views.visitor_payment_callback, name='visitor_payment_callback'),
    path('wallet/visitor-pay/success/<str:order_id>/', wallet_views.visitor_payment_success, name='visitor_payment_success'),
    path('wallet/visitor-pay/failed/', wallet_views.visitor_payment_failed, name='visitor_payment_failed'),
    
    # Admin Super Dashboard
    path('admin/dashboard/', admin_views.admin_super_dashboard, name='admin_super_dashboard'),
    path('admin/categories/', admin_views.manage_categories, name='admin_manage_categories'),
    path('admin/plans/', admin_views.manage_plans, name='admin_manage_plans'),
    path('admin/qr-wallets/', admin_views.manage_qr_wallets, name='admin_manage_qr_wallets'),
    path('admin/qr-wallet/<uuid:wallet_id>/credit/', admin_views.admin_credit_qr_wallet, name='admin_credit_qr_wallet'),
    path('admin/qr-wallet/<uuid:wallet_id>/assign-category/', admin_views.admin_assign_category, name='admin_assign_category'),
    path('admin/qr-wallet/<uuid:wallet_id>/suspend/', admin_views.admin_suspend_wallet, name='admin_suspend_wallet'),
    path('admin/users/', admin_views.admin_user_management, name='admin_user_management'),
    path('admin/orders/', admin_views.manage_tag_orders, name='manage_tag_orders'),
    path('admin/orders/<str:order_id>/update/', admin_views.update_order_status, name='update_order_status'),
    
    # ===== API ENDPOINTS =====
    # Authentication API
    path('api/register/', views.register_api, name='register_api'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/logout/', views.logout_api, name='logout_api'),
    path('api/profile/', views.UserProfileAPIView.as_view(), name='profile_api'),
    path('api/password/change/', views.PasswordChangeAPIView.as_view(), name='password_change_api'),
    
    # Wallet API endpoints
    path('api/wallet/balance/', wallet_views.WalletBalanceAPI.as_view(), name='wallet_balance_api'),
    path('api/wallet/transactions/', wallet_views.WalletTransactionsAPI.as_view(), name='wallet_transactions_api'),
    path('api/wallet/recharge/create/', wallet_views.CreateRechargeOrderAPI.as_view(), name='create_recharge_api'),
    path('api/wallet/recharge/callback/', wallet_views.recharge_callback, name='recharge_callback'),
    path('api/wallet/deduct-credit/', wallet_views.DeductCallCreditAPI.as_view(), name='deduct_credit_api'),
]