from django_extensions.drf.filters import FilterSet

from hotspot.models import Hotspot


class HotspotFilter(FilterSet):
    class Meta:
        model = Hotspot
        fields = {
            'hotspot_source': ['exact', ]
        }
