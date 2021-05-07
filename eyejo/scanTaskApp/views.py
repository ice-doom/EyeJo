from rest_framework import viewsets
from projectApp.models import Asset_task_relationship, Asset_group, Asset
from .api.serializers import *
from rest_framework.decorators import action
from EyeJo.celery import app
from projectApp.config import settings
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework.parsers import JSONParser
import re
import requests
from projectApp.views import LoginRequiredJSONMixin
from EyeJo.tasks import task_func
from projectApp.utils import TargetHandle
from projectApp.views import ViewPagination
from django.db.models import Count
from django.utils import timezone
import yaml


class TaskViewSet(LoginRequiredJSONMixin,
                  mixins.CreateModelMixin,
                  mixins.DestroyModelMixin,
                  viewsets.GenericViewSet):
    serializer_class = TaskSerializer  # 视图使用的序列化器
    http_method_names = ['post']

    @action(methods=['post'], detail=False)
    def check_name(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        query_task_name = data.get('query')
        queryset = Task.objects.filter(name=query_task_name)
        if queryset.exists():
            return Response({"code": 0, "msg": "success", "data": True})
        return Response({"code": 0, "msg": "success", "data": False})

    '''创建'''
    def create(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        task_name = data.pop('task_name')
        asset_id = data.pop('asset_id')
        project_id = data.pop('project_id')

        task_filter = Task.objects.filter(name=task_name)

        if not task_name:
            return Response(settings.ErrorMsg.TaskNameEmpty, 200)

        if task_filter.exists():
            return Response(settings.ErrorMsg.TaskExist, 200)

        re_task = re.findall('[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300ba-zA-Z0-9_-]+', task_name)
        if re_task:
            return Response(settings.ErrorMsg.TaskNameInvalid, 200)
        # 端口输入违规字符
        if data.get('option_ports'):
            re_ports = re.findall('[^\d,-]+', data.get('option_ports'))
            if re_ports:
                return Response(settings.ErrorMsg.PortInvalid, 200)

        if data.get('option_brute_type'):
            re_brute_type = re.findall('[^a-zA-Z0-9-,_]+', data.get('option_brute_type'))
            if re_brute_type:
                return Response(settings.ErrorMsg.BruteTypeInvalid, 200)

        if data.get('option_fuzz_file'):
            re_fuzz_file = re.findall('[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300ba-zA-Z0-9._-]+', data.get('option_fuzz_file'))
            if re_fuzz_file:
                return Response(settings.ErrorMsg.FuzzFileInvalid, 200)

        Task.objects.create(name=task_name, project_id=project_id, status=settings.TaskStatus.WAITING, **data)

        task_id = task_filter.last().id
        project_to_asset_group = Asset_group.objects.filter(asset_id=asset_id).values('id', 'url')
        asset_name = Asset.objects.get(id=asset_id).name

        Asset_task_relationship.objects.bulk_create(map(lambda x: Asset_task_relationship(asset_group_id=x['id'], task_id=task_id), project_to_asset_group.iterator()), batch_size=1000, ignore_conflicts=True)
        asset_group_url_list = [x['url'] for x in project_to_asset_group.iterator()]
        scheme_target_dict = TargetHandle.get_schema_target_dict(asset_group_url_list)
        target_dict = TargetHandle.get_target_dict(asset_group_url_list)

        with open(settings.SETTING_FILE) as f:
            yaml_configuration = yaml.safe_load(f)

        task_data = {
            'yaml_config': yaml_configuration,
            'data': data,
            'scheme_target_dict': scheme_target_dict,
            'target_dict': target_dict,
            'project_id': project_id,
            'task_id': task_id,
            'asset_name': asset_name
        }

        celery_id = task_func.delay(task_data)
        Task.objects.filter(id=task_id).update(celery_id=str(celery_id))
        return Response({"msg": "success", "code": 0})

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        task_name = data.get('query')
        project_id = data.get('project_id')
        page_object = ViewPagination()
        field = data.get('field') or '-id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'
        if project_id:
            queryset = Task.objects.filter(project_id=project_id).order_by(field).distinct()
        else:
            queryset = Task.objects.all().order_by(field).distinct()

        if task_name:
            queryset = queryset.filter(name__contains=task_name).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = TaskSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    '''单个任务删除'''
    @action(methods=['post'], detail=False)
    def delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_id = data.get('id')
        if isinstance(delete_id, str):
            return Response(settings.ErrorMsg.InputIntError, 200)
        try:
            task_get = Task.objects.get(id=delete_id)
            if task_get.status not in ['done', 'stop']:
                return Response(settings.ErrorMsg.TaskDeleteError, 200)
            self.perform_destroy(task_get)
            return Response({"msg": "删除成功", "code": 0}, 200)
        except Task.DoesNotExist:
            return Response(settings.ErrorMsg.DeleteNotFound, 200)

    '''批量删除'''
    @action(methods=['post'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_ids = data.get('id')
        for check_id in delete_ids:
            if isinstance(check_id, str):
                return Response(settings.ErrorMsg.InputIntError, 200)
        task_filter = Task.objects.filter(id__in=delete_ids)
        if task_filter.exists():
            for task_obj in task_filter.iterator():
                if task_obj.status not in ['done', 'stop']:
                    return Response(settings.ErrorMsg.TaskDeleteError, 200)
            self.perform_destroy(task_filter)
            return Response({"msg": "删除成功", "code": 0}, 200)
        return Response(settings.ErrorMsg.DeleteNotFound, 200)

    '''任务停止'''
    @action(methods=['post'], detail=False)
    def stop(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        task_id = data.get('id')
        task_filter = Task.objects.filter(id=task_id).values('celery_id')
        if task_filter.exists():
            celery_id = task_filter[0]['celery_id']
            control = app.control
            control.revoke(celery_id, signal='SIGTERM', terminate=True)
            task_filter.update(status=settings.TaskStatus.STOP, end_time=timezone.now())
            return Response({"msg": "success", "data":[{"task_id": task_id}], "code": 0})
        return Response(settings.ErrorMsg.TaskNotFound)


class VulViewSet(LoginRequiredJSONMixin,
                 viewsets.GenericViewSet):
    http_method_names = ['post']
    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        task_id = data.get('id')
        query_url = data.get('query')
        if isinstance(task_id, str) and not str.isnumeric(task_id):
            return Response(settings.ErrorMsg.InputIntError, 200)
        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'
        queryset = Vulnerability.objects.filter(task__id=task_id).order_by(field)
        if query_url:
            queryset = queryset.filter(url__contains=query_url).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = VulnerabilitySerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

class FuzzViewSet(LoginRequiredJSONMixin,
                  viewsets.GenericViewSet):

    http_method_names = ['post']

    '''查看详情'''
    @action(methods=['post'], detail=False)
    def view(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        task_id = data.get('id')
        url = data.get('url')
        query_fuzz_url = data.get('query')
        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'
        queryset = Fuzz.objects.filter(task_id=task_id, url=url).order_by(field)

        if query_fuzz_url:
            queryset = queryset.filter(fuzz_url__contains=query_fuzz_url).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = Fuzz_viewSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        query_url = data.get('query')
        task_id = data.get('id')
        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'
        queryset = Fuzz.objects.filter(task_id=task_id).values('url').annotate(count=Count('url'))

        if query_url:
            queryset = queryset.filter(url__contains=query_url).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = FuzzSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)


class PocViewSet(LoginRequiredJSONMixin,
                 viewsets.GenericViewSet):

    http_method_names = ['post']

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        query_poc_url = data.get('query')
        task__id = data.get('id')
        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'
        queryset = Poc_check.objects.filter(task_id=task__id).order_by(field)

        if query_poc_url:
            queryset = queryset.filter(poc_url__contains=query_poc_url).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = Poc_checkSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)


class BruteViewSet(LoginRequiredJSONMixin,
                 viewsets.GenericViewSet):

    http_method_names = ['post']

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        query_ip_address = data.get('query')
        task__id = data.get('id')
        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'
        queryset = Brute.objects.filter(task_id=task__id).order_by(field)

        if query_ip_address:
            queryset = queryset.filter(ip_address__contains=query_ip_address).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = BruteSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)


class ConfigViewSet(LoginRequiredJSONMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    http_method_names = ['get', 'post']

    @action(methods=['get'], detail=False)
    def show(self, request, *args, **kwargs):
        with open(settings.SETTING_FILE) as f:
            yaml_configuration = yaml.safe_load(f)

        fofa_api_email = yaml_configuration['fofa_api']['email']
        fofa_api_key = yaml_configuration['fofa_api']['key']
        shodan_api_key = yaml_configuration['shodan_api']['key']
        if fofa_api_email and len(fofa_api_email) > 6:
            yaml_configuration['fofa_api']['email'] = fofa_api_email[:3] + '********' + fofa_api_email[-3:]
        if fofa_api_key and len(fofa_api_key) > 6:
            yaml_configuration['fofa_api']['key'] = fofa_api_key[:3] + '********' + fofa_api_key[-3:]
        if shodan_api_key and len(shodan_api_key) > 6:
            yaml_configuration['shodan_api']['key'] = shodan_api_key[:3] + '********' + shodan_api_key[-3:]
        return Response({"code": 0, "data": yaml_configuration}, 200)

    @action(methods=['post'], detail=False)
    def save(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        msg = "success"
        code = 0

        with open(settings.SETTING_FILE) as f:
            yaml_configuration = yaml.safe_load(f)

        for data_key, data_value in data.items():
            if isinstance(data_value, dict):
                yaml_configuration[data_key].update(data[data_key])
                if data_key == 'fofa_api':
                    url = f'https://fofa.so/api/v1/info/my?email={yaml_configuration[data_key]["email"]}&key={yaml_configuration[data_key]["key"]}'
                    resp = requests.get(url, verify=False)
                    if resp.json().get('error'):
                        msg = "FOFA API密钥错误"
                        code = 701
                elif data_key == 'shodan_api':
                    url = f'https://api.shodan.io/api-info?key={data_value["key"]}'
                    resp = requests.get(url, verify=False)
                    if resp.status_code == 401:
                        msg = "Shodan API密钥错误"
                        code = 702
            else:
                yaml_configuration[data_key] = data_value

        with open(settings.SETTING_FILE, encoding='utf-8', mode='w') as f:
            yaml.dump(yaml_configuration, stream=f, allow_unicode=True)

        return Response({"code": code, "msg": msg}, 200)

