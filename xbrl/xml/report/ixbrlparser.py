from lxml import etree
from xbrl.const import NS
from xbrl.xml.taxonomy.document import SchemaRef
from xbrl.documentloader import DocumentLoader
from xbrl.xml import qname, parser
from xbrl.xbrlerror import XBRLError
from math import log10, fabs, floor
import xbrl.model.report as report 
import logging

from .context import Context
from .unit import Unit
from urllib.parse import urljoin
from .trrcollection import buildTRRCollection

from .parser import XBRLReportParser

class IXBRLReportParser(XBRLReportParser):


    def parse(self, url, src=None):
        if src is None:
            with self.processor.resolver.open(url) as src:
                tree = etree.parse(src, parser())
        else:
            tree = etree.parse(src, parser())
        root = tree.getroot()
        self.ixFactElements = []
        self.ixContinuations = dict()
        self.url = url
        self.parseChildren(root)
        return self.buildReport()

    def parseChildren(self, parent):

        for e in parent.childElements():
            name = etree.QName(e.tag)
            if name.namespace in [NS.ix, NS.ix10]:
                if name.localname == 'header':
                    self.parseIXHeader(e)
                elif name.localname in ["fraction", "nonFraction", "nonNumeric"]:
                    self.ixFactElements.append(e)
                    self.parseChildren(e)
                elif name.localname == 'continuation':
                    self.ixContinuations[e.get("id")] = e
                    self.parseChildren(e)
                elif name.localname == 'exclude':
                    pass
                else:
                    logging.error("Unhandled ix element: ix:%s" % name.localname)
            else:
                self.parseChildren(e)

    def buildReport(self):
        rpt = report.Report(self.taxonomy)
        trr = buildTRRCollection()
        for fe in self.ixFactElements:
            conceptName = fe.qnameAttrValue("name")
            concept = self.taxonomy.concepts.get(conceptName)
            if concept is None:
                raise XBRLError("oime:missingConceptDefinition", "Could not find concept definition for '%s'" % conceptName)

            dims = set()
            dims.add(report.ConceptCoreDimension(concept))

            cid = fe.get("contextRef")
            ctxt = self.contexts.get(cid, None)
            if ctxt is None:
                raise XBRLError("ixbrle:missingContext", "No context with ID '%s'" % cid)

            dims.update(ctxt.asDimensions(self.taxonomy))
            content = ''
            ce = fe
            while True:
                content += self.getRelevantContent(ce)
                contId = ce.get("continuedAt", None)
                if contId is None:
                    break
                ce = self.ixContinuations.get(contId, None)
                if ce is None:
                    raise XBRLError("ixbrle:missingContext", "No continuation element with ID '%s'" % cid)

            uid = fe.get("unitRef", None)
            if uid is not None:
                unit = self.units.get(uid, None)
                if unit is None:
                    raise XBRLError("ixbrle:missingUnit", "No unit with ID '%s'" % cid)
                dims.update(unit.asDimensions())

            fmt = fe.qnameAttrValue("format")
            if fmt is not None:
                transform = trr.getTransform(fmt)
                if transform is None:
                    logging.error("Unknown transform: %s" % fmt.text)
                else:
                    content = transform.transform(content)

            f = report.Fact(fe.get("id", self.generateId()), dimensions = dims, value = content, decimals = self.parseDecimals(fe, value = content))
            rpt.addFact(f)
        return rpt
            

    def getRelevantContent(self, e):
        s = e.text if e.text is not None else ""
        for c in e.childElements():
            if c.tag != qname("ix:exclude"):
                s += self.getRelevantContent(c)
            s += c.tail if c.tail is not None else ""
        return s

    def parseIXHeader(self, header):
        hidden = header.childElement([qname("ix:hidden"), qname("ix10:resources")])
        if hidden is not None:
            self.parseIXHidden(hidden)

        resources = header.childElement([qname("ix:resources"), qname("ix10:resources")])
        if resources is not None:
            self.parseIXResources(resources)

        for e in header.childElements([qname("ix:references"), qname("ix10:references")]):
            td = e.get("target", None) 
            if td is not None:
                logging.error("Ignoring target document '%s'" % td)
                continue

            self.taxonomy = self.getTaxonomy(e)

    def parseIXResources(self, resources):
        for e in resources.childElements():
            if e.tag == qname("xbrli:context"):
                c = Context.from_xml(e)
                self.contexts[c.id] = c
            elif e.tag == qname("xbrli:unit"):
                u = Unit.from_xml(e)
                self.units[u.id] = u
            else:
                logging.warning("Unsupported resources element %s" % e.tag)


    def parseIXHidden(self, hidden):
        pass





