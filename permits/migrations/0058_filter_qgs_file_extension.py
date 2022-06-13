# Generated by Django 3.2.7 on 2022-02-09 12:15

import django.core.validators
from django.db import migrations

import permits.fields


class Migration(migrations.Migration):

    dependencies = [
        ("permits", "0057_add_shortname_to_permitrequest"),
    ]

    operations = [
        migrations.AlterField(
            model_name="qgisproject",
            name="qgis_project_file",
            field=permits.fields.AdministrativeEntityFileField(
                storage=permits.fields.PrivateFileSystemStorage(),
                upload_to="qgis_templates",
                validators=[
                    django.core.validators.FileExtensionValidator(
                        allowed_extensions=["qgs"]
                    )
                ],
                verbose_name="Projet QGIS '*.qgs'",
            ),
        ),
    ]
