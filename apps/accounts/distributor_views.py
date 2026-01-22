"""
Distributor registration and management views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.utils import timezone as django_timezone
from .models import User
from apps.accounts.phone_auth import send_otp, verify_otp


@login_required
@require_http_methods(["GET", "POST"])
def become_distributor(request):
    """
    Step 1: User requests to become a distributor.
    Enter mobile number and verify OTP.
    """
    user = request.user
    
    # Check if already a distributor
    if user.is_distributor:
        messages.info(request, 'You are already registered as a distributor')
        return redirect('accounts:distributor_dashboard')
    
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        # Step 1: Send OTP
        if step == '1':
            phone = request.POST.get('phone', '').strip()
            
            if not phone:
                messages.error(request, 'Phone number is required')
                return redirect('accounts:become_distributor')
            
            # Validate phone number (10 digits)
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 10:
                messages.error(request, 'Please enter a valid 10-digit mobile number')
                return redirect('accounts:become_distributor')
            
            # Check if phone already used by another distributor
            existing = User.objects.filter(
                phone__isnull=False,
                is_distributor=True
            ).exclude(id=user.id)
            
            for u in existing:
                if u.get_decrypted_phone() == phone_digits:
                    messages.error(request, 'This phone number is already registered as a distributor')
                    return redirect('accounts:become_distributor')
            
            # Send OTP
            success, message = send_otp(phone_digits)
            
            if success:
                request.session['distributor_phone'] = phone_digits
                messages.success(request, 'OTP sent to your mobile number')
                return redirect('accounts:become_distributor_verify')
            else:
                messages.error(request, f'Failed to send OTP: {message}')
                return redirect('accounts:become_distributor')
    
    context = {
        'user': user,
    }
    return render(request, 'accounts/become_distributor.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def become_distributor_verify(request):
    """
    Step 2: Verify OTP and register as distributor.
    """
    user = request.user
    phone = request.session.get('distributor_phone')
    
    if not phone:
        messages.error(request, 'Session expired. Please start again.')
        return redirect('accounts:become_distributor')
    
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        
        if not otp:
            messages.error(request, 'Please enter the OTP')
            return redirect('accounts:become_distributor_verify')
        
        # Verify OTP
        success, message = verify_otp(phone, otp)
        
        if success:
            # Register as distributor
            from apps.core.utils import encrypt_data
            user.phone = encrypt_data(phone)
            user.is_phone_verified = True
            user.is_distributor = True
            user.distributor_verified = False  # Admin will verify
            user.distributor_registered_at = django_timezone.now()
            user.save()
            
            # Clear session
            request.session.pop('distributor_phone', None)
            
            messages.success(request, '🎉 Distributor registration successful! Admin will assign your password and verify your account.')
            return redirect('accounts:distributor_pending')
        else:
            messages.error(request, message)
            return redirect('accounts:become_distributor_verify')
    
    context = {
        'phone': phone,
    }
    return render(request, 'accounts/become_distributor_verify.html', context)


@login_required
def distributor_pending(request):
    """
    Show pending verification message.
    """
    user = request.user
    
    if not user.is_distributor:
        return redirect('accounts:dashboard')
    
    if user.distributor_verified:
        return redirect('accounts:distributor_dashboard')
    
    context = {
        'user': user,
        'phone': user.get_decrypted_phone(),
    }
    return render(request, 'accounts/distributor_pending.html', context)


@login_required
def distributor_dashboard(request):
    """
    Distributor dashboard - only accessible after admin verification.
    """
    user = request.user
    
    if not user.is_distributor:
        messages.error(request, 'You are not registered as a distributor')
        return redirect('accounts:dashboard')
    
    if not user.distributor_verified:
        return redirect('accounts:distributor_pending')
    
    # Get distributor statistics
    from apps.gateways.qr_models import PreGeneratedQR
    from apps.accounts.recharge_models import DistributorPayment
    
    # QR codes assigned to this distributor (if any)
    assigned_qrs = PreGeneratedQR.objects.filter(owner=user)
    
    # Payments made through distributor QRs
    payments = DistributorPayment.objects.filter(
        qr_code__owner=user
    ).select_related('qr_code')
    
    total_revenue = sum(p.amount for p in payments if p.status == 'completed')
    
    context = {
        'user': user,
        'phone': user.get_decrypted_phone(),
        'total_qrs': assigned_qrs.count(),
        'activated_qrs': assigned_qrs.filter(status='activated').count(),
        'available_qrs': assigned_qrs.filter(status='available').count(),
        'total_payments': payments.count(),
        'completed_payments': payments.filter(status='completed').count(),
        'total_revenue': total_revenue,
        'recent_payments': payments.order_by('-created_at')[:10],
    }
    return render(request, 'accounts/distributor_dashboard.html', context)


@require_http_methods(["GET", "POST"])
def distributor_login(request):
    """
    Distributor login with mobile number and admin-assigned password.
    """
    if request.user.is_authenticated:
        if request.user.is_distributor and request.user.distributor_verified:
            return redirect('accounts:distributor_dashboard')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '').strip()
        
        if not phone or not password:
            messages.error(request, 'Phone number and password are required')
            return redirect('accounts:distributor_login')
        
        # Validate phone number
        phone_digits = ''.join(filter(str.isdigit, phone))
        if len(phone_digits) != 10:
            messages.error(request, 'Please enter a valid 10-digit mobile number')
            return redirect('accounts:distributor_login')
        
        # Find user by phone
        from apps.core.utils import encrypt_data
        users = User.objects.filter(is_distributor=True)
        
        user_found = None
        for u in users:
            if u.get_decrypted_phone() == phone_digits:
                user_found = u
                break
        
        if not user_found:
            messages.error(request, 'Invalid phone number or password')
            return redirect('accounts:distributor_login')
        
        # Check if verified
        if not user_found.distributor_verified:
            messages.error(request, 'Your distributor account is pending admin verification')
            return redirect('accounts:distributor_login')
        
        # Authenticate with username and password
        authenticated_user = authenticate(
            request,
            username=user_found.username,
            password=password
        )
        
        if authenticated_user:
            login(request, authenticated_user)
            messages.success(request, f'Welcome back, {authenticated_user.first_name or "Distributor"}!')
            return redirect('accounts:distributor_dashboard')
        else:
            messages.error(request, 'Invalid phone number or password')
            return redirect('accounts:distributor_login')
    
    return render(request, 'accounts/distributor_login.html')
