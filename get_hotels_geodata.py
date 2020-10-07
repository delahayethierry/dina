import json
import math
import os
import requests
import config
import urllib3
import utils
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables
CITY_NAME = config.city_name
COUNTRY_NAME = config.country_name
room_types = ['SINGOLE','DOPPIE','TRIPLE','QUADRUPLE','QUINTUPLE','SESTUPLE']
# Env variables
HERE_API_KEY = os.getenv("here_api_key")
hotel_geolocation_cache = {}
# Main method
def get_hotel_geodata(input_file_hotels):

    # Initialize statistical dictionaries
    accommodation_capacity_per_block = {}
    max_accommodation_capacity_per_block = 1
    
    # General stats
    lines_read = 0
    lines_written = 0

    # Toggles whether the input is geolocalized
    geolocalized_input = False
    
    print('Starting to get accommodations geodata from ',input_file_hotels,' on ',datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    # Open the hotels file
    with open(input_file_hotels, encoding='utf-8') as filin_hotels:
        i=0

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
                        filout_accommodations_geolocated = open('output_data/hotels_geolocated.csv', 'w', encoding='utf-8')
                        filout_accommodations_geolocated.write(';'.join(headers + ['latitude','longitude']) + "\n")
            
                # General case: extract the line and parse the data
                else:
                    accommodation_address = ''
                    line_dict = utils.extract_line(headers, line_elements)

                    try:
                        accommodation_year = line_dict['Year']
                        accommodation_month = line_dict['Month']
                    except:
                        #dummy values in case of problem
                        accommodation_year = '2020'
                        accommodation_month = '01'
                    try:
                        accommodation_address = line_dict['INDIRIZZO']
                    except:
                        print('Issue with line: ',lines_read, ' (address) = ',line_elements)
                        
                    hotel_rooms = 0
                    accommodation_capacity = 0
                    try:
                        # We estimate here the maximum accommodation capacity. when a figure is provided under each room type (single, double, triple)
                        # we multiply the number of room x its maximum capacity
                        
                        for i, room_type in enumerate(room_types): 
                            nb_room = line_dict.get(room_type,'0').replace(',','.')
                           
                            if len(nb_room) > 0:
                                hotel_rooms += int(float(nb_room))
                                accommodation_capacity += int(float(nb_room))*(i+1)
                    except:
                        print('Issue with line: ',lines_read, ' (room types) = ',line_elements)
                    
                    # in the dataset, like B&B/independent apartment, the capacity per room is sometimes not provided. So we estimate arbitrarily that the
                    # capacity of the B&B apartment is 2 (as we don't have more information)
                    if accommodation_capacity == 0:
                        accommodation_capacity += 2
                    # Build the full address line
                    address_query = ', '.join([accommodation_address, CITY_NAME, COUNTRY_NAME])
                    #print(f'Parsed line: {hotel_address} - {hotel_rooms}')
                    
                    if geolocalized_input:
                        latitude = line_dict['latitude']
                        longitude = line_dict['longitude']
                        geolocalization_success = True
                    else:
                        # Test is address is in cache
                        if accommodation_address in hotel_geolocation_cache:
                            geolocalization_success = True
                            latitude = hotel_geolocation_cache[accommodation_address][0]
                            longitude = hotel_geolocation_cache[accommodation_address][1]
                            #print ('Found in cache lat/long for ', hotel_address)
                        else:
                            try:
                                geolocalization_success, latitude, longitude = utils.query_geolocalization(accommodation_address, CITY_NAME, COUNTRY_NAME, HERE_API_KEY)
                                if geolocalization_success:
                                    hotel_geolocation_cache[accommodation_address] = [latitude, longitude] #feed the cache with what we have found
                            except:
                                
                                geolocalization_success = False #There is an issue with the address or the geolocation API. We revet to -1, -1 coordinates which will be skipped later on
                                latitude = -1
                                longitude = -1
                                print('Issue with line: ',lines_read, ' (Geolocation API) = ',line_elements)
                    if geolocalization_success:
                        
                        accommodation_block_details = utils.get_city_block(longitude, latitude)
                        accommodation_block_name = accommodation_block_details['name']
                    
                        # Add the hotel to the statistics
                        if accommodation_block_name not in accommodation_capacity_per_block:
                            accommodation_capacity_per_block[accommodation_block_name] = accommodation_block_details
                            accommodation_capacity_per_block[accommodation_block_name]['accommodations_capacity'] = 0
                        accommodation_capacity_per_block[accommodation_block_name]['accommodations_capacity'] += accommodation_capacity
                        accommodation_capacity_per_block[accommodation_block_name]['Year'] = accommodation_year
                        accommodation_capacity_per_block[accommodation_block_name]['Month'] = accommodation_month
                        if accommodation_capacity_per_block[accommodation_block_name]['accommodations_capacity'] > max_accommodation_capacity_per_block:
                            max_accommodation_capacity_per_block = accommodation_capacity_per_block[accommodation_block_name]['accommodations_capacity']

                        # Save geolocalization if needed to avoid duplicate API calls
                        if not geolocalized_input:
                            filout_accommodations_geolocated.write(';'.join(line_elements + [str(latitude), str(longitude)])+'\n')
            
                lines_read += 1
                if lines_read % 50 == 0:
                    print(f'{lines_read} lines processed on', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

            except StopIteration:
                break
            except UnicodeDecodeError:
                print(f'Error: could not decode line {lines_read} {line}')


        # Close the geolocalized file if needed
        if not geolocalized_input:
            filout_accommodations_geolocated.close()

    # Open the output file
    with open('output_data/hotels.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('hotels')+ '\n')

        # Loop over the blocks and fill the lines
        for hotel_block in accommodation_capacity_per_block:
            hotel_rooms_block_details = accommodation_capacity_per_block[hotel_block]
            hotel_rooms_per_block_index = (hotel_rooms_block_details['accommodations_capacity'] / max_accommodation_capacity_per_block) * 10
            line_out_elements = [str(i) for i in [hotel_rooms_block_details['block_ID'], 
                                                  hotel_rooms_block_details['administrative_subdivision'], 
                                                  hotel_rooms_block_details['Year'], hotel_rooms_block_details['Month'], 
                                                  hotel_rooms_per_block_index]]
            filout.write(','.join(line_out_elements) + '\n')
            lines_written += 1
    
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return accommodation_capacity_per_block


# Module execution: launch main method
if __name__ == '__main__':
    
    #get_hotel_geodata(config.city_hotels_input_file)
    get_hotel_geodata(config.city_hotels_input_file_geolocated)

