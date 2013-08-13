import mechanize
import pdb
import time
import rest

APIKEY = ""
REST_EPR = "localhost:9393"
REST_EPR = "ncbo-stg-app-15:80"

class Transaction(object):

    def __init__(self):
        self.api = rest.Rest(REST_EPR)
        self.api.key = APIKEY
        pass

    def sample(self,group,action):
        if group not in self.custom_timers:
            self.custom_timers[group]=[] 
        st = time.time()
        res = action()
        et = time.time()
        self.custom_timers[group].append((st,et))
        return res

    def run(self):
        #run clean timers
        self.start_time = time.time()
        self.custom_timers = dict()

        try:
            ontologies = self.sample('all_ontologies',lambda: self.api.get_all_ontologies())
        except Exception, exc:
            print exc

        #TODO benchamrk include all.

        #for ont in ontologies:
        #    start_timer = time.time()
        #    ont = self.api.get_ontology(ont['acronym'])
        #    latency = time.time() - start_timer
        #    self.custom_timers['single_ontology'] = latency
        #    start_timer = time.time()
        #    ont = self.api.get_ontology(ont['acronym'],include="all")
        #    latency = time.time() - start_timer
        #    self.custom_timers['single_ontology_include_all'] = latency


if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers

