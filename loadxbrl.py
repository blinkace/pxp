#!/usr/bin/env python3
import xbrl
import sys
import logging
import os
import os.path
import argparse
from xbrl.json.report import JSONSerialiser

logging.basicConfig(level=logging.DEBUG)

#for f in os.listdir("packages"):
#    print(f)
#    if os.path.isfile("packages/" + f):
#        resolver.addPackage(TaxonomyPackage("packages/" + f))


parser = argparse.ArgumentParser(description="XBRL Processor")
parser.add_argument('--addTaxonomy', dest="packages", action="append")
parser.add_argument('reports', metavar='REPORT', nargs="+")
args = parser.parse_args()

processor = xbrl.XBRLProcessor()

if args.packages is not None:
    for tp in args.packages:
        print(tp)
        processor.addTaxonomyPackage(tp)

try:
    report = processor.loadXBRLReport(args.reports[0])
    js = JSONSerialiser()
    print(js.serialise(report))

except xbrl.XBRLError as e:
    print("[%s] %s" % (e.code_as_qname, e.message))

