#!/bin/bash
#
# This script fills dbpedia.rdf with the information we need locally.

cat > /tmp/q << EOF
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>

construct {
?name ?p ?o;
}
where {
    # Graphs
    SERVICE <http://live.dbpedia.org/sparql> {
        ?name <http://purl.org/dc/terms/subject> ?cat.
        filter (?cat = <http://dbpedia.org/resource/Category:Individual_graphs> ||
                ?cat = <http://dbpedia.org/resource/Category:Graph_families>)
        ?name ?p ?o;
    }

} ORDER BY ?name
EOF
arq --graph=graphs.ttl --query=/tmp/q --results=rdf > dbpedia.rdf
