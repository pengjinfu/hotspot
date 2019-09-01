import django_filters
from django.db.models import Q
from django_celery_beat.models import PeriodicTask
from django_extensions.drf.viewsets import BasicModelViewSet
from rest_framework import filters
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated

from hotspot.filters import HotspotFilter, HotspotSourceFilter
from hotspot.models import Hotspot, HotspotSource
from hotspot.serializers import HotspotSerializerStrategy, HotspotSourceSerializerStrategy, PeriodicTaskSerializerStrategy


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
    permission_classes = (IsAuthenticatedOrReadOnly,)

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
    search_fields = ('title', 'hotspot_source__name')
    ordering = None

    lookup_field = 'uuid'


class PeriodicTaskViewSet(BasicModelViewSet):
    """
    create:
        创建定时任务详情
    partial_update:
        更新定时任务详情信息
    destroy:
        删除定时任务详情
    retrieve:
        单个获取定时任务详情
    list:
        获取定时任务列表
    """
    serializer_class = PeriodicTaskSerializerStrategy
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = PeriodicTask.objects.filter(~Q(name='celery.backend_cleanup')).all()

    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter)
    # filterset_class = PeriodicTaskFilter
    search_fields = None
    ordering = None

    lookup_field = 'id'
