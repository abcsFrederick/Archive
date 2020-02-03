class Config:
    PLUGIN_NAME = 'Archive'

class development(Config):
    DEBUG = True
    
    MYSQL_CONFIG = {
        'host': 'ivg-webdev',
        'dbname': 'SAIP',
        'user': 'miaot2',
        'password': 'luying0325',
        'port': 3306
    }

    PSQL_CONFIG = {
        'host': 'ivg-webdev',
        'dbname': 'miaot2',
        'user': 'postgres',
        'password': 'admin_password',
        'port': 5432
    }
class production(Config):
    DEBUG = False

    MYSQL_CONFIG = {
        'host': 'ivg-webdev',
        'dbname': 'SAIP',
        'user': 'miaot2',
        'password': 'luying0325',
        'port': 3306
    }

    PSQL_CONFIG = {
        'host': 'ivg-webdev',
        'dbname': 'miaot2',
        'user': 'postgres',
        'password': 'admin_password',
        'port': 5432
    }