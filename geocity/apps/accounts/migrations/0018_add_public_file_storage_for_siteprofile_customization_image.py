# Generated by Django 4.2.10 on 2024-04-16 07:47

import django.core.validators
from django.db import migrations
import geocity.apps.accounts.fields
import geocity.fields


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0017_service_fee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='templatecustomization',
            name='background_image',
            field=geocity.apps.accounts.fields.CustomLoginImageFileField(blank=True, storage=geocity.fields.PublicFileSystemStorage(), upload_to='site_profile_custom_image/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['svg', 'png', 'jpg', 'jpeg'])], verbose_name='Image de fond'),
        ),
    ]
