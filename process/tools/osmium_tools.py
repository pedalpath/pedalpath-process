import osmium

def tag(entity,name):
    return entity.tags[name] if (name in entity.tags) else None

def read_osm_file(filename,Handler,**kwargs):

    idx = osmium.index.create_map('sparse_file_array,data/node-cache.nodecache')
    locations = osmium.NodeLocationsForWays(idx)
    locations.ignore_errors()

    node_reader = osmium.io.Reader(filename, osmium.osm.osm_entity_bits.NODE)
    osmium.apply(node_reader, locations)
    node_reader.close()

    handler = Handler(idx,**kwargs)

    way_reader = osmium.io.Reader(filename, osmium.osm.osm_entity_bits.WAY)
    osmium.apply(way_reader, locations, handler)
    way_reader.close()

    return handler