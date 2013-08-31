import pdb
import time
import api
import sys
import os
import ezbench
import json
import random

class GraphWritterBenchmark(object):

    def __init__(self,client):
        self.client = client

    def run(self):
        graph = "http://data.bioportal.org/benchmark/graph/go"
        f = "./data/NCITNCBO_ecxb.nt"
        f = "./data/go_ecxb.nt"
        #f = "./data/go.nt"
        ctype = "application/x-turtle" #"application/rdf+xml"
        with file(f,"r") as data:
            triples = data.read()
            self.client.append_triples(triples,graph,ctype)
        #"""SELECT (count(?s) as ?c) WHERE { GRAPH <http://data.bioportal.org/benchmark/graph/go> { ?s a ?o }}"""
        self.client.delete_graph(graph)

if __name__ == '__main__':
    epr = sys.argv[1]
    print "Using SPARQL %s ..."%epr

    benchmark = ezbench.Benchmark()
    benchmark.link(api.SPARQL.delete_graph)
    benchmark.link(api.SPARQL.append_triples)
    benchmark.link(api.SPARQL.update)

    client = api.SPARQL(epr)
    gw = GraphWritterBenchmark(client)
    gw.run()
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
