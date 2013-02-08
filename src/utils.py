import json

def get_configuration(path):
    conf = None
    with open(path,"r") as fin:
        conf = json.loads(fin.read())
        fin.close()
    return conf
