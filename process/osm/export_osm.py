import osmium

from tools.utilities import load,Timer
from tools.osmium_tools import tag,read_osm_file

way_scenery = load('data/scenery.json')
way_collisions = load('data/collisions.json')

class Handler(osmium.SimpleHandler):

    def __init__(self, writer, idx):
        osmium.SimpleHandler.__init__(self)
        self.writer = writer
        self.counter = {
            'nodes': 0,
            'ways': 0,
            'relations': 0
        }

    def node(self, node):
        self.counter['nodes'] += 1
        self.writer.add_node(node)

    def way(self, way):
        tags = [tag for tag in way.tags]
        if (way.id < len(way_scenery)):
            tags.append(('scenery',str(len(str(int(way_scenery[way.id][1]))))))
        if (way.id < len(way_collisions)):
            tags.append(('collisions',str(way_collisions[way.id][1])))
        way = way.replace(tags=tags)
        self.counter['ways'] += 1
        self.writer.add_way(way)

    def relation(self, relation):
        self.counter['relations'] += 1
        self.writer.add_relation(relation)


def export_osm():

    input_file = 'data/greater-london-input.osm.pbf'
    output_file = 'data/greater-london-output.osm.pbf'

    writer = osmium.SimpleWriter(output_file)
    handler = Handler(writer,idx)

    node_reader = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.NODE)
    osmium.apply(node_reader, handler)
    node_reader.close()

    way_reader = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.WAY)
    osmium.apply(way_reader, handler)
    way_reader.close()

    realtion_reader = osmium.io.Reader(input_file, osmium.osm.osm_entity_bits.RELATION)
    osmium.apply(realtion_reader, handler)
    realtion_reader.close()

    print(handler.counter)
    writer.close()