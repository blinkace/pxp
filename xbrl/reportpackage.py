from urllib.parse import urlunparse, quote

class ReportPackage:

    def __init__(self, path: str, reports: list):
        self.path = path
        self.reports = reports

    def reportURLs(self):
        ru = []
        for r in self.reports:
            ru.append(urlunparse(('zip','', quote(self.path), '', '', quote(r))))
        return ru
