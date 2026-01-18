"""
Account views and API endpoints.
"""
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.generic import TemplateView, View
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django_ratelimit.decorators import ratelimit
from .models import User, LoginAttempt
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    PasswordChangeSerializer
)


class DashboardView(TemplateView):
    """User dashboard view."""
    template_name = 'accounts/dashboard.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Check if user has any paid categories (prepaid or postpaid)
        from apps.gateways.qr_models import PreGeneratedQR
        user_qr_codes = PreGeneratedQR.objects.filter(
            owner=user,
            status='activated'
        ).select_related('category')
        
        show_wallet = False
        for qr in user_qr_codes:
            if qr.category and qr.category.category_type in ['prepaid', 'postpaid']:
                show_wallet = True
                break
        
        context.update({
            'gateway_usage': user.get_gateway_usage(),
            'recent_gateways': user.gateways.filter(is_active=True)[:5],
            'recent_interactions': user.gateways.filter(is_active=True)
                .prefetch_related('interactions')[:10],
            'show_wallet': show_wallet,
        })
        
        return context


class ProfileView(TemplateView):
    """User profile view."""
    template_name = 'accounts/profile.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get user's QR codes with categories
        from apps.gateways.qr_models import PreGeneratedQR
        from apps.accounts.recharge_models import QRWallet
        from django.db.models import Sum
        
        user_qr_codes = PreGeneratedQR.objects.filter(
            owner=user,
            status='activated'
        ).select_related('category', 'gateway')
        
        # Get unique categories for this user
        categories = set()
        for qr in user_qr_codes:
            if qr.category:
                categories.add(qr.category)
        
        # Check if user has any paid categories (prepaid or postpaid)
        # Only show wallet if user has prepaid or postpaid categories
        show_wallet = False
        for category in categories:
            if category.category_type in ['prepaid', 'postpaid']:
                show_wallet = True
                break
        
        # Calculate total wallet balance across all QR codes
        total_balance = QRWallet.objects.filter(
            qr_code__owner=user,
            is_active=True
        ).aggregate(total=Sum('balance'))['total'] or 0
        
        context['user_qr_codes'] = user_qr_codes
        context['user_categories'] = list(categories)
        context['wallet_balance'] = total_balance
        context['show_wallet'] = show_wallet
        
        return context


# API Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST')
def register_api(request):
    """User registration API endpoint."""
    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user_id': user.id,
            'email': user.email,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@ratelimit(key='ip', rate='10/m', method='POST')
def login_api(request):
    """User login API endpoint."""
    serializer = UserLoginSerializer(data=request.data)
    
    # Log login attempt
    LoginAttempt.objects.create(
        email=request.data.get('email', ''),
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        success=False
    )
    
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Reset failed attempts on successful login
        user.unlock_account()
        
        # Update login attempt
        LoginAttempt.objects.filter(
            email=user.email,
            ip_address=get_client_ip(request)
        ).order_by('-created_at').first().update(success=True)
        
        # Update last login IP
        user.last_login_ip = get_client_ip(request)
        user.save(update_fields=['last_login_ip'])
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user_id': user.id,
            'email': user.email,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
    
    # Handle failed login
    email = request.data.get('email')
    if email:
        try:
            user = User.objects.get(email=email)
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.lock_account()
            
            user.save(update_fields=['failed_login_attempts'])
        except User.DoesNotExist:
            pass
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def logout_api(request):
    """User logout API endpoint."""
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)


def logout_web(request):
    """Web logout view - logs out and redirects to home."""
    from django.contrib.auth import logout as auth_logout
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('core:home')


def phone_login(request):
    """Phone-based login without OTP - creates account if doesn't exist."""
    from django.contrib.auth import login as auth_login
    from .phone_auth import get_or_create_user_by_phone
    
    if request.method == 'POST':
        phone = request.POST.get('phone', '').strip()
        
        if not phone or len(phone) != 10:
            messages.error(request, 'Please enter a valid 10-digit mobile number.')
            return redirect('accounts:phone_login')
        
        # Find user by phone
        users = User.objects.all()
        user_found = None
        
        for user in users:
            if user.get_decrypted_phone() == phone:
                user_found = user
                break
        
        # If user not found, create a new user
        if not user_found:
            user_found, created = get_or_create_user_by_phone(phone, name=f"User {phone[-4:]}")
        
        # Check if user has any QR codes
        from apps.gateways.qr_models import PreGeneratedQR
        user_qr_count = PreGeneratedQR.objects.filter(owner=user_found).count()
        
        # Login the user
        auth_login(request, user_found, backend='django.contrib.auth.backends.ModelBackend')
        
        if user_qr_count == 0:
            # User has no QR codes - show message and redirect to home
            messages.warning(
                request,
                'Welcome! You don\'t have any QR codes yet. Get your first QR code to get started!'
            )
            return redirect('core:home')
        else:
            # User has QR codes - go to dashboard
            messages.success(request, f'Welcome back, {user_found.first_name or user_found.email}!')
            return redirect('accounts:dashboard')
    
    return render(request, 'accounts/phone_login.html')


class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    """User profile API endpoint."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user.profile


class PasswordChangeAPIView(generics.GenericAPIView):
    """Password change API endpoint."""
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_client_ip(request):
    """Get client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip