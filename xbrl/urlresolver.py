import urllib.request
import logging

class URLResolver:

    def __init__(self):
        self.packages = []


    def addPackage(self, package):
        self.packages.append(package)


    def open(self, url):
        for p in self.packages:
            if p.hasFile(url):
                logging.debug("Opening %s from package" % url)
                return p.open(url)
        return urllib.request.urlopen(url)

    

