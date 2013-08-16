import pdb
import time
import api
import sys
import os
import ezbench
import json
import random

class ClassesBenchmark(object):

    def __init__(self,client):
        self.client = client

    def run(self,use_onts=None):
        if use_onts == None:
            use_onts = ["BRO","NIFSTD","ICPC2P","BIOMODELS","PHARE","HINO","NDDF","VO"]
        for acronym in use_onts:
            ont_data = self.client.get_ontology(acronym)
            roots = self.client.get_roots(acronym)
            roots = json.loads(roots)
            classes = []
            page = self.client.get_classes(acronym)
            page = json.loads(page)
            classes.extend(page)
            all_pages = range(2,page["pageCount"]+1)
            random.shuffle(all_pages)
            count = 0
            while count < 3 && len(all_pages) > 0:
                pagen = all_pages.pop(0)
                page = self.client.get_classes(acronym,page=pagen)
                page = json.loads(page)
                classes.extend(page)
                count += 1
            random.shuffle(classes)
            count = 0
            while count < 200 && len(classes) > 0:
                cls = classes.pop(0)
                


if __name__ == '__main__':
    epr = sys.argv[1]
    print "Using %s ..."%epr
    benchmark = ezbench.Benchmark()

    def query_debug(api):
        return api.last_query_info()
    def request_path(api):
        return api.last_request_path

    benchmark.link(api.Rest.get_classes,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_roots,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_tree,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_children,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_descendants,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_ancestors,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_par,subgroups=query_debug,data=request_path)
    api_key = os.environ["NCBO_API_KEY"]
    client = api.Rest(epr,key=api_key)
    clsb = ClassesBenchmark(client)
    clsb.run(use_onts=["BRO"])
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
