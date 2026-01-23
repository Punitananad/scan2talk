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


@require_http_methods(["GET", "POST"])
def distributor_register(request):
    """
    Standalone distributor registration - NO LOGIN REQUIRED.
    Anyone can register to become a distributor.
    Two-step process:
    1. Enter details + mobile number → Send OTP
    2. Verify OTP → Create distributor account (pending admin approval)
    """
    if request.user.is_authenticated and request.user.is_distributor:
        return redirect('accounts:distributor_dashboard')
    
    # Get current step
    step = request.GET.get('step', '1')
    
    # Step 1: Enter details and mobile number
    if step == '1':
        if request.method == 'POST':
            name = request.POST.get('name', '').strip()
            email = request.POST.get('email', '').strip()
            phone = request.POST.get('phone', '').strip()
            account_holder_name = request.POST.get('account_holder_name', '').strip()
            account_number = request.POST.get('account_number', '').strip()
            ifsc_code = request.POST.get('ifsc_code', '').strip().upper()
            
            if not name or not phone or not account_holder_name or not account_number or not ifsc_code:
                messages.error(request, 'Name, phone number, and bank details are required')
                return redirect('accounts:distributor_register')
            
            # Validate phone number
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 10:
                messages.error(request, 'Please enter a valid 10-digit mobile number')
                return redirect('accounts:distributor_register')
            
            # Validate IFSC code format
            if len(ifsc_code) != 11:
                messages.error(request, 'IFSC code must be 11 characters')
                return redirect('accounts:distributor_register')
            
            # Check if phone already exists
            users = User.objects.all()
            for u in users:
                if u.get_decrypted_phone() == phone_digits:
                    messages.error(request, 'This phone number is already registered')
                    return redirect('accounts:distributor_register')
            
            # Check if email already exists
            if email and User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered')
                return redirect('accounts:distributor_register')
            
            # Send OTP
            print(f"\n{'='*60}")
            print(f"📝 DISTRIBUTOR REGISTRATION - STEP 1")
            print(f"   Name: {name}")
            print(f"   Email: {email}")
            print(f"   Phone: {phone_digits}")
            print(f"   Account Holder: {account_holder_name}")
            print(f"   Account Number: {account_number}")
            print(f"   IFSC Code: {ifsc_code}")
            print(f"{'='*60}\n")
            
            success, message = send_otp(phone_digits)
            
            if success:
                # Store details in session
                request.session['dist_reg_name'] = name
                request.session['dist_reg_email'] = email
                request.session['dist_reg_phone'] = phone_digits
                request.session['dist_reg_account_holder'] = account_holder_name
                request.session['dist_reg_account_number'] = account_number
                request.session['dist_reg_ifsc'] = ifsc_code
                
                messages.success(request, 'OTP sent to your mobile number')
                return redirect('/accounts/distributor/register/?step=2')
            else:
                messages.error(request, f'Failed to send OTP: {message}')
                return redirect('accounts:distributor_register')
        
        # GET - show registration form
        return render(request, 'accounts/distributor_register.html', {'step': 1})
    
    # Step 2: Verify OTP and create account
    elif step == '2':
        name = request.session.get('dist_reg_name')
        email = request.session.get('dist_reg_email')
        phone = request.session.get('dist_reg_phone')
        account_holder_name = request.session.get('dist_reg_account_holder')
        account_number = request.session.get('dist_reg_account_number')
        ifsc_code = request.session.get('dist_reg_ifsc')
        
        if not phone or not name or not account_number:
            messages.error(request, 'Session expired. Please start again.')
            return redirect('accounts:distributor_register')
        
        if request.method == 'POST':
            action = request.POST.get('action', 'verify')
            
            # Handle resend OTP
            if action == 'resend':
                success, message = send_otp(phone)
                if success:
                    messages.success(request, 'New OTP sent successfully')
                else:
                    messages.error(request, f'Failed to resend OTP: {message}')
                return redirect('/accounts/distributor/register/?step=2')
            
            # Handle OTP verification
            otp = request.POST.get('otp', '').strip().replace(' ', '')  # Remove all whitespace
            
            if not otp:
                messages.error(request, 'Please enter the OTP')
                return redirect('/accounts/distributor/register/?step=2')
            
            # Validate OTP format (6 digits)
            if not otp.isdigit() or len(otp) != 6:
                messages.error(request, 'OTP must be 6 digits')
                return redirect('/accounts/distributor/register/?step=2')
            
            print(f"\n{'='*60}")
            print(f"🔐 DISTRIBUTOR REGISTRATION - STEP 2")
            print(f"   Phone: {phone}")
            print(f"   OTP Entered: '{otp}' (length: {len(otp)})")
            print(f"   OTP is digits: {otp.isdigit()}")
            print(f"{'='*60}\n")
            
            # Verify OTP
            success, message = verify_otp(phone, otp)
            
            print(f"   Verification Result: {'SUCCESS' if success else 'FAILED'}")
            print(f"   Message: {message}\n")
            
            if success:
                # Create distributor account
                try:
                    from apps.core.utils import encrypt_data
                    import uuid
                    import json
                    
                    # Generate username
                    username = f"dist_{phone[-4:]}_{uuid.uuid4().hex[:6]}"
                    
                    # Prepare bank details as JSON
                    bank_details = {
                        'account_holder_name': account_holder_name,
                        'account_number': account_number,
                        'ifsc_code': ifsc_code
                    }
                    
                    # Create user
                    user = User.objects.create(
                        username=username,
                        email=email if email else f"{username}@distributor.local",
                        first_name=name,
                        phone=encrypt_data(phone),
                        is_phone_verified=True,
                        is_distributor=True,
                        distributor_verified=False,  # Pending admin approval
                        distributor_registered_at=django_timezone.now()
                    )
                    
                    # Store bank details in last_name field temporarily (or create a separate model)
                    # For now, we'll store as JSON in last_name field
                    user.last_name = json.dumps(bank_details)
                    
                    # Set unusable password (OTP login only)
                    user.set_unusable_password()
                    user.save()
                    
                    # Clear session
                    request.session.pop('dist_reg_name', None)
                    request.session.pop('dist_reg_email', None)
                    request.session.pop('dist_reg_phone', None)
                    request.session.pop('dist_reg_account_holder', None)
                    request.session.pop('dist_reg_account_number', None)
                    request.session.pop('dist_reg_ifsc', None)
                    
                    print(f"✅ DISTRIBUTOR ACCOUNT CREATED")
                    print(f"   Username: {username}")
                    print(f"   Email: {user.email}")
                    print(f"   Phone: {phone}")
                    print(f"   Bank Details: {json.dumps(bank_details, indent=2)}\n")
                    
                    messages.success(request, '🎉 Registration successful! Your account is pending admin approval.')
                    return redirect('accounts:distributor_pending_public')
                    
                except Exception as e:
                    print(f"❌ Error creating account: {str(e)}\n")
                    messages.error(request, f'Error creating account: {str(e)}')
                    return redirect('accounts:distributor_register')
            else:
                messages.error(request, message)
                return redirect('/accounts/distributor/register/?step=2')
        
        # GET - show OTP form
        return render(request, 'accounts/distributor_register.html', {
            'step': 2,
            'name': name,
            'phone': phone
        })
    
    # Invalid step
    return redirect('accounts:distributor_register')


def distributor_pending_public(request):
    """
    Public pending page after registration (no login required).
    """
    return render(request, 'accounts/distributor_pending_public.html')


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
            print(f"\n{'='*60}")
            print(f"🔔 DISTRIBUTOR OTP REQUEST")
            print(f"   Phone: {phone_digits}")
            print(f"   User: {user.email}")
            print(f"{'='*60}\n")
            
            success, message = send_otp(phone_digits)
            
            print(f"\n{'='*60}")
            print(f"📤 OTP SEND RESULT")
            print(f"   Success: {success}")
            print(f"   Message: {message}")
            print(f"{'='*60}\n")
            
            if success:
                request.session['distributor_phone'] = phone_digits
                messages.success(request, 'OTP sent to your mobile number. Check your SMS or console output.')
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
        action = request.POST.get('action', 'verify')
        
        # Handle resend OTP
        if action == 'resend':
            print(f"\n{'='*60}")
            print(f"🔄 RESENDING OTP")
            print(f"   Phone: {phone}")
            print(f"{'='*60}\n")
            
            success, message = send_otp(phone)
            
            if success:
                messages.success(request, 'New OTP sent! Check your SMS or console output.')
            else:
                messages.error(request, f'Failed to resend OTP: {message}')
            
            return redirect('accounts:become_distributor_verify')
        
        # Handle OTP verification
        otp = request.POST.get('otp', '').strip()
        
        if not otp:
            messages.error(request, 'Please enter the OTP')
            return redirect('accounts:become_distributor_verify')
        
        print(f"\n{'='*60}")
        print(f"🔐 VERIFYING OTP")
        print(f"   Phone: {phone}")
        print(f"   OTP: {otp}")
        print(f"{'='*60}\n")
        
        # Verify OTP
        success, message = verify_otp(phone, otp)
        
        print(f"\n{'='*60}")
        print(f"✅ VERIFICATION RESULT")
        print(f"   Success: {success}")
        print(f"   Message: {message}")
        print(f"{'='*60}\n")
        
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
    Shows successful payments (commission earned AFTER payment, BEFORE activation).
    """
    user = request.user
    
    if not user.is_distributor:
        messages.error(request, 'You are not registered as a distributor')
        return redirect('accounts:dashboard')
    
    if not user.distributor_verified:
        return redirect('accounts:distributor_pending')
    
    # Get distributor's phone number
    distributor_code = user.get_decrypted_phone()
    
    # Get statistics from DistributorPayment model (payments for QR codes provided by this distributor)
    from apps.accounts.recharge_models import DistributorPayment
    
    # Total QR codes assigned by admin
    total_qrs = user.distributor_total_qr
    
    # Completed payments (commission earned)
    completed_payments = DistributorPayment.objects.filter(
        distributor=user,
        status='completed'
    )
    payment_count = completed_payments.count()
    
    # Available QR codes
    available_qrs = total_qrs - payment_count if total_qrs > payment_count else 0
    
    # Calculate revenue
    commission_per_activation = user.distributor_commission_per_activation
    total_revenue = payment_count * commission_per_activation
    
    # Recent payments (only Commission and Date)
    recent_payments = completed_payments.order_by('-paid_at')[:20]
    
    context = {
        'user': user,
        'phone': distributor_code,
        'total_qrs': total_qrs,
        'activated_qrs': payment_count,  # Represents completed payments
        'available_qrs': available_qrs,
        'commission_per_activation': commission_per_activation,
        'total_revenue': total_revenue,
        'recent_payments': recent_payments,
    }
    return render(request, 'accounts/distributor_dashboard.html', context)


@require_http_methods(["GET", "POST"])
def distributor_login(request):
    """
    Distributor login with mobile number and OTP verification.
    Two-step process:
    1. Enter mobile number → Send OTP
    2. Verify OTP → Login
    """
    if request.user.is_authenticated:
        if request.user.is_distributor and request.user.distributor_verified:
            return redirect('accounts:distributor_dashboard')
        return redirect('accounts:dashboard')
    
    # Get current step from query parameter
    step = request.GET.get('step', '1')
    
    # Step 1: Enter mobile number and send OTP
    if step == '1':
        if request.method == 'POST':
            phone = request.POST.get('phone', '').strip()
            
            if not phone:
                messages.error(request, 'Phone number is required')
                return redirect('accounts:distributor_login')
            
            # Validate phone number
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 10:
                messages.error(request, 'Please enter a valid 10-digit mobile number')
                return redirect('accounts:distributor_login')
            
            # Find distributor by phone
            users = User.objects.filter(is_distributor=True, distributor_verified=True)
            
            print(f"\n{'='*60}")
            print(f"🔐 DISTRIBUTOR LOGIN - STEP 1")
            print(f"   Phone entered: {phone_digits}")
            print(f"   Total verified distributors: {users.count()}")
            print(f"{'='*60}\n")
            
            user_found = None
            for u in users:
                decrypted_phone = u.get_decrypted_phone()
                if decrypted_phone == phone_digits:
                    user_found = u
                    print(f"   ✓ DISTRIBUTOR FOUND: {u.email}")
                    break
            
            if not user_found:
                print(f"\n❌ No verified distributor found with phone: {phone_digits}\n")
                messages.error(request, 'No verified distributor account found with this phone number')
                return redirect('accounts:distributor_login')
            
            # Send OTP
            print(f"📤 Sending OTP to {phone_digits}...")
            success, message = send_otp(phone_digits)
            
            print(f"   Result: {'SUCCESS' if success else 'FAILED'}")
            print(f"   Message: {message}\n")
            
            if success:
                # Store phone in session
                request.session['distributor_login_phone'] = phone_digits
                request.session['distributor_user_id'] = str(user_found.id)  # Convert UUID to string
                
                messages.success(request, 'OTP sent to your mobile number')
                return redirect('/accounts/distributor/login/?step=2')
            else:
                messages.error(request, f'Failed to send OTP: {message}')
                return redirect('accounts:distributor_login')
        
        # GET request - show phone input form
        return render(request, 'accounts/distributor_login.html', {'step': 1})
    
    # Step 2: Verify OTP and login
    elif step == '2':
        phone = request.session.get('distributor_login_phone')
        user_id = request.session.get('distributor_user_id')
        
        if not phone or not user_id:
            messages.error(request, 'Session expired. Please start again.')
            return redirect('accounts:distributor_login')
        
        if request.method == 'POST':
            action = request.POST.get('action', 'verify')
            
            # Handle resend OTP
            if action == 'resend':
                print(f"\n🔄 RESENDING OTP to {phone}\n")
                success, message = send_otp(phone)
                
                if success:
                    messages.success(request, 'New OTP sent successfully')
                else:
                    messages.error(request, f'Failed to resend OTP: {message}')
                
                return redirect('/accounts/distributor/login/?step=2')
            
            # Handle OTP verification
            otp = request.POST.get('otp', '').strip().replace(' ', '')  # Remove all whitespace
            
            if not otp:
                messages.error(request, 'Please enter the OTP')
                return redirect('/accounts/distributor/login/?step=2')
            
            # Validate OTP format (6 digits)
            if not otp.isdigit() or len(otp) != 6:
                messages.error(request, 'OTP must be 6 digits')
                return redirect('/accounts/distributor/login/?step=2')
            
            print(f"\n{'='*60}")
            print(f"🔐 DISTRIBUTOR LOGIN - STEP 2")
            print(f"   Phone: {phone}")
            print(f"   OTP Entered: '{otp}' (length: {len(otp)})")
            print(f"   OTP is digits: {otp.isdigit()}")
            print(f"{'='*60}\n")
            
            # Verify OTP
            success, message = verify_otp(phone, otp)
            
            print(f"   Verification: {'SUCCESS' if success else 'FAILED'}")
            print(f"   Message: {message}\n")
            
            if success:
                # Get user and login
                try:
                    user = User.objects.get(id=user_id, is_distributor=True, distributor_verified=True)
                    
                    # Login the user
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    # Clear session
                    request.session.pop('distributor_login_phone', None)
                    request.session.pop('distributor_user_id', None)
                    
                    print(f"✅ LOGIN SUCCESS - User: {user.email}\n")
                    
                    messages.success(request, f'Welcome back, {user.first_name or "Distributor"}!')
                    return redirect('accounts:distributor_dashboard')
                    
                except User.DoesNotExist:
                    print(f"❌ User not found or not verified\n")
                    messages.error(request, 'Account not found or not verified')
                    return redirect('accounts:distributor_login')
            else:
                messages.error(request, message)
                return redirect('/accounts/distributor/login/?step=2')
        
        # GET request - show OTP input form
        return render(request, 'accounts/distributor_login.html', {
            'step': 2,
            'phone': phone
        })
    
    # Invalid step
    return redirect('accounts:distributor_login')
