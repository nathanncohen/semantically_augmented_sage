r"""
A dbpedia entry is an object, its properties are methods. The data is queried
as you explore the objects.

Some objects have a .sage() method to obtain the actual Sage object.

EXAMPLE::

    sage: g = DbpediaEntry("http://dbpedia.org/resource/Petersen_graph")
    sage: g.girth()
    5
    sage: g.properties()
    [DBpedia entry: Cubic graph,
     DBpedia entry: Snark (graph theory),
     DBpedia entry: Strongly regular graph,
     DBpedia entry: Distance-transitive graph]

    sage: g.subject()
    [DBpedia entry: Category of Individual graphs,
     DBpedia entry: Category of Regular graphs]

    sage: individual = _[0]
    sage: individual.elements()
    [DBpedia entry: BiggsSmith graph,
     DBpedia entry: TutteCoxeter graph,
     DBpedia entry: Bull graph,
     DBpedia entry: Double-star snark,
     DBpedia entry: Truncated tetrahedron,
     DBpedia entry: TutteCoxeter graph,
     DBpedia entry: Tutte 12-cage,
     ...
"""
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF, TURTLE
from collections import defaultdict
import rdflib
from rdflib import URIRef, Namespace

import logging
logging.getLogger().setLevel(logging.ERROR)

if 'local_data' not in locals():
    local_data = rdflib.Graph()

if 'translation_db' not in locals():
    translation_db=rdflib.Graph()
    translation_db.parse("translation.ttl",format="n3")

rdfs    = Namespace("http://www.w3.org/2000/01/rdf-schema#")
sagens  = Namespace("http://www.sagemath.org/#")
dbpedia = Namespace("http://dbpedia.org/resource/")
rdf     = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
dbpprop = Namespace("http://dbpedia.org/property/")
dcterms = Namespace("http://purl.org/dc/terms/")
skos    = Namespace("http://www.w3.org/2004/02/skos/core#")

# If any (?s ?p ?o) gets added to local_data, then ALL (?s * *) must be added!
# All or none.

@cached_function
def add_to_local_db(request):
    r"""
    Add to the local db the result of a given SPARQL query
    """
    global local_data
    sparql = SPARQLWrapper("http://live.dbpedia.org/sparql")
    sparql.setQuery(request)
    sparql.setReturnFormat(RDF)
    q = sparql.query()
    sage.q = q
    q = q.convert()
    local_data = local_data+q

def get_entry_from_dbpedia(URI):
    r"""
    Fetch all triples (<URI>,p,o)
    """
    if rdflib.URIRef(URI) in local_data.subjects():
        return
    add_to_local_db(r"""
    construct {
       <URI> ?p ?o.
       }
    where {
           <URI> ?p ?o.
     }
    """.replace("URI",URI))

def get_category_elements(URI):
    r"""
    Fetch all triples (?s ?p ?o) where ?s has category <URI>
    """
    add_to_local_db(r"""
    construct {
       ?s dcterms:subject <URI>.
       ?s ?p ?o.
       }
    where {
       ?s dcterms:subject/skos:broader* <URI>.
       ?s ?p ?o.
     }
    """.replace("URI",URI))

def get_category_subcategories(URI):
    r"""
    Fetch all triples (?s ?p ?o) where ?s has supercategory <URI>
    """
    add_to_local_db(r"""
    construct {
       ?s skos:broader <URI>.
       ?s ?p ?o.
       }
    where {
       ?s skos:broader <URI>.
       ?s ?p ?o.
     }
    """.replace("URI",URI))

def value_to_sage(v):
    r"""
    Convert a db value into something Sage understands.
    """
    if isinstance(v,rdflib.URIRef):
        return DbpediaEntry(v)
    if v.isnumeric():
        return eval(str(v))
    else:
        return v.toPython()

class DbpediaEntry:
    r"""
    Represents an entry in DBpedia
    """
    def __init__(self,URI):
        if isinstance(URI,rdflib.URIRef):
            URI = URI.toPython()
        get_entry_from_dbpedia(URI)
        self._uriref = rdflib.URIRef(URI)
        d = defaultdict(list)
        for s,p,o in local_data.triples((self._uriref,None,None)):
            p = p.encode('ascii','ignore').split('/')[-1].split('#')[-1]
            d[p].append(o)
            setattr(self,p,self._return_function(p))

        for _,_,o in translation_db.triples((self._uriref,sagens.build,None)):
            setattr(self,'sage', lambda : eval(o))

        self._d = d
        self._is_category = ((self._uriref, rdf.type, skos.Concept)
                             in local_data)

    def _return_function(self,param):
        r"""
        Helper function returning a dbpedia value
        """
        def the_function():
            data = [value_to_sage(x) for x in self._d[param]]
            return data[0] if (isinstance(data,list) and len(data)==1) else data

        return the_function

    def __repr__(self):
        r"""
        Return a 'nice' representation of the object
        """
        try:
            label = self.label()
        except:
            label = self._uriref.toPython()

        if isinstance(label,list):
            label = label[0]

        label = label.encode('ascii','ignore')
        return ("DBpedia entry: "+
                ("Category of " if self._is_category else "")+
                label)

    def elements(self):
        r"""
        Return all elements in the category represented by self.

        Pre-loads all the elements in the db.
        """
        if not self._is_category:
            raise TypeError("This is not a Wikipedia category.")
        get_category_elements(self._uriref.toPython())
        return [DbpediaEntry(s.toPython()) for s,_,_ in
                local_data.triples((None,dcterms.subject,self._uriref))]

    def subcategories(self):
        r"""
        Return all the subcategories of self

        Pre-loads all subcategories in the db.
        """
        if not self._is_category:
            raise TypeError("This is not a Wikipedia category.")
        get_category_subcategories(self._uriref.toPython())
        return [DbpediaEntry(s.toPython()) for s,_,_ in
                local_data.triples((None,skos.broader,self._uriref))]

g = DbpediaEntry("http://dbpedia.org/resource/Petersen_graph")
