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

def dfs_traversal(api,acronym, cls_id, leaves):
    children = api.get_children(acronym,cls_id)
    if len(children) == 0:
        leaves.append((acronym, cls_id))
    if len(leaves) > 500:
        return
    for kid in children:
        dfs_traversal(api, acronym, kid["resource_id"], leaves)

def benchmark_traverse_from_roots(configuration):
    api = rest.Rest(configuration["rest"]["ontologies"])
    api.key="some_bogus_api_key"
    api.use_proxy("localhost","8080")
    api.start_recording("./logs/benchmark_traverse_from_roots.csv")

    leaves = []
    ontologies = api.get_all_ontologies()
    for ontology in ontologies:
        classes = api.get_roots(ontology["acronym"])
        for cls in classes:
            dfs_traversal(api,ontology["acronym"], cls["resource_id"], leaves)


if __name__ == "__main__":
    command = sys.argv[1]
    configuration = utils.get_configuration(sys.argv[2])
    if command == "load_data":
        create_dataset(configuration)
    if command == "gen_logs":
        benchmark_traverse_from_roots(configuration)
