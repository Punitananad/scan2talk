"""
Recharge Plans and QR Wallet Models
"""
from django.db import models
from django.core.validators import MinValueValidator
from apps.core.models import BaseModel
import uuid


class RechargeCategory(BaseModel):
    """
    Categories for QR codes - determines if recharge is needed
    """
    CATEGORY_TYPES = [
        ('free', 'Free - No Recharge Needed'),
        ('prepaid', 'Prepaid - Recharge Required'),
        ('postpaid', 'Postpaid - Bill Later'),
        ('trial', 'Trial - Limited Free Usage'),
    ]
    
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES, default='prepaid')
    description = models.TextField(blank=True)
    
    # Free usage limits (for trial/free categories)
    free_messages_limit = models.IntegerField(default=0, help_text="Free messages per month")
    free_calls_limit = models.IntegerField(default=0, help_text="Free calls per month")
    
    # Pricing (for prepaid/postpaid)
    message_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    call_cost_per_minute = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Display
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code")
    icon = models.CharField(max_length=50, default='💳')
    
    class Meta:
        db_table = 'recharge_categories'
        verbose_name = 'Recharge Category'
        verbose_name_plural = 'Recharge Categories'
        ordering = ['-is_default', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class RechargePlan(BaseModel):
    """
    Recharge plans that users can purchase
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    # Pricing
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Credits
    message_credits = models.IntegerField(default=0, help_text="Number of messages")
    call_minutes = models.IntegerField(default=0, help_text="Call minutes")
    
    # Validity
    validity_days = models.IntegerField(default=30, help_text="Plan validity in days")
    
    # Bonus
    bonus_message_credits = models.IntegerField(default=0)
    bonus_call_minutes = models.IntegerField(default=0)
    
    # Display
    is_popular = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    color = models.CharField(max_length=7, default='#3B82F6')
    
    class Meta:
        db_table = 'recharge_plans'
        verbose_name = 'Recharge Plan'
        verbose_name_plural = 'Recharge Plans'
        ordering = ['display_order', '-amount']
    
    def __str__(self):
        return f"{self.name} - ₹{self.amount}"
    
    @property
    def total_message_credits(self):
        return self.message_credits + self.bonus_message_credits
    
    @property
    def total_call_minutes(self):
        return self.call_minutes + self.bonus_call_minutes


class QRWallet(BaseModel):
    """
    Individual wallet for each QR code
    """
    qr_code = models.OneToOneField(
        'gateways.PreGeneratedQR',
        on_delete=models.CASCADE,
        related_name='qr_wallet'
    )
    
    # Category
    category = models.ForeignKey(
        RechargeCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_wallets'
    )
    
    # Balance
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Credits
    message_credits = models.IntegerField(default=0)
    call_minutes = models.IntegerField(default=0)
    
    # Usage tracking
    total_messages_sent = models.IntegerField(default=0)
    total_calls_made = models.IntegerField(default=0)
    total_call_duration = models.IntegerField(default=0, help_text="Total call duration in seconds")
    
    # Free usage tracking (for trial/free categories)
    free_messages_used = models.IntegerField(default=0)
    free_calls_used = models.IntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True)
    
    # Auto-recharge
    auto_recharge_enabled = models.BooleanField(default=False)
    auto_recharge_plan = models.ForeignKey(
        RechargePlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auto_recharge_wallets'
    )
    auto_recharge_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    
    class Meta:
        db_table = 'qr_wallets'
        verbose_name = 'QR Wallet'
        verbose_name_plural = 'QR Wallets'
    
    def __str__(self):
        return f"Wallet for {self.qr_code.qr_code} - ₹{self.balance}"
    
    def can_send_message(self):
        """Check if QR can send a message"""
        if self.is_suspended:
            return False, "Wallet is suspended"
        
        if not self.category:
            return False, "No category assigned"
        
        # Free category
        if self.category.category_type == 'free':
            if self.category.free_messages_limit == 0:
                return True, "Unlimited free messages"
            if self.free_messages_used < self.category.free_messages_limit:
                return True, "Free message available"
            return False, "Free message limit reached"
        
        # Trial category
        if self.category.category_type == 'trial':
            if self.free_messages_used < self.category.free_messages_limit:
                return True, "Trial message available"
            if self.message_credits > 0:
                return True, "Paid credits available"
            return False, "No credits available"
        
        # Prepaid
        if self.category.category_type == 'prepaid':
            if self.message_credits > 0:
                return True, "Credits available"
            return False, "Insufficient credits"
        
        # Postpaid
        if self.category.category_type == 'postpaid':
            return True, "Postpaid - will be billed"
        
        return False, "Unknown category type"
    
    def can_make_call(self, duration_minutes=1):
        """Check if QR can make a call"""
        if self.is_suspended:
            return False, "Wallet is suspended"
        
        if not self.category:
            return False, "No category assigned"
        
        # Free category
        if self.category.category_type == 'free':
            if self.category.free_calls_limit == 0:
                return True, "Unlimited free calls"
            if self.free_calls_used < self.category.free_calls_limit:
                return True, "Free call available"
            return False, "Free call limit reached"
        
        # Trial category
        if self.category.category_type == 'trial':
            if self.free_calls_used < self.category.free_calls_limit:
                return True, "Trial call available"
            if self.call_minutes >= duration_minutes:
                return True, "Paid minutes available"
            return False, "No call minutes available"
        
        # Prepaid
        if self.category.category_type == 'prepaid':
            if self.call_minutes >= duration_minutes:
                return True, "Minutes available"
            return False, "Insufficient call minutes"
        
        # Postpaid
        if self.category.category_type == 'postpaid':
            return True, "Postpaid - will be billed"
        
        return False, "Unknown category type"
    
    def deduct_message_credit(self):
        """Deduct credit for sending a message"""
        if self.category.category_type in ['free', 'trial']:
            if self.free_messages_used < self.category.free_messages_limit:
                self.free_messages_used += 1
            else:
                self.message_credits -= 1
        elif self.category.category_type == 'prepaid':
            self.message_credits -= 1
        
        self.total_messages_sent += 1
        self.save()
    
    def deduct_call_minutes(self, minutes):
        """Deduct minutes for a call"""
        if self.category.category_type in ['free', 'trial']:
            if self.free_calls_used < self.category.free_calls_limit:
                self.free_calls_used += 1
            else:
                self.call_minutes -= minutes
        elif self.category.category_type == 'prepaid':
            self.call_minutes -= minutes
        
        self.total_calls_made += 1
        self.total_call_duration += (minutes * 60)
        self.save()
    
    def add_credits(self, message_credits=0, call_minutes=0, amount=0):
        """Add credits to wallet"""
        self.message_credits += message_credits
        self.call_minutes += call_minutes
        self.balance += amount
        self.save()


class QRWalletTransaction(BaseModel):
    """
    Transaction history for QR wallets
    """
    TRANSACTION_TYPES = [
        ('recharge', 'Recharge'),
        ('deduction', 'Deduction'),
        ('bonus', 'Bonus'),
        ('refund', 'Refund'),
        ('admin_credit', 'Admin Credit'),
        ('admin_debit', 'Admin Debit'),
    ]
    
    wallet = models.ForeignKey(QRWallet, on_delete=models.CASCADE, related_name='transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Credits
    message_credits = models.IntegerField(default=0)
    call_minutes = models.IntegerField(default=0)
    
    # Reference
    plan = models.ForeignKey(RechargePlan, on_delete=models.SET_NULL, null=True, blank=True)
    reference_id = models.CharField(max_length=100, blank=True)
    
    # Details
    description = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Admin action
    created_by = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='qr_wallet_transactions'
    )
    
    class Meta:
        db_table = 'qr_wallet_transactions'
        verbose_name = 'QR Wallet Transaction'
        verbose_name_plural = 'QR Wallet Transactions'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - ₹{self.amount} - {self.wallet.qr_code.qr_code}"
