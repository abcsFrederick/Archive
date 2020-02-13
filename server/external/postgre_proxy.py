from girder.models.setting import Setting
from girder.exceptions import AccessException
import psycopg2
import psycopg2.extras

class PostgredbProxy(object):
    def __init__(self, logger=None):
        """ conn is an ordinary MongoDB-connection.

        """
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.configuration = Setting().get('Archive.SCIPPY')
        self.conn = self.connection()
        self.logger = logger
        Setting().get('Archive.SCIPPY')

    def connection(self):
        try:
            postgre_connection = psycopg2.connect(
                dbname=self.configuration['dbname'],
                user=self.configuration['user'],
                host=self.configuration['host'],
                password=self.configuration['password'])
            return postgre_connection
        except Exception:
            raise AccessException('Cannot connection to postgre DB on host:%s, databse:%s, user:%s' %
                                  (self.configuration['host'],
                                   self.configuration['dbname'],
                                   self.configuration['user']))
