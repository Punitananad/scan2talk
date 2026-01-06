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
        
        context.update({
            'gateway_usage': user.get_gateway_usage(),
            'recent_gateways': user.gateways.filter(is_active=True)[:5],
            'recent_interactions': user.gateways.filter(is_active=True)
                .prefetch_related('interactions')[:10],
        })
        
        return context


class ProfileView(TemplateView):
    """User profile view."""
    template_name = 'accounts/profile.html'
    
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


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