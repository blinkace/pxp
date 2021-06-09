from urllib.request import pathname2url
from urllib.parse import urlparse, urljoin, urlunparse, quote
import os.path

def urlise(urlOrPath):
    url = urlparse(urlOrPath)
    if url.scheme == '':
        return "file:%s" % pathname2url(os.path.abspath(urlOrPath))
    return urlOrPath

def urljoinz(base, path):
    """Version of urljoin with support for zip: URLs.  Relative URLs are applied to the path in the fragment (i.e. within the ZIP)"""
    url = urlparse(base)
    if url.scheme == 'zip':
        newurl = urljoin(url.fragment, path)
        newpurl = urlparse(newurl)
        if newpurl.scheme == '':
            ret = urlunparse(('zip','', url.path, '', '', newurl))
        else:
            ret = newurl
    else:
        ret = urljoin(base, path)
    return ret


