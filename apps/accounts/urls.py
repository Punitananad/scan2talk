"""
Account URL patterns.
"""
from django.urls import path
from . import views
from . import wallet_views
from . import admin_views
from .distributor_views import (
    become_distributor,
    become_distributor_verify,
    distributor_pending,
    distributor_dashboard,
    distributor_login
)

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
    
    # Razorpay routes
    path('wallet/razorpay/checkout/', wallet_views.razorpay_checkout, name='razorpay_checkout'),
    path('wallet/razorpay/success/', wallet_views.razorpay_payment_success, name='razorpay_payment_success'),
    path('wallet/razorpay/webhook/', wallet_views.razorpay_webhook, name='razorpay_webhook'),
    
    # Visitor payment routes (for prepaid QR codes)
    path('wallet/visitor-pay/<str:identifier>/', wallet_views.initiate_visitor_payment, name='initiate_visitor_payment'),
    path('wallet/visitor-pay/callback/', wallet_views.visitor_payment_callback, name='visitor_payment_callback'),
    path('wallet/visitor-pay/success/<str:order_id>/', wallet_views.visitor_payment_success, name='visitor_payment_success'),
    path('wallet/visitor-pay/failed/', wallet_views.visitor_payment_failed, name='visitor_payment_failed'),
    
    # Distributor payment routes (one-time activation payment)
    path('distributor-payment/<str:qr_code>/', wallet_views.distributor_payment, name='distributor_payment'),
    path('distributor-payment-callback/<str:qr_code>/', wallet_views.distributor_payment_callback, name='distributor_payment_callback'),
    
    # Distributor registration and dashboard
    path('distributor/become/', become_distributor, name='become_distributor'),
    path('distributor/verify/', become_distributor_verify, name='become_distributor_verify'),
    path('distributor/pending/', distributor_pending, name='distributor_pending'),
    path('distributor/dashboard/', distributor_dashboard, name='distributor_dashboard'),
    path('distributor/login/', distributor_login, name='distributor_login'),
    
    # Admin Super Dashboard
    path('admin/dashboard/', admin_views.admin_super_dashboard, name='admin_super_dashboard'),
    path('admin/categories/', admin_views.manage_categories, name='admin_manage_categories'),
    path('admin/plans/', admin_views.manage_plans, name='admin_manage_plans'),
    path('admin/qr-wallets/', admin_views.manage_qr_wallets, name='admin_manage_qr_wallets'),
    path('admin/qr-wallet/<uuid:wallet_id>/credit/', admin_views.admin_credit_qr_wallet, name='admin_credit_qr_wallet'),
    path('admin/qr-wallet/<uuid:wallet_id>/assign-category/', admin_views.admin_assign_category, name='admin_assign_category'),
    path('admin/qr-wallet/<uuid:wallet_id>/suspend/', admin_views.admin_suspend_wallet, name='admin_suspend_wallet'),
    path('admin/users/', admin_views.admin_user_management, name='admin_user_management'),
    path('admin/users/<uuid:user_id>/', admin_views.admin_user_profile, name='admin_user_profile'),
    path('admin/users/<uuid:user_id>/assign-category/', admin_views.admin_assign_user_category, name='admin_assign_user_category'),
    path('admin/users/<uuid:user_id>/add-balance/', admin_views.admin_add_user_balance, name='admin_add_user_balance'),
    path('admin/users/<uuid:user_id>/lock/', admin_views.admin_lock_user, name='admin_lock_user'),
    path('admin/users/<uuid:user_id>/unlock/', admin_views.admin_unlock_user, name='admin_unlock_user'),
    path('admin/orders/', admin_views.manage_tag_orders, name='manage_tag_orders'),
    path('admin/orders/<str:order_id>/', admin_views.order_detail_view, name='order_detail'),
    path('admin/orders/<str:order_id>/update/', admin_views.update_order_status, name='update_order_status'),
    
    # Distributor management
    path('admin/distributors/', admin_views.manage_distributors, name='admin_manage_distributors'),
    path('admin/distributors/<uuid:user_id>/verify/', admin_views.verify_distributor, name='verify_distributor'),
    path('admin/distributors/<uuid:user_id>/reset-password/', admin_views.reset_distributor_password, name='reset_distributor_password'),
    path('admin/distributors/<uuid:user_id>/revoke/', admin_views.revoke_distributor, name='revoke_distributor'),
    
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