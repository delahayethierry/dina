import json
import math
import os
import requests
from datetime import datetime

# Local imports
import config
import utils


# Main method
def get_claims_geodata(input_file_claims):

    # Initialize statistical dictionaries
    security_related_claims_per_block = {}
    lighting_related_claims_per_block = {}
    max_security_related_claims_per_block = 1
    max_lighting_related_claims_per_block = 1
    
    # General stats
    lines_read = 0
    lines_written = 0

    # Dummy year and month variables
    year = '2020'
    month = '01'

    # Toggles whether the input is geolocalized
    geolocalized_input = False

    # Open the wifi file
    with open(input_file_claims) as filin_claims:
        
        while True:
            try:
                line = next(filin_claims)
                line_elements = line.replace('"','').strip('\n').split(';')

                # First line: headers - Only open the geolocalized file if the input is not geolocalized
                if lines_read == 0:
                    headers = line_elements
                    print("Reading " + input_file_wifi)
                    
                    if 'longitude'  in headers and 'latitude' in headers:
                        geolocalized_input = True
                    else:
                        filoutclaims_geolocated = open('output_data/claims_geolocated.csv', 'w')
                        filoutclaims_geolocated.write(';'.join(headers + ['latitude','longitude']) + '\n')
            
                # General case: extract the line and parse the data
                else:
                    line_dict = utils.extract_line(headers, line_elements)

                    # Parse the date
                    claims_date = datetime.strptime(line_dict['Data di presentazione'].replace(',',''),"%d/%m/%Y")
                    claim_year = claims_date.year
                    claim_month = claims_date.month
                    claim_year_month = (session_year, session_month)

                    # Parse other features
                    claim_administrative_division = line_dict['Municipio di riferimento (tramite geo-localizzazione)']
                    claim_typecode = line_dict['Argomento - codice']

                    # Claim types. 150 is lighting, second list is security linked
                    claim_type = None
                    if claim_typecode in ['150']:
                        claim_type = 'Lighting'
                    if claim_typecode in ['296','298','258','259','380','48','288','47','319','49','300','50']:
                        claim_type = 'Security'

                    # Lighting claim
                    if claim_typecode in ['150']:
                        if claim_administrative_division in lighting_related_claims_per_block:
                            lighting_related_claims_per_block[claim_administrative_division] = 0
                        lighting_related_claims_per_block[claim_administrative_division] += 1
                        if lighting_related_claims_per_block[claim_administrative_division] > max_lighting_related_claims_per_block:
                            max_lighting_related_claims_per_block = lighting_related_claims_per_block[claim_administrative_division]

                    # Security claim
                    elif claim_typecode in ['296','298','258','259','380','48','288','47','319','49','300','50']:
                        if claim_administrative_division in security_related_claims_per_block:
                            security_related_claims_per_block[claim_administrative_division] = 0
                        security_related_claims_per_block[claim_administrative_division] += 1
                        if security_related_claims_per_block[claim_administrative_division] > max_security_related_claims_per_block:
                            max_security_related_claims_per_block = security_related_claims_per_block[claim_administrative_division]
            
                lines_read += 1
                if lines_read % 1000 == 0:
                    print(f'Read {lines_read} lines')

            except StopIteration:
                break
            except UnicodeDecodeError:
                print(f'Error: could not decode line {lines_read}')

        # Close the geolocalized file if needed
        if not geolocalized_input:
            filoutclaims_geolocated.close()

    # Open the output file
    with open('output_data/wifi.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('wifi')+ '\n')

        # Loop over the blocks and fill the lines
        for wifi_block in security_related_claims_per_block:
            wifi_usage_block_details = security_related_claims_per_block[wifi_block]
            for session_year_month in security_related_claims_per_block[wifi_block]['usage_per_month']:
                wifi_usage_per_block_index = (wifi_usage_block_details['usage_per_month'][session_year_month]['wifi_usage'] / max_wifi_usage_per_block) * 10
                line_out_elements = [str(i) for i in [wifi_usage_block_details['block_ID'], wifi_usage_block_details['administrative_subdivision'], session_year_month[0], session_year_month[1], wifi_usage_per_block_index]]
                filout.write(','.join(line_out_elements) + '\n')
                lines_written += 1
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')

    return security_related_claims_per_block






# Module execution: launch main method
if __name__ == '__main__':
    
    get_claims_geodata(config.claims_wifi_input_file)

