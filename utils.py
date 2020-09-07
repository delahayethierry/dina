
# Extracts a line as a dictionary. Assumes the number of elements in the line is the same as the number of headers
def extract_line(headers, line_elements):
    
    # Initialize the line dictionary
    line_dict = {}
    
    # Loop over the elements and build the dictionary
    for i, element in enumerate(line_elements):
        line_dict[headers[i]] = element
    
    return line_dict


# Maps a longitude, latitude to a block. This method can be replaced to whatever block is needed (more/less granular, or any function of longitude, latitude)
# TODO put as well min/max of the block somewhere...
def extract_block(longitude, latitude):
    
    # Compute the block name, and default to null if one of the coordinates is missing
    if len(longitude) > 0 and len(latitude) > 0:
        
        # Format issue on some months: replace commas with dots
        longitude = longitude.replace(',','.')
        latitude = latitude.replace(',','.')
    
        # Build the block name
        block_name = "%.2f" % float(longitude) + '-' "%.2f" % float(latitude)
    else:
        block_name = ''
    
    return block_name



