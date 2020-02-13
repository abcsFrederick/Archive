from girder.api.rest import Resource, setResponseHeader, setContentDisposition
from girder.models.setting import Setting
from girder.exceptions import GirderException

from ..external.postgre_proxy import PostgredbProxy
import os
import psycopg2.extras

BUF_SIZE = 65536

class File(Resource):
    def __init__(self):
        self.name = 'SAIPArchiveItemModel'
        super(File, self).__init__()
        self.user = self.getCurrentUser()
        self.PostgreDB = PostgredbProxy().conn
        self.PostgreCursor = self.PostgreDB.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.root = Setting().get('Archive.SCIPPYMOUNT')

    def fullPath(self, sliceId):
        try:
            self.PostgreCursor.execute(
                """SELECT t2.*,pat_path,pat_name FROM 
                (SELECT t1.*,study_path,pat_id,study_description FROM 
                (SELECT t0.*, study_id AS series_study_id,series_path,series_description FROM 
                (SELECT id, series_id AS series_series_id, filename FROM images WHERE id = %s) 
                AS t0 LEFT JOIN series ON t0.series_series_id = series.id) 
                AS t1 LEFT JOIN studies ON t1.series_study_id = studies.id) 
                AS t2 LEFT JOIN patients ON patients.id=t2.pat_id;""",
                (sliceId,))
        except Exception:
            raise GirderException('Query failed when SELECT from images')

        rows = self.PostgreCursor.fetchall()
        if len(rows):
            row = rows[0]
            self.PostgreCursor.close()
            self.PostgreDB.close()
            if row['filename'] is not None\
                and row['pat_path'] is not None\
                and row['study_path'] is not None\
                and row['series_path'] is not None:
                path = os.path.join(self.root,
                                    row['pat_path'], 
                                    row['study_path'], 
                                    row['series_path'], 
                                    row['filename'])
                return row['filename'], path
            else:
                raise GirderException('Rows with id:%s does not have [filename, pat_path, study_path or series_path]' % row['id'])
        else:
            raise GirderException('No slice: %s' % sliceId)
    def fullPathThumbnail(self, series_uid):
        try:
            self.PostgreCursor.execute(
                """SELECT t2.*,pat_path,pat_name FROM 
                (SELECT t1.*,study_path,pat_id,study_description FROM 
                (SELECT series_uid, study_id AS series_study_id,series_path,series_description FROM 
                series WHERE series_uid = %s) 
                AS t1 LEFT JOIN studies ON t1.series_study_id = studies.id) 
                AS t2 LEFT JOIN patients ON patients.id=t2.pat_id;""",
                (series_uid,))
        except Exception:
            raise GirderException('Query failed when SELECT from series')

        rows = self.PostgreCursor.fetchall()
        if len(rows):
            row = rows[0]
            self.PostgreCursor.close()
            self.PostgreDB.close()
            if row['series_uid'] is not None\
                and row['pat_path'] is not None\
                and row['study_path'] is not None\
                and row['series_path'] is not None:
                path = os.path.join(self.root,
                                    row['pat_path'], 
                                    row['study_path'], 
                                    row['series_path'], 
                                    'thmb_' + row['series_uid'] + '.jpg')
                return row['series_uid'], path
            else:
                raise GirderException('Rows with id:%s does not have [series_uid, pat_path, study_path or series_path]' % row['id'])
        else:
            raise GirderException('No thumbnail: %s' % series_uid)
    def downloadFile(self, id, Type, offset=0, headers=True, endByte=None,
                     contentDisposition=None):
        if Type == 'slice':
            filename, path = self.fullPath(id)
        elif Type == 'thumbnail':
            filename, path = self.fullPathThumbnail(id)
            print path
        
        if not os.path.isfile(path):
            raise GirderException(
                'File %s does not exist.' % path,
                'girder.utility.filesystem_assetstore_adapter.'
                'file-does-not-exist')
        if headers:
            stat = os.stat(path)
            endByte = stat.st_size
            setResponseHeader('Accept-Ranges', 'bytes')
            setResponseHeader(
                'Content-Type', 'application/octet-stream')
            setContentDisposition(filename, contentDisposition or 'attachment')
            setResponseHeader('Content-Length', max(endByte - offset, 0))

            # if (offset or endByte < file['size']) and file['size']:
            #     setResponseHeader(
            #         'Content-Range',
            #         'bytes %d-%d/%d' % (offset, endByte - 1, file['size']))
        def stream():
            bytesRead = offset
            with open(path, 'rb') as f:
                if offset > 0:
                    f.seek(offset)

                while True:
                    readLen = min(BUF_SIZE, endByte - bytesRead)
                    if readLen <= 0:
                        break

                    data = f.read(readLen)
                    bytesRead += readLen

                    if not data:
                        break
                    yield data

        return stream
