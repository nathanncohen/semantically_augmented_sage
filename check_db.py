filename = "graphs.ttl"

import rdflib
import rdfextras
rdfextras.registerplugins() # so we can Graph.query()

g=rdflib.Graph()
g.parse(filename,format="n3")
results = g.query("""
SELECT ?g ?o
WHERE {
?g sage:build ?o.
}
ORDER BY (?g)
""").bindings

for r in results:
    cmd = str(r['?o'])
    try:
        exec 'g='+cmd
    except:
        print cmd
