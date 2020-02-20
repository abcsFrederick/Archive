from tests import base
from girder.models.user import User
from girder.constants import SettingDefault
from girder.exceptions import GirderException
import pytest


def setUpModule():
    base.enabledPlugins.append('Archive')
    base.startServer()


def tearDownModule():
    base.stopServer()


class ArchiveTestCase(base.TestCase):
    def setUp(self):
        base.TestCase.setUp(self)
        self.admin = User().createUser('test1', 'password', 'TEST_1', 'admin', 'u123@u.com')
        self.user = User().createUser('test2', 'password2', 'TEST_2', 'user', '2u123@u.com')
        self.notSAIPUser = User().createUser('test3', 'password3', 'TEST_3', 'notSAIPUser', '3u123@u.com')

        SettingDefault.defaults.update({
            'Archive.SCIPPYMOUNT': '/mnt/scippy_images',
            'Archive.SAIP': {
                'host': 'localhost',
                'dbname': 'Archive_SAIP_TEST',
                'user': 'ArchiveTest',
                'password': 'password',
                'port': 3306
            },
            'Archive.SCIPPY': {
                'host': 'localhost',
                'dbname': 'archive_scippy_test',
                'user': 'archivetest',
                'password': 'password',
                'port': 5432
            }
        })


class ArchiveModelTestCase(ArchiveTestCase):
    def testProjectsFetch(self):
        from girder.plugins.Archive.models.folder import Folder
        projects = Folder().getProjects(text=None, user=self.admin)
        self.assertEqual(len(projects), 4)
        projects = Folder().getProjects(text=None, user=self.user)
        self.assertEqual(len(projects), 2)
        with pytest.raises(GirderException, match='Not a registored user of SAIP'):
            projects = Folder().getProjects(text=None, user=self.notSAIPUser)
            self.assertEqual(len(projects), 0)
    
    def testExperimentsFetch(self):
        from girder.plugins.Archive.models.folder import Folder
        experiments = Folder().find(parentId=2, parentType='project')
        self.assertEqual(len(experiments), 5)

    def testPatientsFetch(self):
        from girder.plugins.Archive.models.folder import Folder
        patients = Folder().find(parentId=1, parentType='experiment')
        self.assertEqual(len(patients), 3)
        name, path = Folder().fullPath(id=182, type='patient')
        self.assertEqual(name, '06pettest01')
        with pytest.raises(GirderException, match='No patient: 1'):
            name, path = Folder().fullPath(id=1, type='patient')

    def testStudiesFetch(self):
        from girder.plugins.Archive.models.folder import Folder
        studies = Folder().find(parentId=182, parentType='patient')
        self.assertEqual(len(studies), 4)
        name, path = Folder().fullPath(id=117, type='study')
        self.assertEqual(name, 'prone')

    def testSeriesFetch(self):
        from girder.plugins.Archive.models.item import Item
        series = Item().find(parentId=121)
        self.assertEqual(len(series), 18)
        name, path = Item().fullPath(seriesId=233)
        self.assertEqual(name, 'survey senseC')
        from girder.plugins.Archive.models.file import File
        name, path = File().fullPathThumbnail(
            series_uid='1.3.46.670589.11.17559.5.0.4656.2010081716021473025')
        self.assertEqual(name, '1.3.46.670589.11.17559.5.0.4656.2010081716021473025')
    def testSlices(self):
        from girder.plugins.Archive.models.item import Item
        slices = Item().getFiles(seriesId=233)
        self.assertEqual(len(slices), 15)
        from girder.plugins.Archive.models.file import File
        name, path = File().fullPath(sliceId=5077)
        self.assertEqual(name, '00005077')

