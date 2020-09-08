import math
import utils


# Main method
def get_accidents_geodata(input_file_accidents):

    # Initialize statistical dictionaries
    accidents_per_block = {}
    max_accidents_per_block = 0
    
    # General stats
    lines_read = 0
    lines_written = 0

    # Dummy year and month variables
    year = '2020'
    month = '01'
    
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
                
                accident_block_details = utils.extract_block(line_dict['Longitudine'], line_dict['Latitudine'])
                accident_block_name = accident_block_details['name']
                accident_lighting = line_dict['Illuminazione']
                
                # Add the accident to the statistics
                if accident_block_name not in accidents_per_block:
                    accidents_per_block[accident_block_name] = accident_block_details
                if accident_lighting not in accidents_per_block[accident_block_name]:
                    accidents_per_block[accident_block_name][accident_lighting] = 0
                accidents_per_block[accident_block_name][accident_lighting] += 1
                if accident_lighting == 'Insufficiente':
                    if accidents_per_block[accident_block_name][accident_lighting] > max_accidents_per_block:
                        max_accidents_per_block = int(accidents_per_block[accident_block_name][accident_lighting])
        
            lines_read += 1

    # Open the output file
    with open('output_data/accidents.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('accidents')+ '\n')

        # Loop over the blocks and fill the lines
        for accident_block in accidents_per_block:
            accident_block_details = accidents_per_block[accident_block]
            accidents_per_block_raw = accident_block_details['Insufficiente'] if 'Insufficiente' in accident_block_details else 0
            accidents_per_block_index = math.floor((float(accidents_per_block_raw) / float(max_accidents_per_block)) * 10)
            line_out_elements = [str(i) for i in [accident_block_details['longitude'], accident_block_details['latitude'], year, month, accidents_per_block_index]]
            filout.write(','.join(line_out_elements) + '\n')
            lines_written += 1
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return accidents_per_block




# Module execution: launch main method
if __name__ == '__main__':
    
    input_file_accidents = 'input_data/csv_incidenti_merge_20192020.csv'
    get_accidents_geodata(input_file_accidents)

