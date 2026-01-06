"""
Security and rate limiting middleware.
"""
import time
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    """
    def process_response(self, request, response):
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Global rate limiting middleware for public endpoints.
    """
    def process_request(self, request):
        # Skip rate limiting for authenticated users on non-public endpoints
        if request.user.is_authenticated and not request.path.startswith('/g/'):
            return None
            
        # Get client IP
        ip = self.get_client_ip(request)
        
        # Rate limit key
        cache_key = f"rate_limit:{ip}"
        
        # Get current request count
        current_requests = cache.get(cache_key, 0)
        
        # Rate limit: 60 requests per minute for public endpoints
        if current_requests >= 60:
            return JsonResponse(
                {"detail": "Rate limit exceeded. Please try again later."},
                status=429
            )
        
        # Increment counter
        cache.set(cache_key, current_requests + 1, 60)
        
        return None
    
    def get_client_ip(self, request):
        """Get the client's IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip