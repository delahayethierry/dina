import json
import math
import os
import requests

import utils

# Global variables
CITY_NAME = 'Rome'
COUNTRY_NAME = 'Italy'

# Env variables
HERE_API_KEY = os.getenv("here_api_key")

# Main method
def get_wifi_geodata(input_file_wifi):

    # Initialize statistical dictionaries
    wifi_usage_per_block = {}
    max_wifi_usage_per_block = 1
    
    # General stats
    lines_read = 0
    lines_written = 0

    # Dummy year and month variables
    year = '2020'
    month = '01'

    # Toggles whether the input is geolocalized
    geolocalized_input = False

    # TODO: cache the street name / number lat/long so we don't query the same address twice
    addresses_coordinates = {}
    
    # Open the wifi file
    with open(input_file_wifi) as filin_wifi, open('output_data/wifi_geolocated.csv', 'w') as filout_wifi_geolocated:
        
        while True:
            try:
                line = next(filin_wifi)

                line_elements = line.strip('\n').split(';')

                # First line: headers
                if lines_read == 0:
                    headers = line_elements
                    if 'longitude'  in headers and 'latitude' in headers:
                        geolocalized_input = True
            
                # General case: extract the line and parse the data
                else:
                    line_dict = utils.extract_line(headers, line_elements)
                    
                    # Build the address
                    address_street_type = line_dict['DUG']
                    address_street_name = line_dict['DUF']
                    address_street_number = line_dict['CIVICO']
                    address_full = f'{address_street_number}, {address_street_type} {address_street_name}'

                    # Build the full address line
                    
                    if geolocalized_input:
                        latitude = line_dict['latitude']
                        longitude = line_dict['longitude']
                        geolocalization_success = True
                    elif address_query in addresses_coordinates:
                        latitude, longitude = addesses_coordinates[address_query] 
                        geolocalization_success = True
                    else:
                        geolocalization_success, latitude, longitude = utils.query_geolocalization(address_full, CITY_NAME, COUNTRY_NAME)
                        addresses_coordinates[address_query] = (latitude, longitude)

                    if geolocalization_success:
                        wifi_block_details = utils.get_city_block(longitude, latitude)
                        wifi_block_name = wifi_block_details['name']
                    
                        # Add the wifi usage to the statistics
                        if wifi_block_name not in wifi_usage_per_block:
                            wifi_usage_per_block[wifi_block_name] = wifi_block_details
                            wifi_usage_per_block[wifi_block_name]['wifi_usage'] = 0
                        wifi_usage_per_block[wifi_block_name]['wifi_usage'] += 1
                        if wifi_usage_per_block[wifi_block_name]['wifi_usage'] > max_wifi_usage_per_block:
                            max_wifi_usage_per_block = wifi_usage_per_block[wifi_block_name]['wifi_usage']

                        # Save geolocalization if needed to avoid duplicate API calls
                        if not geolocalized_input:
                            filout_wifi_geolocated.write(';'.join(line_elements + [str(latitude), str(longitude)]))
            
                lines_read += 1
                # TODO for test (avoid too many calls dring test)
                if lines_read == 10:
                    break
                if lines_read % 1000 == 0:
                    print(f'Read {lines_read} lines')

            except StopIteration:
                break
            except UnicodeDecodeError:
                print(f'Error: could not decode line {lines_read}')

    # Open the output file
    with open('output_data/wifi.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('wifi')+ '\n')

        # Loop over the blocks and fill the lines
        for wifi_block in wifi_usage_per_block:
            wifi_usage_block_details = wifi_usage_per_block[wifi_block]
            wifi_usage_per_block_index = (wifi_usage_block_details['wifi_usage'] / max_wifi_usage_per_block) * 10
            line_out_elements = [str(i) for i in [wifi_usage_block_details['block_ID'], wifi_usage_block_details['administrative_subdivision'], year, month, wifi_usage_per_block_index]]
            filout.write(','.join(line_out_elements) + '\n')
            lines_written += 1
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return wifi_usage_per_block






# Module execution: launch main method
if __name__ == '__main__':
    
    input_file_wifi = 'input_data/wifi_usage_rome_202006.csv'
    get_wifi_geodata(input_file_wifi)

