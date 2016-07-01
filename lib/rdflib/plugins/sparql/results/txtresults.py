
from rdflib import URIRef, BNode, Literal
from rdflib.query import ResultSerializer

def _termString(t, namespace_manager):
    if t == None:
        return "-"
    if namespace_manager:
        if isinstance(t, URIRef): 
            return namespace_manager.normalizeUri(t)
        elif isinstance(t, BNode): 
            return t.n3()
        elif isinstance(t, Literal): 
            return t._literal_n3(qname_callback=namespace_manager.normalizeUri)
    else: 
        return t.n3()


class TXTResultSerializer(ResultSerializer): 
    """
    A write only QueryResult serializer for text/ascii tables
    """

    def serialize(self, stream, encoding, namespace_manager = None): 

        """
        return a text table of query results
        """


        def c(s, w):
            """
            center the string s in w wide string
            """
            w -= len(s)
            h1 = h2 = w // 2
            if w % 2: h2 += 1
            return " " * h1 + s + " " * h2

        if self.result.type!='SELECT': 
            raise Exception("Can only pretty print SELECT results!")

        if not self.result:
            return "(no results)\n"
        else:

            keys = sorted(self.result.vars)
            maxlen = [0] * len(keys)
            b = [[_termString(r[k], namespace_manager) for k in keys] for r in self.result]
            for r in b:
                for i in range(len(keys)):
                    maxlen[i] = max(maxlen[i], len(r[i]))

            stream.write(
                "|".join([c(k, maxlen[i]) for i, k in enumerate(keys)]) + "\n")
            stream.write("-" * (len(maxlen)+sum(maxlen)) + "\n")
            for r in sorted(b):
                stream.write("|".join(
                    [t + " " * (i - len(t)) for i, t in zip(maxlen, r)]) + "\n")

