import pycurl
import io, sys, os
import datetime
import requests
import re
import json
import warnings

from girder.models.file import File
from girder.models.item import Item
from girder.models.folder import Folder
from girder.models.collection import Collection
from girder.models.assetstore import Assetstore
from girder.exceptions import GirderException


class AperioProxy(object):
    def __init__(self, username, password, logger=None):
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.crl = pycurl.Curl()
        self.logger = logger
        self.baseURL = 'http://129.43.165.161/'
        self.username = username
        self.password = password
        self.baseLoc = '//at-s-is2.ncifcrf.gov/phl_scanscope/static'
        self.mountLoc = '/mnt/phl_scanscope/static'
        self.crl.setopt(pycurl.USERPWD, username + ':' + password)
        self.crl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)

    def getAnn(self, id):
        e = io.BytesIO()
        self.crl.setopt(pycurl.URL, self.baseURL + '@' + id + '?GETANNOTATIONS')
        self.crl.setopt(pycurl.WRITEFUNCTION, e.write)
        self.crl.perform()

        htmlString = e.getvalue().decode('UTF-8')

        return htmlString

    def getImagePath(self, id):
        e = io.BytesIO()
        self.crl.setopt(pycurl.URL, self.baseURL + '@' + id + '?GETPATH')
        self.crl.setopt(pycurl.WRITEFUNCTION, e.write)
        self.crl.perform()

        imagePath = e.getvalue().decode('UTF-8')
        imagePath = imagePath.replace('\\','/').replace(self.baseLoc, self.mountLoc)
        if imagePath.find("Invalid userid/password:") == 0:
            raise AccessException("username or password is invalid.")
        elif imagePath.find("Image record not found in database") == 0:
            raise AccessException("Image record not found in database.")
        return imagePath

    def getImagePathsByRequestId(self, requestId):
        authURL = self.baseURL+ 'authenticate.php'
        RoleURL = self.baseURL + 'DetermineHierarchy.php?RoleId=99&HierarchyId=1'
        FolderURL = self.baseURL + 'GetFolderTable.php'

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'TimezoneOffset': 14400, 'username': self.username,'password': self.password, 'submit':'User Login'}
        payload3 = {'TableName': 'Specimen', 'PageNumber': 1, 'AJAX': 1, 'FilterValues[]': str(requestId),
                    'FilterColumns[]': 'Column01'}
        with requests.Session() as s:
            authRes = s.post(authURL, headers=headers, data=payload)
            # Success
            roleRes = s.get(RoleURL)
            caseRes = s.post(FolderURL, data=payload3)
            ThumbnailListArray = json.loads(caseRes.text)['ThumbnailList']

            imagePaths = []
            pattern = 'Ids\[\]=([0-9]+)\"'
            recordPattern = '\<TR AccessLevel="Full" (.*)\>'
            imageIdPattern = 'ImageIds=\"([0-9]+)\"'
            for case in ThumbnailListArray:
                caseId = re.search(pattern, case).group(1)
                EditRecordURL = self.baseURL + 'EditRecord.php?TableName=Specimen&Ids[]=' + str(caseId)
                recordRes = s.post(EditRecordURL).text
                records = re.findall(recordPattern, recordRes)

                for image in records:
                    imageId = re.search(imageIdPattern, image).group(1)
                    e = io.BytesIO()
                    self.crl.setopt(pycurl.URL, self.baseURL + '@' + imageId + '?GETPATH')
                    self.crl.setopt(pycurl.WRITEFUNCTION, e.write)
                    self.crl.perform()
                    imagePath = e.getvalue().decode('UTF-8')
                    if imagePath.find("Invalid userid/password:") == 0:
                        warnings.warn("username or password is invalid.")
                        continue
                    elif imagePath.find("Image record not found in database") == 0:
                        warnings.warn("Image record not found in database.")
                        continue
                    imagePath = imagePath.replace('\\','/').replace(self.baseLoc, self.mountLoc)
                    imagePaths.append(imagePath)

        return imagePaths

    def importToGirder(self, requestId, imagePath, user):
        try:
            aperioDBCollection = Collection().find({'name': 'AperioDB'})[0]
        except Exception:
            raise GirderException('Missing AperioDB collection.')

        folderName = os.path.basename(os.path.dirname(imagePath))
        fileName = os.path.basename(imagePath)

        reqFolder = Folder().createFolder(
            parent=aperioDBCollection, name=requestId, parentType='collection', reuseExisting=True, creator=user)
        folder = Folder().createFolder(
            parent=reqFolder, name=folderName, parentType='folder', reuseExisting=True, creator=user)

        item = Item().createItem(fileName, folder=folder, reuseExisting=True, creator=user)
        files = list(Item().childFiles(item))
        exist = list(filter(lambda x: x['name'] == fileName, files))
        if not len(exist):
            fileDoc = {
                'name': fileName,
                'creatorId': user['_id'],
                'created': datetime.datetime.utcnow(),
                'assetstoreId': Assetstore().getCurrent()['_id'],
                'mimeType': 'application/svs',
                'size': os.path.getsize(imagePath),
                'itemId': item['_id'],
                'path': imagePath,
                'imported': True,
                'exts': [
                    'svs'
                ]
            }
            file = File().save(fileDoc)
        else:
            file = exist[0]
        return file, item, reqFolder