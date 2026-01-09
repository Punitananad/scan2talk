"""
Core views for the gateway platform.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponseBadRequest
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.utils import timezone as django_timezone
from django_ratelimit.decorators import ratelimit
from apps.gateways.models import Gateway, EntryPoint
from apps.routing.services import RoutingService
from apps.interactions.services import InteractionService


class HomeView(TemplateView):
    """Homepage view."""
    template_name = 'core/home.html'


class PrivacyPolicyView(TemplateView):
    """Privacy policy view."""
    template_name = 'core/privacy.html'


class TermsOfServiceView(TemplateView):
    """Terms of service view."""
    template_name = 'core/terms.html'


class RefundPolicyView(TemplateView):
    """Refund policy view."""
    template_name = 'core/refund.html'


class ContactView(View):
    """Contact page view with fake form submission."""
    template_name = 'core/contact.html'
    
    def get(self, request):
        """Display contact form."""
        return render(request, self.template_name)
    
    def post(self, request):
        """Handle form submission - show success message without actually sending."""
        # Get form data (but don't actually send it)
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Show success message
        messages.success(
            request,
            f'Thank you {name}! Your message has been sent successfully. '
            'We will get back to you within 24 hours.'
        )
        
        # Redirect back to contact page
        return redirect('core:contact')


class HealthCheckView(View):
    """Health check endpoint for monitoring."""
    
    def get(self, request):
        return JsonResponse({
            'status': 'healthy',
            'timestamp': django_timezone.now().isoformat()
        })


@method_decorator(never_cache, name='dispatch')
@method_decorator(ratelimit(key='ip', rate='10/m', method='GET'), name='get')
@method_decorator(ratelimit(key='ip', rate='5/m', method='POST'), name='post')
class GatewayAccessView(View):
    """
    Public gateway access view for initiating communication.
    This is the main entry point for external users.
    Supports both EntryPoint identifiers and QR codes.
    """
    
    def get(self, request, identifier):
        """Display gateway access form."""
        from apps.gateways.qr_models import PreGeneratedQR
        from apps.accounts.recharge_models import QRWallet
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            gateway = None
            entry_point = None
            qr_obj = None
            
            logger.info(f"Gateway access request for identifier: {identifier}")
            
            # Try to find by EntryPoint first
            try:
                entry_point = EntryPoint.objects.select_related('gateway').get(
                    public_identifier=identifier,
                    is_active=True,
                    gateway__is_active=True
                )
                gateway = entry_point.gateway
                logger.info(f"Found EntryPoint: {entry_point.id}")
            except EntryPoint.DoesNotExist:
                logger.info(f"EntryPoint not found, trying QR code lookup")
                # Try to find by QR code
                try:
                    qr_obj = PreGeneratedQR.objects.select_related('gateway', 'category').get(
                        qr_code=identifier.upper(),
                        status='activated'
                    )
                    
                    logger.info(f"Found QR code: {qr_obj.qr_code}")
                    
                    if not qr_obj.gateway:
                        logger.error(f"QR code {identifier} has no gateway")
                        return render(request, 'core/gateway_not_found.html')
                    
                    logger.info(f"QR gateway: {qr_obj.gateway.id}, is_active: {qr_obj.gateway.is_active}")
                    
                    if not qr_obj.gateway.is_active:
                        logger.error(f"QR code {identifier} gateway is not active")
                        return render(request, 'core/gateway_unavailable.html', {
                            'message': 'This gateway is currently unavailable.'
                        })
                    
                    gateway = qr_obj.gateway
                    logger.info(f"Successfully loaded gateway {gateway.id}")
                except PreGeneratedQR.DoesNotExist:
                    logger.error(f"QR code {identifier} not found or not activated")
                    return render(request, 'core/gateway_not_found.html')
            
            # Check if gateway allows access
            routing_service = RoutingService()
            if not routing_service.can_access_gateway(gateway, request):
                logger.warning(f"Gateway {gateway.id} access denied")
                return render(request, 'core/gateway_unavailable.html', {
                    'message': 'This gateway is currently unavailable.'
                })
            
            # Get available communication channels
            available_channels = routing_service.get_available_channels(gateway)
            
            # Check if this is a prepaid category QR and handle payment
            payment_required = False
            payer = None
            cost_per_action = 0.00
            
            if qr_obj and qr_obj.category and qr_obj.category.category_type == 'prepaid':
                # Check wallet balance
                try:
                    wallet = QRWallet.objects.get(qr_code=qr_obj)
                    
                    if wallet.balance >= 1.00:
                        # Owner has balance - will be deducted
                        payment_required = False
                        payer = 'owner'
                        logger.info(f"Owner has balance: ₹{wallet.balance}")
                    else:
                        # Owner has ₹0 - visitor must pay
                        payment_required = True
                        payer = 'visitor'
                        cost_per_action = 1.00
                        logger.info(f"Owner wallet empty, visitor must pay")
                except QRWallet.DoesNotExist:
                    # No wallet found, treat as free
                    payment_required = False
                    payer = None
                    logger.info(f"No wallet found for QR {identifier}, treating as free")
            
            context = {
                'gateway': gateway,
                'entry_point': entry_point,
                'available_channels': available_channels,
                'identifier': identifier,
                'payment_required': payment_required,
                'payer': payer,
                'cost_per_action': cost_per_action,
            }
            
            logger.info(f"Rendering gateway access page for {identifier}")
            return render(request, 'core/gateway_access.html', context)
            
        except Exception as e:
            # Log the error for debugging
            logger.error(f"Error in gateway access view for {identifier}: {str(e)}", exc_info=True)
            return render(request, 'core/gateway_not_found.html')
    
    def post(self, request, identifier):
        """Process communication request."""
        try:
            # Try to find by EntryPoint first
            try:
                entry_point = EntryPoint.objects.select_related('gateway').get(
                    public_identifier=identifier,
                    is_active=True,
                    gateway__is_active=True
                )
                gateway = entry_point.gateway
            except EntryPoint.DoesNotExist:
                # Try to find by QR code
                from apps.gateways.qr_models import PreGeneratedQR
                qr = PreGeneratedQR.objects.select_related('gateway').get(
                    qr_code=identifier.upper(),
                    status='activated',
                    gateway__is_active=True
                )
                gateway = qr.gateway
                entry_point = None
            
            channel = request.POST.get('channel')
            message = request.POST.get('message', '').strip()
            intent = request.POST.get('intent', 'general')
            
            # Validate inputs
            if not channel or not message:
                messages.error(request, 'Please select a communication method and provide a message.')
                return redirect('core:gateway_access', identifier=identifier)
            
            if len(message) > 500:
                messages.error(request, 'Message is too long. Please keep it under 500 characters.')
                return redirect('core:gateway_access', identifier=identifier)
            
            # Check if prepaid category and handle payment
            try:
                from apps.gateways.qr_models import PreGeneratedQR
                from apps.accounts.recharge_models import QRWallet, QRWalletTransaction
                
                qr = PreGeneratedQR.objects.select_related('category').get(
                    qr_code=identifier.upper(),
                    status='activated'
                )
                
                if qr.category and qr.category.category_type == 'prepaid':
                    try:
                        wallet = QRWallet.objects.get(qr_code=qr)
                        
                        # Check balance
                        if wallet.balance >= 1.00:
                            # Owner has balance - deduct ₹1
                            wallet.balance -= 1.00
                            wallet.save()
                            
                            # Create transaction record
                            QRWalletTransaction.objects.create(
                                wallet=wallet,
                                transaction_type='deduction',
                                amount=1.00,
                                description=f'{channel.upper()} charge - {intent}',
                                notes=f'Message: {message[:50]}'
                            )
                            
                            print(f"✅ Deducted ₹1 from owner's wallet. New balance: ₹{wallet.balance}")
                            # Continue with normal flow
                        else:
                            # Owner has ₹0 - visitor must pay
                            # This should not happen if frontend is working correctly
                            messages.error(request, 'Payment required. Please complete payment to send message.')
                            return redirect('core:gateway_access', identifier=identifier)
                    except QRWallet.DoesNotExist:
                        # No wallet found, continue with normal flow (free)
                        print(f"⚠️ No wallet found for QR {identifier}, treating as free")
                        pass
            except PreGeneratedQR.DoesNotExist:
                pass  # Not a prepaid QR, continue normally
            except Exception as e:
                print(f"❌ Wallet error: {e}")
                pass  # Continue with normal flow if wallet check fails
            
            # Process the communication request
            routing_service = RoutingService()
            interaction_service = InteractionService()
            
            # Check routing rules
            if not routing_service.can_route_request(gateway, channel, intent):
                messages.error(request, 'Communication request cannot be processed at this time.')
                return redirect('core:gateway_access', identifier=identifier)
            
            # Create interaction session
            session_data = {
                'gateway_id': str(gateway.id),
                'channel': channel,
                'message': message,
                'intent': intent,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            }
            
            # Route the communication
            result = interaction_service.initiate_communication(
                gateway=gateway,
                channel=channel,
                message=message,
                intent=intent,
                session_data=session_data
            )
            
            if result['success']:
                return render(request, 'core/communication_sent.html', {
                    'gateway': gateway,
                    'channel': channel,
                    'reference_id': result.get('reference_id'),
                })
            else:
                messages.error(request, result.get('error', 'Failed to send communication.'))
                return redirect('core:gateway_access', identifier=identifier)
                
        except Exception as e:
            messages.error(request, 'An error occurred. Please try again.')
            return redirect('core:gateway_access', identifier=identifier)
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip