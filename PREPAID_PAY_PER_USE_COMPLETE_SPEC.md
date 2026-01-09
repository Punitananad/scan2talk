# Prepaid Pay-Per-Use System - Complete Implementation Specification

## 📋 Executive Summary

This document provides a complete, production-ready specification for implementing a pay-per-use system for Prepaid category QR codes. The system allows owners to start with ₹0 balance and ensures contact always works - either owner pays (if they have balance) or visitor pays (if owner has ₹0).

## 🎯 Core Requirements

### Business Logic
1. **Owner's QR wallet auto-created** with ₹0 balance on activation
2. **If owner has balance**: Deduct ₹1 per call/message from owner's wallet
3. **If owner has ₹0**: Visitor pays ₹1 to contact owner
4. **One-time registration** for owner, then direct contact for visitors
5. **No spam**: ₹1 charge prevents abuse

### Pricing
- **Message**: ₹1 per message
- **Call**: ₹1 per call
- **Who pays**: Owner (if balance > 0) OR Visitor (if owner balance = 0)

## 🏗️ System Architecture

### Phase 1: Auto-Create QR Wallet on Activation
### Phase 2: Balance Checking Logic
### Phase 3: Visitor Payment Flow
### Phase 4: Wallet Deduction Logic
### Phase 5: UI Updates

---

## 📦 PHASE 1: Auto-Create QR Wallet on Activation

### File: `apps/gateways/qr_views.py`
### Function: `activate_qr_code()`

**Current State**: QR activation creates gateway but doesn't create wallet for prepaid categories

**Required Changes**:

```python
# In activate_qr_code() function, after gateway creation and qr.activate()
# Add this code block:

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
```

**Location**: After line where `qr.activate(user, gateway, by_admin=False)` is called

**Testing**:
1. Create a QR code with Prepaid category
2. Activate the QR code
3. Check database: `QRWallet` should exist with `balance=0.00`
4. Verify `qr_code.qr_wallet` relationship works

---

## 📦 PHASE 2: Balance Checking Logic

### File: `apps/core/views.py`
### Class: `GatewayAccessView`

**Current State**: Shows contact form without checking wallet balance

**Required Changes**:

```python
# In get() method, after finding gateway, add balance check:

def get(self, request, identifier):
    """Display gateway access form."""
    try:
        # ... existing code to find gateway ...
        
        # Check if this is a prepaid category QR
        payment_required = False
        payer = None
        cost_per_action = 0.00
        
        try:
            from apps.gateways.qr_models import PreGeneratedQR
            qr = PreGeneratedQR.objects.get(
                qr_code=identifier.upper(),
                status='activated'
            )
            
            if qr.category and qr.category.category_type == 'prepaid':
                # Check wallet balance
                wallet = qr.qr_wallet
                
                if wallet.balance >= 1.00:
                    # Owner has balance - will be deducted
                    payment_required = False
                    payer = 'owner'
                else:
                    # Owner has ₹0 - visitor must pay
                    payment_required = True
                    payer = 'visitor'
                    cost_per_action = 1.00
        except:
            pass  # Not a QR code or no wallet
        
        context = {
            'gateway': gateway,
            'entry_point': entry_point,
            'available_channels': available_channels,
            'identifier': identifier,
            'payment_required': payment_required,
            'payer': payer,
            'cost_per_action': cost_per_action,
        }
        
        return render(request, 'core/gateway_access.html', context)
```

**Testing**:
1. Owner with ₹0 balance: `payment_required=True, payer='visitor'`
2. Owner with ₹10 balance: `payment_required=False, payer='owner'`
3. Free category: `payment_required=False, payer=None`

---

## 📦 PHASE 3: Visitor Payment Flow

### 3.1 New Model: VisitorPayment

**File**: `apps/accounts/recharge_models.py`

```python
class VisitorPayment(BaseModel):
    """
    Track visitor payments when owner's wallet is empty
    """
    qr_code = models.ForeignKey(
        'gateways.PreGeneratedQR',
        on_delete=models.CASCADE,
        related_name='visitor_payments'
    )
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=1.00)
    payment_type = models.CharField(
        max_length=20,
        choices=[('message', 'Message'), ('call', 'Call')],
        default='message'
    )
    
    # Visitor info (optional, for tracking)
    visitor_phone = models.CharField(max_length=20, blank=True)
    visitor_ip = models.GenericIPAddressField(blank=True, null=True)
    
    # PhonePe payment tracking
    order_id = models.CharField(max_length=100, unique=True)
    gateway_order_id = models.CharField(max_length=100, blank=True)
    gateway_payment_id = models.CharField(max_length=100, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Message/Call content (stored after payment)
    message_content = models.TextField(blank=True)
    intent = models.CharField(max_length=50, blank=True)
    channel = models.CharField(max_length=20, blank=True)
    
    # Completion tracking
    communication_sent = models.BooleanField(default=False)
    communication_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'visitor_payments'
        verbose_name = 'Visitor Payment'
        verbose_name_plural = 'Visitor Payments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Visitor Payment ₹{self.amount} - {self.qr_code.qr_code} - {self.status}"
    
    def mark_completed(self, gateway_payment_id):
        """Mark payment as completed"""
        self.status = 'completed'
        self.gateway_payment_id = gateway_payment_id
        self.save()
    
    def mark_failed(self, reason=''):
        """Mark payment as failed"""
        self.status = 'failed'
        self.save()
```

### 3.2 New View: Visitor Payment Initiation

**File**: `apps/accounts/wallet_views.py`

```python
@require_http_methods(["POST"])
def initiate_visitor_payment(request, identifier):
    """
    Initiate visitor payment for contacting owner with ₹0 balance
    POST /api/v1/auth/wallet/visitor-pay/<identifier>/
    """
    try:
        from apps.gateways.qr_models import PreGeneratedQR
        
        # Get QR code
        qr = get_object_or_404(
            PreGeneratedQR,
            qr_code=identifier.upper(),
            status='activated'
        )
        
        # Verify it's prepaid and owner has ₹0
        if not qr.category or qr.category.category_type != 'prepaid':
            return JsonResponse({
                'success': False,
                'error': 'This QR code does not require payment'
            })
        
        wallet = qr.qr_wallet
        if wallet.balance >= 1.00:
            return JsonResponse({
                'success': False,
                'error': 'Owner has balance. No payment required.'
            })
        
        # Get form data
        payment_type = request.POST.get('payment_type', 'message')  # 'message' or 'call'
        message_content = request.POST.get('message', '')
        intent = request.POST.get('intent', 'general')
        channel = request.POST.get('channel', 'sms')
        visitor_phone = request.POST.get('visitor_phone', '')
        
        # Create visitor payment record
        order_id = f"VP{uuid4().hex[:20].upper()}"
        
        visitor_payment = VisitorPayment.objects.create(
            qr_code=qr,
            amount=1.00,
            payment_type=payment_type,
            visitor_phone=visitor_phone,
            visitor_ip=get_client_ip(request),
            order_id=order_id,
            message_content=message_content,
            intent=intent,
            channel=channel,
            status='pending'
        )
        
        # Initiate PhonePe payment
        from apps.accounts.phonepe_service import PhonePeGatewayService
        
        # Create a temporary order object for PhonePe
        class TempOrder:
            def __init__(self, visitor_payment):
                self.order_id = visitor_payment.order_id
                self.amount = visitor_payment.amount
                self.user = type('obj', (object,), {'id': 0})()  # Dummy user
                self.gateway_order_id = ''
                self.status = 'pending'
            
            def save(self):
                pass
            
            def mark_failed(self, reason):
                visitor_payment.mark_failed(reason)
        
        temp_order = TempOrder(visitor_payment)
        result = PhonePeGatewayService.initiate_payment(temp_order)
        
        if result['success']:
            visitor_payment.gateway_order_id = result['transaction_id']
            visitor_payment.save()
            
            return JsonResponse({
                'success': True,
                'payment_url': result['payment_url'],
                'order_id': order_id
            })
        else:
            visitor_payment.mark_failed(result.get('error', 'Payment initiation failed'))
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Payment initiation failed')
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

### 3.3 Visitor Payment Callback

**File**: `apps/accounts/wallet_views.py`

```python
@csrf_exempt
@require_http_methods(["POST", "GET"])
def visitor_payment_callback(request):
    """
    Handle PhonePe callback for visitor payments
    POST/GET /api/v1/auth/wallet/visitor-pay/callback/
    """
    try:
        from apps.accounts.phonepe_service import PhonePeGatewayService
        
        # Get callback data
        if request.method == 'POST':
            callback_data = request.POST.dict()
        else:
            callback_data = request.GET.dict()
        
        # Handle callback
        result = PhonePeGatewayService.handle_callback(callback_data)
        
        if result['success']:
            # Find visitor payment by order_id
            order_id = result.get('order_id', '')
            
            # Check if it's a visitor payment (starts with VP)
            if order_id.startswith('VP'):
                try:
                    visitor_payment = VisitorPayment.objects.get(order_id=order_id)
                    visitor_payment.mark_completed(result.get('payment_id', ''))
                    
                    # Send the message/call now
                    send_visitor_communication(visitor_payment)
                    
                    # Redirect to success page
                    return redirect('accounts:visitor_payment_success', order_id=order_id)
                except VisitorPayment.DoesNotExist:
                    pass
        
        # Redirect to failure page
        return redirect('accounts:visitor_payment_failed')
        
    except Exception as e:
        return redirect('accounts:visitor_payment_failed')


def send_visitor_communication(visitor_payment):
    """
    Send the message/call after visitor payment is completed
    """
    try:
        from apps.interactions.services import InteractionService
        
        qr = visitor_payment.qr_code
        gateway = qr.gateway
        
        if not gateway:
            return
        
        interaction_service = InteractionService()
        
        # Send the communication
        result = interaction_service.initiate_communication(
            gateway=gateway,
            channel=visitor_payment.channel,
            message=visitor_payment.message_content,
            intent=visitor_payment.intent,
            session_data={
                'visitor_payment_id': str(visitor_payment.id),
                'paid_by': 'visitor',
                'amount': float(visitor_payment.amount)
            }
        )
        
        if result['success']:
            visitor_payment.communication_sent = True
            visitor_payment.communication_sent_at = timezone.now()
            visitor_payment.save()
            
    except Exception as e:
        print(f"Error sending visitor communication: {e}")
```

### 3.4 URL Routes

**File**: `apps/accounts/urls.py`

```python
# Add these routes:
path('wallet/visitor-pay/<str:identifier>/', wallet_views.initiate_visitor_payment, name='initiate_visitor_payment'),
path('wallet/visitor-pay/callback/', wallet_views.visitor_payment_callback, name='visitor_payment_callback'),
path('wallet/visitor-pay/success/<str:order_id>/', wallet_views.visitor_payment_success, name='visitor_payment_success'),
path('wallet/visitor-pay/failed/', wallet_views.visitor_payment_failed, name='visitor_payment_failed'),
```

---

## 📦 PHASE 4: Wallet Deduction Logic

### File: `apps/core/views.py`
### Method: `GatewayAccessView.post()`

**Current State**: Sends message without checking/deducting balance

**Required Changes**:

```python
def post(self, request, identifier):
    """Process communication request."""
    try:
        # ... existing code to find gateway ...
        
        channel = request.POST.get('channel')
        message = request.POST.get('message', '').strip()
        intent = request.POST.get('intent', 'general')
        
        # Check if prepaid category and handle payment
        try:
            from apps.gateways.qr_models import PreGeneratedQR
            qr = PreGeneratedQR.objects.get(
                qr_code=identifier.upper(),
                status='activated'
            )
            
            if qr.category and qr.category.category_type == 'prepaid':
                wallet = qr.qr_wallet
                
                # Check balance
                if wallet.balance >= 1.00:
                    # Owner has balance - deduct ₹1
                    wallet.balance -= 1.00
                    wallet.save()
                    
                    # Create transaction record
                    from apps.accounts.recharge_models import QRWalletTransaction
                    QRWalletTransaction.objects.create(
                        wallet=wallet,
                        transaction_type='deduction',
                        amount=1.00,
                        description=f'{channel.upper()} charge - {intent}',
                        notes=f'Message: {message[:50]}'
                    )
                    
                    # Continue with normal flow
                else:
                    # Owner has ₹0 - visitor must pay
                    # Return error, frontend will handle payment
                    messages.error(request, 'Payment required. Please complete payment to send message.')
                    return redirect('core:gateway_access', identifier=identifier)
        except:
            pass  # Not a prepaid QR, continue normally
        
        # ... rest of existing code to send message ...
```

---

## 📦 PHASE 5: UI Updates

### File: `templates/core/gateway_access.html`

**Add payment UI after contact method selection**:

```html
<!-- Payment Notice (shown when owner has ₹0) -->
{% if payment_required and payer == 'visitor' %}
<div class="mb-8" x-show="contactMethod" x-transition>
    <div class="bg-gradient-to-r from-yellow-50 to-orange-50 border-2 border-yellow-300 rounded-xl p-6">
        <div class="flex items-start">
            <div class="w-12 h-12 bg-yellow-100 rounded-full flex items-center justify-center mr-4 flex-shrink-0">
                <svg class="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
            </div>
            <div class="flex-1">
                <h3 class="text-lg font-bold text-yellow-900 mb-2">💳 Small Payment Required</h3>
                <p class="text-yellow-800 mb-3">
                    The vehicle owner's wallet is currently empty. To send your <span x-text="contactMethod === 'message' ? 'message' : 'call request'"></span>, 
                    a small fee of <strong class="text-xl">₹{{ cost_per_action }}</strong> is required.
                </p>
                <div class="bg-white rounded-lg p-4 mb-3">
                    <div class="flex items-center justify-between">
                        <span class="text-gray-700">
                            <span x-show="contactMethod === 'message'">📱 Message Fee</span>
                            <span x-show="contactMethod === 'call'">📞 Call Fee</span>
                        </span>
                        <span class="text-2xl font-bold text-gray-900">₹{{ cost_per_action }}</span>
                    </div>
                </div>
                <p class="text-sm text-yellow-700">
                    ✅ Secure payment via PhonePe<br>
                    ✅ Your <span x-text="contactMethod === 'message' ? 'message' : 'call'"></span> will be sent immediately after payment<br>
                    ✅ One-time payment per contact
                </p>
            </div>
        </div>
    </div>
</div>
{% endif %}
```

**Update submit button logic**:

```html
<button 
    type="button"
    @click="handleAction"
    :disabled="!canSubmit"
    :class="canSubmit ? 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700' : 'bg-gray-400 cursor-not-allowed'"
    class="w-full text-white py-4 px-6 rounded-xl font-bold text-lg transition-all duration-200 shadow-lg"
>
    {% if payment_required and payer == 'visitor' %}
        <span x-show="contactMethod === 'message'">Pay ₹{{ cost_per_action }} & Send Message</span>
        <span x-show="contactMethod === 'call'">Pay ₹{{ cost_per_action }} & Call</span>
    {% else %}
        <span x-show="contactMethod === 'message'">Send Message</span>
        <span x-show="contactMethod === 'call'">Initiate Call</span>
    {% endif %}
    <span x-show="!contactMethod">Select Contact Method</span>
</button>
```

**Update JavaScript**:

```javascript
async handleAction() {
    if (!this.canSubmit) {
        alert('Please complete all required fields');
        return;
    }
    
    {% if payment_required and payer == 'visitor' %}
    // Visitor payment required
    await this.initiateVisitorPayment();
    {% else %}
    // Normal flow (owner pays or free)
    if (this.contactMethod === 'call') {
        await this.initiateCall();
    } else if (this.contactMethod === 'message') {
        this.submitForm();
    }
    {% endif %}
},

async initiateVisitorPayment() {
    this.loading = true;
    this.errorMessage = '';
    
    try {
        const formData = new FormData();
        formData.append('payment_type', this.contactMethod);
        formData.append('message', this.message);
        formData.append('intent', this.reason);
        formData.append('channel', this.channel);
        formData.append('csrfmiddlewaretoken', this.getCookie('csrftoken'));
        
        const response = await fetch('/api/v1/auth/wallet/visitor-pay/{{ identifier }}/', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Redirect to PhonePe payment page
            window.location.href = data.payment_url;
        } else {
            this.errorMessage = data.error || 'Failed to initiate payment';
        }
    } catch (error) {
        this.errorMessage = 'Network error. Please try again.';
    } finally {
        this.loading = false;
    }
},
```

---

## 🗄️ Database Migrations

### Create Migration

```bash
python manage.py makemigrations accounts
python manage.py migrate accounts
```

### Expected Migration

```python
# Generated migration file
operations = [
    migrations.CreateModel(
        name='VisitorPayment',
        fields=[
            ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('amount', models.DecimalField(decimal_places=2, default=1.0, max_digits=10)),
            ('payment_type', models.CharField(choices=[('message', 'Message'), ('call', 'Call')], default='message', max_length=20)),
            ('visitor_phone', models.CharField(blank=True, max_length=20)),
            ('visitor_ip', models.GenericIPAddressField(blank=True, null=True)),
            ('order_id', models.CharField(max_length=100, unique=True)),
            ('gateway_order_id', models.CharField(blank=True, max_length=100)),
            ('gateway_payment_id', models.CharField(blank=True, max_length=100)),
            ('status', models.CharField(choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
            ('message_content', models.TextField(blank=True)),
            ('intent', models.CharField(blank=True, max_length=50)),
            ('channel', models.CharField(blank=True, max_length=20)),
            ('communication_sent', models.BooleanField(default=False)),
            ('communication_sent_at', models.DateTimeField(blank=True, null=True)),
            ('qr_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitor_payments', to='gateways.pregeneratedqr')),
        ],
        options={
            'verbose_name': 'Visitor Payment',
            'verbose_name_plural': 'Visitor Payments',
            'db_table': 'visitor_payments',
            'ordering': ['-created_at'],
        },
    ),
]
```

---

## 🧪 Testing Scenarios

### Test 1: Owner Activates QR (Prepaid Category)
**Steps**:
1. Create QR with Prepaid category
2. Activate QR code
3. Check database

**Expected**:
- `QRWallet` created with `balance=0.00`
- `category` = Prepaid category
- `is_active=True`

### Test 2: Visitor Contacts Owner (Owner has ₹0)
**Steps**:
1. Owner has ₹0 balance
2. Visitor scans QR
3. Visitor selects "Send Message"
4. Visitor sees payment prompt

**Expected**:
- Payment UI shows "₹1 required"
- Button says "Pay ₹1 & Send Message"
- Clicking initiates PhonePe payment

### Test 3: Visitor Completes Payment
**Steps**:
1. Visitor pays ₹1 via PhonePe
2. Payment succeeds
3. Callback received

**Expected**:
- `VisitorPayment` status = 'completed'
- Message sent to owner
- `communication_sent=True`

### Test 4: Owner Recharges Wallet
**Steps**:
1. Owner recharges ₹10
2. Visitor contacts owner
3. No payment prompt shown

**Expected**:
- Visitor sees normal contact form
- Message sent immediately
- ₹1 deducted from owner's wallet
- `QRWalletTransaction` created

### Test 5: Owner Balance Reaches ₹0
**Steps**:
1. Owner has ₹1 balance
2. Visitor 1 contacts (₹1 deducted, balance = ₹0)
3. Visitor 2 contacts (payment required)

**Expected**:
- Visitor 1: Free contact, owner pays
- Visitor 2: Payment prompt, visitor pays

---

## 📊 Admin Dashboard Updates

### View Visitor Payments

**File**: `apps/accounts/admin_views.py`

```python
@staff_member_required
def visitor_payments_dashboard(request):
    """View all visitor payments"""
    from apps.accounts.recharge_models import VisitorPayment
    
    payments = VisitorPayment.objects.select_related('qr_code').order_by('-created_at')[:100]
    
    stats = {
        'total_payments': VisitorPayment.objects.filter(status='completed').count(),
        'total_revenue': VisitorPayment.objects.filter(status='completed').aggregate(
            total=models.Sum('amount')
        )['total'] or 0,
        'pending': VisitorPayment.objects.filter(status='pending').count(),
        'failed': VisitorPayment.objects.filter(status='failed').count(),
    }
    
    context = {
        'payments': payments,
        'stats': stats,
    }
    return render(request, 'admin/visitor_payments.html', context)
```

---

## 🚀 Deployment Checklist

### Before Deployment
- [ ] Create `VisitorPayment` model
- [ ] Run migrations
- [ ] Update `activate_qr_code()` function
- [ ] Update `GatewayAccessView.get()` method
- [ ] Update `GatewayAccessView.post()` method
- [ ] Create visitor payment views
- [ ] Update URL routes
- [ ] Update `gateway_access.html` template
- [ ] Test all scenarios

### After Deployment
- [ ] Verify wallet auto-creation works
- [ ] Test visitor payment flow end-to-end
- [ ] Test owner wallet deduction
- [ ] Monitor PhonePe callbacks
- [ ] Check transaction records

---

## 💡 Key Benefits

1. **Low Barrier to Entry**: Owners can start with ₹0
2. **Always Available**: Contact always works (someone pays)
3. **Fair System**: Owner pays when they can, visitor pays when owner can't
4. **Spam Prevention**: ₹1 charge prevents abuse
5. **Revenue Model**: Platform earns from both sides
6. **Transparent**: Clear payment prompts for visitors

---

## 🔒 Security Considerations

1. **Payment Verification**: Always verify PhonePe callback checksums
2. **Double Payment Prevention**: Check payment status before sending message
3. **Rate Limiting**: Prevent spam payment attempts
4. **IP Tracking**: Track visitor IPs for fraud detection
5. **Transaction Logging**: Log all wallet transactions

---

## 📈 Future Enhancements

1. **Bulk Discounts**: ₹5 for 10 messages
2. **Owner Notifications**: Alert when balance reaches ₹0
3. **Auto-Recharge**: Automatic recharge when balance low
4. **Analytics**: Track visitor payment patterns
5. **Refunds**: Handle failed communications

---

## 📞 Support

For implementation questions or issues:
- Check logs in `/logs/` directory
- Review PhonePe callback responses
- Verify database transactions
- Test in UAT environment first

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-09  
**Status**: Ready for Implementation
