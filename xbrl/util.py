from urllib.request import pathname2url
from urllib.parse import urlparse
import os.path

def urlise(urlOrPath):
    url = urlparse(urlOrPath)
    if url.scheme == '':
        return "file:%s" % pathname2url(os.path.abspath(urlOrPath))
    return urlOrPath
