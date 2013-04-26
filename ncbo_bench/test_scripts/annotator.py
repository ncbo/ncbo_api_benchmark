import mechanize
import pdb
import time
import rest

REST_EPR = "localhost:9393"
APIKEY = ""
REST_EPR = "ncbo-stg-app-15"

ABSTRACTS_TEST_FILE = "./data/Pubmed_ET.txt"

def get_abstracts():
    abstracts = list()
    with file(ABSTRACTS_TEST_FILE,"r") as f_in:
        for line in f_in:
            abstract = line.split("\t")[4]
            if len(abstract.strip()):
                abstracts.append(abstract)
    return abstracts[1:]

class Transaction(object):

    def __init__(self):
        self.api = rest.Rest(REST_EPR)
        self.api.key = APIKEY
        self.abstracts = get_abstracts()
        self.abstract_index = 0
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
            text = self.abstracts[self.abstract_index]
            #for level in [0,2,4,8,16]:
            #for level in [0,2,4]:
            for level in [0]:
                ontologies = self.sample('annotator_%s'%level,lambda: self.api.annotate(text,level))
        except Exception, exc:
            print exc
        self.abstract_index += 1

if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
