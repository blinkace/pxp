#!/usr/bin/env python3
import xbrl
import sys
import logging
import os
import os.path
import argparse
import json
import traceback
from xbrl.json.report import JSONSerialiser
from urllib.parse import urlparse, urljoin
from urllib.request import pathname2url
from lxml import etree

def runSuite(src):
    suite = processor.loadTestSuite(src)
    passed = 0
    run = 0
    for v in suite.variations:
        if args.variations is None or v.id in args.variations:
            print(v.id)
            run += 1
            if len(v.inputs) != 1:
                print("Variation has %d inputs" % len(v.inputs))
            else:
                errors = set()
                try:
                    report = processor.loadXBRLCSVReport(urljoin(suite.url, v.inputs[0].url))
                except xbrl.XBRLError as e:
                    errors = { e.code }
                    if args.verbose:
                        print("[%s] %s" % (e.code, e.message))
                except Exception as e:
                    errors = { etree.QName("{}UncaughtException") }
                    print(traceback.format_exc())
                if (errors == v.errors):
                    print("Pass (%d errors expected)" % len(errors))
                    passed += 1
                else:
                    print("Fail")
                    print("Got: %s Expected: %s" % ("".join(e.text for e in errors), "".join(e.text for e in v.errors)))

    print("%d of %d passed (%.1f%%)" % (passed, run, (100*passed/(run or 1))))

def urlise(urlOrPath):
    url = urlparse(urlOrPath)
    if url.scheme == '':
        return "file:%s" % pathname2url(os.path.abspath(urlOrPath))
    return urlOrPath


#for f in os.listdir("packages"):
#    print(f)
#    if os.path.isfile("packages/" + f):
#        resolver.addPackage(TaxonomyPackage("packages/" + f))


parser = argparse.ArgumentParser(description="XBRL Processor")
parser.add_argument('--addTaxonomy', dest="packages", action="append")
parser.add_argument('--packages', '-p', dest="packageDir", action="append")
parser.add_argument('-c', '--csv', dest="csv", action="store_true")
parser.add_argument('-t', '--testsuite', dest="test", action="store_true")
parser.add_argument('-v', '--verbose', dest="verbose", action="store_true")
parser.add_argument('--debug', dest="debug", action="store_true")
parser.add_argument('--variation', dest="variations", action="append")
parser.add_argument('reports', metavar='REPORT', nargs="+")
args = parser.parse_args()

level = logging.WARNING
if args.debug:
    level = logging.DEBUG
logging.basicConfig(level=level)

processor = xbrl.XBRLProcessor(packageDirs=args.packageDir)

if args.packages is not None:
    for tp in args.packages:
        processor.addTaxonomyPackage(tp)

try:
    src = urlise(args.reports[0])

    #print("Loading: %s" % src)
    
    #report = processor.loadXBRLReport(src)
    if args.csv:
        report = processor.loadXBRLCSVReport(src)
    elif args.test:
        runSuite(src)
    else:
        report = processor.loadIXBRLReport(src)

    js = JSONSerialiser()
#    print(json.dumps(js.serialise(report), indent=2))

except xbrl.XBRLError as e:
    print("[%s] %s" % (e.code_as_qname, e.message))

