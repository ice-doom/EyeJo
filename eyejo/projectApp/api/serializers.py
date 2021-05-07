from rest_framework import serializers
from projectApp.models import Project, Url_info, IPAddress, Subdomain, Asset, Side_station, C_net, Asset_group, Port, \
    Login_site, IP_domain_relationship, Tags, Crawl
from django.utils import timezone


class DateTimeFieldWihTZ(serializers.DateTimeField):
    """ Class to make output of a DateTime Field timezone aware """

    def to_representation(self, value):
        value = timezone.localtime(value)
        return super(DateTimeFieldWihTZ, self).to_representation(value)


class ProjectSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')
    project_count_for_dep = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    def get_project_count_for_dep(self, obj):
        project_count = {
            "site_count": Url_info.objects.filter(project_id=obj.id, screen_status__in=['success', 'false']).count(),
            "domain_count": Subdomain.objects.filter(project_id=obj.id).count(),
            "ip_count": IPAddress.objects.filter(project_id=obj.id).count()
        }
        return project_count


class UrlInfoSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Url_info
        fields = '__all__'

    def get_tags(self, obj):
        tags = Tags.objects.filter(project_id=obj.project_id, url_info_id=obj.id).values_list('name', flat=True)
        return tags

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = '__all__'


class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = '__all__'


class IPSerializer(serializers.ModelSerializer):
    port_set = PortSerializer(many=True, read_only=True)

    class Meta:
        model = IPAddress
        fields = '__all__'


class SubdomainIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPAddress
        fields = ['ip_address']


class IPDomainRelationshipSerializer(serializers.ModelSerializer):
    ip = SubdomainIPSerializer()

    class Meta:
        model = IP_domain_relationship
        fields = ['ip']


class SubdomainSerializer(serializers.ModelSerializer):
    ip_domain_relationship_set = IPDomainRelationshipSerializer(many=True, read_only=True)

    class Meta:
        model = Subdomain
        fields = '__all__'


class LoginSiteSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Login_site
        fields = ('url', 'create_time', 'id')


class CrawlSerializer(serializers.ModelSerializer):
    login_site_set = LoginSiteSerializer(many=True, read_only=True)

    class Meta:
        model = Crawl
        fields = ('crawl_url', 'method', 'headers', 'req_data', 'login_site_set')


class AssetsSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Asset
        fields = '__all__'


class AssetsUrlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset_group
        fields = ('url',)


class AssetsViewSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Asset_group
        fields = '__all__'


class TagsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ('name',)


class SideStationViewSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Side_station
        fields = '__all__'


class CNetViewSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = C_net
        fields = '__all__'
