from lxml import etree
from xbrl.const import NS, LinkType, LinkGroup
from xbrl.xml.taxonomy.document import SchemaRef
from xbrl.documentloader import DocumentLoader
from xbrl.xml import qname, parser, qnameset
from xbrl.xbrlerror import XBRLError
from math import log10, fabs, floor
import xbrl.model.report as report 
import xbrl.model.taxonomy as taxonomy 
import logging
import copy
import decimal

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
        self.relationships = dict()
        self.ixFootnotes = dict()
        self.url = url
        self.hasHeader = False
        self.parseChildren(root)
        if not self.hasHeader:
            raise XBRLError("ixe:missingHeader", "ix:header not found")
        return self.buildReport()

    def parseChildren(self, parent):
        for e in parent.childElements():
            name = etree.QName(e.tag)
            if name.namespace in [NS.ix, NS.ix10]:
                if name.localname == 'header':
                    self.hasHeader = True
                    self.parseIXHeader(e)
                elif name.localname in ["nonFraction", "nonNumeric"]:
                    self.ixFactElements.append(e)
                    self.parseChildren(e)
                elif name.localname == 'continuation':
                    self.ixContinuations[e.get("id")] = e
                    self.parseChildren(e)
                elif name.localname == 'footnote':
                    self.ixFootnotes[e.get("id")] = e
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
        factMap = { f.get("id"): f for f in self.ixFactElements if f.get("id", None) is not None }

        for r in self.relationships:
            if factMap.get(r) is None:
                raise XBRLError("ixe:unresolvableRelationship", "Fact with id '%s' referenced by relationship but is not present in report" % r)

        for fe in self.ixFactElements:
            conceptName = fe.qnameAttrValue("name")
            concept = self.taxonomy.concepts.get(conceptName)
            if concept is None:
                raise XBRLError("oime:missingConceptDefinition", "Could not find concept definition for '%s'" % conceptName)

            dims = set()
            dims.add(report.ConceptCoreDimension(concept))

            cid = fe.get("contextRef")
            ctxt = self.getContext(cid)

            dims.update(ctxt.asDimensions(self.taxonomy))

            escape = etree.QName(fe.tag).localname == 'nonNumeric' and fe.boolAttrValue("escape")
            ce = fe
            if fe.get(qname('xsi:nil'), 'false') in ['1', 'true']:
                content = None
            else:
                content = ''
                while True:
                    if escape:
                        content += self.getRelevantContentWithTags(ce).fragmentToString(current_ns = NS.xhtml, escape = True)
                    else:
                        content += self.getRelevantContent(ce)
                    contId = ce.get("continuedAt", None)
                    if contId is None:
                        break
                    ce = self.ixContinuations.get(contId, None)
                    if ce is None:
                        raise XBRLError("ixe:missingContext", "No continuation element with ID '%s'" % cid)

            uid = fe.get("unitRef", None)
            if uid is not None:
                unit = self.units.get(uid, None)
                if unit is None:
                    raise XBRLError("ixe:missingUnit", "No unit with ID '%s'" % cid)
                dims.update(unit.asDimensions())

            if content is not None:
                fmt = fe.qnameAttrValue("format")
                if fmt is not None:
                    transform = trr.getTransform(fmt)
                    if transform is None:
                        logging.error("Unknown transform: %s" % fmt.text)
                    else:
                        content = transform.transform(content)

                if etree.QName(fe.tag).localname == 'nonFraction':
                    content = content.strip()
                    if fe.get("sign", None) == "-":
                        content = "-" + content

                if etree.QName(fe.tag).localname == 'nonFraction':
                    content = content.strip()
                    scale = fe.get("scale", "0")
                    content = str(decimal.Decimal(content) * decimal.Decimal(10**int(scale)))

            rels = self.relationships.get(fe.get("id", None), {})
            links = {}
            for lt, groups in rels.items():
                for group, targets in groups.items():
                    for target in targets:
                        fnf = rpt.facts.get(target, None)
                        if fnf is None:
                            fn = self.ixFootnotes.get(target)
                            if fn is None:
                                raise XBRLError("ixe:missingTargetFact", "Non-existent fact with id '%s' referenced from relationship" % target)
                            fnf = report.Fact(
                                    target, 
                                    dimensions = { report.ConceptCoreDimension(taxonomy.NoteConcept) },
                                    value = self.getRelevantContentWithTags(fn).fragmentToString(current_ns=NS.xhtml))
                            rpt.addFact(fnf)

                        links.setdefault(lt, {}).setdefault(group, []).append(fnf)

            f = report.Fact(fe.get("id", self.generateId()), dimensions = dims, value = content, decimals = self.parseDecimals(fe, value = content), links = links)
            rpt.addFact(f)
        return rpt
            
    def getRelevantContent(self, e):
        s = e.text if e.text is not None else ""
        for c in e.childElements():
            if c.tag != qname("ix:exclude"):
                s += self.getRelevantContent(c)
            s += c.tail if c.tail is not None else ""
        return s

    def getRelevantContentWithTags(self, e):
        new = copy.deepcopy(e)

        etree.strip_elements(new, '{%s}exclude' % NS.ix, '{%s}exclude' % NS.ix10, with_tail = False)
        etree.strip_tags(new, '{%s}*' % NS.ix, '{%s}*' % NS.ix10)
        return new

    def parseIXHeader(self, header):
        hidden = header.childElement(qnameset({"ix","ix10"}, "hidden"))
        if hidden is not None:
            self.parseIXHidden(hidden)

        resources = header.childElement(qnameset({"ix", "ix10"}, "resources"))
        if resources is not None:
            self.parseIXResources(resources)

        for e in header.childElements(qnameset({"ix", "ix10"}, "references")):
            td = e.get("target", None) 
            if td is not None:
                logging.error("Ignoring target document '%s'" % td)
                continue

            self.taxonomy = self.getTaxonomy(e)

    def parseIXResources(self, resources):
        for e in resources.childElements():
            if e.tag == qname("xbrli:context"):
                self.contextElements[e.get("id")] = e
            elif e.tag == qname("xbrli:unit"):
                u = Unit.from_xml(e)
                self.units[u.id] = u
            elif e.tag in qnameset({"ix", "ix10"}, "relationship"):
                for f in e.get("fromRefs").split():
                    self.relationships.setdefault(f,{}) \
                        .setdefault(e.get("arcrole", LinkType.footnote),{}) \
                        .setdefault(e.get("linkRole", LinkGroup.default),[]) \
                        .extend(e.get("toRefs").split())
            else:
                logging.warning("Unsupported resources element %s" % e.tag)


    def parseIXHidden(self, hidden):
        self.parseChildren(hidden)





