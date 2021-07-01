import re

bcp47_tag = r'''(?x)^(
    (?P<grandfathered>(en-GB-oed|i-ami|i-bnn|i-default|i-enochian|i-hak|i-klingon|i-lux|
    i-mingo|i-navajo|i-pwn|i-tao|i-tay|i-tsu|sgn-BE-FR|sgn-BE-NL|sgn-CH-DE|art-lojban|
    cel-gaulish|no-bok|no-nyn|zh-guoyu|zh-hakka|zh-min|zh-min-nan|zh-xiang))
    |(?:(?P<language>([A-Za-z]{2,3}
    (?:-(?P<extlang>[A-Za-z]{3}(?:-[A-Za-z]{3}){0,2}))?)|[A-Za-z]{4}|[A-Za-z]{5,8})
    (?:-(?P<script>[A-Za-z]{4}))?
    (?:-(?P<region>[A-Za-z]{2}|[0-9]{3}))?
    (?:-(?P<variant>[A-Za-z0-9]{5,8}|[0-9][A-Za-z0-9]{3}))*
    (?:-(?P<extension>[0-9A-WY-Za-wy-z](-[A-Za-z0-9]{2,8})+))*
    (?:-(?P<privateUse1>x(-[A-Za-z0-9]{1,8})+))?)
    |(?P<privateUse2>x(-[A-Za-z0-9]{1,8})+))$'''

RE_BCP47_TAG = re.compile(bcp47_tag)

def isValidLanguageCode(tag):
    return RE_BCP47_TAG.match(tag) is not None 


