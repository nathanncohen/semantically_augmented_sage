#!/bin/bash
#
# This script compares the local data with the data from dbpedia.ttl
#
# It is meant to tell if anything from one side should be included in the other,
# and if there is some inconsistency somewhere between the databases.

###########################
# Do we have all graphs ? #
###########################

echo "Distant graphs not in local database"
cat > /tmp/q << EOF
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <.>

select distinct ?l
where {

  GRAPH <$PWD/dbpedia.ttl> {
    ?name <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:Individual_graphs>.
    ?name rdfs:label ?l.
    filter (lang(?l) = "en")
    filter not exists
    {?name <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:Infinite_graphs>}
  }
  filter not exists
  { ?oo rdfs:label ?l} # hack to avoid utf8 problem
} ORDER BY ?name
EOF
arq --graph=graphs.ttl --namedGraph=$PWD/dbpedia.ttl --query=/tmp/q

####################################################
# Local graphs not in dbpedia (category problem) ? #
####################################################
echo "Local graphs not in dbpedia (category problem)"
cat > /tmp/q << EOF
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX : <.>

select distinct ?l
where {
  ?name rdfs:label ?l

  filter not exists {
      GRAPH <$PWD/dbpedia.ttl> { ?namee ?p ?l }
  }
} ORDER BY ?name
EOF
arq --graph=graphs.ttl --namedGraph=$PWD/dbpedia.ttl --query=/tmp/q

###############################
# Suggestion to add in the db #
###############################
echo "Things that could be added to the db"
cat > /tmp/q << EOF
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix dcterms: <http://purl.org/dc/terms/>

select distinct ?s ?p ?o
where {
  # A dbpedia relation
  GRAPH <$PWD/dbpedia.ttl> {
    ?s ?p ?o
  }

  # Unknown locally
  filter not exists {
      ?s ?p ?o.
  }

  # On a known subject
  filter exists {
    ?s ?pp [].
  }

  # With a know predicate
  filter exists{
    GRAPH <$PWD/ontology.ttl>{
        ?p ?ooooo ?oo
    }
  }

  # With no weird category
  filter (?p != dcterms:subject ||
          str(?o) = "http://dbpedia.org/resource/Category:Individual_graphs" ||
          str(?o) = "http://dbpedia.org/resource/Category:Graph_families")


} ORDER BY ?s
EOF
arq --graph=$PWD/graphs.ttl --namedGraph=$PWD/ontology.ttl --namedGraph=$PWD/dbpedia.ttl --query=/tmp/q

##################
# dbpedia errors #
##################

echo "Mismatches local/dbpedia"
cat > /tmp/q << EOF
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sage:  <http://www.sagemath.org/#>

select distinct ?s ?p ?o
where {
  ?s ?p ?o
  MINUS
  {?s rdfs:label ?o}

  GRAPH <$PWD/dbpedia.ttl> {
    ?s ?p ?oo
    filter not exists { ?s ?p ?o }
  }

} order by ?s
EOF
arq --graph=graphs.ttl --namedgraph=$PWD/dbpedia.ttl --query=/tmp/q

##########################
# missing values dbpedia #
##########################

echo "Missing values dbpedia"
cat > /tmp/q << EOF
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sage:  <http://www.sagemath.org/#>

select distinct ?s ?p ?o
where {
  ?s ?p ?o
  MINUS
  {?s sage:build ?o}

  GRAPH <$PWD/dbpedia.ttl> {
    filter not exists { ?s ?p ?oo }
  }

} order by ?s
EOF
arq --graph=graphs.ttl --namedgraph=dbpedia.ttl --query=/tmp/q
