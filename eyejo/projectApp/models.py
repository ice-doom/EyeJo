# import os
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EyeJo.settings")
# import django
# django.setup()

from django.db import models
from django.utils import timezone


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'project'  # 指明数据库表名


class Url_info(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=550)
    status_code = models.CharField(max_length=4, default=None)
    icons = models.CharField(max_length=500, default=None)
    icons_hash = models.CharField(max_length=32, default=None)
    pic = models.CharField(max_length=500, default=None)
    pic_hash = models.CharField(max_length=32, default=None)
    title = models.CharField(max_length=200, default=None)
    headers = models.CharField(max_length=5000, default=None)
    html = models.CharField(max_length=600, default=None)
    html_copyright = models.CharField(max_length=600, default=None)
    ssl_Organization = models.CharField(max_length=255, default=None)
    finger = models.CharField(max_length=2000, default=None)
    screen_status = models.CharField(max_length=20)
    project = models.ForeignKey(to='Project', to_field='id', on_delete=models.CASCADE, related_name='Project_To_Urlinfo')

    class Meta:
        db_table = 'url_info'  # 指明数据库表名


class Tags(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, default=None)
    url_info = models.ForeignKey(to='Url_info', to_field='id', on_delete=models.CASCADE)
    project = models.ForeignKey(to='Project', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'tags'  # 指明数据库表名


class Subdomain(models.Model):
    id = models.AutoField(primary_key=True)
    subdomain = models.CharField(max_length=260, default=None)
    m_domain = models.CharField(max_length=260, default=None)
    cname = models.CharField(max_length=500, default=None)
    project = models.ForeignKey(to='Project', to_field='id', on_delete=models.CASCADE, related_name='Project_To_Subdomain')

    class Meta:
        db_table = 'subdomain'  # 指明数据库表名


class IPAddress(models.Model):
    id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=20, unique=True)
    country = models.CharField(max_length=255)
    regionName = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    isp = models.CharField(max_length=255)
    asn = models.CharField(max_length=255)
    cdn = models.IntegerField(default=None)
    flag = models.IntegerField(default=0)
    project = models.ForeignKey(to='Project', to_field='id', on_delete=models.CASCADE, related_name='Project_To_IPAddress')

    class Meta:
        db_table = 'ipaddress'  # 指明数据库表名


class IP_domain_relationship(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.ForeignKey(to='IPAddress', to_field='id', on_delete=models.CASCADE)
    subdomain = models.ForeignKey(to='Subdomain', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'ip_domain_relationship'  # 指明数据库表名


class Port(models.Model):
    id = models.AutoField(primary_key=True)
    port = models.CharField(max_length=10)
    protocol = models.CharField(max_length=255, default=None)
    product = models.CharField(max_length=255, default=None)
    version = models.CharField(max_length=255, default=None)
    extrainfo = models.CharField(max_length=255, default=None)
    ip = models.ForeignKey(to='IPAddress', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'port'  # 指明数据库表名


class Asset(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=11)
    create_time = models.DateTimeField(default=timezone.now)
    project = models.ForeignKey(to='Project', to_field='id', on_delete=models.CASCADE, related_name='Project_To_Asset_group')

    class Meta:
        db_table = 'asset'  # 指明数据库表名


class Asset_group(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=550)
    status = models.CharField(max_length=20, default="uncheck")
    create_time = models.DateTimeField(default=timezone.now)
    asset = models.ForeignKey(to='Asset', to_field='id', on_delete=models.CASCADE, related_name='Asset_To_Asset_group')

    class Meta:
        db_table = 'asset_group'  # 指明数据库表名


class Task(models.Model):
    id = models.AutoField(primary_key=True)
    project_id = models.IntegerField()
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=40)
    option_subdomain_collect = models.CharField(max_length=10)
    option_port_scan = models.CharField(max_length=10)
    option_ports = models.CharField(max_length=10000)
    option_sf_info = models.CharField(max_length=10)
    option_fofa_search = models.CharField(max_length=550)
    option_screen_info = models.CharField(max_length=10)
    option_request_site = models.CharField(max_length=10)
    option_poc_scan = models.CharField(max_length=10)
    option_pocss = models.TextField()
    option_fuzz = models.CharField(max_length=10)
    option_fuzz_file = models.CharField(max_length=100)
    option_identify_login = models.CharField(max_length=10)
    option_vul = models.CharField(max_length=10)
    option_brute = models.CharField(max_length=10)
    option_brute_type = models.CharField(max_length=200)
    celery_id = models.CharField(max_length=40)
    create_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'task'  # 指明数据库表名


class Asset_task_relationship(models.Model):
    id = models.AutoField(primary_key=True)
    asset_group = models.ForeignKey(to='Asset_group', to_field='id', on_delete=models.CASCADE)
    task = models.ForeignKey(to='Task', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'asset_task_relationship'  # 指明数据库表名


class Poc_check(models.Model):
    id = models.AutoField(primary_key=True)
    poc_url = models.CharField(max_length=550)
    result_code = models.CharField(max_length=10)
    poc_name = models.CharField(max_length=255)
    verifyinfo = models.CharField(max_length=255)
    create_time = models.DateTimeField(default=timezone.now)
    task = models.ForeignKey(to='Task', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'poc_check'  # 指明数据库表名


class Fuzz(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=550)
    fuzz_url = models.CharField(max_length=550)
    status_code = models.IntegerField()
    lines = models.IntegerField()
    words = models.IntegerField()
    create_time = models.DateTimeField(default=timezone.now)
    task = models.ForeignKey(to='Task', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'fuzz'  # 指明数据库表名


class Vulnerability(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=550)
    payload = models.CharField(max_length=3000)
    snapshot_req = models.TextField()
    vulntype = models.CharField(max_length=100)
    scan_name = models.CharField(max_length=20)
    create_time = models.DateTimeField(default=timezone.now)
    task = models.ForeignKey(to='Task', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'vulnerability'  # 指明数据库表名


class Crawl(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=255)
    crawl_url = models.CharField(max_length=5000)
    method = models.CharField(max_length=10)
    headers = models.CharField(max_length=2000)
    req_data = models.CharField(max_length=5000, default=None)
    is_login = models.IntegerField(default=0)
    create_time = models.DateTimeField(default=timezone.now)
    task = models.ForeignKey(to='Task', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'crawl'  # 指明数据库表名


class Login_site(models.Model):
    id = models.AutoField(primary_key=True)
    url = models.CharField(max_length=550)
    create_time = models.DateTimeField(default=timezone.now)
    crawl = models.ForeignKey(to='Crawl', to_field='id', on_delete=models.CASCADE)
    task = models.ForeignKey(to='Task', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'login_site'  # 指明数据库表名


class Brute(models.Model):
    id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=20)
    port = models.CharField(max_length=10)
    service = models.CharField(max_length=255)
    username = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    create_time = models.DateTimeField(default=timezone.now)
    task = models.ForeignKey(to='Task', to_field='id', on_delete=models.CASCADE)

    class Meta:
        db_table = 'brute'  # 指明数据库表名


class Side_station(models.Model):
    id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=20)
    subdomain = models.CharField(max_length=260)
    title = models.CharField(max_length=200)
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'side_station'  # 指明数据库表名


class C_net(models.Model):
    id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=20)
    ip_c = models.CharField(max_length=20)
    title = models.CharField(max_length=200, default=None)
    create_time = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'c_net'  # 指明数据库表名








