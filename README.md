# PXP

pxp is a light weight, OIM-centric XBRL Processor.  It is intended to provide a
clean and simple CLI and API for making XBRL easy to work with.  For example:

``` 
pxp myfiling.zip -o myfiling.json
```

This will take the XBRL Report Package `myfiling.zip` and convert it into
xBRL-JSON format.

XBRL reports rely on external taxonomies.  pxp will attempt to downloaded
referenced files on demand, but performance can be improved significantly by
downloading the taxonomy as an XBRL Taxonomy Package.  The easiest way to do
this is to place all taxonomy packages in a directory (e.g. `packages`), and
then use the `--packages` or `-p` option with the name of the directory:

``` 
pxp -p packages myfiling.zip -o myfiling.json
```

## Functionality

pxp supports loading from the following formats:

* OIM-compatible xBRL-XML
* Inline XBRL
    * Support for Transformation Rules Registry versions 4 and 5 is incomplete
* xBRL-CSV
* xBRL-JSON

Support for all formats is incomplete, and pxp does not yet pass all tests in
the conformance suites for the above specifications.  This is mainly due to
lack of full data type validation.

pxp supports saving XBRL reports to xBRL-JSON format.

## OIM-centric?

The Open Information Model (OIM) is an initiative to simplify and modernise XBRL.
It supports working with XBRL data in non-XML formats, most notably as xBRL-CSV
and xBRL-JSON.  The OIM, and these new formats, support a simplified subset of
what is permitted in the XML syntax for XBRL.  The main features that are not
supported in OIM are:

* Fractions
* Tuples
* Non-dimensional segment and scenario content
* Complex-typed dimensions

A full list can be found in the [constraints section of the xBRL-XML specification](https://www.xbrl.org/Specification/xbrl-xml/REC-2021-10-13/xbrl-xml-REC-2021-10-13.html#sec-constraints)

pxp is a native OIM processor; it does not support features that are not part
of the OIM.

