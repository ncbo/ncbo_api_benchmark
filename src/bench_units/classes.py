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

class ClassesBenchmark(object):

    def __init__(self,client):
        self.client = client
        self.errors = StringIO.StringIO()

    def run(self,use_onts=None):
        if use_onts == None:
            #errors for roots in NIFSTD and NCIT ICPC2P
            use_onts = ["BRO"]
            #use_onts = ["SNOMEDCT","HINO", "NDDF","VO","BIOMODELS","NCIT","BRO","PHARE"]
        for acronym in use_onts:
            ont_data = self.client.get_ontology(acronym)
            roots = self.client.get_roots(acronym)
            roots = json.loads(roots)
            classes = []
            page = self.client.get_classes(acronym)
            page = json.loads(page)
            classes.extend(page["collection"])
            all_pages = range(2,page["pageCount"]+1)
            random.shuffle(all_pages)
            count = 0
            while count < 5 and len(all_pages) > 0:
                pagen = all_pages.pop(0)
                page = self.client.get_classes(acronym,page=pagen)
                page = json.loads(page)
                classes.extend(page["collection"])
                count += 1

            random.shuffle(classes)
            classes = roots + classes
            count = 0
            while count < 20 and len(classes) > 0:
                count += 1
                cls = classes.pop(0)
                try:
                    self.client.get_class(acronym,cls["@id"])
                    self.client.get_tree(acronym,cls["@id"])
                    if count % 2 == 0:
                        if count % 4 == 0:
                            self.client.get_descendants(acronym,cls["@id"])
                            self.client.get_ancestors(acronym,cls["@id"])
                        self.client.get_parents(acronym,cls["@id"])
                        self.client.get_children(acronym,cls["@id"])
                except Exception, e:
                    self.errors.write("error retrieving %s"%cls["@id"])
                    traceback.print_exc(file=self.errors)

            random.shuffle(classes)
            count = 0
            while count < 40 and len(classes) > 0: 
                try:
                    count += 1
                    cls = classes.pop(0)
                    self.client.get_tree(acronym,cls["@id"])
                    self.client.get_class(acronym,cls["@id"])
                    if count % 2 == 0:
                        if count % 4 == 0:
                            self.client.get_descendants(acronym,cls["@id"])
                            self.client.get_ancestors(acronym,cls["@id"])
                        self.client.get_parents(acronym,cls["@id"])
                        self.client.get_children(acronym,cls["@id"])
                except Exception, e:
                    self.errors.write("error retrieving %s"%cls["@id"])
                    traceback.print_exc(file=self.errors)

                  

if __name__ == '__main__':
    epr = sys.argv[1]

    print "Using %s ..."%epr
    benchmark = ezbench.Benchmark()

    def query_debug(api):
        return api.last_query_info()
    def request_path(api):
        return api.last_request_path

    benchmark.link(api.Rest.get_classes,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_class,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_roots,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_tree,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_children,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_descendants,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_ancestors,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_parents,subgroups=query_debug,data=request_path)
    api_key = os.environ["NCBO_API_KEY"]
    client = api.Rest(epr,key=api_key)
    clsb = ClassesBenchmark(client)
    scr = ezbench.report.ShowThread(benchmark)
    scr.start()
    clsb.run(use_onts=None)
    scr.end()
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
    print clsb.errors.getvalue()



