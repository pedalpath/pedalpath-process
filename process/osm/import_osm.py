import sys
import json
import osmium

from tools.utilities import dump
from tools.osmium_tools import tag,read_osm_file

ways = []
nodes = {}

class Node():
    def __init__(self,ref,location):
        self.ref = ref
        self.lat = location.lat
        self.lon = location.lon
        self.ways = []
    def to_json(self):
        return {
            'ref': self.ref,
            'lat': self.lat,
            'lon': self.lon,
            'ways': self.ways
        }

class Way():
    def __init__(self,way):
        self.id = way.uid
        self.name = tag(way,'name')
        self.access = tag(way,'access')
        self.oneway = tag(way,'oneway')
        self.highway = tag(way,'highway')
        self.cycleway = tag(way,'cycleway')
        self.crossing = tag(way,'crossing')
        self.nodes = [ node.ref for node in way.nodes ]
    def update_nodes(self,locations):
        for (ref,location) in zip(self.nodes,locations):
            if (ref not in nodes):
                nodes[ref] = Node(ref,location)
            yield nodes[ref]
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'access': self.access,
            'oneway': self.oneway,
            'highway': self.highway,
            'cycleway': self.cycleway,
            'crossing': self.crossing,
            'nodes': self.nodes
        }

class RouteHandler(osmium.SimpleHandler):

    def __init__(self,idx):
        osmium.SimpleHandler.__init__(self)
        self.idx = idx

    def way(self, way):
        way = Way(way)
        if (way.highway):
            self.highway(way)

    def highway(self, way):
        way.id = len(ways)
        ways.append(way)
        locations = [self.idx.get(node) for node in way.nodes]
        for node in way.update_nodes(locations):
            node.ways.append(way.id)

def import_osm():

    osm_file = 'data/greater-london-latest.osm.pbf'
    handler = read_osm_file(osm_file,RouteHandler)

    dump(nodes,'data/nodes.json')    
    dump(ways,'data/ways.json') 
