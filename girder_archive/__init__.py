from girder import plugin
from girder.settings import SettingDefault
from .SAIPConfig import PluginSettings
from girder.utility import setting_utilities

from . import rest
# import copy
# from girder import events

@setting_utilities.default(PluginSettings.SCIPPY_MOUNT)
def _defaultSCIPPY_MOUNT():
    return '/mnt/scippy_images'

@setting_utilities.default(PluginSettings.SAIP_CONFIG)
def _defaultSAIP_CONFIG():
    # PluginSettings.SAIP_CONFIG: {
    #     'host': 'ivg-webdev',
    #     'dbname': 'SAIP',
    #     'user': 'miaot2',
    #     'password': 'luying0325',
    #     'port': 3306
    # },
    return {
        'host': 'mysql.ncifcrf.gov',
        'dbname': 'nci_production',
        'user': 'MIPortal',
        'password': 'MIPortal_20181220',
        'port': 3306
    }
@setting_utilities.default(PluginSettings.SCIPPY_CONFIG)
def _defaultSCIPPY_CONFIG():
    return {
        'host': None,
        'dbname': 'scippy',
        'user': 'miaot2',
        'password': 'postgres',
        'port': 5432
    }
    # return {
    #     'host': '129.43.3.27', # fr-s-ivg-mip-s
    #     'dbname': 'scippy',
    #     'user': 'scippy_readonly',
    #     'password': 'cardio372',
    #     'port': 5432
    # }


class ArchivePlugin(plugin.GirderPlugin):
    DISPLAY_NAME = 'Archive'
    CLIENT_SOURCE_PATH = 'web_client'

    def load(self, info):
        info['apiRoot'].archive = rest.Archive()
