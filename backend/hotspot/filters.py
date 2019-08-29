from django_extensions.drf.filters import FilterSet, filters

from hotspot.models import Hotspot, HotspotSource


class HotspotSourceFilter(FilterSet):

    class Meta:
        model = HotspotSource
        fields = {
            'uuid': ['exact', ]
        }


class HotspotFilter(FilterSet):
    hotspot_source = filters.RelatedFilter(HotspotSourceFilter, queryset=HotspotSource.objects.all())

    class Meta:
        model = Hotspot
        fields = {}
