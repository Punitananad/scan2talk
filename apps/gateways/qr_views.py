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
            
            # Use custom batch name with unique suffix to ensure uniqueness
            batch_number = f"{batch_name}-{generate_short_code(4).upper()}"
            
            # Create batch record
            batch = QRBatch.objects.create(
                batch_number=batch_number,
                quantity=quantity,
                purpose=purpose,
                notes=notes,
                category=category,
                created_by=request.user,
                available_count=quantity
            )
            
            # Generate QR codes
            qr_codes = []
            for _ in range(quantity):
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
            
            messages.success(request, f'Successfully generated {quantity} QR codes in batch {batch_number}' + 
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
    """
    try:
        # qr_id is actually gateway_id in this context
        gateway = get_object_or_404(Gateway, id=qr_id)
        
        if not gateway.is_active:
            messages.error(request, f'Gateway is already inactive')
            return redirect('gateways:registrations')
        
        # Deactivate the gateway
        gateway.is_active = False
        gateway.save()
        
        # If there's an associated QR code, reset it
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


@require_http_methods(["GET", "POST"])
def activate_qr_code(request, qr_code):
    """
    User activates their QR code by scanning or entering the code.
    Route: /activate/<qr_code>/
    NO LOGIN REQUIRED - Uses phone OTP authentication
    Auto-login if already activated by this user
    """
    from django.contrib.auth import login
    
    qr = get_object_or_404(PreGeneratedQR, qr_code=qr_code.upper())
    
    # Increment access count
    qr.increment_access_count()
    
    # Check if already activated
    if qr.status == 'activated':
        # If user is authenticated and is the owner, redirect to dashboard
        if request.user.is_authenticated and request.user == qr.owner:
            messages.info(request, f'This QR code is already activated by you.')
            return redirect('accounts:dashboard')
        
        # For everyone else (visitors and non-authenticated users), redirect to contact page
        # This ensures visitors always see the contact form, not the login page
        return redirect('core:gateway_access', identifier=qr.qr_code)
    
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
            
            # Skip OTP verification - go directly to step 3
            # Store phone in session
            request.session['activation_phone'] = phone
            request.session['activation_qr_code'] = qr_code
            
            # Mark phone as verified without OTP
            from apps.accounts.phone_auth import mark_phone_verified
            mark_phone_verified(phone)
            
            messages.success(request, 'Phone number saved. Please enter vehicle details.')
            return redirect(f'/gateways/activate/{qr_code}/?step=3')
        
        context = {'qr': qr, 'step': 1}
        return render(request, 'gateways/activate_step1_phone.html', context)
    
    # Step 2: Verify OTP (DISABLED - skipping OTP verification)
    elif step == '2':
        # Redirect to step 3 directly
        return redirect(f'/gateways/activate/{qr_code}/?step=3')
    
    # Step 3: Enter details and activate
    elif step == '3':
        phone = request.session.get('activation_phone')
        if not phone:
            return redirect(f'/gateways/activate/{qr_code}/?step=1')
        
        # Skip OTP verification check - phone is already marked as verified in step 1
        
        if request.method == 'POST':
            try:
                with transaction.atomic():
                    # Get form data
                    name = request.POST.get('name', '').strip()
                    vehicle_type = request.POST.get('vehicle_type', 'car')
                    vehicle_number = request.POST.get('vehicle_number', '').strip().upper()
                    vehicle_model = request.POST.get('vehicle_model', '').strip()
                    
                    if not name or not vehicle_number:
                        messages.error(request, 'Name and vehicle number are required')
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
                    gateway = Gateway.objects.create(
                        owner=user,
                        owner_name=name,  # Save owner's name
                        title=f"{vehicle_type.title()} - {vehicle_number}",
                        context_type='vehicle',
                        description=f"{vehicle_model}",
                        identifier_text=vehicle_number
                    )
                    
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
    """
    qr = get_object_or_404(PreGeneratedQR, qr_code=qr_code.upper())
    
    # Increment access count
    qr.increment_access_count()
    
    # If not activated, show activation page (for owner to register)
    if qr.status != 'activated':
        return redirect('gateways:activate_qr', qr_code=qr_code)
    
    # If activated, ALWAYS show the gateway contact form (for visitors to contact owner)
    # Never show login page - visitors should directly see contact form
    if qr.gateway:
        return redirect('core:gateway_access', identifier=qr.qr_code)
    
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
