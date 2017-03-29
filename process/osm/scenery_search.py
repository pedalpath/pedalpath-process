import osmium

from tools.utilities import dump
from tools.osmium_tools import tag
from tools.location_matrix import LocationMatrix

class Node():
    def __init__(self,node):
        self.id = node.id
        self.lat = node.location.lat
        self.lon = node.location.lon
        self.name = tag(node,'name')
        self.natural = tag(node,'natural')
        self.tourism = tag(node,'tourism')
    def is_scenic(self):
        return (self.natural or self.tourism)
    def __repr__(self):
        return '{} - {} - {}'.format(
            self.name,
            self.natural,
            self.tourism
        )
    def to_json(self):
        return {
            'id': self.id,
            'lat': self.lat,
            'lon': self.lon,
            'name': self.name,
            'natural': self.natural,
            'tourism': self.tourism
        }

class SceneryHandler(osmium.SimpleHandler):

    def __init__(self,location_matrix):
        osmium.SimpleHandler.__init__(self)
        self.location_matrix = location_matrix

    def node(self,node):
        node = Node(node)
        if (node.is_scenic()):
            self.location_matrix.insert(node.lat,node.lon,node)

def scenery_search():

    osm_file = 'data/greater-london-latest.osm.pbf'

    location_matrix = LocationMatrix()
    handler = SceneryHandler(location_matrix)

    node_reader = osmium.io.Reader(osm_file, osmium.osm.osm_entity_bits.NODE)
    osmium.apply(node_reader, handler)
    node_reader.close()

    dump(location_matrix,'data/scenery.json')
