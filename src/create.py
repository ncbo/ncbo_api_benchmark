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
        if (ontology["acronym"] == "SNOMEDCT" or ontology["acronym"] == "NCBITAXON" or ontology["acronym"] == "BIOMODELS"):
            continue
        submission = api.create_ontology_submission(ontology)
        submissions.append(submission)
        print "created ", submission["@id"]

    for submission in submissions:
        print "parsing ", submission["@id"]
        acr, sid = (submission["ontology"]["acronym"], submission["submissionId"])
        api.parse_submission(acr, sid)
        while True:
            submission_status = api.get_ontology_submission(acr, sid,include="submissionStatus")
            if submission_status["submissionStatus"] != "UPLOADED":
                print "# STATUS =",submission_status["submissionStatus"]
                break
            sys.stdout.write("#")
            sys.stdout.flush()
            time.sleep(5)
        print "parsed."

def dfs_traversal(api,acronym, cls_id, leafs):
    children = api.get_children(acronym,cls_id)
    if len(children) == 0:
        leafs.append((acronym, cls_id))
    if len(leafs) > 100:
        return
    for kid in children:
        dfs_traversal(api, acronym, kid["resource_id"], leafs)

def benchmark_traverse_from_roots(configuration):

    api = rest.Rest(configuration["rest"]["ontologies"])
    api.key="some_bogus_api_key"
    #api.use_proxy("localhost","8080")
    api.start_recording("./logs/benchmark_traverse_from_roots.csv")

    leafs = []
    ontologies = api.get_all_ontologies()
    for ontology in ontologies:
        classes = api.get_roots(ontology["acronym"])
        for cls in classes:
            dfs_traversal(api,ontology["acronym"], cls["resource_id"], leafs)

    #for all roots get descendents (first page) this queries need to be improved
    for cls in classes:
        api.get_descendants(ontology["acronym"], cls["resource_id"])

    #for some leafs get path to root and ancestors
    for (ont_acronym,leaf_cls_id) in leafs:
        api.get_tree(ont_acronym, leaf_cls_id)
        api.get_ancestors(ont_acronym, leaf_cls_id)

    api.stop_recording()

def benchmark_get_all_classes(configuration):
    api = rest.Rest(configuration["rest"]["ontologies"])
    api.key="some_bogus_api_key"
    #api.use_proxy("localhost","8080")
    api.start_recording("./logs/benchmark_get_all_classes.csv")

    leafs = []
    ontologies = api.get_all_ontologies()
    for ontology in ontologies:
        page = 1
        total = 0
        while page:
            page_classes = api.get_classes(ontology["acronym"],page=page)
            total += len(page_classes["class"])
            print "get_classes %s paging %s/%s"%(total,page_classes["page"],
                                                 page_classes["page_count"])
            page = page_classes["next_page"] if "next_page" in page_classes else None
    api.stop_recording()

def benchmark_users(configuration)
    api = rest.Rest(configuration["rest"]["ontologies"])
    api.key="some_bogus_api_key"
    #api.use_proxy("localhost","8080")
    api.start_recording("./logs/benchmark_get_all_users.csv")

    users = api.get_all_users()
    for user in users:
        api.get_user(user["user_id"])
    api.stop_recording()

if __name__ == "__main__":
    command = sys.argv[1]
    configuration = utils.get_configuration(sys.argv[2])
    if command == "load_data":
        create_dataset(configuration)
    if command == "gen_logs":
        benchmark_traverse_from_roots(configuration)
        benchmark_get_all_classes(configuration)
