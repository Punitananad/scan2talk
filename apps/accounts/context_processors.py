"""
Context processors for accounts app.
"""

def wallet_visibility(request):
    """
    Add show_wallet flag to all template contexts.
    Only show wallet if user has prepaid or postpaid categories.
    """
    show_wallet = False
    
    if request.user.is_authenticated:
        from apps.gateways.qr_models import PreGeneratedQR
        
        # Check if user has any QR codes with prepaid or postpaid categories
        user_qr_codes = PreGeneratedQR.objects.filter(
            owner=request.user,
            status='activated'
        ).select_related('category')
        
        for qr in user_qr_codes:
            if qr.category and qr.category.category_type in ['prepaid', 'postpaid']:
                show_wallet = True
                break
    
    return {
        'show_wallet': show_wallet
    }
