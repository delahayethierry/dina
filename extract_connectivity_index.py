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
def extract_connectivity_index(input_file_hotels):

    # Initialize statistical dictionaries
    hotel_rooms_per_block = {}
    max_hotel_rooms_per_block = 1
    
    # General stats
    lines_read = 0
    lines_written = 0
    
    # General variables
    geolocation_url = 'https://geocode.search.hereapi.com/v1/geocode'
    
    # Open the hotels file
    with open(input_file_hotels) as filin_hotels:
        
        for line in filin_hotels:
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
                    hotel_block = utils.extract_block_float(longitude, latitude)
                
                    # Add the hotel to the statistics
                    if hotel_block not in hotel_rooms_per_block:
                        hotel_rooms_per_block[hotel_block] = 0
                    hotel_rooms_per_block[hotel_block] += hotel_rooms
                    if hotel_rooms_per_block[hotel_block] > max_hotel_rooms_per_block:
                        max_hotel_rooms_per_block = hotel_rooms_per_block[hotel_block]
        
            lines_read += 1

    # Open the output file
    with open('hotels_per_block.csv', 'w') as filout:
        for hotel_block in hotel_rooms_per_block:
            hotel_rooms_per_block_raw = hotel_rooms_per_block[hotel_block]
            hotel_rooms_per_block_index = math.floor((hotel_rooms_per_block_raw / max_hotel_rooms_per_block) * 10)
            line_out_elements = [str(i) for i in [hotel_block, hotel_rooms_per_block_raw, hotel_rooms_per_block_index]]
            filout.write(','.join(line_out_elements) + '\n')
            lines_written += 1
    
    
    
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return





# Module execution: launch main method
if __name__ == '__main__':
    
    input_file_hotels = 'hotel_locations.csv'
    extract_connectivity_index(input_file_hotels)

