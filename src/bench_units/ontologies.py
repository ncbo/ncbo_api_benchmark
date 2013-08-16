import pdb
import time
import api
import sys
import os
import ezbench
import json
import random

class OntologiesBenchmark(object):
    def __init__(self,client):
        self.client = client

    def run(self,n=10):
        ontologies = self.client.get_all_ontologies()
        ontologies = json.loads(ontologies)
        random.shuffle(ontologies)
        if n != None:
            ontologies=ontologies[:n]
        for ont in ontologies:
            acronym = ont["acronym"]
            ont_data = self.client.get_ontology(acronym)
            self.client.reviews(acronym)
            self.client.notes(acronym)
            self.client.groups(acronym)
            self.client.submissions(acronym)
            try:
                submission = self.client.get_ontology_submission(acronym)
            except:
                "ontology has no parsed submissions"
                continue

            submission = json.loads(submission)
            if "submissionId" not in submission:
                continue

            sid = submission["submissionId"]
            try:
                self.client.metrics(acronym,sid)
            except:
                pass

if __name__ == '__main__':
    epr = sys.argv[1]
    print "Using %s ..."%epr
    benchmark = ezbench.Benchmark()
    def query_debug(api):
        return api.last_query_info()
    def request_path(api):
        return api.last_request_path

    benchmark.link(api.Rest.get_all_ontologies,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_ontology,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.reviews,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.notes,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.groups,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.submissions,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.metrics,subgroups=query_debug,data=request_path)

    api_key = os.environ["NCBO_API_KEY"]
    client = api.Rest(epr,key=api_key)
    onts = OntologiesBenchmark(client)
    for x in range(20):
        print "running iteration %s"%x
        onts.run(n=10)
        onts.run(n=2)
        onts.run(n=2)
        onts.run(n=2)
    ezbench.report.show(benchmark)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
