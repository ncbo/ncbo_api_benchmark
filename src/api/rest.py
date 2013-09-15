import urllib
import urllib2
import httplib
import mimetypes
import json
import pdb
import multipart

class Rest:
    def __init__(self,host,key=None):
        self.host = host
        self.key = key
        self.user_id = None
        self.record_on_file = None
        self.proxy_host = None
        self.proxy_port = None
        self.last_headers = None
        self.last_request_path = None

    def last_query_info(self):
        trace_headers = filter(lambda x: x.startswith("ncbo-time-goo-"), self.last_headers)
        skip_part = len("ncbo-time-goo-")
        trace_headers = map(lambda x: x[skip_part:].strip().split(": "), trace_headers)
        trace_headers = map(lambda x: (x[0],float(x[1])),trace_headers)
        return dict(trace_headers)

    def ez_data(self):
        return self.last_request_path

    def ez_sub(self):
        return self.last_query_info()

    def last_request_path(self):
        return self.last_request_path

    def use_proxy(self,host,port):
        self.proxy_host = host
        self.proxy_port = port

    def request(self, route, doc, method="GET", files=None):

        if self.key:
            doc["apikey"] = self.key

        if files:
            request = multipart.request(self.host, route, doc.items(), files)
            errcode, errmsg, headers = request.getreply()
            data = request.file.read()
            if errcode / 100 == 2:
               return data
            raise Exception("HTTP error status %s call %s response %s"%(errcode,route,data))
        else:
            conn = None
            if not self.proxy_host:
                conn = httplib.HTTPConnection(self.host)
            else:
                conn = httplib.HTTPConnection(self.proxy_host,self.proxy_port)

            params = urllib.urlencode(doc)
            headers = {}
            if method == "PUT" or method == "POST":
                headers = {"Content-type": "application/x-www-form-urlencoded", 
                          "Accept": "application/json"}
                if self.proxy_host:
                    route = "http://" + self.host + route
                conn.request(method, route, params, headers)
                self.last_request_path = None
            else:
                call =  route + "?" + params
                if self.record_on_file:
                    self.record_on_file.write("GET %s\n"%(call))
                    self.record_on_file.flush()
                if self.proxy_host:
                    call = "http://" + self.host + call
                conn.request(method, call, "", headers)
                self.last_request_path = call
            response = conn.getresponse()
            status, reason = response.status, response.reason
            self.last_headers = response.msg.headers
            data = response.read()
            if status / 100 == 2:
                return data
            raise Exception("HTTP error status %s call %s response %s"%(status,route,data))

    def last_internal_times(self):
        if self.last_headers:
            ncbo_headers = filter(lambda x: x.startswith("ncbo-time"),self.last_headers)
            ncbo_headers = map(lambda x: x.split(":"), ncbo_headers)
            ncbo_headers = map(lambda x: (x[0].strip(),float(x[1].strip())), ncbo_headers)
            return ncbo_headers
        return []

    def post(self, route, doc,files=None):
        return self.request(route, doc, method="POST",files=files)

    def put(self, route, doc,files=None):
        return self.request(route, doc, method="PUT",files=files)

    def get(self,route, params):
        return self.request(route, params, "GET")

    def start_recording(self,on_file):
        self.record_on_file = open(on_file, "w")

    def stop_recording(self):
        self.record_on_file.close()
        self.record_on_file = None

    def get_all_users(self):
        route = "/users"
        data = { "apikey" : self.key }
        return self.get(route,data)

    def get_user(self,user_id):
        route = "/users/%s"%urllib.quote(user_id)
        data = { "apikey" : self.key }
        return self.get(route,data)

    def get_all_ontologies(self):
        route = "/ontologies"
        data = { "apikey" : self.key }
        return self.get(route,data)

    def create_user(self,name,email,password):
        doc = { "email" : email, "password" : password }
        route = "/users/%s"%name
        return self.put(route, doc)

    def create_ontology_submission(self,ontology):
        data_body = None
        data_file = open(ontology["local_path"],"r")
        ontology["administeredBy"] = self.user_id
        ontology["apikey"] = self.key
        ontology["name"] = "ontology name in %s"%ontology["acronym"]
        route = "/ontologies/%s"%ontology["acronym"]
        try:
            response = json.loads(self.put(route,ontology))
        except urllib2.HTTPError, e:
            raise e

        files = [("ontology_data_0", data_file)]
        route_submission = "/ontologies/%s/submissions"%ontology["acronym"]
        try:
            response = json.loads(self.post(route_submission,ontology,files=files))
        except urllib2.HTTPError, e:
            raise e
        return response

    def parse_submission(self, acr, submission_id):
        data = { "apikey" : self.key , "ontology_submission_id" : submission_id}
        route = "/ontologies/%s/submissions/%s/parse"%(acr,submission_id)
        return self.post(route, data)

    def get_ontology(self, acr, submission_id=None,include=None):
        data = { "apikey" : self.key }
        if submission_id:
            data["ontology_submission_id"] = submission_id
        if include:
            data["include"] = include
        route = "/ontologies/%s"%acr
        return self.get(route,data)

    def get_ontology_submission(self, acr, submission_id=None,include=None):
        data = { "apikey" : self.key } 
        if include:
            data["include"]=include
        route = None
        if submission_id:
            route = "/ontologies/%s/submissions/%s"%(acr,submission_id)
        else:
            route = "/ontologies/%s/latest_submission"%acr
        return self.get(route,data)

    def get_roots(self, acr,
            include="prefLabel,definition,synonym,childrenCount,children"):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/classes/roots"%(acr)
        if include:
            data["include"]=include
        return self.get(route,data)

    def get_children(self, acr, cls_id):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/classes/%s/children"%(acr,urllib.quote(cls_id,''))
        return self.get(route,data)

    def get_classes(self, acr, page=1,size=None,
                    include="prefLabel,definition,synonym,childrenCount,children"):
        data = { "apikey" : self.key , "page" : page ,
                 "include" : include }
        if size != None:
            data["size"] = size
        route = "/ontologies/%s/classes"%(acr)
        if include:
            data["include"]=include
        return self.get(route,data)

    def get_tree(self, acr, cls_id,
                 include="prefLabel,definition,synonym,childrenCount,children"):
        data = { "apikey" : self.key, "include": include }
        route = "/ontologies/%s/classes/%s/tree"%(acr,urllib.quote(cls_id,''))
        return self.get(route,data)

    def get_descendants(self, acr, cls_id):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/classes/%s/descendants"%(acr,urllib.quote(cls_id,''))
        return self.get(route,data)

    def get_ancestors(self, acr, cls_id,
             include="prefLabel,definition,synonym,childrenCount"):
        data = { "apikey" : self.key ,"include": include }
        route = "/ontologies/%s/classes/%s/ancestors"%(acr,urllib.quote(cls_id,''))
        return self.get(route,data)

    def get_parents(self, acr, cls_id,
             include="prefLabel,definition,synonym,childrenCount"):
        data = { "apikey" : self.key ,"include": include }
        route = "/ontologies/%s/classes/%s/parents"%(acr,urllib.quote(cls_id,''))
        return self.get(route,data)

    def get_class(self, acr, cls_id,
             include="prefLabel,definition,synonym,properties,childrenCount,children"):
        data = { "apikey" : self.key ,"include": include }
        route = "/ontologies/%s/classes/%s"%(acr,urllib.quote(cls_id,''))
        return self.get(route,data)

    def annotate(self,text,max_level,mappings=None):
        data = { "apikey" : self.key, "text": text, "max_level": max_level, "no_context":"true" }
        if mappings:
            data["mappings"] = "all"
        route = "/annotator"
        return self.get(route,data)

    def mapping_stats(self):
        data = { "apikey" : self.key  }
        route = "/mappings/statistics/ontologies/"
        return self.get(route,data)

    def mapping_stats_ontology(self,ontology):
        data = { "apikey" : self.key  }
        route = "/mappings/statistics/ontologies/"
        route += ontology
        return self.get(route,data)

    def mappings_for_ontology(self, ontology, page = 1):
        data = { "apikey" : self.key, "page" : page, "pagesize": pagesize  }
        route = "ontologies/%s/mappings"%ontology
        return self.get(route,data)

    def mappings_for_class(self, ontology,class_id):
        data = { "apikey" : self.key  }
        class_id_encoded = urllib.quote(class_id,'')
        route = "/ontologies/%s/classes/%s/mappings"%(ontology,class_id_encoded)
        return self.get(route,data)

    def reviews(self,acr):
        data = { "apikey" : self.key  }
        route = "/ontologies/%s/reviews"%acr
        return self.get(route,data)

    def groups(self,acr):
        data = { "apikey" : self.key  }
        route = "/ontologies/%s/groups"%acr
        return self.get(route,data)

    def notes(self,acr):
        data = { "apikey" : self.key  }
        route = "/ontologies/%s/notes"%acr
        return self.get(route,data)

    def submissions(self,acr):
        data = { "apikey" : self.key  }
        route = "/ontologies/%s/submissions"%acr
        return self.get(route,data)

    def metrics(self,acr,submission):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/submissions/%s/metrics"%(acr,submissions)
        return self.get(route,data)



