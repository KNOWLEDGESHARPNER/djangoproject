# Generated by Django 4.1.7 on 2023-03-18 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_rename_given_name_customer_first_name'),
    ]

    operations = [
        migrations.RunSQL("""
             INSERT INTO store_collection (title)
             VALUES ('collection1')
             ""","""
             DELETE FROM store_collection
             WHERE title='collection1'
             """)
    ]
