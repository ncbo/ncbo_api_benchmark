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

class MappingsBenchmark(object):

    def __init__(self,client):
        self.client = client
        self.errors = StringIO.StringIO()

    def run(self):
        onts = self.client.get_all_ontologies()
        acronym = map(lambda x: x["acronym"], onts)

        random.shuffle(acronyms)
        for x in range(30):
            stats = self.client.mapping_stats()

        for x in range(3):
            random.shuffle(acronyms)
            for ont in acronyms:
                stats = self.client.mapping_stats_ontology(ont)
                maps = self.client.mappings_for_ontology(ont)
            
        use_onts = ["SNOMEDCT","HINO", "NDDF","VO","BIOMODELS","NCIT","BRO","PHARE"]
        for acronym in use_onts:
            classes = []

            #random classes to call mappings
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
                    self.client.mappings_for_class(acronym,cls["@id"])
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

    benchmark.link(api.Rest.mapping_stats,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.mapping_stats_ontology,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.mappings_for_ontology,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.mappings_for_class,subgroups=query_debug,data=request_path)

    api_key = os.environ["NCBO_API_KEY"]
    client = api.Rest(epr,key=api_key)
    clsb = MappingsBenchmark(client)
    scr = ezbench.report.ShowThread(benchmark)
    scr.start()
    clsb.run(use_onts=None)
    scr.end()
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
    print clsb.errors.getvalue()



