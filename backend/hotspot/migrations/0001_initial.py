# Generated by Django 2.1.4 on 2019-08-25 08:52

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hotspot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('uuid', models.UUIDField(default=uuid.uuid1, editable=False, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('last_change_time', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text='热点标题', max_length=256)),
                ('uri', models.URLField(help_text='热点uri')),
                ('extra', models.TextField(help_text='额外信息')),
            ],
            options={
                'db_table': 'db_hotspot',
            },
        ),
        migrations.CreateModel(
            name='HotspotSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('uuid', models.UUIDField(default=uuid.uuid1, editable=False, unique=True)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('last_change_time', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text='来源名称', max_length=32)),
                ('desc', models.CharField(help_text='描述', max_length=128)),
                ('icon', models.URLField(help_text='图标', max_length=256)),
            ],
            options={
                'db_table': 'db_hotspot_source',
            },
        ),
        migrations.AddField(
            model_name='hotspot',
            name='hotspot_source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='hotspot_set_by_hotspot_source', to='hotspot.HotspotSource'),
        ),
    ]