import os
import osmium

flexability = (0.06,0.04)
center = (51.465317, -0.109154)

def within_bounds(location):
    coords = (location.lat,location.lon)
    return (
        (abs(center[0] - coords[0]) < flexability[0]) and
        (abs(coords[0] - center[0]) < flexability[0]) and
        (abs(center[1] - coords[1]) < flexability[1]) and
        (abs(coords[1] - center[1]) < flexability[1])
    )

class Handler(osmium.SimpleHandler):

    def __init__(self, writer, idx):
        osmium.SimpleHandler.__init__(self)
        self.writer = writer
        self.idx = idx
        self.counter = {
            'nodes': 0,
            'ways': 0,
            'relations': 0
        }
        self.timer = {
            'search': 0
        }

    def node(self, node):
        if (not within_bounds(node.location)): return
        self.counter['nodes'] += 1
        self.writer.add_node(node)

    def way(self, way):
        if (not within_bounds(self.idx.get(way.nodes[0].ref))): return
        # locations = [self.idx.get(node.ref) for node in way.nodes]
        # path = [(location.lat,location.lon) for location in locations]
        self.counter['ways'] += 1
        self.writer.add_way(way)

    def relation(self, relation):
        self.counter['relations'] += 1
        self.writer.add_relation(relation)


def reduce_osm():

    input_file = 'data/greater-london-latest.osm.pbf'
    
    idx = osmium.index.create_map('sparse_file_array,data/node-cache.nodecache')
    locations = osmium.NodeLocationsForWays(idx)
    locations.ignore_errors()

    output_file = 'data/dulwich.osm.pbf'
    if (os.path.exists(output_file)): os.remove(output_file)
    writer = osmium.SimpleWriter(output_file)
    handler = Handler(writer,idx)

    node_reader = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.NODE)
    osmium.apply(node_reader, locations)
    node_reader.close()

    node_reader = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.NODE)
    osmium.apply(node_reader, handler)
    node_reader.close()

    way_reader = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.WAY)
    osmium.apply(way_reader, locations, handler)
    way_reader.close()

    realtion_reader = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.RELATION)
    osmium.apply(realtion_reader, handler)
    realtion_reader.close()

    print(handler.counter)

    writer.close()
