import json
import math
import os
import requests
from datetime import datetime

# Local imports
import config
import utils
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Global variables
CITY_NAME = config.city_name
COUNTRY_NAME = config.country_name

# Env variables
HERE_API_KEY = os.getenv("here_api_key")
wifi_geolocation_cache = {}
# Main method
def get_wifi_logs_geodata(input_file_wifi):

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

    # Cache the street name / number lat/long so we don't query the same address twice
    addresses_coordinates = {}
    
    # Open the wifi file
    with open(input_file_wifi) as filin_wifi:
        
        while True:
            try:

                 # Extract the next line
                line = next(filin_wifi)
                line_elements = line.replace('"','').strip('\n').split(';')


                # First line: headers - Only open the geolocalized file if the input is not geolocalized
                if lines_read == 0:
                    headers = line_elements
                    print("Reading " + input_file_wifi)
                    if 'longitude'  in headers and 'latitude' in headers:
                        geolocalized_input = True
                    else:
                        filout_wifi_geolocated = open('output_data/wifi_geolocated.csv', 'w')
                        filout_wifi_geolocated.write(';'.join(headers + ['latitude','longitude']) + '\n')
            
                # General case: extract the line and parse the data
                else:
                    line_dict = utils.extract_line(headers, line_elements)
                    
                    # Build the address
                    address_street_type = line_dict['DUG']
                    address_street_name = line_dict['DUF']
                    address_street_number = line_dict['CIVICO']
                    address_full = f'{address_street_number}, {address_street_type} {address_street_name}'

                    # Parse the date
                    session_date = datetime.strptime(line_dict['STARTDATE'].replace(',',''),"%d/%m/%Y")
                    session_year = session_date.year
                    session_month = session_date.month
                    session_year_month = (session_year, session_month)

                    # If no address, do not geolocalize. If there is, try the cache
                    if address_street_name == '':
                        geolocalization_success = False
                    elif geolocalized_input:
                        latitude = line_dict['latitude']
                        longitude = line_dict['longitude']
                        geolocalization_success = True
                    elif address_full in addresses_coordinates:
                        latitude, longitude = addresses_coordinates[address_full] 
                        geolocalization_success = True
                    else:
                        geolocalization_success, latitude, longitude = utils.query_geolocalization(address_full, CITY_NAME, COUNTRY_NAME, HERE_API_KEY)
                        #print(f'Geolocalization for {address_full}: {geolocalization_success}, {latitude}, {longitude}')
                        addresses_coordinates[address_full] = (latitude, longitude)

                    # If we have a geolocalization, add the wifi usage to the stats
                    if geolocalization_success:
                        wifi_block_details = utils.get_city_block(longitude, latitude)
                        wifi_block_name = wifi_block_details['name']
                    
                        # Add the wifi usage to the statistics
                        if wifi_block_name not in wifi_usage_per_block:
                            wifi_usage_per_block[wifi_block_name] = wifi_block_details
                            wifi_usage_per_block[wifi_block_name]['usage_per_month'] = {}
                        if session_year_month not in wifi_usage_per_block[wifi_block_name]['usage_per_month']:
                            wifi_usage_per_block[wifi_block_name]['usage_per_month'][session_year_month] = {}
                            wifi_usage_per_block[wifi_block_name]['usage_per_month'][session_year_month]['wifi_usage'] = 0
                        wifi_usage_per_block[wifi_block_name]['usage_per_month'][session_year_month]['wifi_usage'] += float(line_dict['DOWNLOAD'])
                        if wifi_usage_per_block[wifi_block_name]['usage_per_month'][session_year_month]['wifi_usage'] > max_wifi_usage_per_block:
                            max_wifi_usage_per_block = wifi_usage_per_block[wifi_block_name]['usage_per_month'][session_year_month]['wifi_usage']

                        # Save geolocalization if needed to avoid duplicate API calls
                        if not geolocalized_input:
                            filout_wifi_geolocated.write(';'.join(line_elements + [str(latitude), str(longitude)]) + '\n')
            
                # Logging
                lines_read += 1
                if lines_read % 1000 == 0:
                    print(f'Read {lines_read} lines')

            # Error handling
            except StopIteration:
                break
            except UnicodeDecodeError:
                print(f'Error: could not decode line {lines_read}')

        # Close the geolocalized file if needed
        #if not geolocalized_input:
        #    filout_wifi_geolocated.close()
        #Removed this line because it was causing an issue
    # Open the output file
    with open('output_data/wifi.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('wifi')+ '\n')

        # Loop over the blocks and fill the lines
        for wifi_block in wifi_usage_per_block:
            wifi_usage_block_details = wifi_usage_per_block[wifi_block]
            for session_year_month in wifi_usage_per_block[wifi_block]['usage_per_month']:
                wifi_usage_per_block_index = (wifi_usage_block_details['usage_per_month'][session_year_month]['wifi_usage'] / max_wifi_usage_per_block) * 10
                line_out_elements = [str(i) for i in [wifi_usage_block_details['block_ID'], wifi_usage_block_details['administrative_subdivision'], session_year_month[0], session_year_month[1], wifi_usage_per_block_index]]
                filout.write(','.join(line_out_elements) + '\n')
                lines_written += 1
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return wifi_usage_per_block




# Module execution: launch main method
if __name__ == '__main__':
    
    #get_wifi_geodata(config.city_wifi_input_file)
    get_wifi_logs_geodata(config.city_wifi_input_file_geolocated)

