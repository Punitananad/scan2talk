# Generated migration for commission payment tracking

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_add_distributor_management_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='distributorpayment',
            name='commission_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Commission earned by distributor', max_digits=10),
        ),
        migrations.AddField(
            model_name='distributorpayment',
            name='commission_paid',
            field=models.BooleanField(default=False, help_text='Has the commission been paid to distributor?'),
        ),
        migrations.AddField(
            model_name='distributorpayment',
            name='commission_paid_at',
            field=models.DateTimeField(blank=True, help_text='When was the commission paid?', null=True),
        ),
        migrations.AddField(
            model_name='distributorpayment',
            name='commission_paid_by',
            field=models.ForeignKey(blank=True, help_text='Admin who marked commission as paid', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='commissions_paid', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='distributorpayment',
            name='payment_notes',
            field=models.TextField(blank=True, help_text='Notes about commission payment (transaction ID, etc.)'),
        ),
    ]
