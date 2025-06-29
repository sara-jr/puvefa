# Generated by Django 4.2 on 2025-06-04 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pdv', '0012_article_controlled'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='restored_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='article',
            name='transaction_id',
            field=models.UUIDField(blank=True, null=True),
        ),
    ]
