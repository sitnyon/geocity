# Generated by Django 3.1.4 on 2021-01-21 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('permits', '0010_auto_20201127_1024'),
    ]

    operations = [
        migrations.AddField(
            model_name='worksobjectproperty',
            name='order',
            field=models.IntegerField(default=1, max_length=30, verbose_name='ordre'),
        ),
    ]
