import pdb
import time
import api
import sys
import os
import ezbench
import json
import random
t0 = time.time()
import gzip
import Queue
import threading
from os import listdir
from os.path import isfile, join
import getopt

GRAPH_UPDATE_ID = "http://data.bioportal.org/benchmark/graph/go"

class SparqlQueryBenchmark(object):

    def __init__(self,client,log_queries,n_queries,n_threads,data_folder,do_writes):
        self.client = client
        self.log_queries = log_queries
        self.n_queries = n_queries
        self.n_threads = n_threads
        self.load_query_log()
        self.data_folder = data_folder
        self.do_writes = do_writes
        files = [ f for f in listdir(self.data_folder) if isfile(join(self.data_folder,f)) ]
        files = map(lambda x: join(self.data_folder,x),
                    filter(lambda x: x.endswith("nt.gzip"),files))
        self.write_files = sorted(files,key=lambda x: os.stat(x).st_size,reverse=False)
        self.write_files = self.write_files[0:1]

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
                self.client.query(query_string,parse=False)
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

    def write_graphs(self):
        while not self.queue.empty():
            for f in self.write_files:
                if not self.queue.empty():
                    print "parsing ", f,
                    sys.stdout.flush()
                    ctype = "application/x-turtle" #"application/rdf+xml"
                    with gzip.open(f) as data:
                        triples = data.read()
                        print "[file read]",
                        sys.stdout.flush()
                        t0 = time.time()
                        self.client.append_triples(triples,GRAPH_UPDATE_ID,ctype)
                        print "[done in %.2f sec]"%(time.time()-t0)
                        sys.stdout.flush()
                    data.close()
                    print "deleting graph ...",
                    sys.stdout.flush()
                    t0 = time.time()
                    self.client.delete_graph(GRAPH_UPDATE_ID)
                    print "[done in %.2f sec]"%(time.time()-t0)
                    sys.stdout.flush()

    def run(self):
        if self.do_writes:
            write_thread = threading.Thread(target=self.write_graphs)
            write_thread.start()
        self.run_queries()
        if self.do_writes:
            write_thread.join()
    

if __name__ == '__main__':
    optlist, args = getopt.getopt(sys.argv[1:], 'h:wt:n:d:l:')
    optlist = dict(optlist)
    epr = optlist["-h"]
    log_sparql = optlist["-l"]
    n_queries = int(optlist["-n"])
    n_threads = int(optlist["-t"])
    data_folder = "./data"
    do_writes = "-w" in optlist
    print "Using SPARQL %s"%epr
    print "Using log file %s"%log_sparql
    print "#queries %d #threads %d"%(n_queries,n_threads)
    print "Do writes ",do_writes
    print "Cleaning previous writes ...",
    sys.stdout.flush()
    client = api.SPARQL(epr)
    client.delete_graph(GRAPH_UPDATE_ID)
    print "[Done]"
    sys.stdout.flush()

    benchmark = ezbench.Benchmark()
    benchmark.link(api.SPARQL.query)
    if do_writes:
        benchmark.link(api.SPARQL.delete_graph)
        benchmark.link(api.SPARQL.append_triples)

    gw = SparqlQueryBenchmark(client,log_sparql,n_queries,n_threads,data_folder,do_writes)
    gw.run()
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
