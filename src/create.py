import sys
import time
import sparql
import utils
import pdb
import rest

def check_empty(conf,ask=True):
    for epr in conf["sparql"]:
        epr_sparql = sparql.SPARQL(conf["sparql"][epr])
        res = epr_sparql.query("SELECT * WHERE { ?s a ?o } LIMIT 1")
        if len(res) > 0:
            if ask:
                print "The SPARQL endpoint '%s' is not empty. Empty it to create benchmarks."%epr
                print "Do you want to empty it now ? [type y to confirm]: ",
                sys.stdout.flush()
                reply = sys.stdin.readline().strip()
                if reply == 'y':
                    epr_sparql.update("DELETE { ?s ?p ?o } WHERE { ?s ?p ?o }")
            else:
                sys.exit(1)

def create_dataset(conf):
    ont_sparql = sparql.SPARQL(conf["sparql"]["ontologies"])
    check_empty(conf)
    check_empty(conf,ask=False)

    print "CREATING DATABASE"

    api = rest.Rest(conf["rest"]["ontologies"])
    api.user_id = "benchmark"
    key = api.create_user("benchmark", "benchmark@exmample.org" , "bench_pass")
    api.key = key

    submissions = []
    for ontology in conf["ontologies"]:
        if (ontology["acronym"] == "SNOMEDCT" or ontology["acronym"] == "NCBITAXON"):
            continue
        if ontology["acronym"] != "SOPHARM" and ontology["acronym"] != "MCCL":
            continue
        submission = api.create_ontology_submission(ontology)
        submissions.append(submission)
        print "created ", submission["id"]

    for submission in submissions:
        print "parsing ", submission["id"]
        acr, sid = (submission["ontology"], submission["submissionId"])
        api.parse_submission(acr, sid)
        while True:
            ontology = api.get_ontology(acr, sid)
            if ontology["submissionStatus"] != "UPLOADED":
                print "# STATUS =",ontology["submissionStatus"]
                break
            sys.stdout.write("#")
            sys.stdout.flush()
            time.sleep(5)
        print "parsed."

def term_calls(configuration):
    api = rest.Rest(conf["rest"]["ontologies"])

    log_root_calls = open("./logs/log_root_calls.csv","w")
    ontologies = api.get_all_ontologies()
    for ontology in ontologies:
        log_root_calls.write("on

        classes = api.get_roots(ontology)

if __name__ == "__main__":
    command = sys.argv[1]
    configuration = utils.get_configuration(sys.argv[2])
    if command == "parse"
        create_dataset(configuration)
    if command == "logs"
        create_logs(configuration)
