from projectApp.models import Login_site
from threading import Timer
import subprocess
from projectApp.config import settings
import json
from collections import defaultdict
from projectApp import utils

logger = utils.get_logger()


class FingerMap:

    def __init__(self, project_id, task_id):
        self.project_id = project_id
        self.task_id = task_id
        self.login_site_filter = Login_site.objects.filter(task_id=task_id)
        self.run_count = 0

    def finger_run(self, url, html, headers):
        finger_result = '{}'
        cmd = [settings.FINGER_EXEC, "-host", f"localfile-#-{str(settings.basedir)}/{html}", "-head", headers, "-output", "json", "-apps", settings.FINGER_PATH_LIB]
        rsp = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        timer = Timer(3 * 10, lambda process: process.kill(), [rsp])
        try:
            timer.start()
            output, error = rsp.communicate()
            webinfo = json.loads(output.decode())

            finger_dict = defaultdict(set)
            for matche in webinfo.get('matches'):
                finger_dict[matche['app']['category_names'][0]].add(matche['app_name'])

            finger_dict = {k: list(v) for k, v in finger_dict.items()}
            if finger_dict:
                finger_result = json.dumps(finger_dict)
            if "通用Web管理后台" == finger_dict.get("Web servers"):
                self.login_site_filter.get_or_create(task_id=self.task_id, defaults={'url': url})
        except subprocess.TimeoutExpired:
            logger.warning(f'Error target, is Timeout')
            logger.warning(f'fail_target_url===========>{url}')
        finally:
            timer.cancel()
            return finger_result
