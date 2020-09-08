import math

# Extracts a line as a dictionary. Assumes the number of elements in the line is the same as the number of headers
def extract_line(headers, line_elements):
    
    # Initialize the line dictionary
    line_dict = {}
    
    # Loop over the elements and build the dictionary
    for i, element in enumerate(line_elements):
        line_dict[headers[i]] = element
    
    return line_dict


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
def write_index_headers()

    return 'Latitude,Longitude,Year,Month,Index'


