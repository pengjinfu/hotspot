from rest_framework import routers

from hotspot.views import HotspotViewSet, HotspotSourceViewSet

router = routers.SimpleRouter()

router.register(r'hotspot', HotspotViewSet, base_name='hotspot-view-set')
router.register(r'hotspot-source', HotspotSourceViewSet, base_name='hotspot-source-set')

urlpatterns = []

urlpatterns += router.urls
