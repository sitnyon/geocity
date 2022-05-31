# Generated by Django 3.2.13 on 2022-05-31 07:42

import django.core.validators
from django.db import migrations, models
import permits.fields


class Migration(migrations.Migration):

    dependencies = [
        ('streamblocks', '0002_alter_printblockparagraph_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='printblockmap',
            name='qgis_print_template_name',
            field=models.CharField(default='none', max_length=150, verbose_name="Nom du template d'impression QGIS"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='printblockmap',
            name='qgis_project_file',
            field=permits.fields.AdministrativeEntityFileField(default='invalid', storage=permits.fields.PrivateFileSystemStorage(), upload_to='qgis_templates', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['qgs'])], verbose_name="Projet QGIS '*.qgs'"),
            preserve_default=False,
        ),
    ]
