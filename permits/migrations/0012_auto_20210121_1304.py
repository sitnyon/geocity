# Generated by Django 3.1.4 on 2021-01-21 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0011_worksobjectproperty_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worksobjectproperty',
            name='order',
            field=models.IntegerField(default=1, verbose_name='ordre'),
        ),
    ]
