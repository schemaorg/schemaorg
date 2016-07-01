"""
Utility functions for supporting the XML Schema Datatypes hierarchy
"""

from rdflib import XSD

XSD_DTs = set(
    (XSD.integer, XSD.decimal, XSD.float, XSD.double, XSD.string,
     XSD.boolean, XSD.dateTime, XSD.nonPositiveInteger, XSD.negativeInteger,
     XSD.long, XSD.int, XSD.short, XSD.byte, XSD.nonNegativeInteger,
     XSD.unsignedLong, XSD.unsignedInt, XSD.unsignedShort, XSD.unsignedByte,
     XSD.positiveInteger))

_sub_types = {
    XSD.integer: [
        XSD.nonPositiveInteger, XSD.negativeInteger, XSD.long, XSD.int,
        XSD.short, XSD.byte, XSD.nonNegativeInteger, XSD.positiveInteger,
        XSD.unsignedLong, XSD.unsignedInt, XSD.unsignedShort, XSD.unsignedByte],
}

_super_types = {}
for superdt in XSD_DTs:
    for subdt in _sub_types.get(superdt, []):
        _super_types[subdt] = superdt

# we only care about float, double, integer, decimal
_typePromotionMap = {
    XSD.float: {XSD.integer: XSD.float,
                XSD.decimal: XSD.float,
                XSD.double: XSD.double},

    XSD.double: {XSD.integer: XSD.double,
                 XSD.float: XSD.double,
                 XSD.decimal: XSD.double},

    XSD.decimal: {XSD.integer: XSD.decimal,
                  XSD.float: XSD.float,
                  XSD.double: XSD.double},

    XSD.integer: {XSD.decimal: XSD.decimal,
                  XSD.float: XSD.float,
                  XSD.double: XSD.double}
}


def type_promotion(t1, t2):
    if t2 == None:
        return t1
    t1 = _super_types.get(t1, t1)
    t2 = _super_types.get(t2, t2)
    if t1 == t2:
        return t1  # matching super-types
    try:
        return _typePromotionMap[t1][t2]
    except KeyError:
        raise TypeError(
            'Operators cannot combine datatypes %s and %s' % (t1, t2))
