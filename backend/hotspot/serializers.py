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

        class Meta:
            model = Hotspot
            fields = ALL_FIELDS


class HotspotSourceSerializerStrategy:
    class Create(BasicModelSerializer):
        class Meta:
            model = HotspotSource
            fields = ALL_FIELDS

    class List(LqFlexFieldsModelSerializer):
        last_fetch_data_time = serializers.DateTimeField()

        hotspot_set = HotspotSerializerStrategy.List(many=True, fields='id,title,uri,extra')

        class Meta:
            model = HotspotSource
            fields = ALL_FIELDS

    class Retrieve(LqFlexFieldsModelSerializer):
        class Meta:
            model = HotspotSource
            fields = ALL_FIELDS
