#!/usr/bin/env python3
import xbrl
import sys
import logging
import os
import os.path
import argparse
from xbrl.json.report import JSONSerialiser
from urllib.parse import urlparse
from urllib.request import pathname2url

logging.basicConfig(level=logging.DEBUG)

#for f in os.listdir("packages"):
#    print(f)
#    if os.path.isfile("packages/" + f):
#        resolver.addPackage(TaxonomyPackage("packages/" + f))


parser = argparse.ArgumentParser(description="XBRL Processor")
parser.add_argument('--addTaxonomy', dest="packages", action="append")
parser.add_argument('--packages', '-p', dest="packageDir", action="append")
parser.add_argument('reports', metavar='REPORT', nargs="+")
args = parser.parse_args()

processor = xbrl.XBRLProcessor(packageDirs=args.packageDir)

if args.packages is not None:
    for tp in args.packages:
        processor.addTaxonomyPackage(tp)

try:
    src = args.reports[0]

    # Convert paths to URLs, if required.
    # This probably won't work with Windows-style c:\ URLs
    url = urlparse(src)
    if url.scheme == '':
        src = "file:%s" % pathname2url(os.path.abspath(src))

    print("Loading: %s" % src)
    
    report = processor.loadXBRLReport(src)
    js = JSONSerialiser()
    print(js.serialise(report))

except xbrl.XBRLError as e:
    print("[%s] %s" % (e.code_as_qname, e.message))

