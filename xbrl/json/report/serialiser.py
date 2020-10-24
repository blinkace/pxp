import json

DOCTYPE = "http://www.xbrl.org/WGWD/YYYY-MM-DD/xbrl-json"

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
                "numeric": f.isNumeric
            }
            for d in f.dimensions:
                if d.isCore:
                    name = d.name.localname
                else:
                    name = report.asQName(d.name)
                fjson["dimensions"][name] = d.stringValue
            if f.decimals is not None:
                fjson["decimals"] = f.decimals
            out["facts"][f.id] = fjson
            
        out["documentInfo"]["namespaces"] = report.usedPrefixMap()
        return json.dumps(out, indent = 2)

