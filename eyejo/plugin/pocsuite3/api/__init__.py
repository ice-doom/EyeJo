from plugin.pocsuite3.lib.controller.controller import start
from plugin.pocsuite3.lib.core.common import single_time_warn_message
from plugin.pocsuite3.lib.core.data import conf, kb, logger, paths
from plugin.pocsuite3.lib.core.datatype import AttribDict
from plugin.pocsuite3.lib.core.enums import PLUGIN_TYPE, POC_CATEGORY, VUL_TYPE
from plugin.pocsuite3.lib.core.option import init, init_options
from plugin.pocsuite3.lib.core.plugin import PluginBase, register_plugin
from plugin.pocsuite3.lib.core.poc import POCBase, Output
from plugin.pocsuite3.lib.core.register import (
    load_file_to_module,
    load_string_to_module,
    register_poc,
)
from plugin.pocsuite3.lib.core.settings import DEFAULT_LISTENER_PORT
from plugin.pocsuite3.lib.request import requests
from plugin.pocsuite3.lib.utils import get_middle_text, generate_shellcode_list, random_str
from plugin.pocsuite3.modules.ceye import CEye
from plugin.pocsuite3.modules.listener import REVERSE_PAYLOAD
from plugin.pocsuite3.modules.seebug import Seebug
from plugin.pocsuite3.modules.zoomeye import ZoomEye
from plugin.pocsuite3.modules.shodan import Shodan
from plugin.pocsuite3.modules.fofa import Fofa
from plugin.pocsuite3.modules.censys import Censys
from plugin.pocsuite3.modules.spider import crawl
from plugin.pocsuite3.modules.httpserver import PHTTPServer
from plugin.pocsuite3.shellcodes import OSShellcodes, WebShell
from plugin.pocsuite3.lib.core.interpreter_option import OptDict, OptIP, OptPort, OptBool, OptInteger, OptFloat, OptString, \
    OptItems, OptDict

__all__ = (
    'requests', 'PluginBase', 'register_plugin',
    'PLUGIN_TYPE', 'POCBase', 'Output', 'AttribDict', 'POC_CATEGORY', 'VUL_TYPE',
    'register_poc', 'conf', 'kb', 'logger', 'paths', 'DEFAULT_LISTENER_PORT', 'load_file_to_module',
    'load_string_to_module', 'single_time_warn_message', 'CEye', 'Seebug',
    'ZoomEye', 'Shodan', 'Fofa', 'Censys', 'PHTTPServer', 'REVERSE_PAYLOAD', 'get_listener_ip', 'get_listener_port',
    'get_results', 'init_pocsuite', 'start_pocsuite', 'get_poc_options', 'crawl',
    'OSShellcodes', 'WebShell', 'OptDict', 'OptIP', 'OptPort', 'OptBool', 'OptInteger', 'OptFloat', 'OptString',
    'OptItems', 'OptDict', 'get_middle_text', 'generate_shellcode_list', 'random_str')


def get_listener_ip():
    return conf.connect_back_host


def get_listener_port():
    return conf.connect_back_port


def get_current_poc_obj():
    pass


def get_poc_options(poc_obj=None):
    poc_obj = poc_obj or kb.current_poc
    return poc_obj.get_options()


def get_results():
    return kb.results


def init_pocsuite(options={}):
    init_options(options)
    init()


def start_pocsuite():
    start()
