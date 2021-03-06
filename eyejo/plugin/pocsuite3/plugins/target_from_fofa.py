from plugin.pocsuite3.api import PluginBase
from plugin.pocsuite3.api import PLUGIN_TYPE
from plugin.pocsuite3.api import logger
from plugin.pocsuite3.api import conf
from plugin.pocsuite3.api import Fofa
from plugin.pocsuite3.api import register_plugin
from plugin.pocsuite3.api import kb
from plugin.pocsuite3.lib.core.exception import PocsuitePluginDorkException


class TargetFromFofa(PluginBase):
    category = PLUGIN_TYPE.TARGETS

    def init_fofa_api(self):
        self.fofa = Fofa(user=conf.fofa_user,token=conf.fofa_token)

    def init(self):
        self.init_fofa_api()
        dork = None
        if conf.dork_fofa:
            dork = conf.dork_fofa
        else:
            dork = conf.dork
        if not dork:
            msg = "Need to set up dork (please --dork or --dork-fofa)"
            raise PocsuitePluginDorkException(msg)

        if kb.comparison:
            kb.comparison.add_dork("Fofa", dork)
        info_msg = "[PLUGIN] try fetch targets from Fofa with dork: {0}".format(dork)
        logger.info(info_msg)
        targets = self.fofa.search(dork, conf.max_page, resource=conf.search_type)
        count = 0
        if targets:
            for target in targets:
                if kb.comparison:
                    kb.comparison.add_ip(target, "Fofa")
                if self.add_target(target):
                    count += 1

        info_msg = "[PLUGIN] get {0} target(s) from Fofa".format(count)
        logger.info(info_msg)

register_plugin(TargetFromFofa)
