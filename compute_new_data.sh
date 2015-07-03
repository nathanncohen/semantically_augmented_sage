#!/bin/bash
#
# This script generates some code to add new data to the database. Its output is
# a bash script, that can be run on some other machine. You can also prune the
# computations that you actually want to run.

cat > /tmp/q << EOF
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix sage: <http://www.sagemath.org/#>
prefix dbpprop: <http://dbpedia.org/property/>

select ?guri ?puri ?o ?method ?n
where {
  GRAPH <$PWD/ontology.ttl> {
      ?puri sage:method ?method.
  }
  GRAPH <$PWD/graphs.ttl> {
      ?guri sage:build ?o.
      ?guri dbpprop:vertices ?n.
  }

  filter not exists {
      GRAPH <$PWD/graphs.ttl> {
          ?guri ?puri ?A.
      }
  }
} order by ?n
EOF
arq --namedGraph=$PWD/ontology.ttl --namedGraph=$PWD/graphs.ttl --query=/tmp/q --results=csv | tr -d '\015' > /tmp/q2
tail -n+2 /tmp/q2 | while read l; do
    uri="$(echo $l | cut -d , -f 1)"
    prop="$(echo $(echo $l | cut -d , -f 2))"
    cons="$(echo $(echo $l | cut -d , -f 3))"
    method="$(echo $(echo $l | cut -d , -f 4))"
    echo "echo \"<$uri> <$prop> \$(sage -c 'print $cons.$(echo $method)')\""
done
