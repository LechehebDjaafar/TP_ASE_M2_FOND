# Generated by Django 5.1.3 on 2024-11-23 22:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer_service', '0005_chatcategory_chatmessage_frequentlyaskedquestion_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='frequentlyaskedquestion',
            name='category',
        ),
    ]