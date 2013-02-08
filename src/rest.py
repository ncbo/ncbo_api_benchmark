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
            conn = httplib.HTTPConnection(self.host)
            params = urllib.urlencode(doc)
            headers = {}
            if method == "PUT" or method == "POST":
                headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "application/json"}
                conn.request(method, route, params, headers)
            else:
                conn.request(method, route + "?" + params, "", headers)
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

    def create_user(self,name,email,password):
        doc = { "email" : email, "password" : password }
        route = "/users/%s"%name
        response = json.loads(self.put(route, doc))
        return response["apikey"] if "apikey" in response else "bogus_api_key"

    def create_ontology_submission(self,ontology):
        data_body = None
        data_file = open(ontology["local_path"],"r")
        files = [("ontology_data_0", data_file)]
        ontology["administeredBy"] = self.user_id
        ontology["apikey"] = self.key
        ontology["name"] = "ontology name in %s"%ontology["acronym"]
        route = "/ontologies/%s"%ontology["acronym"]
        try:
            response = json.loads(self.put(route,ontology,files=files))
            return response
        except urllib2.HTTPError, e:
            raise e

    def parse_submission(self, acr, submission_id):
        data = { "apikey" : self.key , "ontology_submission_id" : submission_id}
        route = "/ontologies/%s/submissions/parse"%acr
        response = self.post(route, data)
        return json.loads(response)

    def get_ontology(self, acr, submission_id):
        data = { "apikey" : self.key , "ontology_submission_id" : submission_id}
        route = "/ontologies/%s"%acr
        ontology = json.loads(self.get(route,data))
        return ontology


