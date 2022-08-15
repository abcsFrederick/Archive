from girder.models.setting import Setting

from girder.api.rest import Resource
from girder.api.describe import Description, autoDescribeRoute
from girder.api import access

from girder.constants import TokenScope


from .models.folder import Folder
from .models.item import Item
from .models.file import File
from .SAIPConfig import PluginSettings


class Archive(Resource):
    def __init__(self):
        super(Archive, self).__init__()
        # configSection = config.getConfig().get('server').get('mode')
        # if configSection == 'development':
        #     self.configuration = Setting().get('Archive.SAIP')
        #     print
        # else:
        #     self.configuration = Setting().get('Archive.SCIPPY')
        self.resourceName = 'archive'

        # more secure with login current user info
        # self.route('GET', ('projects', 'ssr',), self.getSSRProjects)
        self.route('GET', ('saip', 'projects',), self.getSAIPProjects)
        self.route('GET', ('saip', 'experiments',), self.getExperiments)
        self.route('GET', ('saip', 'patients',), self.getPatients)
        self.route('GET', ('saip', 'studies',), self.getStudies)
        self.route('GET', ('saip', 'series',), self.getSeries)
        self.route('GET', ('saip', 'slices',), self.getSlices)
        self.route('GET', ('saip', 'slice', 'download',), self.download)
        self.route('GET', ('saip', 'fullPath',), self.getFullPath)

        # self.route('GET', (':id', 'rootpath', 'patient'), self.getPatientSeriesRoot)
        # self.route('GET', (':id', 'rootpath', 'study'), self.getStudySeriesRoot)
        # self.route('GET', (':id', 'rootpath', 'series'), self.getSeriesSeriesRoot)
        # self.route('GET', (':id', 'rootpath', 'experiment'), self.getExperimentSeriesRoot)
        # self.route('GET', (':id', 'rootpath', 'project'), self.getProjectSeriesRoot)
        # self.route('GET',("allpatients",),self.getAllPatients)

        # self.route('GET',('rootpath','itemid'),self.findItemFromPath)
        # self.route('GET',('prepareInputs',),self.prepareInputs)

        # self.route('GET',(':id','SAIPExistingValidation',),self.SAIPExistingValidation)

    @access.token
    @autoDescribeRoute(
        Description('Retrieve all projects under login user.[type=Folder]')
        .param('text', 'Pass to perform a text search.', required=False)
        .pagingParams(defaultSort='lowerName')
        .errorResponse())
    def getSSRProjects(self, text, limit, offset, sort):
        ssrArchive = Folder()
        return ssrArchive.find(text, offset=offset, limit=limit, sort=sort)

    # get SAIP projects
    # TODO: should add and access decorator for NCI user only
    @access.user
    @autoDescribeRoute(
        Description('Retrieve all SAIP projects under login user.[type=Folder]')
        .param('text', 'Pass to perform a text search.', required=False)
        .errorResponse())
    def getSAIPProjects(self, text):
        print(text)
        folder = Folder()
        parentType = 'user'
        return folder.find(None, parentType)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all experiments under project.[type=Folder]')
        .param('id', 'project id.', required=True)
        .errorResponse())
    def getExperiments(self, id):
        folder = Folder()
        parentType = 'project'
        return folder.find(id, parentType)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all patients under experiment.[type=Folder]')
        .param('id', 'experiment id.', required=True)
        .errorResponse())
    def getPatients(self, id):
        folder = Folder()
        parentType = 'experiment'
        return folder.find(id, parentType)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all studies under patient[type=Folder]')
        .param('id', 'patient id.', required=True)
        .errorResponse())
    def getStudies(self, id):
        folder = Folder()
        parentType = 'patient'
        return folder.find(id, parentType)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all series under study[type=Item]')
        .param('id', 'study id.', required=True)
        .errorResponse())
    def getSeries(self, id):
        saipArchive = Item()
        return saipArchive.find(id)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve all slices under series, '
                    'mount partition is /mnt/scippy_images/[type=File]')
        .param('id', 'series id.', required=True)
        .errorResponse())
    def getSlices(self, id):
        saipArchive = Item()
        return saipArchive.getFiles(id)

    @access.public(scope=TokenScope.DATA_READ)
    @autoDescribeRoute(
        Description('Download slice from SAIP image archive[type=File]')
        .param('id', 'slice id.', required=True)
        .param('Type', "Type of the searching", required=True,
               enum=['slice', 'thumbnail'], strip=True)
        .errorResponse())
    def download(self, id, Type):
        file = File()
        return file.downloadFile(id, Type)

    @access.user
    @autoDescribeRoute(
        Description('Retrieve full path for particular type.[type=Folder/Item]')
        .param('id', 'id.', required=True)
        .param('Type', "Type of the searching", required=True,
               enum=['patient', 'study', 'series'], strip=True)
        .errorResponse())
    def getFullPath(self, id, Type):
        if Type == 'patient' or Type == 'study':
            folder = Folder()
            path = folder.fullPath(id, Type)
        elif Type == 'series':
            item = Item()
            path = item.fullPath(id)

        return path


def getSettings(self):
    settings = Setting()
    return {
        PluginSettings.GIRDER_WORKER_TMP:
            settings.get(PluginSettings.GIRDER_WORKER_TMP),
        PluginSettings.TASKS:
            settings.get(PluginSettings.TASKS),
    }
