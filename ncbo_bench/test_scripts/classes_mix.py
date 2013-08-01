import mechanize
import pdb
import time
import rest
import json

APIKEY = ""
REST_EPR = "ncbo-stg-app-15:80"
REST_EPR = "localhost:9393"

class Transaction(object):

    def __init__(self):
        self.api = rest.Rest(REST_EPR)
        self.api.key = APIKEY
        self.ontology = "NDFRT"
        self.pageno = 1
        self.size = 500
        self.roots = None


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
            if not self.roots:
                roots_response = self.sample('roots',
                    lambda: self.api.get_roots(
                        self.ontology,include="prefLabel,definition,synonym,childrenCount"))
                self.roots = json.loads(roots_response)
            classes_response = self.sample('classes_page',
                    lambda: self.api.get_classes(self.ontology,page=self.pageno,size=self.size))
            classes = json.loads(classes_response)
            if classes['nextPage']:
                self.pageno = classes['nextPage']
        except Exception, exc:
            print exc

if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers

