import json
from django.db import models
from django_extensions.db.models import BasicModel


class HotspotSource(BasicModel):
    name = models.CharField(max_length=32, help_text='来源名称')
    desc = models.CharField(max_length=128, help_text='描述', blank=True)
    icon = models.URLField(max_length=256, help_text='图标', blank=True)
    code = models.PositiveSmallIntegerField(unique=True, help_text='来源编码')
    source_uri = models.URLField(null=True, help_text='来源地址')

    last_fetch_data_time = models.DateTimeField(null=True, help_text='最后获取数据的时间')

    @property
    def hotspot_set(self):
        if self.last_fetch_data_time is not None:
            return self.hotspot_set_by_hotspot_source.filter(created_time__gt=self.last_fetch_data_time)
        return []

    class Meta:
        db_table = 'db_hotspot_source'


class Hotspot(BasicModel):
    hotspot_source = models.ForeignKey(HotspotSource, related_name='hotspot_set_by_hotspot_source', on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=256, help_text='热点标题')
    uri = models.URLField(help_text='热点uri', max_length=1024)

    extra = models.TextField(help_text='额外信息')

    @property
    def desc(self):
        return json.loads(self.extra)['count']

    class Meta:
        db_table = 'db_hotspot'
        ordering = ('-created_time', )

