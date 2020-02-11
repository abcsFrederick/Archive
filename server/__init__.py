from girder.constants import  SettingDefault
from .SAIPConfig import PluginSettings

from . import rest
# import copy
# from girder import events

SettingDefault.defaults.update({
    PluginSettings.SAIP_CONFIG: {
        'host': 'ivg-webdev',
        'dbname': 'SAIP',
        'user': 'miaot2',
        'password': 'luying0325',
        'port': 3306
    },
    PluginSettings.SACIPPY_CONFIG: {
        'host': 'ivg-webdev',
        'dbname': 'miaot2',
        'user': 'postgres',
        'password': 'admin_password',
        'port': 5432
    }
})
def load(info):
    # info['apiRoot'].scippy = Prefix()
    info['apiRoot'].Archive = rest.Archive()

