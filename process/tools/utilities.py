import time
import json

class Duration:
    def __init__(self,seconds):
        self.seconds = seconds
    def __repr__(self):
        return '{:0.8f} secs'.format(self.seconds)

class Timer:
    def __init__(self,name):
        self.name = name
        self.start()
    def start(self,name=None):
        self.name = name if name else self.name
        self.start_time = time.perf_counter()
    def finish(self):
        self.stop_time = time.perf_counter()
        self.duration = Duration(self.stop_time - self.start_time)
        print('{}: {}'.format(self.name,self.duration))
        return self.stop_time - self.start_time

def load(filename):
    return json.load(open(filename))

class ClassEncoder(json.JSONEncoder):
    def default(self, obj):
        return obj.to_json()

def dump(data,filename,indent=4):
    json.dump(data,open(filename,'w'),indent=indent,sort_keys=True,cls=ClassEncoder)

