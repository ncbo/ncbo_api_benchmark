import pdb
import sys
import api
import json
import random

# This benchmark gets the lists of users
# shuffles them retrieves first 100 (default)
class UsersBenchmark(object):
    def __init__(self,client:
        self.client = client

    def run(self,n=100):
        users = self.client.get_all_users()
        users = json.loads(users)
        random.shuffle(users)
        for user in users[n]:
            username = user["username"]
            self.client.get_user(username)

if __name__ == '__main__':
    epr = sys.argv[1]
    print "Using %s ..."%epr
    client = api.Rest(epr)
    ub = UsersBenchmark(client)
    ub.run()
