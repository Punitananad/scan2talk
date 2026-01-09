"""
Admin Super Dashboard Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta

from .models import User
from .wallet_models import Wallet, WalletTransaction
from .recharge_models import (
    RechargeCategory, RechargePlan, QRWallet, QRWalletTransaction
)
from apps.gateways.qr_models import PreGeneratedQR, QRBatch
from apps.gateways.models import Gateway
from apps.interactions.models import InteractionLog


@staff_member_required
def admin_super_dashboard(request):
    """
    Super admin dashboard with complete system overview
    """
    # Time filters
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User Statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    new_users_today = User.objects.filter(created_at__date=today).count()
    new_users_week = User.objects.filter(created_at__date__gte=week_ago).count()
    
    # QR Statistics
    total_qr_codes = PreGeneratedQR.objects.count()
    activated_qr_codes = PreGeneratedQR.objects.filter(status='activated').count()
    available_qr_codes = PreGeneratedQR.objects.filter(status='available').count()
    
    # Wallet Statistics
    total_user_wallet_balance = Wallet.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0
    
    total_qr_wallet_balance = QRWallet.objects.aggregate(
        total=Sum('balance')
    )['total'] or 0
    
    total_message_credits = QRWallet.objects.aggregate(
        total=Sum('message_credits')
    )['total'] or 0
    
    total_call_minutes = QRWallet.objects.aggregate(
        total=Sum('call_minutes')
    )['total'] or 0
    
    # Revenue Statistics
    total_revenue = WalletTransaction.objects.filter(
        transaction_type='credit'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    revenue_today = WalletTransaction.objects.filter(
        transaction_type='credit',
        created_at__date=today
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    revenue_week = WalletTransaction.objects.filter(
        transaction_type='credit',
        created_at__date__gte=week_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    revenue_month = WalletTransaction.objects.filter(
        transaction_type='credit',
        created_at__date__gte=month_ago
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Interaction Statistics
    total_interactions = InteractionLog.objects.count()
    interactions_today = InteractionLog.objects.filter(created_at__date=today).count()
    interactions_week = InteractionLog.objects.filter(created_at__date__gte=week_ago).count()
    
    # Category Distribution
    category_stats = QRWallet.objects.values(
        'category__name', 'category__category_type'
    ).annotate(
        count=Count('id'),
        total_balance=Sum('balance')
    ).order_by('-count')
    
    # Recent Activities
    recent_activations = PreGeneratedQR.objects.filter(
        status='activated'
    ).select_related('owner', 'gateway').order_by('-activated_at')[:10]
    
    recent_transactions = WalletTransaction.objects.select_related(
        'wallet__user'
    ).order_by('-created_at')[:10]
    
    # Low balance QR codes
    low_balance_qrs = QRWallet.objects.filter(
        balance__lt=10,
        is_active=True,
        category__category_type='prepaid'
    ).select_related('qr_code', 'category')[:10]
    
    # Suspended wallets
    suspended_wallets = QRWallet.objects.filter(
        is_suspended=True
    ).select_related('qr_code')[:10]
    
    context = {
        # User stats
        'total_users': total_users,
        'active_users': active_users,
        'new_users_today': new_users_today,
        'new_users_week': new_users_week,
        
        # QR stats
        'total_qr_codes': total_qr_codes,
        'activated_qr_codes': activated_qr_codes,
        'available_qr_codes': available_qr_codes,
        
        # Wallet stats
        'total_user_wallet_balance': total_user_wallet_balance,
        'total_qr_wallet_balance': total_qr_wallet_balance,
        'total_message_credits': total_message_credits,
        'total_call_minutes': total_call_minutes,
        
        # Revenue stats
        'total_revenue': total_revenue,
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'revenue_month': revenue_month,
        
        # Interaction stats
        'total_interactions': total_interactions,
        'interactions_today': interactions_today,
        'interactions_week': interactions_week,
        
        # Detailed data
        'category_stats': category_stats,
        'recent_activations': recent_activations,
        'recent_transactions': recent_transactions,
        'low_balance_qrs': low_balance_qrs,
        'suspended_wallets': suspended_wallets,
    }
    
    return render(request, 'admin/super_dashboard.html', context)


@staff_member_required
def manage_categories(request):
    """Manage recharge categories"""
    categories = RechargeCategory.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            category = RechargeCategory.objects.create(
                name=request.POST.get('name'),
                category_type=request.POST.get('category_type'),
                description=request.POST.get('description', ''),
                free_messages_limit=int(request.POST.get('free_messages_limit', 0)),
                free_calls_limit=int(request.POST.get('free_calls_limit', 0)),
                message_cost=float(request.POST.get('message_cost', 0)),
                call_cost_per_minute=float(request.POST.get('call_cost_per_minute', 0)),
                color=request.POST.get('color', '#3B82F6'),
                icon=request.POST.get('icon', '💳'),
            )
            messages.success(request, f'Category "{category.name}" created successfully')
        
        elif action == 'update':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(RechargeCategory, id=category_id)
            category.name = request.POST.get('name')
            category.category_type = request.POST.get('category_type')
            category.description = request.POST.get('description', '')
            category.free_messages_limit = int(request.POST.get('free_messages_limit', 0))
            category.free_calls_limit = int(request.POST.get('free_calls_limit', 0))
            category.message_cost = float(request.POST.get('message_cost', 0))
            category.call_cost_per_minute = float(request.POST.get('call_cost_per_minute', 0))
            category.color = request.POST.get('color', '#3B82F6')
            category.icon = request.POST.get('icon', '💳')
            category.save()
            messages.success(request, f'Category "{category.name}" updated successfully')
        
        elif action == 'delete':
            category_id = request.POST.get('category_id')
            category = get_object_or_404(RechargeCategory, id=category_id)
            category.delete()
            messages.success(request, 'Category deleted successfully')
        
        return redirect('accounts:admin_manage_categories')
    
    context = {'categories': categories}
    return render(request, 'admin/manage_categories.html', context)


@staff_member_required
def manage_plans(request):
    """Manage recharge plans"""
    plans = RechargePlan.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            plan = RechargePlan.objects.create(
                name=request.POST.get('name'),
                description=request.POST.get('description', ''),
                amount=float(request.POST.get('amount')),
                message_credits=int(request.POST.get('message_credits', 0)),
                call_minutes=int(request.POST.get('call_minutes', 0)),
                validity_days=int(request.POST.get('validity_days', 30)),
                bonus_message_credits=int(request.POST.get('bonus_message_credits', 0)),
                bonus_call_minutes=int(request.POST.get('bonus_call_minutes', 0)),
                is_popular=request.POST.get('is_popular') == 'on',
                display_order=int(request.POST.get('display_order', 0)),
                color=request.POST.get('color', '#3B82F6'),
            )
            messages.success(request, f'Plan "{plan.name}" created successfully')
        
        elif action == 'update':
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(RechargePlan, id=plan_id)
            plan.name = request.POST.get('name')
            plan.description = request.POST.get('description', '')
            plan.amount = float(request.POST.get('amount'))
            plan.message_credits = int(request.POST.get('message_credits', 0))
            plan.call_minutes = int(request.POST.get('call_minutes', 0))
            plan.validity_days = int(request.POST.get('validity_days', 30))
            plan.bonus_message_credits = int(request.POST.get('bonus_message_credits', 0))
            plan.bonus_call_minutes = int(request.POST.get('bonus_call_minutes', 0))
            plan.is_popular = request.POST.get('is_popular') == 'on'
            plan.display_order = int(request.POST.get('display_order', 0))
            plan.color = request.POST.get('color', '#3B82F6')
            plan.save()
            messages.success(request, f'Plan "{plan.name}" updated successfully')
        
        elif action == 'delete':
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(RechargePlan, id=plan_id)
            plan.delete()
            messages.success(request, 'Plan deleted successfully')
        
        return redirect('accounts:admin_manage_plans')
    
    context = {'plans': plans}
    return render(request, 'admin/manage_plans.html', context)


@staff_member_required
def manage_qr_wallets(request):
    """Manage all QR wallets"""
    search = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    status_filter = request.GET.get('status', '')
    
    wallets = QRWallet.objects.select_related(
        'qr_code', 'category', 'qr_code__owner'
    ).all()
    
    if search:
        wallets = wallets.filter(
            Q(qr_code__qr_code__icontains=search) |
            Q(qr_code__owner__email__icontains=search)
        )
    
    if category_filter:
        wallets = wallets.filter(category_id=category_filter)
    
    if status_filter == 'active':
        wallets = wallets.filter(is_active=True, is_suspended=False)
    elif status_filter == 'suspended':
        wallets = wallets.filter(is_suspended=True)
    elif status_filter == 'low_balance':
        wallets = wallets.filter(balance__lt=10)
    
    categories = RechargeCategory.objects.all()
    
    context = {
        'wallets': wallets[:100],  # Limit for performance
        'categories': categories,
        'search': search,
        'category_filter': category_filter,
        'status_filter': status_filter,
    }
    return render(request, 'admin/manage_qr_wallets.html', context)


@staff_member_required
@require_http_methods(["POST"])
def admin_credit_qr_wallet(request, wallet_id):
    """Admin adds credits to QR wallet"""
    wallet = get_object_or_404(QRWallet, id=wallet_id)
    
    amount = float(request.POST.get('amount', 0))
    message_credits = int(request.POST.get('message_credits', 0))
    call_minutes = int(request.POST.get('call_minutes', 0))
    notes = request.POST.get('notes', '')
    
    # Add credits
    wallet.add_credits(
        message_credits=message_credits,
        call_minutes=call_minutes,
        amount=amount
    )
    
    # Create transaction
    QRWalletTransaction.objects.create(
        wallet=wallet,
        transaction_type='admin_credit',
        amount=amount,
        message_credits=message_credits,
        call_minutes=call_minutes,
        description=f'Admin credit by {request.user.email}',
        notes=notes,
        created_by=request.user
    )
    
    messages.success(request, f'Credits added to {wallet.qr_code.qr_code}')
    return redirect('accounts:admin_manage_qr_wallets')


@staff_member_required
@require_http_methods(["POST"])
def admin_assign_category(request, wallet_id):
    """Admin assigns category to QR wallet"""
    wallet = get_object_or_404(QRWallet, id=wallet_id)
    category_id = request.POST.get('category_id')
    
    if category_id:
        category = get_object_or_404(RechargeCategory, id=category_id)
        wallet.category = category
        wallet.save()
        messages.success(request, f'Category "{category.name}" assigned to {wallet.qr_code.qr_code}')
    else:
        wallet.category = None
        wallet.save()
        messages.success(request, f'Category removed from {wallet.qr_code.qr_code}')
    
    return redirect('accounts:admin_manage_qr_wallets')


@staff_member_required
@require_http_methods(["POST"])
def admin_suspend_wallet(request, wallet_id):
    """Admin suspends/unsuspends QR wallet"""
    wallet = get_object_or_404(QRWallet, id=wallet_id)
    
    action = request.POST.get('action')
    
    if action == 'suspend':
        wallet.is_suspended = True
        wallet.suspension_reason = request.POST.get('reason', 'Suspended by admin')
        wallet.save()
        messages.success(request, f'Wallet {wallet.qr_code.qr_code} suspended')
    elif action == 'unsuspend':
        wallet.is_suspended = False
        wallet.suspension_reason = ''
        wallet.save()
        messages.success(request, f'Wallet {wallet.qr_code.qr_code} unsuspended')
    
    return redirect('accounts:admin_manage_qr_wallets')


@staff_member_required
def admin_user_management(request):
    """Manage all users"""
    search = request.GET.get('search', '')
    
    users = User.objects.all()
    
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users = users.annotate(
        gateway_count=Count('gateways'),
        wallet_balance=F('wallet__balance')
    ).order_by('-created_at')[:100]
    
    context = {
        'users': users,
        'search': search,
    }
    return render(request, 'admin/user_management.html', context)
