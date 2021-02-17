import pycurl
import io, sys, os

class AperioProxy(object):
    def __init__(self, username, password, logger=None):
        if logger is None:
            import logging
            logger = logging.getLogger(__name__)
        self.crl = pycurl.Curl()
        self.logger = logger
        self.username = username
        self.password = password
        self.crl.setopt(pycurl.USERPWD, username + ':' + password)
        self.crl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
    def getAnn(self, id):
        e = io.BytesIO()
        self.crl.setopt(pycurl.URL, 'http://129.43.165.161/@'+id+'?GETANNOTATIONS')
        self.crl.setopt(pycurl.WRITEFUNCTION, e.write)
        self.crl.perform()

        htmlString = e.getvalue().decode('UTF-8')
        print(len(htmlString))
        return htmlString
    def test(self):
        print('---test-----')