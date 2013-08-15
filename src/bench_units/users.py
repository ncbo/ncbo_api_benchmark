import pdb
import time
import sys
import api
import json
import random
import ezbench
import os

# This benchmark gets the lists of users
# shuffles them retrieves first 100 (default)
class UsersBenchmark(object):
    def __init__(self,client):
        self.client = client

    def run(self,n=100):
        users = self.client.get_all_users()
        users = json.loads(users)
        random.shuffle(users)
        for user in users[:n]:
            username = user["username"]
            self.client.get_user(username)

if __name__ == '__main__':
    epr = sys.argv[1]
    print "Using %s ..."%epr
    benchmark = ezbench.Benchmark()

    def query_debug(api):
        return api.last_query_info()
    def request_path(api):
        return api.last_request_path

    benchmark.link(api.Rest.get_all_users,subgroups=query_debug,data=request_path)
    benchmark.link(api.Rest.get_user,subgroups=query_debug,data=request_path)

    api_key = os.environ["NCBO_API_KEY"]
    client = api.Rest(epr,key=api_key)
    perc_points = [60,90]
    ub = UsersBenchmark(client)
    for x in range(10):
        print "running iteration %s"%x
        ub.run(n=12)
    percs = benchmark.percentiles(include=perc_points)
    print "All groups median (%.3f) worst (%.3f)"%(benchmark.median()["total"],benchmark.maximum()["total"])
    ezbench.report.print_percentiles(percs,out=sys.stdout)
    for g in benchmark.groups():
        print "Group: %s median (%.3f) worst (%.3f)"\
                %(g,benchmark.median(group=g)["total"],benchmark.maximum(group=g)["total"])
        percs = benchmark.percentiles(group=g,include=perc_points)
        ezbench.report.print_percentiles(percs,out=sys.stdout)
    fout = os.path.join("results",
              "bench_" + os.path.basename(__file__) + time.strftime("_%Y%m%d_%H%M_%S.csv"))
    benchmark.save(fout)
