# Generated by Django 3.2.7 on 2021-12-03 13:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("permits", "0050_fix_regex_for_administrative_entity_email"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="qgisproject",
            name="qgis_atlas_coverage_layer",
        ),
        migrations.RemoveField(
            model_name="qgisproject",
            name="qgis_layers",
        ),
    ]
