from girder.models.setting import Setting
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
            print "I am able to connect to the database"
            return postgre_connection
        except Exception:
            print "I am unable to connect to the database"
