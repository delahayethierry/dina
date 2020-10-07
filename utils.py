

import folium
import geopandas as gpd
import json
import math
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import pyproj
import requests
import shapely.geometry
from pyproj import Transformer
from shapely.geometry import Polygon

# Local imports
import config

# Import grid csvs
administrative_subdivision_lookup_df = pd.read_csv(config.administrative_subdivision_lookup,names = ['data', 'id', 'display_name'])
city_grid_df = pd.read_csv(config.city_grid_csv_file)

# Generate city_grid.geojson file based on a bounding box (SW-NE Coordinates to cover) and width/height
# as defined in config.py in variables block_width and block_height
def generate_city_grid():

    # Get the lower-left and upper-right bounds from the Municipi shapes to center the map
    administrative_subdivisions_shapes_bounds = folium.GeoJson(config.administrative_subdivision_geojson_file).get_bounds()
    print('Generating a city grid with blocks of ',config.block_width,'meters x ',config.block_height,' meters, using this bounding box: ',administrative_subdivisions_shapes_bounds)
    
    # Set up projections
    transformer = Transformer.from_crs('epsg:4326', 'epsg:3857') # transformer to translate epsh:4326 to epsg:3857 = metric; same as EPSG:900913
    transformer_back = Transformer.from_crs('epsg:3857', 'epsg:4326') # transformer to transform from metric to epsg:4326
    
    # Create corners of rectangle to be transformed to a grid
    sw = shapely.geometry.Point(administrative_subdivisions_shapes_bounds[0])
    ne = shapely.geometry.Point(administrative_subdivisions_shapes_bounds[1])

    # Project corners to target projection
    transformed_sw = transformer.transform(sw.x, sw.y)  # Transform NW point to 3857
    transformed_ne = transformer.transform(ne.x, ne.y)  # .. same for SE

    # Read the GeoJson file downloaded from Public Administration Open Data portals, and which contains the shapes 
    # of administrative subdivisions like Municipi in Roma
    municipi_df = gpd.read_file(config.administrative_subdivision_geojson_file)

    # Initialize iterator
    i = 0
    
    #List which will be used as columns/properties in the GeoJsona and CSV files to be generated
    properties_block_ID = []
    properties_administrative_subdivision = []
    
    #List of geometries representing the polygones (= rectangles) to define the city blocks
    gridpoints = []
    
    #Lists to generate the csv file which will bake subsequent processes easier and optimized (like )
    blocks_sw_longitude = []
    blocks_sw_latitude = []
    blocks_ne_longitude = []
    blocks_ne_latitude = []
    blocks_centroid_longitude = []
    blocks_centroid_latitude = []
    
    # Loop to generate the city grid
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
            
            blocks_sw_longitude.append(grid_sw[1])
            blocks_sw_latitude.append(grid_sw[0])
            blocks_ne_longitude.append(grid_ne[1])
            blocks_ne_latitude.append(grid_ne[0])
            
            blocks_centroid_longitude.append (grid_sw[1]+(grid_ne[1]-grid_sw[1])/2)
            blocks_centroid_latitude.append (grid_sw[0]+(grid_ne[0]-grid_sw[0])/2)
            
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

    # Create the geopandas dataframe
    grid_geojson = gpd.GeoDataFrame({'geometry': gridpoints, 'block_ID': properties_block_ID,
                             'administrative_subdivision': properties_administrative_subdivision}, crs='EPSG:4326')
    grid_geojson.to_file(config.city_grid_geojson_file, driver='GeoJSON')
    print ('City Grid save in GeoJson format in ', config.city_grid_geojson_file,", ",str(i-1),' blocks created')

    # Create the grid as pandas dataframe and save to csv
    grid_csv = pd.DataFrame({'block_ID': properties_block_ID, 'administrative_subdivision': properties_administrative_subdivision, 
                            'sw_longitude': blocks_sw_longitude,'sw_latitude': blocks_sw_latitude,
                            'ne_longitude': blocks_ne_longitude,'ne_latitude': blocks_ne_latitude, 
                            'centroid_longitude': blocks_centroid_longitude , 'centroid_latitude': blocks_centroid_latitude , })
    grid_csv.to_csv(config.city_grid_csv_file, index=False)
    print ('City Grid save in CSV format in ', config.city_grid_csv_file,", ",str(i-1),' blocks created')

    
# Extracts a line as a dictionary. Assumes the number of elements in the line is the same as the number of headers
def extract_line(headers, line_elements):
    
    # Initialize the line dictionary
    line_dict = {}
    
    # Loop over the elements and build the dictionary
    for i, element in enumerate(line_elements):
        line_dict[headers[i]] = element
    
    return line_dict

# Gets the administrative division ID from its name
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
        block = get_city_block(longitude, latitude)
    else:
        block = build_dummy_city_block()
    
    return block


# Gets the corresponding city block from coordinates
def get_city_block(longitude, latitude):

    try:
        longitude_float = float(longitude)
        latitude_float = float(latitude)
        inblock_df = city_grid_df[(city_grid_df.sw_longitude <= longitude_float) & (city_grid_df.ne_longitude >= longitude_float) 
                                & (city_grid_df.sw_latitude <= latitude_float) & (city_grid_df.ne_latitude >= latitude_float)]
        if len(inblock_df.index) > 0:
            block_name = {
            'block_ID' : inblock_df['block_ID'].iloc[0],
            'administrative_subdivision' : inblock_df['administrative_subdivision'].iloc[0]
            }
            block_name['name'] = inblock_df['block_ID'].iloc[0]
        else:
            block_name = build_dummy_city_block()
    except:
        block_name = build_dummy_city_block()
    return block_name

# Builds a dummy city block for cases where we do not have the coordinates
def build_dummy_city_block():

    block_name = {
        'block_ID' : -1,
        'administrative_subdivision' : 0
    }
    block_name['name'] = ''
    
    return block_name


# Calls the HERE api to get a geolocalization for an address
def query_geolocalization(address, city_name, country_name, here_api_key):

    # General variables
    geolocation_url = 'https://geocode.search.hereapi.com/v1/geocode'

    # Build the full address line
    address_query = ', '.join([address, city_name, country_name])
    
    # Build the geolocation request
    address_query_params = {
        "q": address_query, 
        'apikey': here_api_key
    }
    response = requests.get(geolocation_url, params=address_query_params, verify = False)
    response_json = json.loads(response.text)

    # If response successful, fill the coordinates. Else, put dummy values
    if 'items' in response_json and len(response_json['items']) > 0:
        geolocalization_success = True
        longitude = response_json['items'][0]['position']['lng']
        latitude = response_json['items'][0]['position']['lat']
    else:
        geolocalization_success = False
        longitude = -1
        latitude = -1

    return geolocalization_success, latitude, longitude



# Writes the headers for the index files to be used for mapping
def get_index_headers():

    return ['block_ID','administrative_subdivision','Year','Month'] #,'Index']


# Writes the headers for the index files to be used for mapping. Replaces the last column with the datasource name
def write_index_headers(datasource_name):

    return ','.join(get_index_headers() + [datasource_name])


# Module execution: launch main method
if __name__ == '__main__':
    generate_city_grid()
    
    
