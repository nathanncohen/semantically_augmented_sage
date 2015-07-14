# This script compares the local data with the data from dbpedia.ttl
#
# It is meant to tell if anything from one side should be included in the other,
# and if there is some inconsistency somewhere between the databases.

import rdflib
import rdfextras
rdfextras.registerplugins() # so we can Graph.query()

# All entries in the database with a sage:build predicate.
dbpedia=rdflib.Graph()
dbpedia.parse("dbpedia.ttl",format="n3")
local=rdflib.Graph()
local.parse("graphs.ttl",format="n3")
ontology=rdflib.Graph()
ontology.parse("ontology.ttl",format="n3")

###########################
# Do we have all graphs ? #
###########################

print "=== Distant graphs not in local database === \n"

sparql_all_individual_finite_graph = ("""
select distinct ?l ?name where {
    ?name <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:Individual_graphs>.
    ?name rdfs:label ?l.
    filter (lang(?l) = 'en')
    filter not exists
    {?name <http://purl.org/dc/terms/subject> <http://dbpedia.org/resource/Category:Infinite_graphs>}
}""")
dbpedia_graphs = [x['l'] for x in dbpedia.query(sparql_all_individual_finite_graph)]
local_graphs   = [x['l'] for x in   local.query(sparql_all_individual_finite_graph)]

for g in set(dbpedia_graphs).difference(local_graphs):
    print g

####################################################
# Local graphs not in dbpedia (category problem) ? #
####################################################

print "\n=== Local graphs not in dbpedia === \n"

for g in set(local_graphs).difference(dbpedia_graphs):
    print g

######################################
# Possible additions to the local db #
######################################

print "\n=== Possible additions to the local db === \n"
predicates = set(ontology.subjects())
local_finite_graphs = set(x['name'] for x in   local.query(sparql_all_individual_finite_graph))
for (s,p,o) in dbpedia.triples((None,None,None)):
    if (p not in predicates or
        s not in local_finite_graphs or
	unicode(p) == u'http://purl.org/dc/terms/subject' or
        (s,p,o) in local):
        continue
    print map(unicode,(s,p,o))

#########################################
# Local values disagreeing with dbpedia #
#########################################

print "\n=== Local values disagreeing with dbpedia === \n"
for (s,p,o) in local:
    if (s,p,None) in dbpedia and (s,p,o) not in dbpedia:
       print map(unicode,(s,p,o))

#################################
# Possible additions to dbpedia #
#################################

print "\n=== possible additions to dbpedia === \n"
for (s,p,o) in local:
    if 'sagemath.org' not in unicode(p) and (s,p,o) not in dbpedia:
       print map(unicode,(s,p,o))
