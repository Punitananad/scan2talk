"""
Wallet management models for user balance and transactions.
"""
import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone as django_timezone
from django.core.validators import MinValueValidator


class Wallet(models.Model):
    """
    User wallet for managing balance and call credits.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    
    # Balance in rupees
    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Call credits (1 rupee = 1 call)
    call_credits = models.PositiveIntegerField(default=0)
    
    # Tracking
    total_recharged = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_spent = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_calls_made = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_frozen = models.BooleanField(default=False)
    frozen_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_recharge_at = models.DateTimeField(null=True, blank=True)
    last_transaction_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'wallets'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active', 'is_frozen']),
        ]
    
    def __str__(self):
        return f"Wallet for {self.user.email} - ₹{self.balance} ({self.call_credits} credits)"
    
    def add_balance(self, amount, transaction_type='recharge', reference=None, notes=''):
        """Add balance to wallet and update call credits."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if self.is_frozen:
            raise ValueError("Wallet is frozen")
        
        self.balance += Decimal(str(amount))
        # 1 rupee = 1 call credit
        credits_to_add = int(amount)
        self.call_credits += credits_to_add
        
        if transaction_type == 'recharge':
            self.total_recharged += Decimal(str(amount))
            self.last_recharge_at = django_timezone.now()
        
        self.last_transaction_at = django_timezone.now()
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=self.balance,
            credits_after=self.call_credits,
            reference=reference,
            notes=notes
        )
        
        return self
    
    def deduct_balance(self, amount, transaction_type='call', reference=None, notes=''):
        """Deduct balance from wallet."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if self.is_frozen:
            raise ValueError("Wallet is frozen")
        
        if self.balance < Decimal(str(amount)):
            raise ValueError("Insufficient balance")
        
        self.balance -= Decimal(str(amount))
        self.total_spent += Decimal(str(amount))
        self.last_transaction_at = django_timezone.now()
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=-amount,
            balance_after=self.balance,
            credits_after=self.call_credits,
            reference=reference,
            notes=notes
        )
        
        return self
    
    def deduct_call_credit(self, qr_code=None, notes=''):
        """Deduct one call credit (costs 1 rupee)."""
        if self.call_credits <= 0:
            raise ValueError("No call credits available")
        
        if self.is_frozen:
            raise ValueError("Wallet is frozen")
        
        self.call_credits -= 1
        self.total_calls_made += 1
        self.balance -= Decimal('1.00')
        self.total_spent += Decimal('1.00')
        self.last_transaction_at = django_timezone.now()
        self.save()
        
        # Create transaction record
        WalletTransaction.objects.create(
            wallet=self,
            transaction_type='call',
            amount=Decimal('-1.00'),
            balance_after=self.balance,
            credits_after=self.call_credits,
            reference=qr_code,
            notes=notes or 'Call credit used'
        )
        
        return self
    
    def freeze(self, reason=''):
        """Freeze wallet to prevent transactions."""
        self.is_frozen = True
        self.frozen_reason = reason
        self.save()
    
    def unfreeze(self):
        """Unfreeze wallet."""
        self.is_frozen = False
        self.frozen_reason = ''
        self.save()
    
    def has_sufficient_credits(self, required=1):
        """Check if wallet has sufficient call credits."""
        return self.call_credits >= required and not self.is_frozen


class WalletTransaction(models.Model):
    """
    Record of all wallet transactions.
    """
    TRANSACTION_TYPES = [
        ('recharge', 'Recharge'),
        ('call', 'Call Credit Used'),
        ('refund', 'Refund'),
        ('adjustment', 'Admin Adjustment'),
        ('bonus', 'Bonus Credit'),
        ('penalty', 'Penalty Deduction'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    balance_after = models.DecimalField(max_digits=10, decimal_places=2)
    credits_after = models.PositiveIntegerField(default=0)
    
    # Payment gateway details
    payment_id = models.CharField(max_length=100, blank=True, db_index=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    
    # Reference and notes
    reference = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'wallet_transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
            models.Index(fields=['payment_id']),
            models.Index(fields=['payment_status']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - ₹{self.amount} ({self.created_at})"
    
    def mark_completed(self):
        """Mark transaction as completed."""
        self.payment_status = 'completed'
        self.completed_at = django_timezone.now()
        self.save()
    
    def mark_failed(self, reason=''):
        """Mark transaction as failed."""
        self.payment_status = 'failed'
        self.notes = f"{self.notes}\nFailed: {reason}".strip()
        self.save()


class RechargeOrder(models.Model):
    """
    Recharge orders for tracking payment gateway transactions.
    """
    STATUS_CHOICES = [
        ('created', 'Created'),
        ('pending', 'Pending Payment'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recharge_orders'
    )
    wallet = models.ForeignKey(
        Wallet,
        on_delete=models.CASCADE,
        related_name='recharge_orders'
    )
    
    # Order details
    order_id = models.CharField(max_length=100, unique=True, db_index=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    credits_to_add = models.PositiveIntegerField()
    
    # Payment gateway details
    gateway_order_id = models.CharField(max_length=200, blank=True)
    gateway_payment_id = models.CharField(max_length=200, blank=True)
    gateway_signature = models.CharField(max_length=500, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', db_index=True)
    failure_reason = models.TextField(blank=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'recharge_orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['order_id']),
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['gateway_order_id']),
        ]
    
    def __str__(self):
        return f"Order {self.order_id} - ₹{self.amount} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = self.generate_order_id()
        if not self.credits_to_add:
            self.credits_to_add = int(self.amount)
        super().save(*args, **kwargs)
    
    def generate_order_id(self):
        """Generate unique order ID."""
        import time
        timestamp = int(time.time())
        random_suffix = uuid.uuid4().hex[:6].upper()
        return f"ORD{timestamp}{random_suffix}"
    
    def mark_completed(self, gateway_payment_id='', gateway_signature=''):
        """Mark order as completed and credit wallet."""
        if self.status == 'completed':
            return
        
        self.status = 'completed'
        self.gateway_payment_id = gateway_payment_id
        self.gateway_signature = gateway_signature
        self.completed_at = django_timezone.now()
        self.save()
        
        # Credit wallet
        self.wallet.add_balance(
            amount=float(self.amount),
            transaction_type='recharge',
            reference=self.order_id,
            notes=f'Recharge order {self.order_id}'
        )
    
    def mark_failed(self, reason=''):
        """Mark order as failed."""
        self.status = 'failed'
        self.failure_reason = reason
        self.save()
