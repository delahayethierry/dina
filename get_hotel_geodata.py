import json
import math
import os
import requests
import config

import utils

# Global variables
CITY_NAME = config.city_name
COUNTRY_NAME = config.country_name
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

    # Toggles whether the input is geolocalized
    geolocalized_input = False
    
    # Open the hotels file
    with open(input_file_hotels) as filin_hotels:
        
        while True:
            try:
                line = next(filin_hotels)

                line_elements = line.strip('\n').split(';')

                # First line: headers
                if lines_read == 0:
                    headers = line_elements
                    if 'longitude'  in headers and 'latitude' in headers:
                        geolocalized_input = True
                    else:
                        filout_hotels_geolocated = open('output_data/hotels_geolocated.csv', 'w')
                        filout_hotels_geolocated.write(';'.join(headers + ['latitude','longitude']) + '\n')
            
                # General case: extract the line and parse the data
                else:
                    line_dict = utils.extract_line(headers, line_elements)
                    
                    hotel_address = line_dict['INDIRIZZO']
                    hotel_rooms = 0
                    for room_type in ['SINGOLE','DOPPIE','TRIPLE','QUADRUPLE','QUINTUPLE','SESTUPLE']:
                        if len(line_dict[room_type]) > 0:
                            hotel_rooms += int(line_dict[room_type])

                    # Build the full address line
                    address_query = ', '.join([hotel_address, CITY_NAME, COUNTRY_NAME])
                    #print(f'Parsed line: {hotel_address} - {hotel_rooms}')
                    
                    if geolocalized_input:
                        latitude = line_dict['latitude']
                        longitude = line_dict['longitude']
                        geolocalization_success = True
                    else:
                        geolocalization_success, latitude, longitude = query_geolocalization(hotel_address)

                    if geolocalization_success:
                        hotel_block_details = utils.get_city_block(longitude, latitude)
                        hotel_block_name = hotel_block_details['name']
                    
                        # Add the hotel to the statistics
                        if hotel_block_name not in hotel_rooms_per_block:
                            hotel_rooms_per_block[hotel_block_name] = hotel_block_details
                            hotel_rooms_per_block[hotel_block_name]['rooms'] = 0
                        hotel_rooms_per_block[hotel_block_name]['rooms'] += hotel_rooms
                        if hotel_rooms_per_block[hotel_block_name]['rooms'] > max_hotel_rooms_per_block:
                            max_hotel_rooms_per_block = hotel_rooms_per_block[hotel_block_name]['rooms']

                        # Save geolocalization if needed to avoid duplicate API calls
                        if not geolocalized_input:
                            filout_hotels_geolocated.write(';'.join(line_elements + [str(latitude), str(longitude)]))
            
                lines_read += 1
                if lines_read % 1000 == 0:
                    print(f'Read {lines_read} lines')

            except StopIteration:
                break
            except UnicodeDecodeError:
                print(f'Error: could not decode line {lines_read}')


        # Close the geolocalized file if needed
        if not geolocalized_input:
            filout_hotels_geolocated.close()

    # Open the output file
    with open('output_data/hotels.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('hotels')+ '\n')

        # Loop over the blocks and fill the lines
        for hotel_block in hotel_rooms_per_block:
            hotel_rooms_block_details = hotel_rooms_per_block[hotel_block]
            hotel_rooms_per_block_index = (hotel_rooms_block_details['rooms'] / max_hotel_rooms_per_block) * 10
            line_out_elements = [str(i) for i in [hotel_rooms_block_details['block_ID'], hotel_rooms_block_details['administrative_subdivision'], year, month, hotel_rooms_per_block_index]]
            filout.write(','.join(line_out_elements) + '\n')
            lines_written += 1
    
    
    
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return hotel_rooms_per_block



def query_geolocalization(hotel_address):

    # General variables
    geolocation_url = 'https://geocode.search.hereapi.com/v1/geocode'

    # Build the full address line
    address_query = ', '.join([hotel_address, CITY_NAME, COUNTRY_NAME])
    
    # Build the geolocation request
    address_query_params = {
        "q": address_query, 
        'apikey': HERE_API_KEY
    }
    response = requests.get(geolocation_url, params=address_query_params)
    response_json = json.loads(response.text)

    # If response successful, fill the coordinates. Else, put dummy values
    if len(response_json['items']) > 0:
        geolocalization_success = True
        longitude = response_json['items'][0]['position']['lng']
        latitude = response_json['items'][0]['position']['lat']
    else:
        geolocalization_success = False
        longitude = -1
        latitude = -1

    return geolocalization_success, latitude, longitude




# Module execution: launch main method
if __name__ == '__main__':
    
    get_hotel_geodata(config.city_hotels_input_file_geolocated)

