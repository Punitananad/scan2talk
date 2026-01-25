"""
User and authentication models.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone as django_timezone
from apps.core.utils import encrypt_data, decrypt_data

# Import wallet models to register them
from .wallet_models import Wallet, WalletTransaction, RechargeOrder

# Import recharge models to register them
from .recharge_models import RechargeCategory, RechargePlan, QRWallet, QRWalletTransaction, DistributorPayment


class User(AbstractUser):
    """
    Custom user model with enhanced security and business fields.
    """
    ROLE_CHOICES = [
        ('individual', 'Individual'),
        ('business', 'Business'),
        ('enterprise', 'Enterprise'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255, blank=True)  # Encrypted
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='individual')
    is_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    # Business fields
    company_name = models.CharField(max_length=255, blank=True)
    business_registration = models.CharField(max_length=100, blank=True)
    
    # Subscription and limits
    subscription_tier = models.CharField(max_length=20, default='free')
    gateway_limit = models.PositiveIntegerField(default=5)
    monthly_interaction_limit = models.PositiveIntegerField(default=100)
    
    # Distributor fields
    is_distributor = models.BooleanField(default=False)
    distributor_verified = models.BooleanField(default=False)
    distributor_registered_at = models.DateTimeField(null=True, blank=True)
    distributor_total_qr = models.PositiveIntegerField(default=0, help_text="Total QR codes assigned by admin")
    distributor_commission_per_activation = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Commission earned per QR activation")
    distributor_revoked = models.BooleanField(default=False, help_text="Has distributor status been revoked?")
    distributor_revoked_at = models.DateTimeField(null=True, blank=True, help_text="When was distributor status revoked?")
    distributor_revoked_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='distributors_revoked',
        help_text='Admin who revoked distributor status'
    )
    distributor_revoke_reason = models.TextField(blank=True, help_text="Reason for revoking distributor status")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['subscription_tier']),
        ]
    
    def save(self, *args, **kwargs):
        # Encrypt phone number before saving
        if self.phone and not self.phone.startswith('gAAAAAB'):  # Not already encrypted
            self.phone = encrypt_data(self.phone)
        super().save(*args, **kwargs)
    
    def get_decrypted_phone(self):
        """Get decrypted phone number."""
        if self.phone:
            try:
                return decrypt_data(self.phone)
            except:
                return self.phone
        return ''
    
    def is_account_locked(self):
        """Check if account is locked due to failed login attempts."""
        if self.account_locked_until:
            return django_timezone.now() < self.account_locked_until
        return False
    
    def lock_account(self, duration_minutes=30):
        """Lock account for specified duration."""
        self.account_locked_until = django_timezone.now() + django_timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Unlock account and reset failed attempts."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def can_create_gateway(self):
        """Check if user can create more gateways."""
        current_count = self.gateways.filter(is_active=True).count()
        return current_count < self.gateway_limit
    
    def get_gateway_usage(self):
        """Get gateway usage statistics."""
        total_gateways = self.gateways.filter(is_active=True).count()
        return {
            'used': total_gateways,
            'limit': self.gateway_limit,
            'remaining': max(0, self.gateway_limit - total_gateways)
        }


class UserProfile(models.Model):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # Privacy settings
    public_profile = models.BooleanField(default=False)
    show_activity = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'


class UserSession(models.Model):
    """
    Track user sessions for security monitoring.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    last_activity = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]


class LoginAttempt(models.Model):
    """
    Track login attempts for security monitoring.
    """
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    success = models.BooleanField()
    failure_reason = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'login_attempts'
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]