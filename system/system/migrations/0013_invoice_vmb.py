# Generated by Django 4.2.21 on 2025-06-05 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0012_alter_invoice_due_date_alter_invoiceline_product_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='VMB',
            field=models.BooleanField(default=False, help_text='VMB?'),
        ),
    ]
