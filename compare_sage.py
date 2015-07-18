# This file is meant for knowing what in Sage should be added to the database.

def individual_graphs():
    r"""
    Return a list of Sage commands building each 'individual graph'
    """
    import inspect
    l = []
    import sage.graphs.graph_generators
    G = sage.graphs.graph_generators.GraphGenerators
    methods = [x for x in dir(G)
               if x[0] != "_" and x != "sage"]
    for m_name in methods:
        m = getattr(G,m_name)
        args = inspect.getargspec(m)
        defaults = args.defaults
        nargs = len(args.args)
        if (nargs == 0 or (defaults is not None and args.defaults.count(None) == nargs)):
            l.append("graphs."+m_name)

    l.remove("graphs.line_graph_forbidden_subgraphs")
    return l

import rdflib
translation_db=rdflib.Graph()
translation_db.parse("translation.ttl",format="n3")

print "==> missing from the db"
for x in set(individual_graphs()).difference(str(x) for x in translation_db.objects()):
    print x
