from girder.models.setting import Setting
import mysql.connector as mariadb

class MariadbProxy(object):
    def __init__(self, logger=None):
        """ conn is an ordinary MongoDB-connection.

        """
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.configuration = Setting().get('Archive.SAIP')
        self.conn = self.connection()
        self.logger = logger
        Setting().get('Archive.SAIP')

    def connection(self):
        try:
            mariadb_connection = mariadb.connect(
                host=self.configuration['host'], 
                port=self.configuration['port'], 
                user=self.configuration['user'],
                password=self.configuration['password'], 
                database=self.configuration['dbname'])
            print "I am able to connect to fr-s-mysql-4 database"
            return mariadb_connection
        except mariadb.Error as error:
            print("Error: {}".format(error))