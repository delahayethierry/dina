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
def get_hotel_geodata(input_file_hotels):

    # Initialize statistical dictionaries
    hotel_rooms_per_block = {}
    max_hotel_rooms_per_block = 1
    
    # General stats
    lines_read = 0
    lines_written = 0

    # Dummy year and month variables
    year = '2020'
    month = '01'
    
    # General variables
    geolocation_url = 'https://geocode.search.hereapi.com/v1/geocode'
    
    # Open the hotels file
    with open(input_file_hotels) as filin_hotels:
        
        while True:
            try:
                line = next(filin_hotels)

                line_elements = line.split(';')

                # First line: headers
                if lines_read == 0:
                    headers = line_elements
            
                # General case: extract the line and parse the data
                else:
                    line_dict = utils.extract_line(headers, line_elements)
                    
                    hotel_address = line_dict['INDIRIZZO']
                    hotel_rooms = int(line_dict['SINGOLE']) + int(line_dict['SINGOLE']) + int(line_dict['DOPPIE']) + int(line_dict['TRIPLE']) + int(line_dict['QUADRUPLE']) + int(line_dict['QUINTUPLE']) + int(line_dict['SESTUPLE'])
                    
                    # Build the full address line
                    address_query = ', '.join([hotel_address, CITY_NAME, COUNTRY_NAME])
                    print(f'Parsed line: {hotel_address} - {hotel_rooms}')
                    
                    # Build the geolocation request
                    leg_data_json = {
                        "q": address_query, 
                        'apikey': HERE_API_KEY
                    }
                    response = requests.get(geolocation_url, params=leg_data_json)
                    print(f'Out: {response.text}')
                    response_json = json.loads(response.text)
                    if len(response_json['items']) > 0:
                        longitude = response_json['items'][0]['position']['lng']
                        latitude = response_json['items'][0]['position']['lat']
                        print(longitude, latitude)
                        hotel_block_details = utils.extract_block_float(longitude, latitude)
                        hotel_block_name = hotel_block_details['name']
                    
                        # Add the hotel to the statistics
                        if hotel_block_name not in hotel_rooms_per_block:
                            hotel_rooms_per_block[hotel_block_name] = hotel_block_details
                            hotel_rooms_per_block[hotel_block_name]['rooms'] = 0
                        hotel_rooms_per_block[hotel_block_name]['rooms'] += hotel_rooms
                        if hotel_rooms_per_block[hotel_block_name]['rooms'] > max_hotel_rooms_per_block:
                            max_hotel_rooms_per_block = hotel_rooms_per_block[hotel_block_name]['rooms']
            
                lines_read += 1

            except StopIteration:
                break
            except UnicodeDecodeError:
                print(f'Error: could not decode line {lines_read}')

    # Open the output file
    with open('map/connectivity_needs_index.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers()+ '\n'))

        # Loop over the blocks and fill the lines
        for hotel_block in hotel_rooms_per_block:
            hotel_rooms_block_details = hotel_rooms_per_block[hotel_block]
            hotel_rooms_per_block_index = math.floor((hotel_rooms_block_details['rooms'] / max_hotel_rooms_per_block) * 10)
            line_out_elements = [str(i) for i in [hotel_rooms_block_details['longitude'], hotel_rooms_block_details['latitude'], year, month, hotel_rooms_per_block_index]]
            filout.write(','.join(line_out_elements) + '\n')
            lines_written += 1
    
    
    
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return hotel_rooms_per_block





# Module execution: launch main method
if __name__ == '__main__':
    
    input_file_hotels = 'hotel_locations.csv'
    get_hotel_geodata(input_file_hotels)

