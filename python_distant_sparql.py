from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
sparql = SPARQLWrapper("http://dbpedia.org/sparql")
sparql.setQuery("""
select distinct * where {
    ?s rdf:type yago:IndividualGraphs;
       foaf:isPrimaryTopicOf ?url
    FILTER NOT EXISTS { ?s dbpprop:chromaticNumber ?o }
 } LIMIT 100

""")
print '\n\n*** JSON Example'
sparql.setReturnFormat(JSON)
q = sparql.query()
results = q.convert()
results = [{k:result[k][u"value"] for k in result} for result in results["results"]["bindings"]]
