from django.conf.urls import url, include
from scanTaskApp.views import TaskViewSet, VulViewSet, FuzzViewSet, PocViewSet, ConfigViewSet, BruteViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'task', TaskViewSet, basename='task')
router.register(r'vul', VulViewSet, basename='vul')
router.register(r'fuzz', FuzzViewSet, basename='fuzz')
router.register(r'fuzz_view', FuzzViewSet, basename='fuzz_view')
router.register(r'poc', PocViewSet, basename='poc')
router.register(r'brute', BruteViewSet, basename='brute')
router.register(r'config', ConfigViewSet, basename='config')
urlpatterns = [
    url('', include(router.urls))
]
# urlpatterns += router.urls




