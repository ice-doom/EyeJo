from django.conf.urls import url, include
from .views import ProjectViewSet, Url_infoViewSet, IPViewSet, DomainViewSet, AssetsViewSet, LoginSiteViewSet, UserInfoViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('all', ProjectViewSet, basename='project')
router.register(r'url_info', Url_infoViewSet, basename='url_info')
router.register(r'ip', IPViewSet, basename='ip')
router.register(r'domain', DomainViewSet, basename='domain')
router.register(r'login_site', LoginSiteViewSet, basename='login_site')
router.register(r'assets', AssetsViewSet, basename='assets')
router.register(r'userinfo', UserInfoViewSet, basename='userinfo')
urlpatterns = [
    url('', include(router.urls)),
]
# urlpatterns += router.urls





