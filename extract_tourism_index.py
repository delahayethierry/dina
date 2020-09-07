import utils

# Global variables
CITY_NAME = 'Rome'
COUNTRY_NAME = 'ITALY'

# Env variables
here_api_key = os.getenv("here_api_key")

header = {'apikey': here_api_key}

# Main method
def extract_lighting_index(input_file_accidents):

    # Initialize statistical dictionaries
    accidents_per_block = {}
    
    # General stats
    lines_read = 0
    lines_written = 0
    
    # Open the accidents file
    with open(input_file_accidents) as filin_accidents:
        
        for line in filin_accidents:
            line_elements = line.split(';')

            # First line: headers
            if lines_read == 0:
                headers = line_elements
        
            # General case: extract the line and parse the data
            else:
                line_dict = utils.extract_line(headers, line_elements)
                
                hotel_address = line_dict['INDIRIZZO']
                hotel_rooms = int(line_dict['SINGOLE']) + int(line_dict['SINGOLE']) + int(line_dict['DOPPIE']) + int(line_dict['TRIPLE']) + int(line_dict['QUADRUPLE']) + int(line_dict['QUINTUPLE']) + int(line_dict['SESTUPLE'])
                print(f'Parsed line: {hotel_address} - {hotel_rooms}')
        
            lines_read += 1

    # Open the output file
    with open('hotels_per_block.csv', 'w') as filout:
        for accident_block in accidents_per_block:
            #line_out_elements = [accident_block, str(accidents_per_block[accident_block]['Insufficiente']) if 'Insufficiente' in accidents_per_block[accident_block] else '0']
            #filout.write(','.join(line_out_elements) + '\n')
            lines_written += 1
    
    
    
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return





# Module execution: launch main method
if __name__ == '__main__':
    
    input_file_accidents = 'hotel_locations.csv'
    extract_lighting_index(input_file_accidents)

