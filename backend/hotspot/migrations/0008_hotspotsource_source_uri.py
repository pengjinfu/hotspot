# Generated by Django 2.2 on 2019-08-26 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hotspot', '0007_hotspotsource_last_fetch_data_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotspotsource',
            name='source_uri',
            field=models.URLField(help_text='来源地址', null=True),
        ),
    ]
