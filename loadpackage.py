#!/usr/bin/env python3
import xbrlparser
from xbrlparser.taxonomypackage import TaxonomyPackage
import sys

tp = TaxonomyPackage(sys.argv[1])

url = "http://www.xbrl.org/2013/inlineXBRL/xhtml/xhtml-style-1.xsd"
if tp.hasFile(url):
    print("Found")
    with tp.open(url) as fin:
        print(fin.read().decode("utf-8"))




