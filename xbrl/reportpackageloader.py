import zipfile
import re
from .reportpackage import ReportPackage

class ReportPackageLoader:

    def load(self, path):
        with zipfile.ZipFile(path) as zf:
            contents = zf.namelist()
            top = {item.split('/')[0] for item in contents if '/' in item}
            if len(top) != 1:
                raise XBRLError("tpe:invalidDirectoryStructure", "Multiple top-level directories")
            tld = top.pop()
            reports = list(item for item in contents if re.match('%s/reports.*\.(html?|xhtml|xbrl)$' % tld, item) is not None)
        return ReportPackage(path, reports)




