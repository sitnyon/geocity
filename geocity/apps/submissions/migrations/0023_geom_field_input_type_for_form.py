# Generated by Django 4.2.4 on 2023-09-13 06:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('forms', '0026_geom_field_input_type_for_form'),
        ('submissions', '0022_contactform_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalsubmissiongeotime',
            name='field',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='forms.field'),
        ),
        migrations.AddField(
            model_name='historicalsubmissiongeotime',
            name='form',
            field=models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='forms.form'),
        ),
        migrations.AddField(
            model_name='submissiongeotime',
            name='field',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='geo_time', to='forms.field'),
        ),
        migrations.AddField(
            model_name='submissiongeotime',
            name='form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='geo_time', to='forms.form'),
        ),
    ]
