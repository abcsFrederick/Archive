from girder.models.collection import Collection
from girder.models.folder import Folder as FolderModel
from ..SSRConfig import Config as SSRConfig
from girder.api.rest import Resource
from girder.constants import AccessType

class SSRArchive(Resource):
  """docstring for SSR"""
  def __init__(self):
    self.name = 'SSRArchive'
    super(SSRArchive, self).__init__()
    self.user = self.getCurrentUser()

  def find(self, text, limit, offset, sort):
    ssr_archive = Collection().textSearch(SSRConfig.ARCHIVE_NAME, user=self.user)
    ssr_archive_id = list(ssr_archive)[0]['_id']
    parent = self.model('collection').load(
                ssr_archive_id, user=self.user, level=AccessType.READ, exc=True)
    filters = {}
    if text:
      filters['$text'] = {
          '$search': text
      }
    return FolderModel().childFolders(
                parentType='collection', parent=parent, user=self.user,
                offset=offset, limit=limit, sort=sort, filters=filters)