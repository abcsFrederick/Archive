import os
from girder.models.setting import Setting
from girder.api.rest import Resource
from girder.exceptions import GirderException

from ..external.postgre_proxy import PostgredbProxy
import psycopg2.extras


class Item(Resource):
    def __init__(self):
        self.name = 'SAIPArchiveItemModel'
        super(Item, self).__init__()
        self.user = self.getCurrentUser()
        self.PostgreDB = PostgredbProxy().conn
        self.PostgreCursor = self.PostgreDB.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.root = Setting().get('Archive.SCIPPYMOUNT')

    def find(self, parentId, text=None):
        result = self.getSeries(parentId)

        return result

    def getSeries(self, studyId):
        try:
            self.PostgreCursor.execute(
                """SELECT id,series_uid,modality,series_path,
                series_description from series WHERE study_id=%s""" % studyId)
        except Exception:
            raise GirderException('Query failed when SELECT from series')

        rows = self.PostgreCursor.fetchall()

        self.PostgreCursor.close()
        self.PostgreDB.close()
        return rows

    def getFiles(self, seriesId):
        try:
            self.PostgreCursor.execute(
                """SELECT id,image_uid,image_number,filename
                 from images WHERE series_id=%s""" % seriesId)
        except Exception:
            raise GirderException('Query failed when SELECT from images')
        rows = self.PostgreCursor.fetchall()

        self.PostgreCursor.close()
        self.PostgreDB.close()
        return rows

    def fullPath(self, seriesId):
        try:
            self.PostgreCursor.execute(
                """SELECT t2.*,pat_path,pat_name FROM
                (SELECT t1.*,study_path,pat_id,study_description FROM
                (SELECT id, study_id AS series_study_id,series_path,series_description FROM
                series WHERE id = %s)
                AS t1 LEFT JOIN studies ON t1.series_study_id = studies.id)
                AS t2 LEFT JOIN patients ON patients.id=t2.pat_id;""",
                (seriesId,))
        except Exception:
            raise GirderException('Query failed when SELECT from series')

        rows = self.PostgreCursor.fetchall()
        if len(rows):
            row = rows[0]
            self.PostgreCursor.close()
            self.PostgreDB.close()
            if row['pat_path'] is not None\
                    and row['study_path'] is not None\
                    and row['series_path'] is not None:
                path = os.path.join(self.root,
                                    row['pat_path'],
                                    row['study_path'],
                                    row['series_path'])
                return row['series_description'], path
            else:
                raise GirderException('Rows with id:%s does not have'
                                      ' [ pat_path, study_path or series_path]' % row['id'])
        else:
            raise GirderException('No series: %s' % seriesId)
