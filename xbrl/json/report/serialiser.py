import json
from xbrl.const import DocumentType

DOCTYPE = DocumentType.xbrljson_wgwd

class JSONSerialiser:

    def serialise(self, report):
        out = {
            "documentInfo": {
                "documentType": DOCTYPE,
                "namespaces": {}
            },
            "facts": {
            }
        }

        for fid, f in report.facts.items():
            fjson = {
                "dimensions": {},
                "value":  f.concept.datatype.stringValue(f.value),
                #"numeric": f.isNumeric
            }
            for n, d in f.dimensions.items():
                if d.isCore:
                    name = n.localname
                else:
                    name = report.asQName(n)
                fjson["dimensions"][name] = d.stringValue
            if f.decimals is not None:
                fjson["decimals"] = f.decimals
            out["facts"][f.id] = fjson

        out["documentInfo"]["taxonomy"] = list(r.href for r in report.taxonomy.identifier)
            
        out["documentInfo"]["namespaces"] = report.usedPrefixMap()
        return out

