#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

# To be executed in the SchemaTerms/example-code/{example} directory
import os
for path in [os.getcwd(),"..","../..","../../.."]: #Adds in current, example-code, and SchemaTerms directory into path
  sys.path.insert( 1, path ) #Pickup libs from local  directories
from sdoterm import SdoTerm
import schematerms_pb2

sdotypemap = {
    SdoTerm.TYPE: schematerms_pb2.TermType.TYPE,
    SdoTerm.PROPERTY: schematerms_pb2.TermType.PROPERTY,
    SdoTerm.DATATYPE: schematerms_pb2.TermType.DATATYPE,
    SdoTerm.ENUMERATION: schematerms_pb2.TermType.ENUMERATION,
    SdoTerm.ENUMERATIONVALUE: schematerms_pb2.TermType.ENUMERATIONVALUE,
    SdoTerm.REFERENCE: schematerms_pb2.TermType.REFERENCE
}

#Populate termdescriptor - message common sub-message of all (except REFERENCE)
def _termdescriptorPopulate(termdesc,term):
    termdesc.termType = sdotypemap[term.termType]
    termdesc.uri = term.uri
    if term.termType != SdoTerm.REFERENCE:
        termdesc.label = term.label
        termdesc.acknowledgements.extend(term.acknowledgements)
        for i in term.superPaths:
            sp = termdesc.superPaths.add()
            sp.superPath.extend(terms2IdString(i))
        termdesc.comment = term.comment
        termdesc.equivalents.extend(terms2IdString(term.equivalents))
        termdesc.pending = term.pending
        termdesc.retired = term.retired
        termdesc.sources.extend(term.sources)
        termdesc.supersededBy = term.supersededBy
        termdesc.supersedes.extend(term.supersedes)
    
#Populate message for passed simple (non-expanded) term
#If msg != None the empty message will have been created by previous nested add() call
#If no msg passed one of appropriate type is created
def _populateSimpleMsg(msg=None,term=None,inTermStack=False):
    if not msg:
        if term.termType == SdoTerm.TYPE or term.termType == SdoTerm.DATATYPE or term.termType == SdoTerm.ENUMERATION:
            msg = schematerms_pb2.SDOBaseType()
        elif term.termType == SdoTerm.PROPERTY:
            msg = schematerms_pb2.SDOProperty()
        elif term.termType == SdoTerm.ENUMERATIONVALUE:
            msg = schematerms_pb2.SDOEnumerationValue()
        elif term.termType == SdoTerm.REFERENCE:
            msg = schematerms_pb2.SDOReference()
        else:
            print("Unknown term type '%s'" % term.termType)

    msg.id = term.id
    if term.termType == SdoTerm.REFERENCE:
        #Reference message only has id & uri values
        msg.uri = term.uri
    else:
        #Populate standard submessage
        _termdescriptorPopulate(msg.termdescriptor.add(),term)
    
        if term.termType == SdoTerm.TYPE or term.termType == SdoTerm.DATATYPE or term.termType == SdoTerm.ENUMERATION:
            msg.properties.extend(term.properties)
            msg.expectedTypeFor.extend(term.expectedTypeFor)
            msg.termStack.extend(term.termStack)
            msg.subs.extend(term.subs)
            msg.supers.extend(term.supers)
            if term.termType == SdoTerm.ENUMERATION:
                msg.enumerationMembers.extend(term.enumerationMembers)
        elif term.termType == SdoTerm.PROPERTY:
            msg.domainIncludes.extend(terms2IdString(term.domainIncludes))
            msg.rangeIncludes.extend(terms2IdString(term.rangeIncludes))
            if term.inverse:
                msg.inverse = term2IdString(term.inverse)
            msg.termStack.extend(terms2IdString(term.termStack))
            msg.subs.extend(terms2IdString(term.subs))
            msg.supers.extend(terms2IdString(term.supers))
        elif term.termType == SdoTerm.ENUMERATIONVALUE:
            msg.enumerationParent = term2IdString(term.enumerationParent)
    return msg

#Populate message for passed expanded term
#If msg != None the empty message will have been created by previous nested add() call
#If no msg passed one of appropriate type is created
def _populateExpandedMsg(msg=None,term=None,inTermStack=False):
    if not msg:
        if term.termType == SdoTerm.TYPE or term.termType == SdoTerm.DATATYPE or term.termType == SdoTerm.ENUMERATION:
            if not inTermStack:
                msg = schematerms_pb2.SDOBaseTypeExpanded()
            else:
                #Termstack nested terms do not have their termstack expanded
                msg = schematerms_pb2.SDOBaseTypeExpandedPropsOnly()
        else:
            print("Unknown term type '%s'" % term.termType)

    msg.id = term.id
    _termdescriptorPopulate(msg.termdescriptor.add(),term)

    for i in term.properties:
        _populateMsg(msg.properties.add(),i)
    for i in term.expectedTypeFor:
        _populateMsg(msg.expectedTypeFor.add(),i)
    msg.termStack.extend(terms2IdString(term.termStack))
    msg.subs.extend(terms2IdString(term.subs))
    msg.supers.extend(terms2IdString(term.supers))
    if term.termType == SdoTerm.ENUMERATION:
        msg.enumerationMembers.extend(terms2IdString(term.enumerationMembers))
    return msg

def terms2IdString(terms):
    ret = []
    for t in terms:
        ret.append(term2IdString(t))
    return ret

def term2IdString(term):
    if isinstance(term, str):
        return term
    return term.id

#Populate message for passed term 
#If msg != None the empty message will have been created by previous nested add() call
def _populateMsg(msg=None,term=None,inTermStack=False):
    if term.expanded:
        if term.termType == SdoTerm.TYPE or term.termType == SdoTerm.DATATYPE or term.termType == SdoTerm.ENUMERATION:
            return _populateExpandedMsg(msg=msg,term=term,inTermStack=inTermStack)
    
    return _populateSimpleMsg(msg=msg,term=term,inTermStack=inTermStack)
    
def sdotermToProtobuf(term):
    return _populateMsg(term=term)
    
def protobufToMsg(buf):
    return buf.SerializeToString()

def protobufToText(buf):
    return str(buf)
    
def sdotermToProtobufMsg(term):
    return protobufToMsg(sdotermToProtobuf(term=term))

def sdotermToProtobufText(term):
    return protobufToText(sdotermToProtobuf(term=term))
