from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF, TURTLE
from collections import defaultdict
import rdflib
from rdflib import URIRef

import logging
logging.getLogger().setLevel(logging.ERROR)

if 'local_data' not in locals():
    local_data = rdflib.Graph()

rdf_type = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")

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
       ?s <http://purl.org/dc/terms/subject> <URI>.
       ?s ?p ?o.
       }
    where {
       ?s <http://purl.org/dc/terms/subject> <URI>.
       ?s ?p ?o.
     }
    """.replace("URI",URI))

def get_category_subcategories(URI):
    r"""
    Fetch all triples (?s ?p ?o) where ?s has supercategory <URI>
    """
    add_to_local_db(r"""
    construct {
       ?s <http://www.w3.org/2004/02/skos/core#broader> <URI>.
       ?s ?p ?o.
       }
    where {
       ?s <http://www.w3.org/2004/02/skos/core#broader> <URI>.
       ?s ?p ?o.
     }
    """.replace("URI",URI))

class DbpediaEntry:
    r"""
    Represents an entry in DBpedia
    """
    def __init__(self,URI):
        get_entry_from_dbpedia(URI)
        self._uriref = rdflib.URIRef(URI)
        d = defaultdict(list)
        for s,p,o in local_data.triples((self._uriref,None,None)):
            p = p.encode('ascii','ignore').split('/')[-1].split('#')[-1]
            d[p].append(o)
            setattr(self,p,self._return_function(p))

        self._d = d
        self._is_category = ((self._uriref, rdf_type, URIRef("http://www.w3.org/2004/02/skos/core#Concept"))
                             in local_data)

    def _return_function(self,param):
        r"""
        Helper function returning a dbpedia value
        """
        def the_function():
            data = self._d[param]
            data = [DbpediaEntry(x.toPython()) if isinstance(x,rdflib.URIRef) else x.toPython()
                    for x in data]
            return data[0] if (isinstance(data,list) and len(data)==1) else data

        return the_function

    def __repr__(self):
        r"""
        Return a 'nice' representation of the object
        """
        label = self.label()
        if isinstance(label,list):
            if len(label) == 0:
                label = self._uriref.toPython()
            else:
                label = label[0]
        label = label.encode('ascii','ignore')
        return ("DBpedia entry: "+
                ("Category of " if self._is_category else "")+
                label)

    def elements(self):
        r"""
        Return all elements in the category represented by self
        """
        if not self._is_category:
            raise TypeError("This is not a Wikipedia category.")
        get_category_elements(self._uriref.toPython())
        return [DbpediaEntry(s.toPython()) for s,_,_ in
                local_data.triples((None,rdflib.URIRef("http://purl.org/dc/terms/subject"),self._uriref))]

    def subcategories(self):
        r"""
        Return all the subcategories of self
        """
        if not self._is_category:
            raise TypeError("This is not a Wikipedia category.")
        get_category_subcategories(self._uriref.toPython())
        return [DbpediaEntry(s.toPython()) for s,_,_ in
                local_data.triples((None,rdflib.URIRef("http://www.w3.org/2004/02/skos/core#broader"),self._uriref))]

    def sage(self):
        r"""
        Return the Sage function associated with self (if known/available).
        """
        translation_db=rdflib.Graph()
        translation_db.parse("graphs.ttl",format="n3")
        for _,_,o in translation_db.triples((self._uriref,rdflib.URIRef("http://www.sagemath.org/#build"),None)):
            return eval(o)
        raise RuntimeError("No translation found")

g = DbpediaEntry("http://dbpedia.org/resource/Petersen_graph")
