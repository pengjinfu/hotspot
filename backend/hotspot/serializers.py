from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django_extensions.drf.serializers.serializers import LqFlexFieldsModelSerializer, BasicModelSerializer
from rest_framework import serializers
from rest_framework.serializers import ALL_FIELDS

from hotspot.models import Hotspot, HotspotSource


class HotspotSerializerStrategy:
    class Create(BasicModelSerializer):
        class Meta:
            model = Hotspot
            fields = ALL_FIELDS

    class List(LqFlexFieldsModelSerializer):
        extra = serializers.CharField(source='desc')

        class HotspotSourceSerializer(LqFlexFieldsModelSerializer):
            class Meta:
                model = HotspotSource
                fields = ALL_FIELDS

        expandable_fields = {
            'hotspot_source_ex': (HotspotSourceSerializer, {'fields': 'id,name,icon', 'source': 'hotspot_source'})
        }

        class Meta:
            model = Hotspot
            fields = ALL_FIELDS


class HotspotSourceSerializerStrategy:
    class Create(BasicModelSerializer):
        class Meta:
            model = HotspotSource
            fields = ALL_FIELDS

    class List(LqFlexFieldsModelSerializer):
        hotspot_set = HotspotSerializerStrategy.List(many=True, fields='id,title,uri,extra')

        class Meta:
            model = HotspotSource
            fields = ALL_FIELDS

    class Retrieve(LqFlexFieldsModelSerializer):
        hotspot_set = HotspotSerializerStrategy.List(many=True, fields='id,title,uri,extra')

        class Meta:
            model = HotspotSource
            fields = ALL_FIELDS


class IntervalScheduleSerializerStrategy:

    class Create(BasicModelSerializer):

        class Meta:
            model = IntervalSchedule
            fields = ALL_FIELDS

    class List(LqFlexFieldsModelSerializer):

        class Meta:
            model = IntervalSchedule
            fields = ALL_FIELDS

    class Update(BasicModelSerializer):

        class Meta:
            model = IntervalSchedule
            fields = ALL_FIELDS

    class Retrieve(LqFlexFieldsModelSerializer):

        class Meta:
            model = IntervalSchedule
            fields = ALL_FIELDS

    class FlexField(LqFlexFieldsModelSerializer):
        class Meta:
            model = IntervalSchedule
            fields = ALL_FIELDS


class PeriodicTaskSerializerStrategy:
    class Create(BasicModelSerializer):

        class Meta:
            model = PeriodicTask
            fields = ALL_FIELDS

    class List(LqFlexFieldsModelSerializer):

        expandable_fields = {
            'interval': (IntervalScheduleSerializerStrategy.Retrieve, {'fields': 'every,period,id'})
        }

        class Meta:
            model = PeriodicTask
            fields = ALL_FIELDS

    class Update(BasicModelSerializer):

        class Meta:
            model = PeriodicTask
            fields = ('interval', 'enabled')

    class Retrieve(LqFlexFieldsModelSerializer):

        class Meta:
            model = PeriodicTask
            fields = ALL_FIELDS
