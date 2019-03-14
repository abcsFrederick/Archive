# from .scippySyncer import sync as scippySync
# from .filesystemSyncer import sync as filesystemSync
# from girder.api.rest import Resource
# from girder.api.describe import Description, autoDescribeRoute
# from girder.api import access
#
#
# class Synchronizer(Resource):
#     def __init__(self):
#         super(Synchronizer, self).__init__()
#         self.resourceName = 'Synchronizer'
#         self.route('GET', ("scippyMntSync",), self.scippyMntSync)
#         self.route('GET', ("filesystemSync",), self.filesystemSync)
#
#     @access.admin
#     @autoDescribeRoute(
#         Description('Scippy mount files synchronization')
#         .errorResponse())
#     def scippyMntSync(self):
#         print 'Scippy'
#         scippySync('mnt').start()
#
#     @access.admin
#     @autoDescribeRoute(
#         Description('Filesystem files synchronization')
#         .errorResponse())
#     def filesystemSync(self):
#         filesystemSync('filesystem').start()
#
#
# def load(info):
#     # info['apiRoot'].scippy = Prefix()
#     info['apiRoot'].Synchronizer = Synchronizer()
