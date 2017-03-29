import osmium

from tools.utilities import dump
from tools.osmium_tools import tag,read_osm_file

ways = []

class Way:
    def __init__(self,way):
        self.name = tag(way,'name')
        self.leisure = tag(way,'leisure')
        self.landuse = tag(way,'landuse')
        self.boundary = tag(way,'boundary')
    def is_nature(self):
        return (
            (self.leisure == 'common') or
            (self.leisure == 'garden') or
            (self.leisure == 'nature_reserve') or
            (self.landuse == 'village_green') or
            (self.landuse == 'recreation_ground') or
            (self.boundary == 'national park') or
            (self.boundary == 'protected_area')
        )
    def update_nodes(self,locations):
        self.nodes = [
            {
                'lat': location.lat,
                'lon': location.lon
            }
            for location in locations
        ]
    def to_json(self):
        return {
            'name': self.name,
            'nodes': self.nodes,
            'leisure': self.leisure,
            'landuse': self.landuse,
            'boundary': self.boundary
        }


class Handler(osmium.SimpleHandler):

    def __init__(self,idx):
        osmium.SimpleHandler.__init__(self)
        self.idx = idx

    def way(self, way):
        way = Way(way)
        if (way.is_nature()):
            locations = [self.idx.get(node) for node in way.nodes]
            way.update_nodes(locations)
            ways.append(way)
        
def nature_search():

    osm_file = 'data/greater-london-latest.osm.pbf'
    handler = read_osm_file(osm_file,Handler)
    dump(ways,'data/nature.json')