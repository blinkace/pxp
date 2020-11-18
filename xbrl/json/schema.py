import jsonschema
import sys
import os
import json
import io

class fixResolver(jsonschema.RefResolver):
    def __init__(self, schemaAbs, schema):
        jsonschema.RefResolver.__init__(self, base_uri = schemaAbs, referrer = None)
        self.store[ schemaAbs ] = schema

def dict_raise_on_duplicates(ordered_pairs):
    """Reject duplicate keys."""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
           raise ValueError("duplicate key: %r" % (k,))
        else:
           d[k] = v
    return d


def json_validate(schemaFile, fin, reject_bom = False):
    schema = None
    if schemaFile is not None:
        schemaAbs = 'file://' + os.path.abspath(schemaFile)
        with open(schemaFile) as f:
            schema = json.load(f)
    try:
        try:
            instance = json.load(fin, object_pairs_hook=dict_raise_on_duplicates)
        except json.decoder.JSONDecodeError as e:
            if str(e).startswith("Unexpected UTF-8 BOM") and not reject_bom:
                instance = json.load(io.open(instanceFile, 'r', encoding='utf-8-sig'), object_pairs_hook=dict_raise_on_duplicates)
            else:
                return str(e)
        except UnicodeDecodeError as e:
            return str(e)
        except ValueError as e:
            return str(e)
        if schema is not None:
            jsonschema.validate(instance, schema, resolver = fixResolver(schemaAbs, schema))
    except (jsonschema.exceptions.ValidationError, jsonschema.exceptions.RefResolutionError) as e:
        return getattr(e, 'message', str(e))
    except json.decoder.JSONDecodeError as e:
        return "Invalid JSON: " + str(e)
    return None
