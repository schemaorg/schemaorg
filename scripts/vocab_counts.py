# The file containing the actual counts is not checked in.
# This file has the script for bucketizing the counts

import sys

def vocab_term (term) :
    parts = term.split('/', 4)
    if (len(parts) < 4) :
        return None 
    domain = parts[2]
    if (not (domain == "schema.org")) :
        return None
    else :
        return parts[3]

counts = {}
def addCount (term, count) :
    if (term in counts) :
        counts[term] = counts[term] + count
    else:
        counts[term] = count
        
def bucket (vt, count) :
    if (vt != None):
        if (count < 10) :
            return None
        elif (count < 100) :
            return "%s\t%i" % (vt, 1)
        elif (count < 1000) :
            return "%s\t%i" % (vt, 2)
        elif (count < 10000) :
            return "%s\t%i" % (vt, 3)
        elif (count < 50000) :
            return "%s\t%i" % (vt, 4)
        elif (count < 100000) :
            return "%s\t%i" % (vt, 5)
        elif (count < 250000) :
            return "%s\t%i" % (vt, 7)
        elif (count < 500000) :
            return "%s\t%i" % (vt, 8)
        elif (count < 1000000) :
            return "%s\t%i" % (vt, 9)
        else:
            return "%s\t%i" % (vt, 10)

input_file = sys.argv[1]


if (input_file != None):
    f = open(input_file)
    if (f != None):
        for line in f:            
            parts = line.strip().split(',')
            if (len(parts) > 1):
                term = parts[0]
                count = 0
                count_string = parts[1].replace(' ', '')
                try:
                    count = int(parts[1])
                except:
                    count = 0
                term = vocab_term(term)
                addCount(term, count)
        for term in sorted(counts.keys(), key= lambda term: counts[term], reverse=True):
            print bucket(term, counts[term])
    else:
        print "Cannot open file " + input_file
