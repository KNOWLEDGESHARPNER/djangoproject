# Generated by Django 4.1.7 on 2023-04-05 04:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0015_alter_order_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customer',
            options={'ordering': ['user__first_name', 'user__last_name'], 'permissions': [('view_history', 'Can view history')]},
        ),
    ]