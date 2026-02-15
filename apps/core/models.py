"""
Core models for the gateway platform.
"""
import uuid
from django.db import models
from django.utils import timezone as django_timezone

# Import pricing models
from .pricing_models import PricingSettings


class BaseModel(models.Model):
    """
    Abstract base model with common fields.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class TagOrder(models.Model):
    """
    Physical QR tag orders from customers.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('cod_pending', 'COD Pending Delivery'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online Payment'),
        ('cod', 'Cash on Delivery'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_id = models.CharField(max_length=20, unique=True, db_index=True)
    
    # Customer Details
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    
    # Delivery Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)
    
    # Order Details
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='online', help_text="Payment method chosen by customer")
    
    # Distributor tracking (commission earned on successful payment)
    distributor_code = models.CharField(max_length=15, blank=True, db_index=True, help_text="Distributor's mobile number")
    
    # Tracking
    tracking_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tag_orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_id']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['phone']),
            models.Index(fields=['email']),
        ]
        app_label = 'core'
    
    def __str__(self):
        return f"{self.order_id} - {self.name} ({self.get_status_display()})"
    
    def get_full_address(self):
        """Get formatted full address."""
        return f"{self.address}, {self.city}, {self.state} - {self.pincode}"
    
    def mark_as_shipped(self, tracking_number=''):
        """Mark order as shipped."""
        self.status = 'shipped'
        self.shipped_at = django_timezone.now()
        if tracking_number:
            self.tracking_number = tracking_number
        self.save()
    
    def mark_as_delivered(self):
        """Mark order as delivered."""
        self.status = 'delivered'
        self.delivered_at = django_timezone.now()
        self.save()
