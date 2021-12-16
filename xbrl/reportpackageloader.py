import zipfile
import re
from .reportpackage import ReportPackage
from xbrl.xbrlerror import XBRLError

class ReportPackageLoader:

    def load(self, path):
        with zipfile.ZipFile(path) as zf:
            contents = zf.namelist()
            top = {item.split('/')[0] for item in contents if '/' in item}
            if len(top) != 1:
                raise XBRLError("tpe:invalidDirectoryStructure", "Multiple top-level directories")
            tld = top.pop()
            if not any(f.startswith('%s/reports/' % tld) for f in contents):
                raise XBRLError("pyxbrle:missingReportsDirectory", "Report package does not contain a 'reports' directory")
            reports = list(item for item in contents if re.match('%s/reports.*\.(html?|xhtml|xbrl)$' % tld, item) is not None)
            if any(r.endswith('.xbrl') and r.count('/') > 2 for r in reports):
                raise XBRLError("pyxbrle:misplacedXBRLFile", ".xbrl file found in subdirectory of reports directory")

        return ReportPackage(path, reports)




