from rest_framework import routers

from hotspot.views import HotspotViewSet, HotspotSourceViewSet, PeriodicTaskViewSet

router = routers.SimpleRouter()

router.register(r'hotspot', HotspotViewSet, base_name='hotspot-view-set')
router.register(r'hotspot-source', HotspotSourceViewSet, base_name='hotspot-source-set')
router.register(r'periodic-tasks', PeriodicTaskViewSet, base_name='periodic-task-view-set')

urlpatterns = []

urlpatterns += router.urls
