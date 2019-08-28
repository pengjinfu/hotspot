import django_filters
from django_extensions.drf.viewsets import BasicModelViewSet
from rest_framework import filters
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from hotspot.filters import HotspotFilter
from hotspot.models import Hotspot, HotspotSource
from hotspot.serializers import HotspotSerializerStrategy, HotspotSourceSerializerStrategy


class HotspotSourceViewSet(BasicModelViewSet):
    """
    create:
        创建热点来源详情
    partial_update:
        更新热点来源详情信息
    destroy:
        删除热点来源详情
    retrieve:
        单个获取热点来源详情
    list:
        获取热点来源列表
    """
    serializer_class = HotspotSourceSerializerStrategy
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly, )

    queryset = HotspotSource.objects.all()

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter)
    # filterset_class = HotspotSourceFilter
    search_fields = None
    ordering = None

    lookup_field = 'uuid'

class HotspotViewSet(BasicModelViewSet):
    """
    create:
        创建热点详情
    partial_update:
        更新热点详情信息
    destroy:
        删除热点详情
    retrieve:
        单个获取热点详情
    list:
        获取热点列表
    """
    serializer_class = HotspotSerializerStrategy
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticatedOrReadOnly,)

    queryset = Hotspot.objects.all()

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter)
    filterset_class = HotspotFilter
    search_fields = None
    ordering = None

    lookup_field = 'uuid'
