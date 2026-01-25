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
    RechargeCategory, RechargePlan, QRWallet, QRWalletTransaction, DistributorPayment
)
from apps.gateways.qr_models import PreGeneratedQR, QRBatch
from apps.gateways.models import Gateway
from apps.interactions.models import InteractionLog
from apps.core.models import TagOrder


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
    
    # Tag Orders Statistics
    total_tag_orders = TagOrder.objects.count()
    pending_tag_orders = TagOrder.objects.filter(status='pending').count()
    
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
        
        # Tag Orders stats
        'total_tag_orders': total_tag_orders,
        'pending_tag_orders': pending_tag_orders,
        
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
                distributor_activation_fee=float(request.POST.get('distributor_activation_fee', 0)),
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
            category.distributor_activation_fee = float(request.POST.get('distributor_activation_fee', 0))
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
    """Manage all users - shows everyone who has logged in"""
    search = request.GET.get('search', '')
    
    # Get ALL users (whether they have vehicles/gateways or not)
    users = User.objects.all()
    
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(phone__icontains=search)
        )
    
    # Annotate with related counts and wallet balance
    # Note: Apply slice [:100] at the very end after all filters and annotations
    users = users.select_related('wallet').annotate(
        gateway_count=Count('gateways', filter=Q(gateways__is_active=True)),
        qr_count=Count('qr_codes', distinct=True),
        wallet_balance=F('wallet__balance')
    ).order_by('-created_at')[:100]
    
    context = {
        'users': users,
        'search': search,
        'total_users': User.objects.count(),
    }
    return render(request, 'admin/user_management.html', context)


@staff_member_required
def admin_user_profile(request, user_id):
    """
    Complete A-to-Z user profile view
    Shows everything about a user in one place
    """
    try:
        user = get_object_or_404(User, id=user_id)
        
        # Get all categories for the dropdown
        categories = RechargeCategory.objects.all()
        
        # Get all related data with error handling
        try:
            gateways = Gateway.objects.filter(owner=user).select_related().order_by('-created_at')
        except Exception as e:
            gateways = Gateway.objects.none()
            
        try:
            qr_codes = PreGeneratedQR.objects.filter(owner=user).select_related('gateway', 'category').order_by('-created_at')
        except Exception as e:
            qr_codes = PreGeneratedQR.objects.none()
        
        # Wallet data with error handling
        wallet = None
        wallet_transactions = []
        try:
            wallet = user.wallet
            wallet_transactions = WalletTransaction.objects.filter(
                wallet=wallet
            ).order_by('-created_at')[:20]
        except Exception as e:
            pass
        
        # QR Wallet data with error handling
        try:
            qr_wallets = QRWallet.objects.filter(
                qr_code__owner=user
            ).select_related('qr_code', 'category')
        except Exception as e:
            qr_wallets = QRWallet.objects.none()
        
        # Get user's primary category (from their QR codes)
        try:
            user_categories = qr_codes.filter(category__isnull=False).values_list('category__name', flat=True).distinct()
        except Exception as e:
            user_categories = []
        
        # Recharge orders with error handling
        try:
            from apps.core.models import TagOrder
            recharge_orders = TagOrder.objects.filter(
                email=user.email
            ).order_by('-created_at')[:10]
        except Exception as e:
            recharge_orders = []
        
        # Interaction logs with error handling
        try:
            interaction_logs = InteractionLog.objects.filter(
                gateway__owner=user
            ).select_related('gateway').order_by('-created_at')[:20]
        except Exception as e:
            interaction_logs = InteractionLog.objects.none()
        
        # Login attempts with error handling
        try:
            from .models import LoginAttempt
            login_attempts = LoginAttempt.objects.filter(
                email=user.email
            ).order_by('-created_at')[:20]
        except Exception as e:
            login_attempts = []
        
        # Statistics - calculate counts before slicing with error handling
        try:
            total_gateways = gateways.count()
            active_gateways = gateways.filter(is_active=True).count()
        except:
            total_gateways = 0
            active_gateways = 0
            
        try:
            total_qr_codes = qr_codes.count()
            activated_qr_codes = qr_codes.filter(status='activated').count()
            available_qr_codes = qr_codes.filter(status='available').count()
        except:
            total_qr_codes = 0
            activated_qr_codes = 0
            available_qr_codes = 0
            
        try:
            total_interactions = interaction_logs.count()
        except:
            total_interactions = 0
            
        try:
            total_orders = recharge_orders.count() if hasattr(recharge_orders, 'count') else len(recharge_orders)
        except:
            total_orders = 0
        
        # Calculate failed logins separately (before the slice)
        try:
            from .models import LoginAttempt
            failed_logins = LoginAttempt.objects.filter(
                email=user.email,
                success=False
            ).count()
        except:
            failed_logins = 0
        
        # Calculate wallet stats with error handling
        total_recharged = 0
        total_spent = 0
        if wallet:
            try:
                total_recharged = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type='credit'
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                total_spent = WalletTransaction.objects.filter(
                    wallet=wallet,
                    transaction_type='debit'
                ).aggregate(total=Sum('amount'))['total'] or 0
            except:
                pass
        
        stats = {
            'total_gateways': total_gateways,
            'active_gateways': active_gateways,
            'total_qr_codes': total_qr_codes,
            'activated_qr_codes': activated_qr_codes,
            'available_qr_codes': available_qr_codes,
            'total_interactions': total_interactions,
            'wallet_balance': wallet.balance if wallet else 0,
            'total_recharged': total_recharged,
            'total_spent': total_spent,
            'total_orders': total_orders,
            'failed_logins': failed_logins,
        }
        
        # QR Wallet totals with error handling
        try:
            qr_wallet_totals = qr_wallets.aggregate(
                total_balance=Sum('balance'),
                total_message_credits=Sum('message_credits'),
                total_call_minutes=Sum('call_minutes')
            )
        except:
            qr_wallet_totals = {
                'total_balance': 0,
                'total_message_credits': 0,
                'total_call_minutes': 0
            }
        
        context = {
            'profile_user': user,
            'categories': categories,
            'user_categories': list(user_categories),
            'gateways': gateways,
            'qr_codes': qr_codes,
            'wallet': wallet,
            'wallet_transactions': wallet_transactions,
            'qr_wallets': qr_wallets,
            'qr_wallet_totals': qr_wallet_totals,
            'recharge_orders': recharge_orders,
            'interaction_logs': interaction_logs,
            'login_attempts': login_attempts,
            'stats': stats,
        }
        
        return render(request, 'admin/user_profile.html', context)
        
    except Exception as e:
        messages.error(request, f'Error loading user profile: {str(e)}')
        return redirect('accounts:admin_user_management')


@staff_member_required
@require_http_methods(["POST"])
def admin_assign_user_category(request, user_id):
    """Assign category to all user's QR codes"""
    user = get_object_or_404(User, id=user_id)
    category_id = request.POST.get('category_id')
    
    if category_id:
        category = get_object_or_404(RechargeCategory, id=category_id)
        
        # Update all user's QR codes with this category
        qr_codes = PreGeneratedQR.objects.filter(owner=user)
        updated_count = qr_codes.update(category=category)
        
        # Also update QR wallets
        QRWallet.objects.filter(qr_code__owner=user).update(category=category)
        
        messages.success(request, f'Assigned category "{category.name}" to {updated_count} QR codes for user {user.email}')
    else:
        # Remove category from all QR codes
        qr_codes = PreGeneratedQR.objects.filter(owner=user)
        updated_count = qr_codes.update(category=None)
        
        messages.success(request, f'Removed category from {updated_count} QR codes for user {user.email}')
    
    return redirect('accounts:admin_user_profile', user_id=user_id)


@staff_member_required
@require_http_methods(["POST"])
def admin_add_user_balance(request, user_id):
    """Add balance to user's wallet"""
    try:
        from decimal import Decimal
        
        user = get_object_or_404(User, id=user_id)
        amount = Decimal(str(request.POST.get('amount', 0)))
        
        if amount > 0:
            try:
                wallet = user.wallet
            except:
                from .wallet_models import Wallet
                wallet = Wallet.objects.create(user=user, balance=Decimal('0'))
            
            # Add balance
            wallet.balance += amount
            wallet.save()
            
            # Create transaction record
            try:
                WalletTransaction.objects.create(
                    wallet=wallet,
                    transaction_type='credit',
                    amount=amount,
                    balance_after=wallet.balance,
                    description=f'Admin credit by {request.user.email}',
                    reference_id=f'ADMIN-{timezone.now().timestamp()}'
                )
            except Exception as e:
                # If transaction record fails, still show success for balance update
                pass
            
            messages.success(request, f'Added ₹{amount} to {user.email}\'s wallet. New balance: ₹{wallet.balance}')
        else:
            messages.error(request, 'Invalid amount')
    except Exception as e:
        messages.error(request, f'Error adding balance: {str(e)}')
    
    return redirect('accounts:admin_user_profile', user_id=user_id)



@staff_member_required
@require_http_methods(["POST"])
def admin_lock_user(request, user_id):
    """Lock user account"""
    user = get_object_or_404(User, id=user_id)
    
    user.is_active = False
    user.save()
    
    messages.success(request, f'User account {user.email} has been locked')
    return redirect('accounts:admin_user_profile', user_id=user_id)


@staff_member_required
@require_http_methods(["POST"])
def admin_unlock_user(request, user_id):
    """Unlock user account"""
    user = get_object_or_404(User, id=user_id)
    
    user.is_active = True
    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.save()
    
    messages.success(request, f'User account {user.email} has been unlocked')
    return redirect('accounts:admin_user_profile', user_id=user_id)



@staff_member_required
def manage_tag_orders(request):
    """
    Manage physical tag orders - view, update status, track delivery
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    
    # Base queryset
    orders = TagOrder.objects.all()
    
    # Apply filters
    if status_filter != 'all':
        orders = orders.filter(status=status_filter)
    
    if search_query:
        orders = orders.filter(
            Q(order_id__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Statistics
    stats = {
        'total': TagOrder.objects.count(),
        'pending': TagOrder.objects.filter(status='pending').count(),
        'processing': TagOrder.objects.filter(status='processing').count(),
        'shipped': TagOrder.objects.filter(status='shipped').count(),
        'delivered': TagOrder.objects.filter(status='delivered').count(),
        'total_revenue': TagOrder.objects.aggregate(
            total=Sum('total_amount')
        )['total'] or 0,
        'total_tags': TagOrder.objects.aggregate(
            total=Sum('quantity')
        )['total'] or 0,
    }
    
    context = {
        'orders': orders[:100],  # Limit to 100 for performance
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': TagOrder.STATUS_CHOICES,
    }
    
    return render(request, 'admin/manage_tag_orders.html', context)


@staff_member_required
@staff_member_required
@require_http_methods(["POST"])
def update_order_status(request, order_id):
    """
    Update order status (AJAX endpoint)
    """
    try:
        order = get_object_or_404(TagOrder, order_id=order_id)
        new_status = request.POST.get('status')
        tracking_number = request.POST.get('tracking_number', '')
        notes = request.POST.get('notes', '')
        
        if new_status not in dict(TagOrder.STATUS_CHOICES):
            return JsonResponse({'success': False, 'error': 'Invalid status'})
        
        # Update order
        order.status = new_status
        if tracking_number:
            order.tracking_number = tracking_number
        if notes:
            order.notes = notes
        
        # Set timestamps
        if new_status == 'shipped' and not order.shipped_at:
            order.shipped_at = timezone.now()
        elif new_status == 'delivered' and not order.delivered_at:
            order.delivered_at = timezone.now()
        
        order.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Order {order_id} updated to {order.get_status_display()}'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
@require_http_methods(["POST"])
def delete_order(request, order_id):
    """
    Delete an order (AJAX endpoint)
    """
    try:
        order = get_object_or_404(TagOrder, order_id=order_id)
        order_display = f"{order.order_id} ({order.name})"
        
        # Delete the order
        order.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Order {order_display} has been deleted successfully'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@staff_member_required
def order_detail_view(request, order_id):
    """
    View detailed information about a specific order.
    Shows customer details, order items, payment info, delivery status, etc.
    """
    order = get_object_or_404(TagOrder, order_id=order_id)
    
    context = {
        'order': order,
        'status_choices': TagOrder.STATUS_CHOICES,
    }
    
    return render(request, 'admin/order_detail.html', context)


@staff_member_required
def manage_distributors(request):
    """
    Manage distributor registrations - view, verify, assign passwords
    Commission tracked on SUCCESSFUL PAYMENT, not activation.
    Shows revoked distributors separately with option to restore.
    """
    # Get filter parameters
    status_filter = request.GET.get('status', 'active')  # active, pending, verified, revoked, all
    search_query = request.GET.get('search', '')
    
    # Base queryset - all distributors
    distributors = User.objects.filter(is_distributor=True)
    
    # Apply filters
    if status_filter == 'pending':
        distributors = distributors.filter(distributor_verified=False, distributor_revoked=False)
    elif status_filter == 'verified':
        distributors = distributors.filter(distributor_verified=True, distributor_revoked=False)
    elif status_filter == 'active':
        distributors = distributors.filter(distributor_revoked=False)
    elif status_filter == 'revoked':
        distributors = distributors.filter(distributor_revoked=True)
    # 'all' shows everything
    
    if search_query:
        distributors = distributors.filter(
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    distributors = distributors.order_by('-distributor_registered_at')
    
    # Get payment stats for each distributor
    from apps.accounts.recharge_models import DistributorPayment
    
    distributor_list = []
    for dist in distributors:
        # Get distributor's phone (used as code)
        dist_phone = dist.get_decrypted_phone()
        
        # Count completed payments for this distributor
        completed_payments = DistributorPayment.objects.filter(
            distributor=dist,
            status='completed'
        ).count()
        
        # Calculate revenue
        total_revenue = completed_payments * dist.distributor_commission_per_activation
        
        distributor_list.append({
            'user': dist,
            'phone': dist_phone,
            'total_qr': dist.distributor_total_qr,
            'commission': dist.distributor_commission_per_activation,
            'activated_qr_count': completed_payments,  # Now represents completed payments
            'available_qr': dist.distributor_total_qr - completed_payments if dist.distributor_total_qr > completed_payments else 0,
            'total_revenue': total_revenue,
        })
    
    # Statistics
    from apps.gateways.qr_models import PreGeneratedQR
    stats = {
        'total': User.objects.filter(is_distributor=True).count(),
        'pending': User.objects.filter(is_distributor=True, distributor_verified=False, distributor_revoked=False).count(),
        'verified': User.objects.filter(is_distributor=True, distributor_verified=True, distributor_revoked=False).count(),
        'active': User.objects.filter(is_distributor=True, distributor_revoked=False).count(),
        'revoked': User.objects.filter(is_distributor=True, distributor_revoked=True).count(),
        'total_qrs': PreGeneratedQR.objects.filter(owner__is_distributor=True).count(),
        'activated_qrs': PreGeneratedQR.objects.filter(owner__is_distributor=True, status='activated').count(),
    }
    
    context = {
        'distributors': distributor_list,
        'stats': stats,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'admin/manage_distributors.html', context)


@staff_member_required
@require_http_methods(["POST"])
def verify_distributor(request, user_id):
    """
    Verify distributor and assign password
    """
    # CRITICAL: Get the distributor user by ID
    user = get_object_or_404(User, id=user_id, is_distributor=True)
    password = request.POST.get('password', '').strip()
    
    # SAFETY CHECK: Make sure we're not modifying the logged-in admin
    if user.id == request.user.id:
        messages.error(request, '❌ ERROR: Cannot modify your own admin account!')
        return redirect('accounts:admin_manage_distributors')
    
    # SAFETY CHECK: Make sure target user is actually a distributor
    if not user.is_distributor:
        messages.error(request, '❌ ERROR: User is not a distributor!')
        return redirect('accounts:admin_manage_distributors')
    
    # SAFETY CHECK: Don't modify superuser accounts
    if user.is_superuser or user.is_staff:
        messages.error(request, '❌ ERROR: Cannot modify admin/staff accounts!')
        return redirect('accounts:admin_manage_distributors')
    
    print(f"\n{'='*60}")
    print(f"🔐 VERIFYING DISTRIBUTOR")
    print(f"   Admin user: {request.user.email} (ID: {request.user.id})")
    print(f"   Target user: {user.email} (ID: {user.id})")
    print(f"   Username: {user.username}")
    print(f"   Phone: {user.get_decrypted_phone()}")
    print(f"   Is distributor: {user.is_distributor}")
    print(f"   Is staff: {user.is_staff}")
    print(f"   Is superuser: {user.is_superuser}")
    print(f"   Password length: {len(password)}")
    print(f"{'='*60}\n")
    
    if not password:
        messages.error(request, 'Password is required')
        return redirect('accounts:admin_manage_distributors')
    
    if len(password) < 6:
        messages.error(request, 'Password must be at least 6 characters')
        return redirect('accounts:admin_manage_distributors')
    
    # Set password and verify - ONLY for the distributor user
    user.set_password(password)
    user.distributor_verified = True
    user.save()
    
    print(f"\n{'='*60}")
    print(f"✅ DISTRIBUTOR VERIFIED")
    print(f"   User: {user.email} (ID: {user.id})")
    print(f"   Password set: YES")
    print(f"   Has usable password: {user.has_usable_password()}")
    print(f"   Verified: {user.distributor_verified}")
    print(f"   Admin user unchanged: {request.user.email}")
    print(f"{'='*60}\n")
    
    messages.success(request, f'✅ Distributor {user.first_name} verified successfully!')
    return redirect('accounts:admin_manage_distributors')


@staff_member_required
@require_http_methods(["POST"])
def update_distributor_details(request, user_id):
    """
    Update distributor QR count and commission
    """
    user = get_object_or_404(User, id=user_id, is_distributor=True)
    
    # SAFETY CHECK: Make sure we're not modifying the logged-in admin
    if user.id == request.user.id:
        messages.error(request, '❌ ERROR: Cannot modify your own admin account!')
        return redirect('accounts:admin_manage_distributors')
    
    # Get form data
    total_qr = request.POST.get('total_qr', '0').strip()
    commission = request.POST.get('commission', '0').strip()
    
    try:
        total_qr = int(total_qr)
        commission = float(commission)
        
        if total_qr < 0:
            messages.error(request, 'Total QR codes cannot be negative')
            return redirect('accounts:admin_manage_distributors')
        
        if commission < 0:
            messages.error(request, 'Commission cannot be negative')
            return redirect('accounts:admin_manage_distributors')
        
        # Update distributor details
        user.distributor_total_qr = total_qr
        user.distributor_commission_per_activation = commission
        user.save()
        
        print(f"\n{'='*60}")
        print(f"✅ DISTRIBUTOR DETAILS UPDATED")
        print(f"   User: {user.first_name} ({user.get_decrypted_phone()})")
        print(f"   Total QR: {total_qr}")
        print(f"   Commission: ₹{commission}")
        print(f"{'='*60}\n")
        
        messages.success(request, f'✅ Updated details for {user.first_name}')
        return redirect('accounts:admin_manage_distributors')
        
    except ValueError:
        messages.error(request, 'Invalid number format')
        return redirect('accounts:admin_manage_distributors')
    
    messages.success(request, f'✅ Distributor {user.email} verified and password assigned!')
    return redirect('accounts:admin_manage_distributors')


@staff_member_required
@require_http_methods(["POST"])
def reset_distributor_password(request, user_id):
    """
    Reset distributor password
    """
    # CRITICAL: Get the distributor user by ID
    user = get_object_or_404(User, id=user_id, is_distributor=True)
    password = request.POST.get('password', '').strip()
    
    # SAFETY CHECK: Make sure we're not modifying the logged-in admin
    if user.id == request.user.id:
        messages.error(request, '❌ ERROR: Cannot modify your own admin account!')
        return redirect('accounts:admin_manage_distributors')
    
    # SAFETY CHECK: Make sure target user is actually a distributor
    if not user.is_distributor:
        messages.error(request, '❌ ERROR: User is not a distributor!')
        return redirect('accounts:admin_manage_distributors')
    
    # SAFETY CHECK: Don't modify superuser accounts
    if user.is_superuser or user.is_staff:
        messages.error(request, '❌ ERROR: Cannot modify admin/staff accounts!')
        return redirect('accounts:admin_manage_distributors')
    
    print(f"\n{'='*60}")
    print(f"🔐 RESETTING DISTRIBUTOR PASSWORD")
    print(f"   Admin user: {request.user.email} (ID: {request.user.id})")
    print(f"   Target user: {user.email} (ID: {user.id})")
    print(f"   Is distributor: {user.is_distributor}")
    print(f"   Is staff: {user.is_staff}")
    print(f"   Password length: {len(password)}")
    print(f"{'='*60}\n")
    
    if not password:
        messages.error(request, 'Password is required')
        return redirect('accounts:admin_manage_distributors')
    
    if len(password) < 6:
        messages.error(request, 'Password must be at least 6 characters')
        return redirect('accounts:admin_manage_distributors')
    
    # Reset password - ONLY for the distributor user
    user.set_password(password)
    user.save()
    
    print(f"\n{'='*60}")
    print(f"✅ PASSWORD RESET")
    print(f"   User: {user.email} (ID: {user.id})")
    print(f"   Admin user unchanged: {request.user.email}")
    print(f"{'='*60}\n")
    
    messages.success(request, f'✅ Password reset for distributor {user.email}')
    return redirect('accounts:admin_manage_distributors')


@staff_member_required
@require_http_methods(["POST"])
def revoke_distributor(request, user_id):
    """
    Revoke distributor status (soft delete - can be undone)
    """
    from django.utils import timezone as django_timezone
    
    user = get_object_or_404(User, id=user_id, is_distributor=True)
    reason = request.POST.get('reason', '').strip()
    
    # Mark as revoked instead of removing distributor status
    user.distributor_revoked = True
    user.distributor_revoked_at = django_timezone.now()
    user.distributor_revoked_by = request.user
    user.distributor_revoke_reason = reason
    user.save()
    
    messages.success(request, f'Distributor status revoked for {user.email}. Can be undone if needed.')
    return redirect('accounts:admin_manage_distributors')


@staff_member_required
@require_http_methods(["POST"])
def unrevoke_distributor(request, user_id):
    """
    Undo distributor revocation (restore distributor status)
    """
    user = get_object_or_404(User, id=user_id, is_distributor=True, distributor_revoked=True)
    
    # Restore distributor status
    user.distributor_revoked = False
    user.distributor_revoked_at = None
    user.distributor_revoked_by = None
    user.distributor_revoke_reason = ''
    user.save()
    
    messages.success(request, f'Distributor status restored for {user.email}')
    return redirect('accounts:admin_manage_distributors')



@staff_member_required
def manage_commission_payments(request):
    """
    Manage distributor commission payments
    Shows all commissions (paid and unpaid) with ability to mark as paid
    """
    from django.db.models import Sum, Count, Q
    from datetime import datetime, timedelta
    
    # Get filter parameters
    distributor_filter = request.GET.get('distributor', '')
    status_filter = request.GET.get('status', 'unpaid')  # unpaid, paid, all
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base query - only completed payments
    payments = DistributorPayment.objects.filter(
        status='completed',
        distributor__isnull=False
    ).select_related('distributor', 'qr_code', 'commission_paid_by')
    
    # Apply filters
    if distributor_filter:
        payments = payments.filter(distributor__id=distributor_filter)
    
    if status_filter == 'unpaid':
        payments = payments.filter(commission_paid=False)
    elif status_filter == 'paid':
        payments = payments.filter(commission_paid=True)
    # 'all' shows everything
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            payments = payments.filter(paid_at__gte=date_from_obj)
        except:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            payments = payments.filter(paid_at__lte=date_to_obj)
        except:
            pass
    
    # Order by payment date (newest first)
    payments = payments.order_by('-paid_at')
    
    # Calculate summary statistics
    total_commissions = payments.aggregate(
        total=Sum('commission_amount')
    )['total'] or 0
    
    paid_commissions = payments.filter(commission_paid=True).aggregate(
        total=Sum('commission_amount')
    )['total'] or 0
    
    unpaid_commissions = payments.filter(commission_paid=False).aggregate(
        total=Sum('commission_amount')
    )['total'] or 0
    
    # Get distributor summary
    distributor_summary = DistributorPayment.objects.filter(
        status='completed',
        distributor__isnull=False
    ).values(
        'distributor__id',
        'distributor__first_name',
        'distributor__email'
    ).annotate(
        total_sales=Count('id'),
        total_earned=Sum('commission_amount'),
        total_paid=Sum('commission_amount', filter=Q(commission_paid=True)),
        total_unpaid=Sum('commission_amount', filter=Q(commission_paid=False))
    ).order_by('-total_earned')
    
    # Get today's earnings for each distributor
    today = timezone.now().date()
    for dist in distributor_summary:
        today_earnings = DistributorPayment.objects.filter(
            distributor__id=dist['distributor__id'],
            status='completed',
            paid_at__date=today
        ).aggregate(total=Sum('commission_amount'))['total'] or 0
        dist['today_earnings'] = today_earnings
    
    # Get all distributors for filter dropdown
    all_distributors = User.objects.filter(
        is_distributor=True,
        distributor_verified=True
    ).order_by('first_name')
    
    context = {
        'payments': payments,
        'total_commissions': total_commissions,
        'paid_commissions': paid_commissions,
        'unpaid_commissions': unpaid_commissions,
        'distributor_summary': distributor_summary,
        'all_distributors': all_distributors,
        'status_filter': status_filter,
        'distributor_filter': distributor_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'admin/manage_commission_payments.html', context)


@staff_member_required
@require_http_methods(["POST"])
def mark_commissions_paid(request):
    """
    Mark selected commissions as paid
    """
    import json
    from django.utils import timezone as django_timezone
    
    try:
        # Get selected payment IDs
        payment_ids = request.POST.getlist('payment_ids[]')
        payment_notes = request.POST.get('payment_notes', '').strip()
        
        if not payment_ids:
            return JsonResponse({
                'success': False,
                'message': 'No commissions selected'
            })
        
        # Update payments
        payments = DistributorPayment.objects.filter(
            id__in=payment_ids,
            status='completed',
            commission_paid=False
        )
        
        updated_count = 0
        total_amount = 0
        
        for payment in payments:
            payment.commission_paid = True
            payment.commission_paid_at = django_timezone.now()
            payment.commission_paid_by = request.user
            if payment_notes:
                payment.payment_notes = payment_notes
            payment.save()
            
            updated_count += 1
            total_amount += payment.commission_amount
        
        return JsonResponse({
            'success': True,
            'message': f'Marked {updated_count} commission(s) as paid (₹{total_amount})',
            'count': updated_count,
            'amount': float(total_amount)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Error: {str(e)}'
        })


@staff_member_required
@require_http_methods(["POST"])
def mark_commission_unpaid(request, payment_id):
    """
    Mark a single commission as unpaid (undo payment)
    """
    try:
        payment = get_object_or_404(DistributorPayment, id=payment_id)
        
        payment.commission_paid = False
        payment.commission_paid_at = None
        payment.commission_paid_by = None
        payment.save()
        
        messages.success(request, f'Commission marked as unpaid: ₹{payment.commission_amount}')
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
    
    return redirect('accounts:manage_commission_payments')
