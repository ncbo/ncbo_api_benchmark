import sys
import urllib,urllib2
import traceback
import pdb
import time
import json
import os
import subprocess

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
    def __init__(self,epr,api_key=None):
        self.epr = "http://" + epr
        self.api_key = api_key
        self.history = []

    def update(self,u):
        return update4s(u,self.epr + "/update/",api_key=self.api_key)

    def query(self,x,soft_limit=-1,parse=True):
        self.history.append(x)
        o=query(PREFIXES+x,self.epr + "/sparql/",f='application/json',api_key=self.api_key,soft_limit=soft_limit)
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
    for sol in j["results"]["bindings"]:
        sols.append(sol2dict(sol))
    return sols

def query(q,epr,f='application/json',api_key=None,soft_limit=-1,rules="NONE"):
    try:
        params = {'query': q}
        if api_key:
            print "submitting apikey with query", api_key
            params["apikey"]=api_key
        else:
            pass
            #params["apikey"]=API_KEY_ADMIN
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

def update4s(update,epr,api_key=None):
    try:
        p = {'update': update.encode("utf-8")}
        if api_key:
            p["apikey"] = api_key
        params = urllib.urlencode(p)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(epr,params)
        request.get_method = lambda: 'POST'
        url = opener.open(request)
        return url.read()
    except Exception, e:
        traceback.print_exc(file=sys.stdout)
        raise e
