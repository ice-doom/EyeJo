from rest_framework import serializers
from projectApp.models import Task, Fuzz, Poc_check, Vulnerability, Brute
from projectApp.api.serializers import DateTimeFieldWihTZ
from django.db.models import Count


class TaskSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')
    end_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')
    task_count_for_dep = serializers.SerializerMethodField()
    options_for_dep = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id', 'create_time', 'end_time', 'name', 'status', 'task_count_for_dep', 'options_for_dep']

    def get_task_count_for_dep(self, obj):
        task_count = {
            "vul_count": Vulnerability.objects.filter(task_id=obj.id).count(),
            "poc_count": Poc_check.objects.filter(task_id=obj.id).count(),
            "fuzz_count": Fuzz.objects.filter(task_id=obj.id).values('url').annotate(count=Count('url')).count(),
            "brute_count": Brute.objects.filter(task_id=obj.id).count(),
        }
        return task_count

    def get_options_for_dep(self, obj):
        options = {}
        if obj.option_subdomain_collect:
            options['subdomain_collect'] = True
        if obj.option_port_scan:
            options['port_scan'] = True
        if obj.option_sf_info:
            options['sf_info'] = True
        if obj.option_request_site:
            if obj.option_screen_info:
                options['screen_info'] = True
            else:
                options['request_site'] = True
        if obj.option_poc_scan:
            options['poc_scan'] = True
        if obj.option_fuzz:
            options['fuzz'] = True
        if obj.option_identify_login:
            options['identify_login'] = True
        if obj.option_vul:
            options['vul'] = True
        if obj.option_brute:
            options['brute'] = True
        return options


class FuzzSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField()

    class Meta:
        model = Fuzz
        fields = ('url', 'count')


class Fuzz_viewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fuzz
        fields = '__all__'


class Poc_checkSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Poc_check
        fields = '__all__'


class VulnerabilitySerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Vulnerability
        fields = '__all__'


class BruteSerializer(serializers.ModelSerializer):
    create_time = DateTimeFieldWihTZ(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = Brute
        fields = '__all__'
