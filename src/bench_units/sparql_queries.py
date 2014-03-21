import pdb
import time
import api
import sys
import os
import ezbench
import json
import random
import gzip
import Queue
import threading

GRAPH_UPDATE_ID = "http://data.bioportal.org/benchmark/graph/go"

class SparqlQueryBenchmark(object):

    def __init__(self,client,log_queries,n_queries,n_threads):
        self.client = client
        self.log_queries = log_queries
        self.n_queries = n_queries
        self.n_threads = n_threads
        self.load_query_log()

    def load_query_log(self):
        data = gzip.open(self.log_queries)
        current = []
        queries = []
        print "Parsing query log ..."
        for line in data:
            line = line.strip("\n")
            if line.startswith("####"):
                if len(current) > 0:
                    queries.append("\n".join(current))
                    current = []
            else:
                current.append(line)
            if len(queries) >= self.n_queries:
                break
        data.close()
        self.queue = Queue.Queue()
        for q in queries:
            self.queue.put(q)
        print "Queue loaded with %d queries"%(self.queue.qsize())

    def run_queue_query(self):
        while True:
            try:
                query_string = self.queue.get(False)
                self.client.query(query_string)
            except Queue.Empty, exc:
                return

    def run_queries(self):
        threads = []
        for x in range(self.n_threads):
            t = threading.Thread(target=self.run_queue_query)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

    def run(self):
        self.run_queries()
    
    def write(self):
        f = "./data/NCITNCBO_ecxb.nt"
        f = "./data/go_ecxb.nt"
        #f = "./data/go.nt"
        ctype = "application/x-turtle" #"application/rdf+xml"
        with file(f,"r") as data:
            triples = data.read()
            self.client.append_triples(triples,graph,ctype)
        #"""SELECT (count(?s) as ?c) WHERE { GRAPH <http://data.bioportal.org/benchmark/graph/go> { ?s a ?o }}"""
        self.client.delete_graph(GRAPH_UPDATE_ID)

if __name__ == '__main__':
    epr = sys.argv[1]
    log_sparql = sys.argv[2]
    n_queries = 10000
    n_threads = 8
    if len(sys.argv) > 3:
        n_queries = int(sys.argv[3])
    if len(sys.argv) > 4:
        n_threads = int(sys.argv[4])
    print "Using SPARQL %s"%epr
    print "Using log file %s"%log_sparql
    print "#queries %d #threads %d"%(n_queries,n_threads)

    benchmark = ezbench.Benchmark()
    #benchmark.link(api.SPARQL.delete_graph)
    #benchmark.link(api.SPARQL.append_triples)
    #benchmark.link(api.SPARQL.update)
    benchmark.link(api.SPARQL.query)

    client = api.SPARQL(epr)
    gw = SparqlQueryBenchmark(client,log_sparql,n_queries,n_threads)
    gw.run()
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
