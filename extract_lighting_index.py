


# Main method
def extract_lighting_index(input_file_accidents):

    # Initialize statistical dictionaries
    accidents_per_block = {}
    
    # General stats
    lines_read = 0
    
    # Open the accidents file
    with open(input_file_accidents) as filin_accidents:
        
        for line in filin_accidents:
            line_elements = line.split(';')

            # First line: headers
            if lines_read == 0:
                headers = line_elements
        
            # General case: extract the line and parse the data
            else:
                line_dict = extract_line(headers, line_elements)
                
                accident_block = extract_block(line_dict['Longitudine'], line_dict['Latitudine'])
                accident_lighting = line_dict['Illuminazione']
                print(f'Parsed line: {accident_block}, {accident_lighting}')
        
            lines_read += 1

    # Print some stats
    print(f'Read lines: {lines_read}')

    return


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





# Module execution: launch main method
if __name__ == '__main__':
    
    input_file_accidents = 'csv_incidenti_merge_20192020.csv'
    extract_lighting_index(input_file_accidents)

