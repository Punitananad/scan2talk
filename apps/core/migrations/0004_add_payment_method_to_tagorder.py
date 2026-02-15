# Generated migration for adding payment_method field to TagOrder

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_tagorder_distributor_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagorder',
            name='payment_method',
            field=models.CharField(
                max_length=20,
                choices=[('online', 'Online Payment'), ('cod', 'Cash on Delivery')],
                default='online',
                help_text="Payment method chosen by customer"
            ),
        ),
        migrations.AlterField(
            model_name='tagorder',
            name='status',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('pending', 'Pending'),
                    ('processing', 'Processing'),
                    ('cod_pending', 'COD Pending Delivery'),
                    ('shipped', 'Shipped'),
                    ('delivered', 'Delivered'),
                    ('cancelled', 'Cancelled'),
                ],
                default='pending'
            ),
        ),
    ]
