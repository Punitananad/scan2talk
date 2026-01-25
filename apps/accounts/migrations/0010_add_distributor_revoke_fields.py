# Generated migration for distributor revoke tracking

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_add_commission_payment_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='distributor_revoked',
            field=models.BooleanField(default=False, help_text='Has distributor status been revoked?'),
        ),
        migrations.AddField(
            model_name='user',
            name='distributor_revoked_at',
            field=models.DateTimeField(blank=True, help_text='When was distributor status revoked?', null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='distributor_revoked_by',
            field=models.ForeignKey(blank=True, help_text='Admin who revoked distributor status', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='distributors_revoked', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='user',
            name='distributor_revoke_reason',
            field=models.TextField(blank=True, help_text='Reason for revoking distributor status'),
        ),
    ]
