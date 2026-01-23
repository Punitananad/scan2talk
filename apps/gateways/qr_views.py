"""
Views for QR code generation and management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone as django_timezone
from django.db import transaction, models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status

from .qr_models import PreGeneratedQR, QRBatch
from .models import Gateway
from apps.core.utils import generate_short_code
import uuid


@staff_member_required
@require_http_methods(["GET", "POST"])
def generate_qr_codes(request):
    """
    Admin view to generate batch of QR codes.
    Route: /gqr/
    """
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 10))
            batch_name = request.POST.get('batch_name', '').strip()
            purpose = request.POST.get('purpose', '')
            notes = request.POST.get('notes', '')
            category_id = request.POST.get('category', '')
            action = request.POST.get('action', 'generate_only')  # New: get action type
            qr_type = request.POST.get('qr_type', 'single')  # New: get QR type (single or pair)
            
            # Debug logging
            print(f"🔍 QR Generation Request:")
            print(f"   - Quantity: {quantity}")
            print(f"   - QR Type: {qr_type}")
            print(f"   - Action: {action}")
            
            if quantity < 1 or quantity > 1000:
                messages.error(request, 'Quantity must be between 1 and 1000')
                return redirect('gateways:generate_qr')
            
            if not batch_name:
                messages.error(request, 'Batch name is required')
                return redirect('gateways:generate_qr')
            
            # Get category if provided
            category = None
            if category_id:
                from apps.accounts.recharge_models import RechargeCategory
                try:
                    category = RechargeCategory.objects.get(id=category_id)
                except RechargeCategory.DoesNotExist:
                    messages.error(request, 'Invalid category selected')
                    return redirect('gateways:generate_qr')
            
            # Calculate actual QR codes to generate based on type
            # quantity = number of QR codes to generate (not vehicles)
            # For single: generate exactly the quantity specified
            # For pair: generate quantity * 2 (pair for each vehicle)
            if qr_type == 'single':
                qr_codes_to_generate = quantity
                vehicle_count = quantity
            else:  # pair
                qr_codes_to_generate = quantity * 2
                vehicle_count = quantity
            
            print(f"   - QR codes to generate: {qr_codes_to_generate}")
            print(f"   - Vehicle count: {vehicle_count}")
            
            # Use custom batch name with unique suffix to ensure uniqueness
            batch_number = f"{batch_name}-{generate_short_code(4).upper()}"
            
            # Create batch record
            batch = QRBatch.objects.create(
                batch_number=batch_number,
                quantity=qr_codes_to_generate,  # Store actual QR count
                purpose=purpose,
                notes=notes + (f"\n[QR Type: {qr_type.upper()} - {vehicle_count} vehicle{'s' if vehicle_count != 1 else ''}]" if notes else f"[QR Type: {qr_type.upper()} - {vehicle_count} vehicle{'s' if vehicle_count != 1 else ''}]"),
                category=category,
                created_by=request.user,
                available_count=qr_codes_to_generate
            )
            
            print(f"✅ Creating batch {batch_number} with {qr_codes_to_generate} QR codes")
            
            # Generate QR codes
            qr_codes = []
            for i in range(qr_codes_to_generate):
                qr = PreGeneratedQR.objects.create(
                    batch_number=batch_number,
                    category=category
                )
                qr_codes.append(qr)
                
                # Create QR wallet if category is assigned
                if category:
                    from apps.accounts.recharge_models import QRWallet
                    QRWallet.objects.create(
                        qr_code=qr,
                        category=category
                    )
            
            print(f"✅ Generated {len(qr_codes)} QR codes successfully")
            
            # Check if user wants to download PDF immediately
            if action == 'generate_and_download_pdf':
                # Redirect to preview page first
                qr_type_msg = f"{qr_type} ({vehicle_count} vehicle{'s' if vehicle_count != 1 else ''}, {qr_codes_to_generate} QR code{'s' if qr_codes_to_generate != 1 else ''})"
                messages.success(request, f'Generated {qr_type_msg} in batch {batch_number}')
                return redirect('gateways:batch_preview_page', batch_number=batch_number)
            else:
                # Just show success message and redirect to dashboard
                qr_type_msg = f"{qr_type} - {vehicle_count} vehicle{'s' if vehicle_count != 1 else ''}, {qr_codes_to_generate} QR code{'s' if qr_codes_to_generate != 1 else ''}"
                messages.success(request, f'Successfully generated {qr_type_msg} in batch {batch_number}' + 
                               (f' with category {category.name}' if category else ''))
                return redirect('gateways:qr_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error generating QR codes: {str(e)}')
            return redirect('gateways:generate_qr')
    
    # GET request - show form
    from apps.accounts.recharge_models import RechargeCategory
    categories = RechargeCategory.objects.filter(is_active=True)
    
    context = {
        'total_qr_codes': PreGeneratedQR.objects.count(),
        'available_qr_codes': PreGeneratedQR.objects.filter(status='available').count(),
        'activated_qr_codes': PreGeneratedQR.objects.filter(status='activated').count(),
        'categories': categories,
    }
    return render(request, 'gateways/generate_qr.html', context)


@staff_member_required
def batch_preview_page(request, batch_number):
    """
    Preview page showing sample QR and download options.
    """
    batch = get_object_or_404(QRBatch, batch_number=batch_number)
    qr_count = PreGeneratedQR.objects.filter(batch_number=batch_number).count()
    
    context = {
        'batch': batch,
        'batch_number': batch_number,
        'qr_count': qr_count,
    }
    return render(request, 'gateways/batch_preview.html', context)


@staff_member_required
def tag_clean_view(request):
    """
    Display the clean tag design page.
    """
    return render(request, 'gateways/tag_clean.html')


def tag_print_design(request):
    """
    Display the print-ready tag design with sample QR codes for testing.
    """
    from apps.core.utils import generate_qr_code
    import base64
    from django.conf import settings
    
    # Generate sample QR codes for testing the design
    sample_qr_codes = ['SAMPLE001', 'SAMPLE002', 'SAMPLE003', 'SAMPLE004', 
                       'SAMPLE005', 'SAMPLE006', 'SAMPLE007', 'SAMPLE008']
    
    qr_data_list = []
    protocol = 'http' if settings.DEBUG else 'https'
    
    for qr_code in sample_qr_codes:
        url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{qr_code}/"
        qr_image_file = generate_qr_code(url)
        qr_image_file.seek(0)
        qr_base64 = base64.b64encode(qr_image_file.read()).decode('utf-8')
        
        qr_data_list.append({
            'qr_code': qr_code,
            'qr_code_data': qr_base64
        })
    
    # Split into pages (8 tags per page: 2 cols x 4 rows)
    tags_per_page = 8
    qr_pages = [qr_data_list[i:i + tags_per_page] for i in range(0, len(qr_data_list), tags_per_page)]
    
    context = {
        'qr_pages': qr_pages,
        'is_preview': True,
    }
    
    return render(request, 'gateways/tag_print_design.html', context)


@staff_member_required
def qr_dashboard(request):
    """
    Dashboard to view and manage all QR codes.
    """
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    batch_filter = request.GET.get('batch', '')
    category_filter = request.GET.get('category', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    qr_codes = PreGeneratedQR.objects.select_related('owner', 'gateway', 'category').all()
    
    # Apply filters
    if status_filter:
        qr_codes = qr_codes.filter(status=status_filter)
    if batch_filter:
        qr_codes = qr_codes.filter(batch_number=batch_filter)
    if category_filter:
        qr_codes = qr_codes.filter(category_id=category_filter)
    if search:
        qr_codes = qr_codes.filter(qr_code__icontains=search)
    
    # Get batches and categories for filter dropdowns
    batches = QRBatch.objects.all().order_by('-created_at')
    from apps.accounts.recharge_models import RechargeCategory
    categories = RechargeCategory.objects.filter(is_active=True)
    
    # Statistics
    stats = {
        'total': PreGeneratedQR.objects.count(),
        'available': PreGeneratedQR.objects.filter(status='available').count(),
        'reserved': PreGeneratedQR.objects.filter(status='reserved').count(),
        'activated': PreGeneratedQR.objects.filter(status='activated').count(),
        'expired': PreGeneratedQR.objects.filter(status='expired').count(),
    }
    
    # Category-wise statistics
    category_stats = []
    for category in categories:
        cat_qr_count = PreGeneratedQR.objects.filter(category=category).count()
        cat_activated = PreGeneratedQR.objects.filter(category=category, status='activated').count()
        category_stats.append({
            'category': category,
            'total': cat_qr_count,
            'activated': cat_activated,
            'available': cat_qr_count - cat_activated
        })
    
    context = {
        'qr_codes': qr_codes[:100],  # Limit to 100 for performance
        'batches': batches,
        'categories': categories,
        'category_stats': category_stats,
        'stats': stats,
        'status_filter': status_filter,
        'batch_filter': batch_filter,
        'category_filter': category_filter,
        'search': search,
    }
    return render(request, 'gateways/qr_dashboard.html', context)


@staff_member_required
def category_users_view(request, category_id):
    """
    View all users/QR codes under a specific category.
    """
    from apps.accounts.recharge_models import RechargeCategory
    category = get_object_or_404(RechargeCategory, id=category_id)
    
    # Get all QR codes in this category
    qr_codes = PreGeneratedQR.objects.filter(category=category).select_related(
        'owner', 'gateway', 'category'
    ).order_by('-activated_at', '-created_at')
    
    # Get activated QR codes with user details
    activated_qrs = qr_codes.filter(status='activated')
    
    # Statistics for this category
    stats = {
        'total_qr': qr_codes.count(),
        'activated': activated_qrs.count(),
        'available': qr_codes.filter(status='available').count(),
        'total_access': qr_codes.aggregate(total=models.Sum('access_count'))['total'] or 0,
    }
    
    context = {
        'category': category,
        'qr_codes': qr_codes,
        'activated_qrs': activated_qrs,
        'stats': stats,
    }
    return render(request, 'gateways/category_users.html', context)


@staff_member_required
def registrations_page(request):
    """
    Dedicated page showing all vehicle registrations (active gateways).
    Shows both QR-based and direct registrations.
    Allows admin to deactivate registrations.
    """
    # Get filter parameters
    search = request.GET.get('search', '')
    
    # Get all active vehicle gateways
    registrations = Gateway.objects.filter(
        is_active=True,
        context_type='vehicle'
    ).select_related('owner').prefetch_related('qr_code').order_by('-created_at')
    
    # Apply search filter
    if search:
        registrations = registrations.filter(
            models.Q(identifier_text__icontains=search) |
            models.Q(owner_name__icontains=search) |
            models.Q(owner__phone_number__icontains=search) |
            models.Q(owner__email__icontains=search)
        )
    
    # Get QR codes for each gateway
    registration_data = []
    for gateway in registrations:
        # Try to find associated QR code
        try:
            qr_code = PreGeneratedQR.objects.get(gateway=gateway)
        except PreGeneratedQR.DoesNotExist:
            qr_code = None
        
        registration_data.append({
            'gateway': gateway,
            'qr_code': qr_code,
            'has_qr': qr_code is not None
        })
    
    # Statistics
    stats = {
        'total_registrations': Gateway.objects.filter(is_active=True, context_type='vehicle').count(),
        'total_access_count': PreGeneratedQR.objects.filter(status='activated').aggregate(
            total=models.Sum('access_count')
        )['total'] or 0,
        'total_interactions': Gateway.objects.filter(is_active=True).aggregate(
            total=models.Sum('total_interactions')
        )['total'] or 0,
    }
    
    context = {
        'registration_data': registration_data,
        'stats': stats,
        'search': search,
    }
    return render(request, 'gateways/registrations.html', context)


@staff_member_required
@require_http_methods(["POST"])
def deregister_qr(request, qr_id):
    """
    Deregister/deactivate a gateway registration.
    Works for both QR-based and direct registrations.
    
    IMPORTANT: This is the ONLY legitimate way to deactivate a gateway.
    Admin explicitly chooses to deregister a vehicle.
    """
    try:
        # qr_id is actually gateway_id in this context
        gateway = get_object_or_404(Gateway, id=qr_id)
        
        if not gateway.is_active:
            messages.error(request, f'Gateway is already inactive')
            return redirect('gateways:registrations')
        
        # Deactivate the gateway (admin action only)
        gateway.is_active = False
        gateway.save()
        
        # If there's an associated QR code, reset it to available
        try:
            qr = PreGeneratedQR.objects.get(gateway=gateway)
            qr.status = 'available'
            qr.owner = None
            qr.gateway = None
            qr.activated_at = None
            qr.save()
            messages.success(request, f'Successfully deregistered vehicle {gateway.identifier_text} and freed QR code {qr.qr_code}')
        except PreGeneratedQR.DoesNotExist:
            messages.success(request, f'Successfully deregistered vehicle {gateway.identifier_text}')
        
        return redirect('gateways:registrations')
        
    except Exception as e:
        messages.error(request, f'Error deregistering: {str(e)}')
        return redirect('gateways:registrations')


@staff_member_required
@require_http_methods(["GET"])
def qr_detail(request, qr_id):
    """
    View detailed information about a QR code and its activation.
    """
    qr = get_object_or_404(PreGeneratedQR, id=qr_id)
    
    context = {
        'qr': qr,
        'gateway': qr.gateway,
        'owner': qr.owner,
    }
    return render(request, 'gateways/qr_detail.html', context)


@staff_member_required
@require_http_methods(["GET"])
def delete_qr(request, qr_id):
    """
    Delete a single QR code.
    """
    qr = get_object_or_404(PreGeneratedQR, id=qr_id)
    qr_code = qr.qr_code
    qr.delete()
    
    messages.success(request, f'QR code {qr_code} deleted successfully')
    return redirect('gateways:qr_dashboard')


@staff_member_required
@require_http_methods(["GET"])
def delete_all_qr(request):
    """
    Delete all QR codes and batches.
    """
    qr_count = PreGeneratedQR.objects.count()
    batch_count = QRBatch.objects.count()
    
    PreGeneratedQR.objects.all().delete()
    QRBatch.objects.all().delete()
    
    messages.success(request, f'Deleted {qr_count} QR codes and {batch_count} batches')
    return redirect('gateways:qr_dashboard')


@staff_member_required
@require_http_methods(["GET"])
def delete_batch(request, batch_number):
    """
    Delete all QR codes in a batch.
    """
    batch = get_object_or_404(QRBatch, batch_number=batch_number)
    qr_count = PreGeneratedQR.objects.filter(batch_number=batch_number).count()
    
    PreGeneratedQR.objects.filter(batch_number=batch_number).delete()
    batch.delete()
    
    messages.success(request, f'Deleted batch {batch_number} with {qr_count} QR codes')
    return redirect('gateways:qr_dashboard')


@staff_member_required
@require_http_methods(["POST"])
def activate_qr_for_user(request, qr_id):
    """
    Admin can activate a QR code for a specific user.
    """
    try:
        qr = get_object_or_404(PreGeneratedQR, id=qr_id)
        user_id = request.POST.get('user_id')
        
        if not user_id:
            messages.error(request, 'User ID is required')
            return redirect('gateways:qr_dashboard')
        
        from apps.accounts.models import User
        user = get_object_or_404(User, id=user_id)
        
        # Create a gateway for the user
        gateway = Gateway.objects.create(
            owner=user,
            title=f"Vehicle Gateway - {qr.qr_code}",
            context_type='vehicle',
            description='Activated by admin'
        )
        
        # Activate QR code
        qr.activate(user, gateway, by_admin=True)
        
        messages.success(request, f'QR code {qr.qr_code} activated for user {user.email}')
        return redirect('gateways:qr_dashboard')
        
    except Exception as e:
        messages.error(request, f'Error activating QR code: {str(e)}')
        return redirect('gateways:qr_dashboard')


@require_http_methods(["POST"])
def resend_otp_view(request, qr_code):
    """
    Resend OTP to the phone number stored in session.
    Route: /activate/<qr_code>/resend-otp/
    """
    phone = request.session.get('activation_phone')
    
    if not phone:
        messages.error(request, 'Session expired. Please start again.')
        return redirect(f'/gateways/activate/{qr_code}/?step=1')
    
    from apps.accounts.phone_auth import resend_otp
    success, message = resend_otp(phone)
    
    if success:
        messages.success(request, 'OTP resent successfully')
    else:
        messages.error(request, f'Failed to resend OTP: {message}')
    
    return redirect(f'/gateways/activate/{qr_code}/?step=2')


@require_http_methods(["GET", "POST"])
def activate_qr_code(request, qr_code):
    """
    User activates their QR code by scanning or entering the code.
    Route: /activate/<qr_code>/
    NO LOGIN REQUIRED - Uses phone OTP authentication
    
    IMPORTANT: Once activated, QR becomes public-facing permanently.
    No repeated activation checks, no owner-side messages.
    """
    from django.contrib.auth import login
    
    qr = get_object_or_404(PreGeneratedQR, qr_code=qr_code.upper())
    
    # Increment access count
    qr.increment_access_count()
    
    # If already activated, ALWAYS redirect to public contact page
    # No messages, no checks, no owner logic - just direct access
    if qr.status == 'activated':
        return redirect('core:gateway_access', identifier=qr.qr_code)
    
    # CRITICAL: Check if category is assigned
    # QR codes without category CANNOT be activated
    if not qr.category:
        context = {
            'qr_code': qr.qr_code,
            'error_title': 'Category Not Assigned',
            'error_message': 'This QR code cannot be activated yet. The administrator needs to assign a category first.',
            'support_message': 'Please contact support or wait for the administrator to complete the setup.'
        }
        return render(request, 'gateways/activation_blocked.html', context)
    
    # DISTRIBUTOR CATEGORY: Check if payment is required
    if qr.category.category_type == 'distributor':
        from apps.accounts.recharge_models import DistributorPayment
        
        # Check if payment exists and is completed
        try:
            payment = DistributorPayment.objects.get(qr_code=qr)
            if payment.status != 'completed':
                # Payment pending or failed - redirect to payment page
                return redirect('accounts:distributor_payment', qr_code=qr.qr_code)
        except DistributorPayment.DoesNotExist:
            # No payment record - redirect to payment page
            return redirect('accounts:distributor_payment', qr_code=qr.qr_code)
    
    # Check if available
    if qr.status != 'available':
        messages.error(request, f'This QR code is {qr.status} and cannot be activated')
        return redirect('core:home')
    
    # Multi-step activation process
    step = request.GET.get('step', '1')
    
    # Step 1: Enter phone number
    if step == '1':
        if request.method == 'POST':
            phone = request.POST.get('phone', '').strip()
            
            if not phone:
                messages.error(request, 'Phone number is required')
                return redirect(f'/gateways/activate/{qr_code}/?step=1')
            
            # Validate phone number (10 digits)
            phone_digits = ''.join(filter(str.isdigit, phone))
            if len(phone_digits) != 10:
                messages.error(request, 'Please enter a valid 10-digit mobile number')
                return redirect(f'/gateways/activate/{qr_code}/?step=1')
            
            # Send OTP
            from apps.accounts.phone_auth import send_otp
            success, message = send_otp(phone_digits)
            
            if success:
                # Store phone in session
                request.session['activation_phone'] = phone_digits
                request.session['activation_qr_code'] = qr_code
                
                messages.success(request, 'OTP sent to your mobile number')
                return redirect(f'/gateways/activate/{qr_code}/?step=2')
            else:
                messages.error(request, f'Failed to send OTP: {message}')
                return redirect(f'/gateways/activate/{qr_code}/?step=1')
        
        context = {'qr': qr, 'step': 1}
        return render(request, 'gateways/activate_step1_phone.html', context)
    
    # Step 2: Verify OTP
    elif step == '2':
        phone = request.session.get('activation_phone')
        if not phone:
            return redirect(f'/gateways/activate/{qr_code}/?step=1')
        
        if request.method == 'POST':
            otp = request.POST.get('otp', '').strip()
            
            if not otp:
                messages.error(request, 'Please enter the OTP')
                return redirect(f'/gateways/activate/{qr_code}/?step=2')
            
            # Verify OTP
            from apps.accounts.phone_auth import verify_otp, mark_phone_verified
            success, message = verify_otp(phone, otp)
            
            if success:
                # Mark phone as verified in both cache AND session
                mark_phone_verified(phone)
                request.session['phone_verified'] = True
                request.session['verified_phone'] = phone
                request.session.modified = True  # Force session save
                
                print(f"✅ OTP verified, session updated: phone_verified=True, verified_phone={phone}")
                
                messages.success(request, 'Mobile number verified successfully')
                return redirect(f'/gateways/activate/{qr_code}/?step=3')
            else:
                messages.error(request, message)
                return redirect(f'/gateways/activate/{qr_code}/?step=2')
        
        context = {'qr': qr, 'step': 2, 'phone': phone}
        return render(request, 'gateways/activate_step2_otp.html', context)
    
    # Step 3: Enter details and activate
    elif step == '3':
        phone = request.session.get('activation_phone')
        if not phone:
            messages.error(request, 'Session expired. Please start again.')
            return redirect(f'/gateways/activate/{qr_code}/?step=1')
        
        # Check verification in session first, then cache
        session_verified = request.session.get('phone_verified', False)
        verified_phone = request.session.get('verified_phone')
        
        from apps.accounts.phone_auth import is_phone_verified
        cache_verified = is_phone_verified(phone)
        
        print(f"🔍 Step 3 verification check:")
        print(f"   - Phone: {phone}")
        print(f"   - Session verified: {session_verified}")
        print(f"   - Verified phone in session: {verified_phone}")
        print(f"   - Cache verified: {cache_verified}")
        
        # Accept if EITHER session OR cache shows verified
        if not (session_verified and verified_phone == phone) and not cache_verified:
            print(f"❌ Verification failed - redirecting to step 2")
            messages.error(request, 'Please verify your mobile number first')
            return redirect(f'/gateways/activate/{qr_code}/?step=2')
        
        print(f"✅ Verification passed - proceeding with activation")
        
        if request.method == 'POST':
            try:
                with transaction.atomic():
                    # Get form data
                    name = request.POST.get('name', '').strip()
                    vehicle_type = request.POST.get('vehicle_type', 'car')
                    vehicle_number = request.POST.get('vehicle_number', '').strip().upper()
                    vehicle_model = request.POST.get('vehicle_model', '').strip()
                    distributor_code = request.POST.get('distributor_code', '').strip()
                    
                    if not name or not vehicle_number:
                        messages.error(request, 'Name and vehicle number are required')
                        return redirect(f'/gateways/activate/{qr_code}/?step=3')
                    
                    # Validate distributor code if provided
                    if distributor_code:
                        if not distributor_code.isdigit() or len(distributor_code) != 10:
                            messages.error(request, 'Distributor code must be a 10-digit mobile number')
                            return redirect(f'/gateways/activate/{qr_code}/?step=3')
                    
                    # Check if vehicle number already exists
                    existing_gateway = Gateway.objects.filter(
                        identifier_text=vehicle_number,
                        is_active=True
                    ).first()
                    
                    if existing_gateway:
                        # Show detailed error page
                        context = {
                            'vehicle_number': vehicle_number,
                            'qr_code': qr_code,
                            'existing_owner': existing_gateway.owner_name or 'Another user'
                        }
                        return render(request, 'gateways/vehicle_already_registered.html', context)
                    
                    # Get or create user
                    from apps.accounts.phone_auth import get_or_create_user_by_phone
                    user, created = get_or_create_user_by_phone(phone, name)
                    
                    # Create gateway for the user
                    # CRITICAL: Gateway must be created as active and remain active permanently
                    gateway = Gateway.objects.create(
                        owner=user,
                        owner_name=name,  # Save owner's name
                        title=f"{vehicle_type.title()} - {vehicle_number}",
                        context_type='vehicle',
                        description=f"{vehicle_model}",
                        identifier_text=vehicle_number,
                        distributor_code=distributor_code if distributor_code else '',  # Save distributor code
                        is_active=True  # Explicitly set to active
                    )
                    
                    print(f"\n{'='*60}")
                    print(f"✅ GATEWAY CREATED")
                    print(f"   Owner: {name}")
                    print(f"   Vehicle: {vehicle_number}")
                    print(f"   Distributor Code: {distributor_code if distributor_code else 'None'}")
                    print(f"{'='*60}\n")
                    
                    # Activate QR code
                    qr.activate(user, gateway, by_admin=False)
                    
                    # Auto-create QR wallet if category is prepaid
                    if qr.category and qr.category.category_type == 'prepaid':
                        from apps.accounts.recharge_models import QRWallet
                        
                        # Create wallet with ₹0 balance
                        wallet, created = QRWallet.objects.get_or_create(
                            qr_code=qr,
                            defaults={
                                'category': qr.category,
                                'balance': 0.00,  # Start with ₹0
                                'is_active': True
                            }
                        )
                        
                        if created:
                            print(f"✅ Auto-created QR wallet for {qr.qr_code} with ₹0 balance")
                    
                    # Auto-login the user
                    from django.contrib.auth import login
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    
                    # Clear session
                    request.session.pop('activation_phone', None)
                    request.session.pop('activation_qr_code', None)
                    
                    # Success message and redirect to dashboard
                    messages.success(request, f'🎉 Activation successful! Welcome {name}!')
                    return redirect('accounts:dashboard')
                    
            except Exception as e:
                messages.error(request, f'Error activating QR code: {str(e)}')
                return redirect(f'/gateways/activate/{qr_code}/?step=3')
        
        context = {'qr': qr, 'step': 3, 'phone': phone}
        return render(request, 'gateways/activate_step3_details.html', context)
    
    # Invalid step
    return redirect(f'/gateways/activate/{qr_code}/?step=1')


def public_qr_access(request, qr_code):
    """
    Public access to QR code - shows contact form or activation page.
    Route: /g/<qr_code>/
    
    IMPORTANT: Once activated, always shows public contact page.
    No owner checks, no authentication logic - pure public access.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        qr = get_object_or_404(PreGeneratedQR, qr_code=qr_code.upper())
        
        logger.info(f"Public QR access for: {qr.qr_code}, status: {qr.status}")
        
        # Increment access count
        qr.increment_access_count()
        
        # CRITICAL: Check if category is assigned
        if not qr.category:
            logger.warning(f"QR {qr.qr_code} has no category assigned")
            context = {
                'qr_code': qr.qr_code,
                'error_title': 'Category Not Assigned',
                'error_message': 'This QR code is not ready for use yet. The administrator needs to assign a category first.',
                'support_message': 'Please contact support or wait for the administrator to complete the setup.'
            }
            return render(request, 'gateways/activation_blocked.html', context)
        
        # If not activated, redirect to activation page
        if qr.status != 'activated':
            logger.info(f"QR {qr.qr_code} not activated, redirecting to activation")
            return redirect('gateways:activate_qr', qr_code=qr_code)
        
        # Check if gateway exists
        if not qr.gateway:
            logger.error(f"QR {qr.qr_code} has no gateway")
            return render(request, 'gateways/qr_not_found.html')
        
        # If activated, ALWAYS show the public contact page
        # This is the permanent behavior - no exceptions
        logger.info(f"QR {qr.qr_code} activated, redirecting to gateway access")
        return redirect('core:gateway_access', identifier=qr.qr_code)
        
    except Exception as e:
        logger.error(f"Error in public_qr_access for {qr_code}: {str(e)}", exc_info=True)
        return render(request, 'gateways/qr_not_found.html')



# API Endpoints

@api_view(['POST'])
@permission_classes([IsAdminUser])
def api_generate_qr_batch(request):
    """
    API endpoint to generate QR codes in batch.
    POST /api/gateways/qr/generate/
    """
    try:
        quantity = int(request.data.get('quantity', 10))
        purpose = request.data.get('purpose', '')
        notes = request.data.get('notes', '')
        
        if quantity < 1 or quantity > 1000:
            return Response(
                {'error': 'Quantity must be between 1 and 1000'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate batch number
        batch_number = f"BATCH-{django_timezone.now().strftime('%Y%m%d')}-{generate_short_code(6).upper()}"
        
        # Create batch record
        batch = QRBatch.objects.create(
            batch_number=batch_number,
            quantity=quantity,
            purpose=purpose,
            notes=notes,
            created_by=request.user,
            available_count=quantity
        )
        
        # Generate QR codes
        qr_codes = []
        for _ in range(quantity):
            qr = PreGeneratedQR.objects.create(
                batch_number=batch_number
            )
            qr_codes.append({
                'id': str(qr.id),
                'qr_code': qr.qr_code,
                'activation_url': qr.get_activation_url(),
                'status': qr.status
            })
        
        return Response({
            'success': True,
            'batch_number': batch_number,
            'quantity': quantity,
            'qr_codes': qr_codes
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_my_qr_codes(request):
    """
    Get QR codes owned by the current user.
    GET /api/gateways/qr/my/
    """
    qr_codes = PreGeneratedQR.objects.filter(owner=request.user).select_related('gateway')
    
    data = [{
        'id': str(qr.id),
        'qr_code': qr.qr_code,
        'status': qr.status,
        'activated_at': qr.activated_at,
        'access_count': qr.access_count,
        'gateway': {
            'id': str(qr.gateway.id),
            'title': qr.gateway.title,
            'context_type': qr.gateway.context_type
        } if qr.gateway else None,
        'activation_url': qr.get_activation_url(),
        'access_url': qr.get_access_url()
    } for qr in qr_codes]
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_activate_qr(request, qr_code):
    """
    API endpoint to activate a QR code.
    POST /api/gateways/qr/activate/<qr_code>/
    """
    try:
        qr = get_object_or_404(PreGeneratedQR, qr_code=qr_code.upper())
        
        if qr.status != 'available':
            return Response(
                {'error': f'QR code is {qr.status} and cannot be activated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get vehicle details
        vehicle_type = request.data.get('vehicle_type', 'car')
        vehicle_number = request.data.get('vehicle_number', '')
        vehicle_model = request.data.get('vehicle_model', '')
        
        with transaction.atomic():
            # Create gateway
            gateway = Gateway.objects.create(
                owner=request.user,
                title=f"{vehicle_type.title()} - {vehicle_number}",
                context_type='vehicle',
                description=f"{vehicle_model}",
                identifier_text=vehicle_number
            )
            
            # Activate QR
            qr.activate(request.user, gateway, by_admin=False)
        
        return Response({
            'success': True,
            'qr_code': qr.qr_code,
            'gateway_id': str(gateway.id),
            'access_url': qr.get_access_url()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
