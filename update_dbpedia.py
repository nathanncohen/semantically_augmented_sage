from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF, TURTLE
import rdflib
sparql = SPARQLWrapper("http://live.dbpedia.org/sparql")
sparql.setQuery("""
construct {
  ?s ?p ?o.
}
where {
    {
       ?s <http://dbpedia.org/property/vertices> [].
       ?s ?p ?o.
    }
    UNION
    {
       ?s <http://www.w3.org/2004/02/skos/core#broader>+ <http://dbpedia.org/resource/Category:Graph_theory>.
       ?s ?p ?o.
    }
 }
""")
sparql.setReturnFormat(TURTLE)
q = sparql.query()
q = results = q.convert()
with open('dbpedia.ttl','w') as f:
    f.write(q)

#results = [{k:result[k][u"value"] for k in result} for result in results["results"]["bindings"]]
