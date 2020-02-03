import psycopg2
import psycopg2.extras
from girder.api.rest import Resource
from girder.api.describe import Description, autoDescribeRoute
from girder.api import access
# import json
# import datetime
from os import listdir
import os
from girder.models.collection import Collection as girderCollection
from girder.models.folder import Folder as FolderModel
# from girder.models.item import Item as ItemModel
# from girder.models.file import File as FileModel
from girder.constants import AccessType
from girder.models.assetstore import Assetstore
from girder.utility import assetstore_utilities, config
from .models.SSRArchive import SSRArchive
from .models.SAIPArchive import SAIPArchive
import SAIPConfig
# import copy
# from girder import events


class Archive(Resource):
    def __init__(self):
        super(Archive, self).__init__()
        configSection = config.getConfig().get('server').get('mode')
        if configSection == 'development':
            self.configuration = SAIPConfig.development
        else:
            self.configuration = SAIPConfig.production
        self.resourceName = SAIPConfig.Config.PLUGIN_NAME

        self.mnt = '/mnt/scippy_images/'
        # more secure with login current user info
        self.route('GET', ('projects', 'ssr',), self.getSSRProjects)
        self.route('GET', ('projects', 'saip',), self.getSAIPProjects)
        self.route('GET', (':id', 'experiments'), self.getExperiments)
        self.route('GET', (':id', 'patients'), self.getPatients)
        self.route('GET', (':id', 'rootpath', 'patient'), self.getPatientSeriesRoot)
        self.route('GET', (':id', 'rootpath', 'study'), self.getStudySeriesRoot)
        self.route('GET', (':id', 'rootpath', 'series'), self.getSeriesSeriesRoot)
        self.route('GET', (':id', 'rootpath', 'experiment'), self.getExperimentSeriesRoot)
        self.route('GET', (':id', 'rootpath', 'project'), self.getProjectSeriesRoot)
        # self.route('GET',("allpatients",),self.getAllPatients)
        self.route('GET', (':id', 'studies'), self.getStudies)
        self.route('GET', (':id', 'series'), self.getSeries)
        self.route('GET', (':patientid', ':studyid', ':seriesid', 'slices'), self.getSlices)
        # self.route('GET',('rootpath','itemid'),self.findItemFromPath)
        # self.route('GET',('prepareInputs',),self.prepareInputs)

        self.route('GET',(':id','SAIPExistingValidation',),self.SAIPExistingValidation)

        self.mountCollectionName = 'mnt'
        self.scippyName = 'scippy_images'
        for x in girderCollection().textSearch(self.mountCollectionName):
            self.mountId = x.get('_id')
            parentType = 'collection'
            parent = girderCollection().load(
                self.mountId, level=AccessType.READ, exc=True)

            filters = {}
            filters['name'] = self.scippyName
            self.scippyArchiveId = list(FolderModel().childFolders(
                parentType=parentType, parent=parent, filters=filters))[0].get('_id')

    '''
        Validate if specified study is already existed under SAIP collection. If is exist already update, else create one.
        return will be a folder object.
    '''
    @access.user
    @autoDescribeRoute(
        Description('Validate if specified study is already existed under SAIP collection. If is exist already update, else create one.')
        .responseClass('SAIP')
        .param('id', 'Study id.', paramType='path')
        .errorResponse()
    )
    def SAIPExistingValidation(self, id):
        assetstoreId = Assetstore().getCurrent()['_id']
        assetstore = Assetstore().load(id=assetstoreId)
        adapter = assetstore_utilities.getAssetstoreAdapter(assetstore)
        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                """SELECT t2.*,series_path,series_description FROM
                 (SELECT t1.*,pat_path,pat_name FROM
                 (SELECT pat_id,id AS study_id,study_path,
                 study_description FROM studies WHERE id =%s)
                 AS t1 LEFT JOIN patients ON t1.pat_id=patients.id)
                 AS t2 LEFT JOIN series ON series.study_id=t2.study_id""",
                (id,))
        except Exception:
            print "I can't SELECT from studies"

        series_roots_obj = {'series_roots': [], 'seriesId': [], 'identity': []}

        dirpath = '/'+self.mountCollectionName + '/' + self.scippyName
        self.filters = {}
        toImport = {}
        for row in cur:
            # if row['pat_path'] is not None\
            self.studyFolderName = row['study_description'] or row['study_path']
            self.filters['name'] = self.studyFolderName

            series_path = os.path.join(dirpath, row['pat_path'],row['study_path'],row['series_path'])
            print series_path
            for file_paths, file_dirs, file_names in os.walk(series_path):
                for file_name in file_names:
                    if file_name != '.DS_Store':
                        file_path = os.path.join(file_paths, file_name)
                        stat = os.stat(file_path)
                        toImport[file_path] = {
                            'mtime': stat.st_mtime, 'size': stat.st_size,
                            'name': row['series_description'] or "None"
                        }
        # print toImport
        self.SAIPCollectionName = 'SAIP'
        for x in girderCollection().textSearch(self.SAIPCollectionName):
            self.SAIPId = x.get('_id')
            self.parentType = 'collection'
            self.parent = girderCollection().load(
                    self.SAIPId, level=AccessType.READ, exc=True)
            self.SAIPArchiveFolder = list(FolderModel().childFolders(
                    parentType=self.parentType, parent=self.parent, filters=self.filters))
        
        if len(self.SAIPArchiveFolder):
            study_folder = self.SAIPArchiveFolder[0]
        else:
            study_folder = FolderModel().createFolder(
                        self.parent, self.studyFolderName, parentType=self.parentType,
                        public=True, creator=self.getCurrentUser())
        # print study_folder
        for filePath, newFile in toImport.items():
            # print filePath
            # print newFile['name']
            dirs = os.path.dirname(filePath).split('/')

            adapter._importDataAsItem(  # os.path.dirname(filePath) right
                    newFile['name'], self.getCurrentUser(), study_folder,
                    os.path.dirname(filePath), [os.path.basename(filePath)],
                    reuseExisting=True)
        # # logger.info('Imported %s to %s' %
        # #             (filePath, os.path.join(self.collectionPath, relpath)))
        return study_folder

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all projects under login user.')
        .param('text', 'Pass to perform a text search.', required=False)
        .pagingParams(defaultSort='lowerName')
        .errorResponse())
    def getSSRProjects(self, text, limit, offset, sort):
        ssrArchive = SSRArchive()
        return ssrArchive.find(text, offset=offset, limit=limit, sort=sort)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all SAIP projects under login user.')
        .param('text', 'Pass to perform a text search.', required=False)
        .errorResponse())
    def getSAIPProjects(self, text):
        
        saipArchive = SAIPArchive()
        return saipArchive.find(text)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all experiments under project.')
        .param('id', 'project id.', paramType='path')
        .errorResponse())
    def getExperiments(self, id):
        try:
            mariadb_connection = mariadb.connect(
                host=self.configuration.MYSQL_CONFIG['host'], 
                port=self.configuration.MYSQL_CONFIG['port'], 
                user=self.configuration.MYSQL_CONFIG['user'],
                password=self.configuration.MYSQL_CONFIG['password'], 
                database=self.configuration.MYSQL_CONFIG['dbname'])
            print "I am able to connect to fr-s-mysql-4 database"
        except mariadb.Error as error:
            print("Error: {}".format(error))

        cursor = mariadb_connection.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT * FROM imaging_experiments WHERE project_id=%s", (id,))
        experiments = cursor.fetchall()
        cursor.close()
        mariadb_connection.close()
        return experiments

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all patients under experiment.')
        .param('id', 'experiment id.', paramType='path')
        .errorResponse())
    def getPatients(self, id):
        try:
            mariadb_connection = mariadb.connect(
                host=self.configuration.MYSQL_CONFIG['host'], 
                port=self.configuration.MYSQL_CONFIG['port'], 
                user=self.configuration.MYSQL_CONFIG['user'],
                password=self.configuration.MYSQL_CONFIG['password'], 
                database=self.configuration.MYSQL_CONFIG['dbname'])
            print "I am able to connect to fr-s-mysql-4 database"
        except mariadb.Error as error:
            print("Error: {}".format(error))

        cursor = mariadb_connection.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT * FROM imaging_participants WHERE experiment_id=%s", (id,))

        patients = []

        for row in cursor:
            patients.append(row['patient_id'])
        cursor.close()
        mariadb_connection.close()

        # query from postgre
        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute("""SELECT id, pat_name,
             pat_mrn, pat_path FROM patients WHERE id IN %s""",
                        (tuple(patients),))
        except Exception:
            print "I can't SELECT from studies"

        rows = cur.fetchall()
        cur.close()
        conn.close()
        return rows

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all series Root under experiment.')
        .param('id', 'experiment id.', paramType='path')
        .errorResponse())
    def getProjectSeriesRoot(self, id):

        try:
            mariadb_connection = mariadb.connect(
                host=self.configuration.MYSQL_CONFIG['host'], 
                port=self.configuration.MYSQL_CONFIG['port'], 
                user=self.configuration.MYSQL_CONFIG['user'],
                password=self.configuration.MYSQL_CONFIG['password'], 
                database=self.configuration.MYSQL_CONFIG['dbname'])
            print "I am able to connect to fr-s-mysql-4 database"
        except mariadb.Error as error:
            print("Error: {}".format(error))

        cursor = mariadb_connection.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT * FROM imaging_experiments WHERE project_id=%s", (id,))

        experiments = []
        for row in cursor:
            experiments.append(row['id'])

        cursor = mariadb_connection.cursor(buffered=True, dictionary=True)
        if len(experiments) == 1:
            experiments = experiments
            cursor.execute("SELECT * FROM imaging_participants WHERE experiment_id = %s"
                           % experiments[0])

        else:
            experiments = tuple(experiments)
            cursor.execute("SELECT * FROM imaging_participants WHERE experiment_id in %s"
                           % (experiments,))

        patients = []

        for row in cursor:
            patients.append(row['patient_id'])
        cursor.close()
        mariadb_connection.close()

        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                """SELECT t2.*,series_path,series_description FROM
                 (SELECT t1.*,id AS study_id,study_path,study_description FROM
                 (SELECT id AS pat_id, pat_path,pat_name FROM patients WHERE id in %s)
                 AS t1 LEFT JOIN studies ON t1.pat_id =studies.pat_id)
                 AS t2 LEFT JOIN series ON t2.study_id = series.study_id""",
                (tuple(patients),))
        except Exception:
            print "I can't SELECT from studies"

        series_roots_obj = {'series_roots': [], 'seriesId': [], 'identity': []}

        for row in cur:
            if row['pat_path'] is not None\
                    and row['study_path'] is not None\
                    and row['series_path'] is not None:
                series_roots_obj['series_roots'].append(
                    row['pat_path'] + '/' + row['study_path'] + '/'
                    + row['series_path'])
                series_roots_obj['identity'].append(
                    row['pat_name'] + '/' + row['study_description'] + '/'
                    + row['series_description'])
                parentType = 'folder'
                parent = FolderModel().load(
                    self.scippyArchiveId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['pat_path']
                self.patientFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=parent, filters=filters))[0].get('_id')

                patient = FolderModel().load(
                    self.patientFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['study_path']
                self.studyFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=patient, filters=filters))[0].get('_id')

                study = FolderModel().load(
                    self.studyFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['series_path']
                self.seriesItemId = list(FolderModel().childItems(
                    folder=study, filters=filters))[0].get('_id')

                series_roots_obj['seriesId'].append(self.seriesItemId)
        cur.close()
        conn.close()
        return series_roots_obj

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all series Root under experiment.')
        .param('id', 'experiment id.', paramType='path')
        .errorResponse())
    def getExperimentSeriesRoot(self, id):
        try:
            mariadb_connection = mariadb.connect(
                host=self.configuration.MYSQL_CONFIG['host'], 
                port=self.configuration.MYSQL_CONFIG['port'], 
                user=self.configuration.MYSQL_CONFIG['user'],
                password=self.configuration.MYSQL_CONFIG['password'], 
                database=self.configuration.MYSQL_CONFIG['dbname'])
        except mariadb.Error as error:
            print("Error: {}".format(error))

        cursor = mariadb_connection.cursor(buffered=True, dictionary=True)
        cursor.execute("SELECT * FROM imaging_participants WHERE experiment_id=%s", (id,))

        patients = []

        for row in cursor:
            patients.append(row['patient_id'])
        cursor.close()
        mariadb_connection.close()

        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                """SELECT t2.*,series_path,series_description FROM
                 (SELECT t1.*,id AS study_id,study_path,study_description FROM
                 (SELECT id AS pat_id, pat_path, pat_name FROM patients WHERE id in %s)
                 AS t1 LEFT JOIN studies ON t1.pat_id =studies.pat_id)
                 AS t2 LEFT JOIN series ON t2.study_id = series.study_id""",
                (tuple(patients),))
        except Exception:
            print "I can't SELECT from studies"

        series_roots_obj = {'series_roots': [], 'seriesId': [], 'identity': []}

        for row in cur:
            if row['pat_path'] is not None\
                    and row['study_path'] is not None\
                    and row['series_path'] is not None:
                series_roots_obj['series_roots'].append(
                    row['pat_path'] + '/' + row['study_path'] + '/'
                    + row['series_path'])
                series_roots_obj['identity'].append(
                    row['pat_name'] + '/' + row['study_description'] + '/'
                    + row['series_description'])
                print series_roots_obj
                parentType = 'folder'
                parent = FolderModel().load(
                    self.scippyArchiveId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['pat_path']
                print filters
                self.patientFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=parent, filters=filters))[0].get('_id')
                print list(FolderModel().childFolders(
                    parentType=parentType, parent=parent, filters=filters))
                patient = FolderModel().load(
                    self.patientFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['study_path']
                self.studyFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=patient, filters=filters))[0].get('_id')

                study = FolderModel().load(
                    self.studyFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['series_path']
                self.seriesItemId = list(FolderModel().childItems(
                    folder=study, filters=filters))[0].get('_id')

                series_roots_obj['seriesId'].append(self.seriesItemId)
        cur.close()
        conn.close()
        return series_roots_obj

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all series Root under patient.')
        .param('id', 'patient id.', paramType='path')
        .errorResponse())
    def getPatientSeriesRoot(self, id):
        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                """SELECT t2.*,series_path,series_description FROM
                 (SELECT t1.*,id AS study_id,study_path,study_description FROM
                 (SELECT id AS pat_id, pat_path,pat_name FROM patients WHERE id=%s)
                 AS t1 LEFT JOIN studies ON t1.pat_id =studies.pat_id)
                 AS t2 LEFT JOIN series ON t2.study_id = series.study_id""",
                (id,))
        except Exception:
            print "I can't SELECT from studies"

        series_roots_obj = {'series_roots': [], 'seriesId': [], 'identity': []}

        for row in cur:
            if row['pat_path'] is not None\
                    and row['study_path'] is not None\
                    and row['series_path'] is not None:
                series_roots_obj['series_roots'].append(
                    row['pat_path'] + '/' + row['study_path'] + '/'
                    + row['series_path'])
                series_roots_obj['identity'].append(
                    row['pat_name'] + '/' + row['study_description'] + '/'
                    + row['series_description'])

                parentType = 'folder'
                parent = FolderModel().load(
                    self.scippyArchiveId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['pat_path']
                self.patientFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=parent, filters=filters))[0].get('_id')

                patient = FolderModel().load(
                    self.patientFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['study_path']
                self.studyFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=patient, filters=filters))[0].get('_id')

                study = FolderModel().load(
                    self.studyFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['series_path']
                self.seriesItemId = list(FolderModel().childItems(
                    folder=study, filters=filters))[0].get('_id')

                series_roots_obj['seriesId'].append(self.seriesItemId)

        cur.close()
        conn.close()
        return series_roots_obj

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all series Root under study.')
        .param('id', 'study id.', paramType='path')
        .errorResponse())
    def getStudySeriesRoot(self, id):
        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                """SELECT t2.*,series_path,series_description FROM
                 (SELECT t1.*,pat_path,pat_name FROM
                 (SELECT pat_id,id AS study_id,study_path,
                 study_description FROM studies WHERE id =%s)
                 AS t1 LEFT JOIN patients ON t1.pat_id=patients.id)
                 AS t2 LEFT JOIN series ON series.study_id=t2.study_id""",
                (id,))
        except Exception:
            print "I can't SELECT from studies"

        series_roots_obj = {'series_roots': [], 'seriesId': [], 'identity': []}

        for row in cur:
            print row
            if row['pat_path'] is not None\
                    and row['study_path'] is not None\
                    and row['series_path'] is not None:
                series_roots_obj['series_roots'].append(
                    row['pat_path'] + '/' + row['study_path'] + '/'
                    + row['series_path'])
                series_roots_obj['identity'].append(
                    row['pat_name'] + '/' + row['study_description'] + '/'
                    + row['series_description'])

                parentType = 'folder'
                parent = FolderModel().load(
                    self.scippyArchiveId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['pat_path']
                self.patientFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=parent, filters=filters))[0].get('_id')
                
                patient = FolderModel().load(
                    self.patientFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['study_path']
                self.studyFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=patient, filters=filters))[0].get('_id')

                study = FolderModel().load(
                    self.studyFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['series_path']
                self.seriesItemId = list(FolderModel().childItems(
                    folder=study, filters=filters))[0].get('_id')

                series_roots_obj['seriesId'].append(self.seriesItemId)

        cur.close()
        conn.close()
        return series_roots_obj

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all series Root of series.')
        .param('id', 'study id.', paramType='path')
        .errorResponse())
    def getSeriesSeriesRoot(self, id):
        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                """SELECT t2.*,pat_path,pat_name FROM
                 (SELECT t1.*,study_path,pat_id,study_description FROM
                 (SELECT study_id AS series_study_id,series_path,series_description FROM
                 series WHERE id =%s)
                 AS t1 LEFT JOIN studies ON t1.series_study_id = studies.id)
                 AS t2 LEFT JOIN patients ON patients.id=t2.pat_id;""",
                (id,))
        except Exception:
            print "I can't SELECT from studies"

        series_roots_obj = {'series_roots': [], 'seriesId': [], 'identity': []}

        for row in cur:
            if row['pat_path'] is not None\
                    and row['study_path'] is not None\
                    and row['series_path'] is not None:
                series_roots_obj['series_roots'].append(
                    row['pat_path'] + '/' + row['study_path'] + '/'
                    + row['series_path'])
                series_roots_obj['identity'].append(
                    row['pat_name'] + '/' + row['study_description'] + '/'
                    + row['series_description'])

                parentType = 'folder'
                parent = FolderModel().load(
                    self.scippyArchiveId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['pat_path']
                self.patientFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=parent, filters=filters))[0].get('_id')

                patient = FolderModel().load(
                    self.patientFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['study_path']
                self.studyFolderId = list(FolderModel().childFolders(
                    parentType=parentType, parent=patient, filters=filters))[0].get('_id')

                study = FolderModel().load(
                    self.studyFolderId, level=AccessType.READ, exc=True)

                filters = {}
                filters['name'] = row['series_path']
                self.seriesItemId = list(FolderModel().childItems(
                    folder=study, filters=filters))[0].get('_id')

                series_roots_obj['seriesId'].append(self.seriesItemId)
        cur.close()
        conn.close()
        return series_roots_obj

    # @access.user
    # @autoDescribeRoute(
    #     Description('Retrieve all patients')
    #     .errorResponse())
    # def getAllPatients(self):
    #     try:
    #         conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    # user=self.configuration.PSQL_CONFIG['user'],
                                    # host=self.configuration.PSQL_CONFIG['host'],
                                    # password=self.configuration.PSQL_CONFIG['password'])
    #         print "I am able to connect to the database"
    #     except Exception:
    #         print "I am unable to connect to the database"
    #     cur = conn.cursor()
    #     try:
    #         cur.execute("""SELECT id,pat_name,pat_mrn,pat_path,mod_time from patients""")
    #     except Exception:
    #         print "I can't SELECT from patients"
    #
    #     rows = cur.fetchall()
    #
    #     cur.close()
    #     conn.close()
    #     return rows

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all studies under patient')
        .param('id', 'patient id.', paramType='path')
        .errorResponse())
    def getStudies(self, id):
        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute("""SELECT id,studyid,study_path,
            study_description FROM studies WHERE pat_id=%s""" % id)
        except Exception:
            print "I can't SELECT from studies"

        rows = cur.fetchall()

        cur.close()
        conn.close()
        return rows

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all series under study')
        .param('id', 'study id.', paramType='path')
        .errorResponse())
    def getSeries(self, id):
        try:
            conn = psycopg2.connect(dbname=self.configuration.PSQL_CONFIG['dbname'],
                                    user=self.configuration.PSQL_CONFIG['user'],
                                    host=self.configuration.PSQL_CONFIG['host'],
                                    password=self.configuration.PSQL_CONFIG['password'])
            print "I am able to connect to the database"
        except Exception:
            print "I am unable to connect to the database"
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        try:
            cur.execute(
                """SELECT id,series_uid,modality,series_path,
                series_description from series WHERE study_id=%s""" % id)
        except Exception:
            print "I can't SELECT from series"

        rows = cur.fetchall()

        cur.close()
        conn.close()
        return rows

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all slices under series,mount partition is /mnt/scippy_images/')
        .param('patientid', 'patient id.', paramType='path')
        .param('studyid', 'study id.', paramType='path')
        .param('seriesid', 'series id.', paramType='path')
        .errorResponse())
    def getSlices(self, patientid, studyid, seriesid):
        filesList = []
        flag = 0
        pathString = self.mnt + patientid + '/' + studyid + '/' + seriesid
        for files in listdir(pathString):
            print pathString + '/' + files
            fileName, file_extension = os.path.splitext(pathString + '/' + files)
            print file_extension
            if file_extension == '.jpg':
                flag = 1
            else:
                if files == 'DICOMDIR':
                    print 'Skip DICOMDIR'
                else:
                    filesList.append(files)
        if flag == 0:
            return 'Not a valid Dicom folder'
        else:
            return filesList

    # @access.user(scope=TokenScope.DATA_WRITE)
    # @autoDescribeRoute(
    #     Description('Retrieve all different patients')
    #     .responseClass('Folder')
    #     .modelParam('id', model=FolderModel, level=AccessType.READ)
    #     .errorResponse('ID was invalid.')
    #     .errorResponse('Read access was denied on the parent resource.', 403))
    # def diff(self,folder):
    #
    #     def diffPat(first, second):
    #         second = set(second)
    #         return [item for item in first if item not in second]
    #
    #     try:
    #         conn = psycopg2.connect("dbname='miaot2'"
    #                                 " user='miaot2'"
    #                                 " host='ivg-webdev'"
    #                                 " password='luying0325'")
    #         print "I am able to connect to the database"
    #     except Exception:
    #         print "I am unable to connect to the database"
    #     cur = conn.cursor()
    #     try:
    #         cur.execute("""SELECT pat_path from patients""")
    #     except Exception:
    #         print "I can't SELECT from patients"
    #
    #     rows = cur.fetchall()
    #
    #     cur.close()
    #     conn.close()
    #     new = [item for sublist in rows for item in sublist]
    #
    #
    #     user = self.getCurrentUser()
    #     #parent = self.model('folder').load(folder, user=user, level=AccessType.READ, exc=True)
    #     rows = FolderModel().childFolders(parentType='folder', parent=folder,user=user)
    #     exit=[]
    #     for sub in rows:
    #         exit.append(sub['name'])
    #
    #     difference=diffPat(new,exit)
    #     return exit,len(difference)


def load(info):
    # info['apiRoot'].scippy = Prefix()
    info['apiRoot'].Archive = Archive()
