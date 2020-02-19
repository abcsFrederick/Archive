from tests import base
from girder.models.user import User


def setUpModule():
    base.enabledPlugins.append('Archive')
    base.startServer()


def tearDownModule():
    base.stopServer()


class ARCHIVETestCase(base.TestCase):

    def setUp(self):
        base.TestCase.setUp(self)

        self.user = User().createUser('user', 'password', 'test', 'user', 'u123@u.com')

    # def testGetProjects(self):
        # print '----------testGetProjects-------------'
        # projectsRes = self.request(path='/scippy/miaot2/projects', isJson=False, user=self.user)
        # self.assertStatus(projectsRes, 200)
        # # check access permission required
        # projectsRes = self.request(path='/scippy/miaot2/projects', isJson=False)
        # self.assertStatus(projectsRes, 401)
