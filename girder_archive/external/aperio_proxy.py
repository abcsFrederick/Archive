import pycurl
import io, sys, os

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

        return imagePath

    def getImagePathsByRequestId(self, requestId):
        pass