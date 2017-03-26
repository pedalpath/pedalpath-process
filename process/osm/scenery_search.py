import osmium

from tools.map_tools import tag
from tools.utilities import dump

class Node():
    def __init__(self,node):
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
            'lat': self.lat,
            'lon': self.lon,
            'name': self.name,
            'natural': self.natural,
            'tourism': self.tourism
        }

class LocationMatrix:

    SIZE = 100000
    # 111,111 meters (111.111 km) in the y direction is 1 degree (of latitude)
    # 111,111 * cos(latitude) meters in the x direction is 1 degree (of longitude)

    def __init__(self):
        self.matrix = {}

    def _round(self,degrees):
        return str(int(round(degrees*self.SIZE)))

    def insert(self,lat,lon,data):
        lat_ref = self._round(lat)
        lon_ref = self._round(lon)
        self.matrix[lat_ref] = self.matrix.get(lat_ref,{})
        self.matrix[lat_ref][lon_ref] = self.matrix[lat_ref].get(lon_ref,{})
        self.matrix[lat_ref][lon_ref]['{},{}'.format(lat,lon)] = data

    def get(self,lat,lon):
        lat_ref = self._round(lat)
        lon_ref = self._round(lon)
        row = self.matrix.get(lat_ref,{})
        cell = row.get(lon_ref,{})
        if (len(cell)):
            (lat,lon) = cell.keys()[0].split(',')
            data = cell[(lat,lon)]
            return {
                'lat': lat,
                'lon': lon,
                'data': data
            }

    def find(self,lat,lon):
        result = self.get(lat,lon)
        if (result):
            result['steps'] = 0
            return result
        for i in range(-1,2,2):
            for j in range(-1,2,2):
                _lat = lat+(i*self.SIZE)
                _lon = lon+(j*self.SIZE)
                result = self.get(_lat,_lon)
                if (result):
                    result['steps'] = 1
                    return result

    def to_json(self):
        return self.matrix

class SceneryHandler(osmium.SimpleHandler):

    def __init__(self,location_matrix):
        osmium.SimpleHandler.__init__(self)
        self.location_matrix = location_matrix

    def node(self,node):
        node = Node(node)
        if (node.is_scenic()):
            self.location_matrix.insert(node.lat,node.lon,node)


def main():

    osm_file = 'data/greater-london-latest.osm.pbf'

    location_matrix = LocationMatrix()
    handler = SceneryHandler(location_matrix)

    node_reader = osmium.io.Reader(osm_file, osmium.osm.osm_entity_bits.NODE)
    osmium.apply(node_reader, handler)
    node_reader.close()

    dump(location_matrix,'data/scenery.json')
