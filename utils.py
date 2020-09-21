import math
import folium
import config
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
from pyproj import Transformer
import shapely.geometry
from shapely.geometry import Polygon

import geopandas as gpd

administrative_subdivision_lookup_df = pd.read_csv(config.municipi_lookup,names = ['data', 'id', 'display_name'])


# Generate city_grid.geojson file based on a bounding box (SW-NE Coordinates to cover) and width/height
# as defined in config.py in variables block_width and block_height
def generate_city_grid():

    # Get the lower-left and upper-right bounds from the Municipi shapes to center the map
    administrative_subdivisions_shapes_bounds = folium.GeoJson(config.administrative_subdivision_geojson_file).get_bounds()
    print('Generating a city grid with blocks of ',config.block_width,'meters x ',config.block_height,' meters, using this bounding box: ',administrative_subdivisions_shapes_bounds)
    # Set up projections
    # 'epsg:3857' = metric; same as EPSG:900913
    transformer = Transformer.from_crs('epsg:4326', 'epsg:3857')
    transformer_back = Transformer.from_crs(
        'epsg:3857', 'epsg:4326')    # go back to 'epsg:4326'
    # Create corners of rectangle to be transformed to a grid
    sw = shapely.geometry.Point(administrative_subdivisions_shapes_bounds[0])
    ne = shapely.geometry.Point(administrative_subdivisions_shapes_bounds[1])

    # Project corners to target projection
    transformed_sw = transformer.transform(
        sw.x, sw.y)  # Transform NW point to 3857
    transformed_ne = transformer.transform(ne.x, ne.y)  # .. same for SE

    municipi_df = gpd.read_file(config.administrative_subdivision_geojson_file)
    

    i = 0
    # Iterate over 2D area
    gridpoints = []
    properties_block_ID = []
    properties_administrative_subdivision = []
    x = transformed_sw[0]
    while x < transformed_ne[0]:
        y = transformed_sw[1]
        while y < transformed_ne[1]:
            grid_sw = transformer_back.transform(x, y)
            grid_se = transformer_back.transform(x+config.block_width, y)
            grid_ne = transformer_back.transform(
                x+config.block_width, y+config.block_height)
            grid_nw = transformer_back.transform(x, y+config.block_height)
            block_polygon = shapely.geometry.Polygon([
                [grid_sw[1], grid_sw[0]],
                [grid_se[1], grid_se[0]],
                [grid_ne[1], grid_ne[0]],
                [grid_nw[1], grid_nw[0]]])
            gridpoints.append(block_polygon)
            administrative_subdivision = ''
            for index, row in municipi_df.iterrows():
                if block_polygon.centroid.within(row['geometry']):
                    administrative_subdivision = " ".join(row['nome'].split()).strip()
                    break
            properties_administrative_subdivision.append(str(get_administrative_division_id_from_name(administrative_subdivision)))
            properties_block_ID.append(i)
            i += 1
            y += config.block_height
        x += config.block_width

    grid = gpd.GeoDataFrame({'geometry': gridpoints, 'block_ID': properties_block_ID,
                             'administrative_subdivision': properties_administrative_subdivision}, crs='EPSG:4326')
    grid.to_file("./input_data/city_grid.geojson", driver='GeoJSON')
    print ('City Grid save in ./input_data/city_grid.geojson, ',str(i-1),' blocks created')
    return grid

# Extracts a line as a dictionary. Assumes the number of elements in the line is the same as the number of headers
def extract_line(headers, line_elements):
    
    # Initialize the line dictionary
    line_dict = {}
    
    # Loop over the elements and build the dictionary
    for i, element in enumerate(line_elements):
        line_dict[headers[i]] = element
    
    return line_dict

def get_administrative_division_id_from_name(name_in_text):
    
    if name_in_text in administrative_subdivision_lookup_df['data'].values:
        return administrative_subdivision_lookup_df[administrative_subdivision_lookup_df.data == name_in_text].id.index[0]
    else:
        return ''

# Maps a longitude, latitude to a block. This method can be replaced to whatever block is needed (more/less granular, or any function of longitude, latitude)
# This larger method takes strings
# TODO put as well min/max of the block somewhere...
def extract_block(longitude, latitude):
    
    # Compute the block name, and default to null if one of the coordinates is missing
    if len(longitude) > 0 and len(latitude) > 0:
        
        # Format issue on some months: replace commas with dots
        longitude = longitude.replace(',','.')
        latitude = latitude.replace(',','.')
    
        # Build the block name
        block = extract_block_float(longitude, latitude)
    else:
        block = build_dummy_block()
    
    return block


# Maps a longitude, latitude to a block. This method can be replaced to whatever block is needed (more/less granular, or any function of longitude, latitude)
def extract_block_float(longitude, latitude):

    longitude_float = float(longitude)
    latitude_float = float(latitude)

    block_name = {
        'longitude' : (float(math.floor(longitude_float*100))+0.5)/100,
        'latitude' : (float(math.floor(latitude_float*100))+0.5)/100
    }
    block_name['name'] = str(block_name['longitude']) + '-' + str(block_name['latitude'])
    
    return block_name


# Builds a dummy block for cases where we do not have the coordinates
def build_dummy_block():

    block_name = {
        'longitude' : 0,
        'latitude' : 0
    }
    block_name['name'] = ''
    
    return block_name


# Writes the headers for the index files to be used for mapping
def get_index_headers():

    return ['Latitude','Longitude','Year','Month'] #,'Index']


# Writes the headers for the index files to be used for mapping. Replaces the last column with the datasource name
def write_index_headers(datasource_name):

    return ','.join(get_index_headers() + [datasource_name])


# Module execution: launch main method
if __name__ == '__main__':
    generate_city_grid()