from tests import base
from girder.models.assetstore import Assetstore
from girder.models.user import User


# from server import Scippy


def setUpModule():
    base.enabledPlugins.append('SAIP')
    base.startServer()


def tearDownModule():
    base.stopServer()


class SAIPTestCase(base.TestCase):

    def setUp(self):
        super(SAIPTestCase, self).setUp()

        self.AssetstoreId = Assetstore().getCurrent()
        self.user = User().createUser('user', 'password', 'test', 'user', 'u123@u.com')

    def testGetProjects(self):
        # print '----------testGetProjects-------------'
        projectsRes = self.request(path='/scippy/miaot2/projects', isJson=False, user=self.user)
        self.assertStatus(projectsRes, 200)
        # check access permission required
        projectsRes = self.request(path='/scippy/miaot2/projects', isJson=False)
        self.assertStatus(projectsRes, 401)

