import mechanize
import pdb
import time
import rest

APIKEY = ""
REST_EPR = "ncbo-stg-app-15:80"
REST_EPR = "localhost:9393"

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
            classes_response = self.sample('classes_page',lambda: self.api.get_classes("SNOMEDCT"))
            #classes = json.loads(classes_response)
        except Exception, exc:
            print exc

if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
