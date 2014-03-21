import pdb
import time
import api
import sys
import os
import ezbench
import json
import random
import traceback
import StringIO

ABSTRACTS_TEST_FILE = "./data/Pubmed_ET.txt"

def get_abstracts():
    abstracts = list()
    with file(ABSTRACTS_TEST_FILE,"r") as f_in:
        for line in f_in:
            abstract = line.split("\t")[4]
            if len(abstract.strip()):
                abstracts.append(abstract)
    return abstracts[1:]

class AnnotatorBenchmark(object):

    def __init__(self,client):
        self.client = client
        self.errors = StringIO.StringIO()
        print "parsing abstracts ..."
        self.abstracts = get_abstracts()
        print "abstracts parsed"


    def run(self):
        try:
            for i in range(len(self.abstracts)):
                abst = self.abstracts[i]
                t0 = time.time()
                print abst
                response = self.client.annotate(abst)
                print "response in %.3f"%(time.time()-t0)
                #self.client.annotate_with_mappings(acronym,abst)
                #self.client.annotate_with_hierarchy(acronym,abst)
                #self.client.annotate_with_mappings_hiearchies(acronym,abst)
        except Exception, e:
            self.errors.write("error annotating abstract %d"%i)
            traceback.print_exc(file=self.errors)


if __name__ == '__main__':
    epr = sys.argv[1]

    print "Using %s ..."%epr
    benchmark = ezbench.Benchmark()

    def query_debug(api):
        return api.last_query_info()
    def request_path(api):
        return api.last_request_path

    benchmark.link(api.Rest.annotate,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.annotate_with_hierarchy,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.annotate_with_mappings,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.annotate_with_mappings_hiearchies,
            subgroups=query_debug,data=request_path)

    api_key = os.environ["NCBO_API_KEY"]
    client = api.Rest(epr,key=api_key)
    clsb = AnnotatorBenchmark(client)
    #scr = ezbench.report.ShowThread(benchmark)
    #scr.start()
    print "running benchmark"
    clsb.run()
    #scr.end()
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
    print clsb.errors.getvalue()
