import urllib
import urllib2
import httplib
import mimetypes
import json
import pdb
import multipart

class Rest:
    def __init__(self,host):
        self.host = host
        self.key = None
        self.user_id = None
        self.record_on_file = None
        self.proxy_host = None
        self.proxy_port = None

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
                headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
                if self.proxy_host:
                    route = "http://" + self.host + route
                conn.request(method, route, params, headers)
            else:
                call =  route + "?" + params
                if self.record_on_file:
                    self.record_on_file.write("GET %s\n"%(call))
                    self.record_on_file.flush()
                if self.proxy_host:
                    call = "http://" + self.host + call
                conn.request(method, call, "", headers)
            response = conn.getresponse()
            status, reason = response.status, response.reason
            data = response.read()
            if status / 100 == 2:
                return data
            raise Exception("HTTP error status %s call %s response %s"%(status,route,data))

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

    def get_all_ontologies(self):
        route = "/ontologies"
        data = { "apikey" : self.key }
        return json.loads(self.get(route,data))

    def create_user(self,name,email,password):
        doc = { "email" : email, "password" : password }
        route = "/users/%s"%name
        response = json.loads(self.put(route, doc))
        return response["apikey"] if "apikey" in response else "bogus_api_key"

    def create_ontology_submission(self,ontology):
        data_body = None
        data_file = open(ontology["local_path"],"r")
        ontology["administeredBy"] = self.user_id
        ontology["apikey"] = self.key
        ontology["name"] = "ontology name in %s"%ontology["acronym"]
        route = "/ontologies/%s"%ontology["acronym"]
        try:
            response = json.loads(self.put(route,ontology,files=files))
            response = json.loads(self.put(route,ontology))
        except urllib2.HTTPError, e:

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
        response = self.post(route, data)
        return json.loads(response)

    def get_ontology(self, acr, submission_id):
        data = { "apikey" : self.key , "ontology_submission_id" : submission_id}
        route = "/ontologies/%s"%acr
        ontology = json.loads(self.get(route,data))
        return ontology

    def get_ontology_submission(self, acr, submission_id,include=None):
        data = { "apikey" : self.key , "ontology_submission_id" : submission_id}
        if include:
            data["include"]=include
        route = "/ontologies/%s/submissions/%s"%(acr,submission_id)
        data_back = json.loads(self.get(route,data))
        return data_back

    def get_roots(self, acr):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/classes/roots"%(acr)
        return json.loads(self.get(route,data))

    def get_children(self, acr, cls_id):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/classes/%s/children"%(acr,urllib.quote(cls_id,''))
        return json.loads(self.get(route,data))["classes"]

    def get_classes(self, acr, page=1,size=500):
        data = { "apikey" : self.key , "page" : page , "size" : size }
        route = "/ontologies/%s/classes"%(acr)
        return json.loads(self.get(route,data))

    def get_tree(self, acr, cls_id):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/classes/%s/tree"%(acr,urllib.quote(cls_id,''))
        return json.loads(self.get(route,data))

    def get_descendants(self, acr, cls_id):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/classes/%s/descendants"%(acr,urllib.quote(cls_id,''))
        return json.loads(self.get(route,data))

    def get_ancestors(self, acr, cls_id):
        data = { "apikey" : self.key }
        route = "/ontologies/%s/classes/%s/ancestors"%(acr,urllib.quote(cls_id,''))
        return json.loads(self.get(route,data))
