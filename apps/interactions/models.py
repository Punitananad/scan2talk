"""
Interaction tracking and session management models.
"""
import uuid
from django.db import models
from django.utils import timezone as django_timezone
from apps.core.models import BaseModel
from apps.gateways.models import Gateway


class InteractionSession(BaseModel):
    """
    Temporary session for communication interactions.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('blocked', 'Blocked'),
    ]
    
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='interaction_sessions'
    )
    session_token = models.CharField(max_length=100, unique=True)
    
    # Request details
    channel = models.CharField(max_length=20)
    intent = models.CharField(max_length=20)
    message = models.TextField()
    
    # Client information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    
    # Session management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    expires_at = models.DateTimeField()
    
    # Processing
    processed_at = models.DateTimeField(null=True, blank=True)
    response_sent = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'interaction_sessions'
        indexes = [
            models.Index(fields=['session_token']),
            models.Index(fields=['gateway', 'status']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"Session {self.session_token} - {self.gateway.title}"
    
    def is_expired(self):
        """Check if session is expired."""
        return django_timezone.now() > self.expires_at
    
    def mark_completed(self):
        """Mark session as completed."""
        self.status = 'completed'
        self.processed_at = django_timezone.now()
        self.save(update_fields=['status', 'processed_at'])
    
    def mark_blocked(self):
        """Mark session as blocked."""
        self.status = 'blocked'
        self.processed_at = django_timezone.now()
        self.save(update_fields=['status', 'processed_at'])


class InteractionLog(BaseModel):
    """
    Log of all communication interactions.
    """
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='interactions'
    )
    session = models.ForeignKey(
        InteractionSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    
    # Communication details
    channel_used = models.CharField(max_length=20)
    intent = models.CharField(max_length=20)
    message_content = models.TextField()
    
    # Timing
    initiated_at = models.DateTimeField(default=django_timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Status
    was_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=100, blank=True)
    success = models.BooleanField(default=False)
    error_message = models.TextField(blank=True)
    
    # Client information
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Response details
    response_sent = models.BooleanField(default=False)
    response_channel = models.CharField(max_length=20, blank=True)
    response_message = models.TextField(blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)  # Additional data like location, device info, etc.
    
    class Meta:
        db_table = 'interaction_logs'
        indexes = [
            models.Index(fields=['gateway', 'initiated_at']),
            models.Index(fields=['channel_used']),
            models.Index(fields=['intent']),
            models.Index(fields=['was_blocked']),
            models.Index(fields=['success']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.gateway.title} - {self.channel_used} - {self.initiated_at}"
    
    def calculate_duration(self):
        """Calculate and update interaction duration."""
        if self.completed_at and self.initiated_at:
            delta = self.completed_at - self.initiated_at
            self.duration_seconds = int(delta.total_seconds())
            self.save(update_fields=['duration_seconds'])
    
    def mark_completed(self, success=True, error_message=''):
        """Mark interaction as completed."""
        self.completed_at = django_timezone.now()
        self.success = success
        self.error_message = error_message
        self.calculate_duration()
        self.save(update_fields=['completed_at', 'success', 'error_message', 'duration_seconds'])


class CommunicationAttempt(models.Model):
    """
    Track individual communication attempts (SMS, WhatsApp, etc.).
    """
    ATTEMPT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('rejected', 'Rejected'),
    ]
    
    interaction_log = models.ForeignKey(
        InteractionLog,
        on_delete=models.CASCADE,
        related_name='communication_attempts'
    )
    
    # Communication details
    channel = models.CharField(max_length=20)
    recipient = models.CharField(max_length=255)  # Phone number, email, etc.
    message_content = models.TextField()
    
    # Status tracking
    status = models.CharField(max_length=20, choices=ATTEMPT_STATUS_CHOICES, default='pending')
    external_id = models.CharField(max_length=255, blank=True)  # Provider's message ID
    
    # Timing
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_code = models.CharField(max_length=50, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    
    # Provider details
    provider_name = models.CharField(max_length=50, blank=True)  # 'twilio', 'whatsapp', etc.
    provider_response = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'communication_attempts'
        indexes = [
            models.Index(fields=['interaction_log', 'status']),
            models.Index(fields=['channel']),
            models.Index(fields=['status']),
            models.Index(fields=['external_id']),
        ]
    
    def __str__(self):
        return f"{self.channel} to {self.recipient} - {self.status}"
    
    def mark_sent(self, external_id=''):
        """Mark attempt as sent."""
        self.status = 'sent'
        self.sent_at = django_timezone.now()
        self.external_id = external_id
        self.save(update_fields=['status', 'sent_at', 'external_id'])
    
    def mark_delivered(self):
        """Mark attempt as delivered."""
        self.status = 'delivered'
        self.delivered_at = django_timezone.now()
        self.save(update_fields=['status', 'delivered_at'])
    
    def mark_failed(self, error_code='', error_message=''):
        """Mark attempt as failed."""
        self.status = 'failed'
        self.failed_at = django_timezone.now()
        self.error_code = error_code
        self.error_message = error_message
        self.save(update_fields=['status', 'failed_at', 'error_code', 'error_message'])


class InteractionFeedback(models.Model):
    """
    Feedback from gateway owners about interactions.
    """
    FEEDBACK_TYPE_CHOICES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate'),
        ('helpful', 'Helpful'),
        ('resolved', 'Issue Resolved'),
        ('escalate', 'Needs Escalation'),
    ]
    
    interaction_log = models.OneToOneField(
        InteractionLog,
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPE_CHOICES)
    notes = models.TextField(blank=True)
    
    # Actions taken
    blocked_contact = models.BooleanField(default=False)
    forwarded_to_support = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'interaction_feedback'
        indexes = [
            models.Index(fields=['feedback_type']),
            models.Index(fields=['created_at']),
        ]


class InteractionAnalytics(models.Model):
    """
    Daily analytics aggregation for interactions.
    """
    gateway = models.ForeignKey(
        Gateway,
        on_delete=models.CASCADE,
        related_name='interaction_analytics'
    )
    date = models.DateField()
    
    # Volume metrics
    total_interactions = models.PositiveIntegerField(default=0)
    successful_interactions = models.PositiveIntegerField(default=0)
    blocked_interactions = models.PositiveIntegerField(default=0)
    failed_interactions = models.PositiveIntegerField(default=0)
    
    # Channel breakdown
    sms_interactions = models.PositiveIntegerField(default=0)
    whatsapp_interactions = models.PositiveIntegerField(default=0)
    ivr_interactions = models.PositiveIntegerField(default=0)
    email_interactions = models.PositiveIntegerField(default=0)
    
    # Intent breakdown
    general_interactions = models.PositiveIntegerField(default=0)
    emergency_interactions = models.PositiveIntegerField(default=0)
    complaint_interactions = models.PositiveIntegerField(default=0)
    business_interactions = models.PositiveIntegerField(default=0)
    
    # Performance metrics
    avg_response_time_seconds = models.FloatField(null=True, blank=True)
    peak_hour = models.PositiveIntegerField(null=True, blank=True)  # 0-23
    
    # Geographic data (if available)
    top_countries = models.JSONField(default=dict)
    top_cities = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(default=django_timezone.now)
    
    class Meta:
        db_table = 'interaction_analytics'
        unique_together = ['gateway', 'date']
        indexes = [
            models.Index(fields=['gateway', 'date']),
            models.Index(fields=['date']),
        ]