import collections

from rdflib import URIRef, Graph, Literal
from rdflib.namespace import VOID, RDF


def generateVoID(g, dataset=None, res=None, distinctForPartitions=True):
    """
    Returns a new graph with a VoID description of the passed dataset

    For more info on Vocabulary of Interlinked Datasets (VoID), see:
    http://vocab.deri.ie/void

    This only makes two passes through the triples (once to detect the types
    of things)

    The tradeoff is that lots of temporary structures are built up in memory
    meaning lots of memory may be consumed :)
    I imagine at least a few copies of your original graph.

    the distinctForPartitions parameter controls whether
    distinctSubjects/objects are tracked for each class/propertyPartition
    this requires more memory again

    """

    typeMap = collections.defaultdict(set)
    classes = collections.defaultdict(set)
    for e, c in g.subject_objects(RDF.type):
        classes[c].add(e)
        typeMap[e].add(c)

    triples = 0
    subjects = set()
    objects = set()
    properties = set()
    classCount = collections.defaultdict(int)
    propCount = collections.defaultdict(int)

    classProps = collections.defaultdict(set)
    classObjects = collections.defaultdict(set)
    propSubjects = collections.defaultdict(set)
    propObjects = collections.defaultdict(set)

    for s, p, o in g:

        triples += 1
        subjects.add(s)
        properties.add(p)
        objects.add(o)

        # class partitions
        if s in typeMap:
            for c in typeMap[s]:
                classCount[c] += 1
                if distinctForPartitions:
                    classObjects[c].add(o)
                    classProps[c].add(p)

        # property partitions
        propCount[p] += 1
        if distinctForPartitions:
            propObjects[p].add(o)
            propSubjects[p].add(s)

    if not dataset:
        dataset = URIRef("http://example.org/Dataset")

    if not res:
        res = Graph()

    res.add((dataset, RDF.type, VOID.Dataset))

    # basic stats
    res.add((dataset, VOID.triples, Literal(triples)))
    res.add((dataset, VOID.classes, Literal(len(classes))))

    res.add((dataset, VOID.distinctObjects, Literal(len(objects))))
    res.add((dataset, VOID.distinctSubjects, Literal(len(subjects))))
    res.add((dataset, VOID.properties, Literal(len(properties))))

    for i, c in enumerate(classes):
        part = URIRef(dataset + "_class%d" % i)
        res.add((dataset, VOID.classPartition, part))
        res.add((part, RDF.type, VOID.Dataset))

        res.add((part, VOID.triples, Literal(classCount[c])))
        res.add((part, VOID.classes, Literal(1)))

        res.add((part, VOID["class"], c))

        res.add((part, VOID.entities, Literal(len(classes[c]))))
        res.add((part, VOID.distinctSubjects, Literal(len(classes[c]))))

        if distinctForPartitions:
            res.add(
                (part, VOID.properties, Literal(len(classProps[c]))))
            res.add((part, VOID.distinctObjects,
                    Literal(len(classObjects[c]))))

    for i, p in enumerate(properties):
        part = URIRef(dataset + "_property%d" % i)
        res.add((dataset, VOID.propertyPartition, part))
        res.add((part, RDF.type, VOID.Dataset))

        res.add((part, VOID.triples, Literal(propCount[p])))
        res.add((part, VOID.properties, Literal(1)))

        res.add((part, VOID.property, p))

        if distinctForPartitions:

            entities = 0
            propClasses = set()
            for s in propSubjects[p]:
                if s in typeMap:
                    entities += 1
                for c in typeMap[s]:
                    propClasses.add(c)

            res.add((part, VOID.entities, Literal(entities)))
            res.add((part, VOID.classes, Literal(len(propClasses))))

            res.add((part, VOID.distinctSubjects,
                    Literal(len(propSubjects[p]))))
            res.add((part, VOID.distinctObjects,
                    Literal(len(propObjects[p]))))

    return res, dataset
