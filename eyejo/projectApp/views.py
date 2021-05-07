from django import http
from projectApp.config import settings
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination,_positive_int
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework import viewsets, mixins
from rest_framework.decorators import action
from django.http import HttpResponse
from projectApp.utils import TargetHandle, check_black_ip
from EyeJo.tasks import task_func
from projectApp.api.serializers import *
from projectApp.models import Project, Task, Asset, Asset_task_relationship, Url_info
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import InvalidPage
from pathlib import Path
from collections import defaultdict
from plugin.extra import SideStationInfo, CNetInfo
import datetime
import yaml
import xlwt
import re
from io import BytesIO


class LoginView(APIView):
    def post(self, request):
        data = JSONParser().parse(request)
        username = data.get('username')
        password = data.get('password')
        remembered = data.get('remembered')
        user = authenticate(request, username=username, password=password)
        if user is None:
            return http.JsonResponse(settings.ErrorMsg.LoginFail)
        login(request, user)
        if remembered != True:
            # 如果没有记住，session在关闭浏览器后立刻失效
            request.session.set_expiry(0)
        else:
            # 如果记住，设置session有效期为14天（默认）
            request.session.set_expiry(None)
        response = http.JsonResponse({"msg": "success", "code": 0})
        response.set_cookie(key='username', value=user.username)
        return response


class LogoutView(APIView):
    def get(self, request):
        # logout()，会清理 session
        logout(request)
        response = http.JsonResponse({"msg": "success", "code": 0})
        # 手动删除返回的cookie
        response.delete_cookie('username')
        return response


# 继承LoginRequiredMixin类，重写handle_no_permission()方法
class LoginRequiredJSONMixin(LoginRequiredMixin):
    # 若用户未登录，直接返回json给前端
    def handle_no_permission(self):
        return http.JsonResponse(settings.ErrorMsg.NotLogin)


class ViewPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_query_param = 'page'

    def paginate_queryset(self, queryset, request, view=None):
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except InvalidPage:
            self.page = paginator.page(1)
            # msg = self.invalid_page_message.format(
            #     page_number=page_number, message=str(exc)
            # )
            # raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True

        self.request = request
        return list(self.page)

    def get_page_size(self, request):
        if self.page_size_query_param:
            try:
                return _positive_int(request.get(self.page_size_query_param),
                                     strict=True,
                                     cutoff=self.max_page_size
                                     )
            except (KeyError, ValueError):
                pass

        return self.page_size

    def get_paginated_response(self, data):
        return Response({
            'code': 0,
            'msg': 'success',
            'total': self.page.paginator.count,
            'data': data,
        })


class UserInfoViewSet(LoginRequiredJSONMixin,
                      viewsets.GenericViewSet):
    http_method_names = ['get']

    @action(methods=['get'], detail=False)
    def check(self, request, *args, **kwargs):
        return Response({"msg": "success", "code": 0}, 200)


class ProjectViewSet(LoginRequiredJSONMixin, mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     viewsets.GenericViewSet):
    http_method_names = ['get', 'post']

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)

        project_name = data.get('query')
        field = data.get('field') or '-id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'
        page_object = ViewPagination()
        queryset = Project.objects.all().order_by(field)

        if project_name:
            queryset = queryset.filter(name__contains=project_name).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = ProjectSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    '''单个项目删除'''
    @action(methods=['post'], detail=False)
    def delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_id = data.get('id')
        if isinstance(delete_id, str) and str.isnumeric(delete_id):
            return Response(settings.ErrorMsg.InputIntError, 200)
        try:
            project_get = Project.objects.get(id=delete_id)
            asset_task_status = Asset_task_relationship.objects.filter(asset_group__asset__project_id=delete_id).values(
                'task__name', 'task__status').distinct()

            for task_status in asset_task_status.iterator():
                if task_status['task__status'] not in ['done', 'stop']:
                    msg = settings.ErrorMsg.TaskDeleteError.copy()
                    msg.update({"msg": f"{msg['msg']}, Task: {task_status['task__name']}"})
                    return Response(msg, 200)
                task_obj = Task.objects.filter(name=task_status['task__name'])
                self.perform_destroy(task_obj)
            self.perform_destroy(project_get)
            return Response({"msg": "删除成功", "code": 0}, 200)
        except Project.DoesNotExist:
            return Response(settings.ErrorMsg.DeleteNotFound, 200)

    '''批量删除'''
    @action(methods=['post'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_ids = data.get('id')
        for check_id in delete_ids:
            if isinstance(check_id, str) and str.isnumeric(check_id):
                return Response(settings.ErrorMsg.InputIntError, 200)
        project_filter = Project.objects.filter(id__in=delete_ids)
        if project_filter.exists():
            asset_task_status = Asset_task_relationship.objects.filter(
                asset_group__asset__project_id__in=delete_ids).values('task__name', 'task__status').distinct()
            task_name_list = []
            for task_status in asset_task_status.iterator():
                if task_status['task__status'] not in ['done', 'stop']:
                    msg = settings.ErrorMsg.TaskDeleteError.copy()
                    msg.update({"task": f"任务名: {task_status['task__name']}"})
                    return Response(msg, 200)
                task_name_list.append(task_status['task__name'])
            task_filter = Task.objects.filter(name__in=task_name_list)
            self.perform_destroy(project_filter)
            self.perform_destroy(task_filter)
            return Response({"msg": "success", "code": 0}, 200)
        return Response(settings.ErrorMsg.DeleteNotFound, 200)

    '''创建项目的初始化信息'''
    @action(methods=['get'], detail=False)
    def add_info(self, request, *args, **kwargs):
        fuzz_arg = [str(fuzz_file).replace(f'{settings.FUZZ_PATH}/', '') for fuzz_file in
                    Path(settings.FUZZ_PATH).iterdir() if fuzz_file.suffix == '.txt']
        port_arg = settings.TOP_PORT

        poc_arg_dict = defaultdict(list)
        for absolute_path in Path(settings.POC_PATH).iterdir():
            if absolute_path.is_dir():
                for poc_file in absolute_path.iterdir():
                    relative_path = str(poc_file).split(f'{settings.POC_PATH}/')[-1]
                    poc_arg_dict[relative_path.split('/')[0]].append(relative_path.split('/')[1])

        data = {
            "fuzz_file": fuzz_arg,
            "ports": port_arg,
            "pocss": poc_arg_dict,
            "brute_file": settings.BRUTE_SERVICE
        }
        return Response({"msg": "success", "code": 0, "data": data}, 200)

    '''创建'''
    def create(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        project_name = data.pop('project_name')

        # 限制前端输入的内容
        if not project_name:
            return Response(settings.ErrorMsg.ProjectNameEmpty, 200)

        if Project.objects.filter(name=project_name).exists():
            return Response(settings.ErrorMsg.ProjectExist, 200)

        re_project = re.findall(
            '[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300ba-zA-Z0-9_-]+',
            project_name)
        if re_project:
            return Response(settings.ErrorMsg.ProjectNameInvalid, 200)

        if data.get('option_ports'):
            re_ports = re.findall('[^\d,-]+', data.get('option_ports'))
            if re_ports:
                return Response(settings.ErrorMsg.PortInvalid, 200)

        if data.get('option_brute_type'):
            re_brute_type = re.findall('[^a-zA-Z0-9-,_]+', data.get('option_brute_type'))
            if re_brute_type:
                return Response(settings.ErrorMsg.BruteTypeInvalid, 200)

        if data.get('option_fuzz_file'):
            re_fuzz_file = re.findall(
                '[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300ba-zA-Z0-9._-]+',
                data.get('option_fuzz_file'))
            if re_fuzz_file:
                return Response(settings.ErrorMsg.FuzzFileInvalid, 200)

        targets = data.pop('targets')
        targets = targets.strip().lower()
        target_list = re.split(r",|\s+", targets)
        scheme_target_dict = TargetHandle.get_schema_target_dict(target_list)
        target_dict = TargetHandle.get_target_dict(target_list)
        if scheme_target_dict.get(False):
            msg = settings.ErrorMsg.TargetInvalid.copy()
            msg.update({"target": scheme_target_dict.get(False)})
            return Response(msg, 200)
        for ip in target_dict['ip']:
            if check_black_ip(ip):
                msg = settings.ErrorMsg.IPInBlackIpc.copy()
                msg.update({"ip": ip})
                return Response(msg, 200)

        with open(settings.SETTING_FILE) as f:
            yaml_configuration = yaml.safe_load(f)

        project_obj = Project.objects.create(name=project_name)
        Asset.objects.create(project_id=project_obj.id, name=f'{project_name}-默认资产组')
        task_obj = Task.objects.create(name=f'{project_name}-新建任务', project_id=project_obj.id, status=settings.TaskStatus.WAITING, **data)
        task_data = {
            'yaml_config': yaml_configuration,
            'data': data,
            'scheme_target_dict': scheme_target_dict,
            'target_dict': target_dict,
            'project_id': project_obj.id,
            'task_id': task_obj.id
        }
        celery_id = task_func.delay(task_data)
        Task.objects.filter(id=task_obj.id).update(celery_id=str(celery_id))
        return Response({"msg": "创建成功", "code": 0})


class Url_infoViewSet(LoginRequiredJSONMixin,
                      mixins.DestroyModelMixin,
                      viewsets.GenericViewSet):
    http_method_names = ['post']

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        project_id = data.get('id')
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if isinstance(project_id, str) and not str.isnumeric(project_id):
            return Response(settings.ErrorMsg.InputIntError, 200)

        if field == 'icons':
            field = 'icons_hash'
        elif field == 'pic':
            field = 'pic_hash'

        if order == 'desc':
            field = f'-{field}'

        query_dict = {}
        for data_key, data_value in data.items():
            # if data_key not in ['field', 'order', 'page', 'limit', 'id']:
            if data_key in ['icons_hash', 'pic_hash', 'url', 'title']:
                query_dict[f'{data_key}__contains'] = data_value
            elif data_key == 'finger':
                query_dict['finger__icontains'] = data_value
            elif data_key == 'tag_name':
                query_dict['tags__name'] = data_value

        queryset = Url_info.objects.filter(project_id=project_id, screen_status__in=['success', 'false']).order_by(
            field)
        page_object = ViewPagination()
        if query_dict:
            queryset = queryset.filter(**query_dict).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = UrlInfoSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    @action(methods=['post'], detail=False)
    def export(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        project_id = data.get('id')
        url_info = Url_info.objects.filter(project_id=project_id, screen_status__in=['success', 'false'])
        workbook = xlwt.Workbook(encoding='utf-8')
        sheet = workbook.add_sheet("站点详情")
        cols = 0
        font = xlwt.Font()
        font.bold = True
        style0 = xlwt.XFStyle()
        style0.font = font

        first_line_list = ['URL', '状态码', '标题', '指纹']
        for num in range(0, len(first_line_list)):
            sheet.write(cols, num, first_line_list[num], style0)

        cols += 1
        for query in url_info.iterator():
            sheet.write(cols, 0, query.url)
            sheet.write(cols, 1, query.status_code)
            sheet.write(cols, 2, query.title)
            sheet.write(cols, 3, query.finger)
            cols += 1

        ipaddress_info = IPAddress.objects.filter(project_id=project_id).values(
            'ip_domain_relationship__subdomain__subdomain', 'ip_domain_relationship__subdomain__m_domain', 'ip_address',
            'port__port', 'port__protocol')
        sheet = workbook.add_sheet("资产信息")
        cols = 0

        first_line_list = ['主域名', '子域名', 'IP地址', '端口', '端口协议']
        for num in range(0, len(first_line_list)):
            sheet.write(cols, num, first_line_list[num], style0)

        cols += 1
        for query in ipaddress_info.iterator():
            sheet.write(cols, 0, query['ip_domain_relationship__subdomain__m_domain'])
            sheet.write(cols, 1, query['ip_domain_relationship__subdomain__subdomain'])
            sheet.write(cols, 2, query['ip_address'])
            sheet.write(cols, 3, query['port__port'])
            sheet.write(cols, 4, query['port__protocol'])
            cols += 1

        # 创建操作二进制数据的对象
        output = BytesIO()
        # 将excel数据写入到内存中
        workbook.save(output)
        # 设置文件读取的偏移量，0表示从头读起
        output.seek(0)
        nowtime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        # 设置HTTP的报头为二进制流
        response = HttpResponse(output.getvalue(), content_type='application/octet-stream')
        # 设置文件名
        # response_headers.update({"Content-Disposition": f"attachment; filename=export-{nowtime}.xls"})
        response['Content-Disposition'] = f'filename=export-{project_id}-{nowtime}.xls'
        return response

    @action(methods=['post'], detail=False)
    def tags_show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        query_tag = data.get('query')
        project_id = data.get('project_id')

        page_object = ViewPagination()
        queryset = Tags.objects.filter(project_id=project_id).values('name').distinct()
        if query_tag:
            queryset = queryset.filter(name__contains=f'{query_tag}')
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = TagsViewSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    @action(methods=['post'], detail=False)
    def tags_add(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        url_info_id_list = data.get('id')
        project_id = data.get('project_id')
        name = data.get('name')
        if not url_info_id_list:
            return settings.ErrorMsg.TagsAddError
        Tags.objects.bulk_create(
            map(lambda url_info_id: Tags(name=name, url_info_id=url_info_id, project_id=project_id), url_info_id_list),
            batch_size=1000, ignore_conflicts=True)
        return Response({"msg": "success", "code": 0})

    @action(methods=['post'], detail=False)
    def tags_delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_name = data.get('name')
        project_id = data.get('project_id')
        assets_group_queryset = Tags.objects.filter(name=delete_name, project_id=project_id)
        if assets_group_queryset.exists():
            self.perform_destroy(assets_group_queryset)
            return Response({"msg": "success", "code": 0}, 200)
        return Response(settings.ErrorMsg.DeleteNotFound, 200)


class IPViewSet(LoginRequiredJSONMixin,
                viewsets.GenericViewSet):
    http_method_names = ['post']

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        project_id = data.get('id')
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'

        query_dict = {}
        for data_key, data_value in data.items():
            if data_key in ['port', 'protocol']:
                query_dict[f'port__{data_key}__contains'] = data_value
            elif data_key == 'ip_address':
                query_dict[f'{data_key}__contains'] = data_value
        queryset = IPAddress.objects.filter(project_id=project_id).order_by(field)
        page_object = ViewPagination()
        if query_dict:
            queryset = queryset.filter(**query_dict).order_by(field).distinct()
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = IPSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    '''获取旁站信息'''
    @action(methods=['post'], detail=False)
    def side_station(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        ip = data.get('ip')
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'

        queryset = Side_station.objects.filter(ip_address=ip).order_by(field)

        page_object = ViewPagination()
        if not queryset.exists():
            SideStationInfo(ip).info()
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = SideStationViewSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    '''获取C段信息'''
    @action(methods=['post'], detail=False)
    def cnet(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        ip = data.get('ip')
        ip_c = f"{'.'.join(ip.split('.')[:3])}.0/24"
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'

        queryset = C_net.objects.filter(ip_c=ip_c).order_by(field)
        page_object = ViewPagination()
        if not queryset.exists():
            CNetInfo(ip).main()
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = CNetViewSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)


class DomainViewSet(LoginRequiredJSONMixin,
                    viewsets.GenericViewSet):
    http_method_names = ['post']

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        project__id = data.get('id')
        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'

        query_dict = {}
        for data_key, data_value in data.items():
            if data_key in ['subdomain']:
                query_dict[f'{data_key}__contains'] = data_value
            elif data_key in ['ip_address']:
                query_dict[f'ip_domain_relationship__ip__{data_key}__contains'] = data_value
        queryset = Subdomain.objects.filter(project__id=project__id).order_by(field)

        if query_dict:
            queryset = queryset.filter(**query_dict).order_by(field).distinct()
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = SubdomainSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)


class LoginSiteViewSet(LoginRequiredJSONMixin,
                       viewsets.GenericViewSet):
    http_method_names = ['post']

    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        query_subdomain = data.get('query')
        project_id = data.get('id')
        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'

        queryset = Crawl.objects.filter(task__project_id=project_id, is_login=1).order_by(field).distinct()
        if query_subdomain:
            queryset = queryset.filter(subdomain__contains=query_subdomain).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = CrawlSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)


class AssetsViewSet(LoginRequiredJSONMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    http_method_names = ['post']

    @action(methods=['post'], detail=False)
    def check_name(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        query_project_name = data.get('query')
        queryset = Project.objects.filter(name=query_project_name)
        if queryset.exists():
            return Response({"code": 0, "msg": "success", "data": True})
        return Response({"code": 0, "msg": "success", "data": False})

    '''资产组创建'''
    def create(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        project_id = data.get('project_id')
        asset_group_name = data.get('name')
        tag_name = data.get('tag_name')
        input_type = data.get('input_type')
        if Asset.objects.filter(project_id=project_id, name=asset_group_name).exists():
            return Response(settings.ErrorMsg.AssetExist)
        re_asset = re.findall('[^\u4e00-\u9fa5a-zA-Z0-9_-]+', asset_group_name)
        if re_asset:
            return Response(settings.ErrorMsg.AssetNameInvalid, 200)

        if tag_name:
            asset_obj = Asset.objects.create(project_id=project_id, name=asset_group_name)
            url_list = Tags.objects.filter(name__in=tag_name, project_id=project_id).values_list('url_info__url', flat=True)
            Asset_group.objects.bulk_create(map(lambda x: Asset_group(asset_id=asset_obj.id, url=x), url_list),
                                            batch_size=1000, ignore_conflicts=True)
            return Response({"msg": "success", "code": 0})

        asset_group_url = data.get('url')
        if not asset_group_url:
            return Response(settings.ErrorMsg.AssetUrlEmpty, 200)

        asset_group_url = re.split(r",|\s+", asset_group_url)
        scheme_target_dict = TargetHandle.get_schema_target_dict(asset_group_url)

        if scheme_target_dict.get(False):
            msg = settings.ErrorMsg.TargetInvalid.copy()
            msg.update({"target": scheme_target_dict.get(False)})
            return Response(msg, 200)

        asset_obj = Asset.objects.create(project_id=project_id, name=asset_group_name)

        domain_cname_dict = TargetHandle.domain_list_get_cname(scheme_target_dict.get('domain'))
        subdomain_save_list = []
        for subdomain in scheme_target_dict.get('domain'):
            subdomain = TargetHandle.get_target(subdomain).get('new_target')
            m_domain = TargetHandle.get_main_domain(subdomain)
            subdomain_save_list.append(Subdomain(project_id=project_id, subdomain=subdomain, m_domain=m_domain, cname=domain_cname_dict.get(subdomain)))
        Subdomain.objects.bulk_create(subdomain_save_list, ignore_conflicts=True)

        asset_group_url = scheme_target_dict.get('domain') + scheme_target_dict.get('ip')
        if input_type == 2:
            is_domain_resolution = data.get('is_domain_resolution')

            if not is_domain_resolution:
                scheme_target_dict['domain'] = []

            with open(settings.SETTING_FILE) as f:
                yaml_configuration = yaml.safe_load(f)
            TargetHandle.GetIpInfo(scheme_target_dict, project_id, asset_obj.id, yaml_configuration).main()

        Asset_group.objects.bulk_create(map(lambda x: Asset_group(asset_id=asset_obj.id, url=x), asset_group_url),
                                        batch_size=1000, ignore_conflicts=True)
        return Response({"msg": "success", "code": 0})

    '''项目的资产组列表'''
    @action(methods=['post'], detail=False)
    def show(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        query_asset_name = data.get('query')
        project__id = data.get('id')

        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'
        queryset = Asset.objects.filter(project_id=project__id).order_by(field)
        if query_asset_name:
            queryset = queryset.filter(project_id=project__id, name__contains=query_asset_name).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = AssetsSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    '''查看项目的资产组'''
    @action(methods=['post'], detail=False)
    def url_info(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        project_id = data.get('id')
        page_object = ViewPagination()
        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'

        query_dict = {}
        for data_key, data_value in data.items():
            if data_key in ['url', 'status']:
                query_dict[f'{data_key}__contains'] = data_value
        queryset = Asset_group.objects.filter(asset__project_id=project_id).values('url').order_by(field).distinct()
        if query_dict:
            queryset = queryset.filter(**query_dict).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = AssetsUrlSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    '''查看详情'''
    @action(methods=['post'], detail=False)
    def view(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        asset_id = data.get('id')
        page_object = ViewPagination()

        field = data.get('field') or 'id'
        order = data.get('order') or 'asc'
        if order == 'desc':
            field = f'-{field}'

        query_dict = {}
        for data_key, data_value in data.items():
            if data_key in ['url', 'status']:
                query_dict[f'{data_key}__contains'] = data_value
        queryset = Asset_group.objects.filter(asset_id=asset_id).order_by(field)

        if query_dict:
            queryset = queryset.filter(**query_dict).order_by(field)
        page_chapter = page_object.paginate_queryset(queryset, data)
        serializer = AssetsViewSerializer(instance=page_chapter, many=True)
        return page_object.get_paginated_response(serializer.data)

    '''添加新目标进资产组'''
    @action(methods=['post'], detail=False)
    def add(self, request, *args, **kwargs):

        data = JSONParser().parse(request)
        asset_id = data.get('id')
        tag_name = data.get('tag_name')
        project_id = data.get('project_id')
        is_domain_resolution = data.get('is_domain_resolution')
        if tag_name:
            url_list = Tags.objects.filter(name__in=tag_name, url_info__project_id=project_id).values_list(
                'url_info__url', flat=True)
            Asset_group.objects.bulk_create(map(lambda x: Asset_group(asset_id=asset_id, url=x), url_list),
                                            batch_size=1000, ignore_conflicts=True)
            return Response({"msg": "success", "code": 0})

        asset_group_url = re.split(r",|\s+", data.get('url'))
        scheme_target_dict = TargetHandle.get_schema_target_dict(asset_group_url)
        asset_group_url = scheme_target_dict.get('domain') + scheme_target_dict.get('ip')

        domain_cname_dict = TargetHandle.domain_list_get_cname(scheme_target_dict.get('domain'))
        subdomain_save_list = []
        for subdomain in scheme_target_dict.get('domain'):
            subdomain = TargetHandle.get_target(subdomain).get('new_target')
            m_domain = TargetHandle.get_main_domain(subdomain)
            subdomain_save_list.append(Subdomain(project_id=project_id, subdomain=subdomain, m_domain=m_domain, cname=domain_cname_dict.get(subdomain)))
        Subdomain.objects.bulk_create(subdomain_save_list, ignore_conflicts=True)

        if not is_domain_resolution:
            scheme_target_dict['domain'] = []

        with open(settings.SETTING_FILE) as f:
            yaml_configuration = yaml.safe_load(f)
        TargetHandle.GetIpInfo(scheme_target_dict, project_id, asset_id, yaml_configuration).main()
        Asset_group.objects.bulk_create(map(lambda x: Asset_group(asset_id=asset_id, url=x), asset_group_url),
                                        batch_size=1000, ignore_conflicts=True)
        return Response({"msg": "success", "code": 0})

    '''单个资产删除'''
    @action(methods=['post'], detail=False)
    def url_delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_id = data.get('id')
        assets_group_queryset = Asset_group.objects.filter(id=delete_id)
        if assets_group_queryset.exists():
            self.perform_destroy(assets_group_queryset)
            return Response({"msg": "success", "code": 0}, 200)
        return Response(settings.ErrorMsg.DeleteNotFound, 200)

    '''批量资产删除'''
    @action(methods=['post'], detail=False)
    def url_multiple_delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_ids = data.get('id')
        assets_group_queryset = Asset_group.objects.filter(id__in=delete_ids)

        if assets_group_queryset.exists():
            self.perform_destroy(assets_group_queryset)
            return Response({"msg": "success", "code": 0}, 200)
        return Response(settings.ErrorMsg.DeleteNotFound, 200)

    '''单个资产组删除'''
    @action(methods=['post'], detail=False)
    def delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_id = data.get('id')
        assets_queryset = Asset.objects.filter(id=delete_id)
        if assets_queryset.exists():
            self.perform_destroy(assets_queryset)
            return Response({"msg": "success", "code": 0}, 200)
        return Response(settings.ErrorMsg.DeleteNotFound, 200)

    '''批量资产组删除'''
    @action(methods=['post'], detail=False)
    def multiple_delete(self, request, *args, **kwargs):
        data = JSONParser().parse(request)
        delete_ids = data.get('id')
        assets_queryset = Asset.objects.filter(id__in=delete_ids)
        if assets_queryset.exists():
            self.perform_destroy(assets_queryset)
            return Response({"msg": "success", "code": 0}, 200)
        return Response(settings.ErrorMsg.DeleteNotFound, 200)

