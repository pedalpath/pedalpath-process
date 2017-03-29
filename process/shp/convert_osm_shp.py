#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from osgeo import ogr, osr

def convert_osm_shp():

    osm_file = "data/dulwich.osm.pbf" 
    osm_layer = "lines" 
    shp_file = "data/dulwich.shp" 

    # open input eight sets 
    idrv = ogr.GetDriverByName("OSM")
    if idrv is None:
        sys.exit("OSM can not read data")
    ids = idrv.Open(osm_file, False)
    if ids is None:
        sys.exit("Unable to open eight file '{}'".format(osm_file))
    ilayer = ids.GetLayerByName(osm_layer)
    if ilayer is None:
        sys.exit("Invalid file OSM")
    os.environ['OGR_INTERLEAVED_READING'] = 'YES'  # required to read more data

    # Create an empty shapefile 
    odrv = ogr.GetDriverByName("ESRI Shapefile")
    if odrv is None:
        sys.exit("Unable to write to ESRI shapefile")

    # overwrite existing shapefile 
    if os.path.exists(shp_file):
        odrv.DeleteDataSource(shp_file)
    ods = odrv.CreateDataSource(shp_file)
    if ods is None:
        sys.exit("Unable to create Shapefile file '{}'".format(shp_file))

    # to set the coordinate system for input and output(S-JTSK) 
    srs_source = ilayer.GetSpatialRef()
    srs_target = osr.SpatialReference()
    srs_target.ImportFromEPSG(5514)

    # set transform 
    coord_trans = osr.CoordinateTransformation(srs_source, srs_target)
    olayer = ods.CreateLayer(shp_file.split('.')[0],
                             srs_target, ogr.wkbLineString, ['ENCODING=UTF-8'])

    # Create attributes for the output layer 
    field_name = ogr.FieldDefn("typ", ogr.OFTString)
    field_name.SetWidth(254)
    olayer.CreateField(field_name)

    featDefn = olayer.GetLayerDefn()

    # dictionary for converting the type of communication 
    stype = {'motorway'  : 'dálnice',
             'trunk'     : 'rychlostní silnice',
             'primary'   : '1. třída',
             'secondary' : '2. třída',
             'tertiary'  : '3. třída'}

    # new reading is purely specialty OSM driver !!! 
    read_osm = True
    while read_osm:
        read_osm = False
        
        for idx in range(ids.GetLayerCount()):
            layer = ids.GetLayer(idx)
            layer_name = layer.GetName()
            print("Reading '{}'...".format(layer_name))
            while True:
                # retrieve the next element from the inlet 
                ifeature = layer.GetNextFeature()
                if ifeature is None:
                    break
                
                read_osm = True
                # skip other layers 
                if layer_name != 'lines':
                    continue

                # MANUAL attribute filter 
                ltype = ifeature.GetField('highway')
                if not ltype or ltype not in ('motorway', 'trunk', 'primary', 'secondary', 'tertiary',
                                              'motorway_link', 'trunk_link', 'primary_link',
                                              'secondary_link', 'tertiary_link'):
                    continue
                
                # geometry transform S-JTSK 
                geom = ifeature.GetGeometryRef()
                geom.Transform(coord_trans)
                
                # writing the new element in the output layer 
                ofeature = ogr.Feature(featDefn)
                ofeature.SetGeometry(geom)
                ofeature.SetField("typ", stype.get(ifeature.GetField('highway').split('_',1)[0], 'neklasifikováno'))
                olayer.CreateFeature(ofeature)
            
    print("{} fearures written to output".format(olayer.GetFeatureCount()))

    # closing input and output layer 
    ids.Destroy()
    ods.Destroy()