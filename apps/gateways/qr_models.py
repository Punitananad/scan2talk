"""
Pre-generated QR code models for vehicle gateway system.
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone as django_timezone
from apps.core.utils import generate_short_code, generate_qr_code


class PreGeneratedQR(models.Model):
    """
    Pre-generated QR codes that can be activated by users later.
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('activated', 'Activated'),
        ('expired', 'Expired'),
        ('disabled', 'Disabled'),
    ]
    
    SERVICE_MODE_CHOICES = [
        ('direct', 'Direct Service (Free)'),
        ('wallet', 'Wallet Service (Paid)'),
        ('both', 'Both Services'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.CharField(max_length=20, unique=True, db_index=True)
    qr_image = models.ImageField(upload_to='qr_codes/pregenerated/', null=True, blank=True)
    
    # Service mode configuration (Admin controlled)
    service_mode = models.CharField(
        max_length=20,
        choices=SERVICE_MODE_CHOICES,
        default='direct',
        help_text='Admin decides if this QR uses wallet service, direct service, or both'
    )
    wallet_enabled = models.BooleanField(
        default=False,
        help_text='Enable wallet-based paid calls for this QR'
    )
    direct_service_enabled = models.BooleanField(
        default=True,
        help_text='Enable free direct service for this QR'
    )
    
    # Status and ownership
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', db_index=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_codes'
    )
    gateway = models.OneToOneField(
        'Gateway',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_code'
    )
    
    # Activation details
    activation_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    activated_by_admin = models.BooleanField(default=False)
    
    # Metadata
    batch_number = models.CharField(max_length=50, blank=True, db_index=True)
    category = models.ForeignKey(
        'accounts.RechargeCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_codes',
        help_text='Category determines pricing and features'
    )
    notes = models.TextField(blank=True)
    
    # Tracking
    access_count = models.PositiveIntegerField(default=0)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'pregenerated_qr_codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['qr_code']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['batch_number']),
        ]
    
    def __str__(self):
        return f"QR-{self.qr_code} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Generate QR code if not provided
        if not self.qr_code:
            self.qr_code = self.generate_unique_code()
        
        # Generate activation token if not provided
        if not self.activation_token:
            self.activation_token = self.generate_activation_token()
        
        # Check if we need to generate QR image
        generate_image = not self.qr_image and not kwargs.pop('skip_qr_generation', False)
        
        super().save(*args, **kwargs)
        
        # Generate QR image after saving (only once)
        if generate_image:
            self.generate_qr_image()
    
    def generate_unique_code(self):
        """Generate a unique QR code identifier."""
        while True:
            code = generate_short_code(8).upper()
            if not PreGeneratedQR.objects.filter(qr_code=code).exists():
                return code
    
    def generate_activation_token(self):
        """Generate a unique activation token."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def generate_qr_image(self):
        """Generate QR code image."""
        # Use http for local development, https for production
        protocol = 'http' if settings.DEBUG else 'https'
        url = f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{self.qr_code}/"
        qr_image = generate_qr_code(url)
        self.qr_image.save(
            f'qr_{self.qr_code}.png',
            qr_image,
            save=False  # Don't trigger another save
        )
        # Save only the qr_image field
        super(PreGeneratedQR, self).save(update_fields=['qr_image'])
    
    def get_activation_url(self):
        """Get the activation URL for this QR code."""
        protocol = 'http' if settings.DEBUG else 'https'
        return f"{protocol}://{settings.PLATFORM_DOMAIN}/gateways/activate/{self.qr_code}/"
    
    def get_access_url(self):
        """Get the access URL after activation."""
        protocol = 'http' if settings.DEBUG else 'https'
        if self.status == 'activated' and self.gateway:
            return f"{protocol}://{settings.PLATFORM_DOMAIN}/g/{self.qr_code}/"
        return self.get_activation_url()
    
    def activate(self, user, gateway=None, by_admin=False):
        """
        Activate this QR code for a user.
        CRITICAL: Once activated, the QR and gateway must remain permanently valid.
        """
        if self.status != 'available':
            raise ValueError(f"QR code is {self.status}, cannot activate")
        
        if not gateway:
            raise ValueError("Gateway is required for activation")
        
        if not gateway.is_active:
            raise ValueError("Gateway must be active for activation")
        
        self.owner = user
        self.gateway = gateway
        self.status = 'activated'
        self.activated_at = django_timezone.now()
        self.activated_by_admin = by_admin
        self.save()
        
        return self
    
    def reserve(self, user):
        """Reserve this QR code for a user (temporary hold)."""
        if self.status != 'available':
            raise ValueError(f"QR code is {self.status}, cannot reserve")
        
        self.owner = user
        self.status = 'reserved'
        self.save()
        
        return self
    
    def release(self):
        """Release a reserved QR code back to available."""
        if self.status == 'reserved':
            self.owner = None
            self.status = 'available'
            self.save()
        
        return self
    
    def increment_access_count(self):
        """Increment the access counter."""
        self.access_count += 1
        self.last_accessed_at = django_timezone.now()
        self.save(update_fields=['access_count', 'last_accessed_at'])
    
    def is_expired(self):
        """Check if QR code has expired."""
        if self.expires_at:
            return django_timezone.now() > self.expires_at
        return False


class QRBatch(models.Model):
    """
    Batch of pre-generated QR codes for tracking and management.
    """
    STATUS_CHOICES = [
        ('generated', 'Generated'),
        ('sent_for_print', 'Sent for Print'),
        ('printing', 'Printing'),
        ('printed', 'Printed'),
        ('delivered', 'Delivered'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_number = models.CharField(max_length=50, unique=True, db_index=True)
    quantity = models.PositiveIntegerField()
    purpose = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    # Print Status Tracking
    print_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='generated',
        help_text='Current status of batch printing'
    )
    sent_for_print_at = models.DateTimeField(null=True, blank=True)
    printing_started_at = models.DateTimeField(null=True, blank=True)
    printed_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    print_notes = models.TextField(blank=True, help_text='Notes about printing process')
    
    # Category assignment
    category = models.ForeignKey(
        'accounts.RechargeCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_batches',
        help_text='Category for all QR codes in this batch'
    )
    
    # Statistics
    activated_count = models.PositiveIntegerField(default=0)
    reserved_count = models.PositiveIntegerField(default=0)
    available_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_qr_batches'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'qr_batches'
        ordering = ['-created_at']
        verbose_name_plural = 'QR Batches'
    
    def __str__(self):
        return f"Batch {self.batch_number} ({self.quantity} codes)"
    
    def update_statistics(self):
        """Update batch statistics."""
        qr_codes = PreGeneratedQR.objects.filter(batch_number=self.batch_number)
        self.activated_count = qr_codes.filter(status='activated').count()
        self.reserved_count = qr_codes.filter(status='reserved').count()
        self.available_count = qr_codes.filter(status='available').count()
        self.save(update_fields=['activated_count', 'reserved_count', 'available_count'])
    
    def get_status_display_color(self):
        """Get color for status badge."""
        colors = {
            'generated': 'blue',
            'sent_for_print': 'yellow',
            'printing': 'orange',
            'printed': 'green',
            'delivered': 'purple',
        }
        return colors.get(self.print_status, 'gray')

