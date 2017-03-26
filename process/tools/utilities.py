import json

def load(filename):
    return json.load(open(filename))

class ClassEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.to_json()

def dump(data,filename,indent=4):
    json.dump(data,open(filename,'w'),indent=indent,sort_keys=True,cls=ClassEncoder)