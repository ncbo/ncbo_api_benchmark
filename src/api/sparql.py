import sys
import urllib,urllib2
import traceback
import pdb
import time
import json
import os

PREFIXES = """PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dc:   <http://purl.org/dc/elements/1.1/>
PREFIX dct:  <http://purl.org/dc/terms/>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX bio:  <http://purl.org/vocab/bio/0.1/>
PREFIX meta: <http://bioportal.bioontology.org/metadata/def/>
PREFIX graphs: <http://purl.bioontology.org/def/graphs/>
PREFIX omv: <http://omv.ontoware.org/2005/05/ontology#>
PREFIX maps: <http://protege.stanford.edu/ontologies/mappings/mappings.rdfs#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX umls: <http://bioportal.bioontology.org/ontologies/umls/>
"""

class SPARQL:
    def __init__(self,epr):
        self.epr = "http://" + epr

    def delete_graph(self,g):
        try:
            response = delete_graph(self.epr,g)
        except Exception, e:
            print "error deleting graph"
            print e
        #self.update("DROP GRAPH <%s>"%g)

    def update(self,u):
        return update4s(u,self.epr + "/update/")

    def append_triples(self,data,graph,contenttype):
        return append_triples(data,self.epr + "/data/",graph,contenttype)

    def query(self,x,soft_limit=-1,parse=True):
        o=query(PREFIXES+x,self.epr + "/sparql/",f='application/json',soft_limit=soft_limit)
        if parse:
            return parse_json_result(o)
        else:
            return o

def sol2dict(sol):
    d=dict()
    for v in sol:
        if "value" in sol[v]:
            d[v]=sol[v]["value"]
        else:
            d[v]=None

    return d

def parse_json_result(res):
    j=json.loads(res)
    sols = []
    if "results" not in j and "boolean" in j:
        return j["boolean"]
    for sol in j["results"]["bindings"]:
        sols.append(sol2dict(sol))
    return sols

def query(q,epr,f='application/json',soft_limit=-1,rules="NONE"):
    try:
        params = {'query': q}
        params["soft-limit"]=str(soft_limit)
        params["rules"]=rules
        params = urllib.urlencode(params)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(epr+'?'+params)
        request.add_header('Accept', f)
        request.get_method = lambda: 'GET'
        url = opener.open(request)
        content = url.read()
        url.close()
        opener.close()
        return content
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        raise e

def delete_graph(epr,graph):
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        params = urllib.urlencode({})
        request = urllib2.Request("%s/data/%s"%(epr,graph),params)
        request.get_method = lambda: 'DELETE'
        url = opener.open(request)
        return url.read()
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        raise e

def update4s(update,epr):
    try:
        p = {'update': update.encode("utf-8")}
        params = urllib.urlencode(p)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(epr,params)
        request.get_method = lambda: 'POST'
        url = opener.open(request)
        return url.read()
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        raise e

def append_triples(data,epr,graph,contenttype):
    try:
        p = {'graph': graph,'data': data,'mime-type' : contenttype }
        params = urllib.urlencode(p)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(epr,params)
        request.get_method = lambda: 'POST'
        url = opener.open(request)
        return url.read()
    except Exception, e:
        raise e
