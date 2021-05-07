from girder.models.setting import Setting
from girder.exceptions import AccessException
import mysql.connector as mariadb


class MariadbProxy(object):
    def __init__(self, logger=None):
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.conn = self.connection(Setting().get('Archive.SAIP'))
        self.logger = logger
        Setting().get('Archive.SAIP')

    def connection(self, configuration):
        try:
            mariadb_connection = mariadb.connect(
                host=configuration['host'],
                port=configuration['port'],
                user=configuration['user'],
                password=configuration['password'],
                database=configuration['dbname'],
                auth_plugin='mysql_native_password')
            return mariadb_connection
        except Exception:
            raise AccessException('Cannot connection to mariaDB on host:%s, databse:%s, user:%s' %
                                  (configuration['host'],
                                   configuration['dbname'],
                                   configuration['user']))
