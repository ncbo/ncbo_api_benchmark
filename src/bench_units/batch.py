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

ONT_URI = "http://data.bioontology.org/ontologies/%s"
class BatchBenchmark(object):

    def __init__(self,client):
        self.client = client
        self.errors = StringIO.StringIO()

    def run(self):
        use_onts = ["SNOMEDCT","HINO", "NDDF","VO","BIOMODELS","NCIT","BRO","PHARE"]
        use_onts = ["SNOMEDCT","BIOMODELS","NCIT","NDDF"]
        classes = []
        for acronym in use_onts:
            ont_data = self.client.get_ontology(acronym)
            roots = self.client.get_roots(acronym)
            roots = json.loads(roots)
            page = self.client.get_classes(acronym,include="prefLabel")
            page = json.loads(page)
            classes.extend(map(lambda x: {"class" : x["@id"] , "ontology" : ONT_URI%acronym},
                                page["collection"]))
            all_pages = range(2,page["pageCount"]+1)
            random.shuffle(all_pages)
            count = 0
            while count < 200 and len(all_pages) > 0:
                pagen = all_pages.pop(0)
                page = self.client.get_classes(acronym,page=pagen,size=100)
                page = json.loads(page)
                classes.extend(map(lambda x: {"class" : x["@id"] , "ontology" : ONT_URI%acronym},
                                page["collection"]))
                count += 1

            classes.extend(map(lambda x: {"class" : x["@id"] , "ontology" : ONT_URI%acronym},
                                roots))
            random.shuffle(classes)

        for x in range(15):
            for y in range(2):
                collection = []
                for x in range(10):
                    collection.append(classes.pop(0))
                self.client.batch_10(collection)
                collection = []
                for x in range(50):
                    collection.append(classes.pop(0))
                self.client.batch_50(collection)
            collection = []
            for x in range(100):
                collection.append(classes.pop(0))
            self.client.batch_100(collection)
            collection = []
            for x in range(500):
                collection.append(classes.pop(0))
            self.client.batch_500(collection)

if __name__ == '__main__':
    epr = sys.argv[1]

    print "Using %s ..."%epr
    benchmark = ezbench.Benchmark()

    def query_debug(api):
        return api.last_query_info()
    def request_path(api):
        return api.last_request_path

    benchmark.link(api.Rest.batch_10,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.batch_50,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.batch_100,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.batch_500,subgroups=query_debug,data=request_path)

    api_key = os.environ["NCBO_API_KEY"]
    client = api.Rest(epr,key=api_key)
    clsb = BatchBenchmark(client)
    scr = ezbench.report.ShowThread(benchmark)
    scr.start()
    clsb.run()
    scr.end()
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
    print clsb.errors.getvalue()



