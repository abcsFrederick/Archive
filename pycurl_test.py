import io
import pycurl
import certifi

url = "https://fslspw-aprap01p.nih.gov/imageserver/@17147881?GETPATH"
username = "MiaoT"
password = "IVGtacl1011"

crl = pycurl.Curl()

crl.setopt(pycurl.SSL_VERIFYPEER, False)

crl.setopt(pycurl.USERPWD, username + ':' + password)

crl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)

crl.setopt(pycurl.URL, url)

e = io.BytesIO()

crl.setopt(pycurl.WRITEFUNCTION, e.write)

crl.perform()
