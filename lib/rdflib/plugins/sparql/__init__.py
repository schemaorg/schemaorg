"""
SPARQL implementation for RDFLib

.. versionadded:: 4.0
"""


SPARQL_LOAD_GRAPHS = True
"""
If True, using FROM <uri> and FROM NAMED <uri>
will load/parse more data 
"""


SPARQL_DEFAULT_GRAPH_UNION = True
"""
If True - the default graph in the RDF Dataset is the union of all
named graphs (like RDFLib's ConjunctiveGraph)
"""


CUSTOM_EVALS = {}
"""
Custom evaluation functions

These must be functions taking (ctx, part) and raise
NotImplementedError if they cannot handle a certain part
"""


PLUGIN_ENTRY_POINT = 'rdf.plugins.sparqleval'



from . import parser
from . import operators
from . import parserutils

from .processor import prepareQuery, processUpdate

assert parser
assert operators
assert parserutils

try:
    from pkg_resources import iter_entry_points
except ImportError:
    pass  # TODO: log a message
else:
    for ep in iter_entry_points(PLUGIN_ENTRY_POINT):
        CUSTOM_EVALS[ep.name] = ep.load()
