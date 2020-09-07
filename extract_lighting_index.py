import math
import utils


# Main method
def extract_lighting_index(input_file_accidents):

    # Initialize statistical dictionaries
    accidents_per_block = {}
    max_accidents_per_block = 0
    
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
                
                accident_block = utils.extract_block(line_dict['Longitudine'], line_dict['Latitudine'])
                accident_lighting = line_dict['Illuminazione']
                
                # Add the accident to the statistics
                if accident_block not in accidents_per_block:
                    accidents_per_block[accident_block] = {}
                if accident_lighting not in accidents_per_block[accident_block]:
                    accidents_per_block[accident_block][accident_lighting] = 0
                accidents_per_block[accident_block][accident_lighting] += 1
                if accidents_per_block[accident_block][accident_lighting] > max_accidents_per_block:
                    max_accidents_per_block = accidents_per_block[accident_block][accident_lighting]
        
            lines_read += 1

    # Open the output file
    with open('accidents_per_block.csv', 'w') as filout:
        for accident_block in accidents_per_block:
            accidents_per_block_raw = accidents_per_block[accident_block]['Insufficiente'] if 'Insufficiente' in accidents_per_block[accident_block] else '0'
            accidents_per_block_index = math.floor((accidents_per_block_raw / max_accidents_per_block) * 10)
            line_out_elements = [accident_block, accidents_per_block_raw, accidents_per_block_index]
            filout.write(','.join(line_out_elements) + '\n')
            lines_written += 1
    
    
    
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return




# Module execution: launch main method
if __name__ == '__main__':
    
    input_file_accidents = 'csv_incidenti_merge_20192020.csv'
    extract_lighting_index(input_file_accidents)

