import osmium

class Handler(osmium.SimpleHandler):

    def __init__(self, idx, writer):
        osmium.SimpleHandler.__init__(self)
        self.idx = idx
        self.writer = writer

    def node(self, node):
        self.writer.add_node(node)

    def way(self, way):
        self.writer.add_way(way)

    def relation(self, relation):
        print('relation')
        self.writer.add_relation(relation)

if (__name__ == "__main__"):

    input_file = 'data/greater-london-input.osm.pbf'
    output_file = 'data/greater-london-output.osm.pbf'
    
    writer = osmium.SimpleWriter(output_file)
    idx = osmium.index.create_map('sparse_file_array,data/node-cache.nodecache')
    handler = Handler(idx,writer)

    locations = osmium.NodeLocationsForWays(idx)
    locations.ignore_errors()

    nodes = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.NODE)
    osmium.apply(nodes, locations, handler)
    nodes.close()

    ways = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.WAY)
    osmium.apply(ways, handler)
    ways.close()

    relations = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.RELATION)
    osmium.apply(relations, handler)
    relations.close()

    writer.close()
