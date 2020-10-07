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
    lines_written_for_lighting_claims = 0
    lines_written_for_security_claims = 0

    # Dummy year and month variables
    year = '2020'
    month = '01'


    # Open the wifi file
    with open(input_file_claims) as filin_claims:
        
        while True:
            try:
                line = next(filin_claims)
                line_elements = line.replace('"','').strip('\n').split(';')

                # First line: headers - Only open the geolocalized file if the input is not geolocalized
                if lines_read == 0:
                    headers = line_elements
                    print("Reading " + input_file_claims)
                 
           
                # General case: extract the line and parse the data
                else:
                    line_dict = utils.extract_line(headers, line_elements)

                    # Parse the date
                    #claims_date = datetime.strptime(line_dict['Data di presentazione'].replace(',',''),"%d/%m/%Y")
                    claim_year = int(line_dict['Year'])
                    claim_month = int(line_dict['Month'])
                    claim_year_month = (claim_year, claim_month)

                    # Parse other features
                    claim_administrative_subdivision = line_dict['Municipio di riferimento (tramite geo-localizzazione)']                        
                    
                    # Do not process claims where administrative subdivision is not specified
                    if claim_administrative_subdivision != "n.d.":
                        claim_associated_blocks =  []
                        
                        claim_typecode = line_dict['Argomento - codice']

                        # Claim types. 150 is lighting, second list is security linked based on Roma City claim management system
                        claim_type = None
                        if claim_typecode in ['150']:
                            claim_associated_blocks =  utils.get_city_blocks_from_administrative_subdivision(claim_administrative_subdivision)
                            
                            
                            for lighting_claim_block_details in claim_associated_blocks:
                                
                                lighting_claim_block_name = lighting_claim_block_details['name']
                            
                                # Add the claims to the statistics
                                if lighting_claim_block_name not in lighting_related_claims_per_block:
                                    lighting_related_claims_per_block[lighting_claim_block_name] = lighting_claim_block_details
                                    lighting_related_claims_per_block[lighting_claim_block_name]['claims_per_month'] = {}
                            
                                if claim_year_month not in lighting_related_claims_per_block[lighting_claim_block_name]['claims_per_month']:
                                    lighting_related_claims_per_block[lighting_claim_block_name]['claims_per_month'][claim_year_month] = {}
                                    lighting_related_claims_per_block[lighting_claim_block_name]['claims_per_month'][claim_year_month]['nb_claims'] = 0
                                lighting_related_claims_per_block[lighting_claim_block_name]['claims_per_month'][claim_year_month]['nb_claims'] += 1
                                
                                if lighting_related_claims_per_block[lighting_claim_block_name]['claims_per_month'][claim_year_month]['nb_claims'] > max_lighting_related_claims_per_block:
                                    max_lighting_related_claims_per_block = lighting_related_claims_per_block[lighting_claim_block_name]['claims_per_month'][claim_year_month]['nb_claims']
                            
                        else:        
                            if claim_typecode in ['296','298','258','259','380','48','288','47','319','49','300','50']:
                                claim_associated_blocks =  utils.get_city_blocks_from_administrative_subdivision(claim_administrative_subdivision)
                                
                                for security_claim_block_details in claim_associated_blocks:
                                        
                                        security_claim_block_name = security_claim_block_details['name']
                                    
                                        # Add the claims to the statistics
                                        if security_claim_block_name not in security_related_claims_per_block:
                                            security_related_claims_per_block[security_claim_block_name] = security_claim_block_details
                                            security_related_claims_per_block[security_claim_block_name]['claims_per_month'] = {}
                                    
                                        if claim_year_month not in security_related_claims_per_block[security_claim_block_name]['claims_per_month']:
                                            security_related_claims_per_block[security_claim_block_name]['claims_per_month'][claim_year_month] = {}
                                            security_related_claims_per_block[security_claim_block_name]['claims_per_month'][claim_year_month]['nb_claims'] = 0
                                        security_related_claims_per_block[security_claim_block_name]['claims_per_month'][claim_year_month]['nb_claims'] += 1
                                        
                                        if security_related_claims_per_block[security_claim_block_name]['claims_per_month'][claim_year_month]['nb_claims'] > max_security_related_claims_per_block:
                                            max_security_related_claims_per_block = security_related_claims_per_block[security_claim_block_name]['claims_per_month'][claim_year_month]['nb_claims']                            
                        
                
                lines_read += 1
                if lines_read % 500 == 0:
                    print(f'Read {lines_read} lines')

            except StopIteration:
                break
            except UnicodeDecodeError:
                print(f'Error: could not decode line {lines_read}')

    # Need to save the 2 files
    
    # Open the lighting_claims output file
    with open('output_data/lighting_claims.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('lighting_claims')+ '\n')

        # Loop over the blocks and fill the lines
        for lighting_claim_block in lighting_related_claims_per_block:
            lighting_claim_block_details = lighting_related_claims_per_block[lighting_claim_block]
            
            for claim_year_month in lighting_claim_block_details['claims_per_month']:
                lighting_claims_per_block_index = (lighting_claim_block_details['claims_per_month'][claim_year_month]['nb_claims'] / max_lighting_related_claims_per_block) * 10
                line_out_elements = [str(i) for i in [lighting_claim_block_details['block_ID'], lighting_claim_block_details['administrative_subdivision'], 
                                                      claim_year_month[0], claim_year_month[1], lighting_claims_per_block_index]]
                filout.write(','.join(line_out_elements) + '\n')
                
                lines_written_for_lighting_claims += 1
    
    # Open the security_claims output file
    with open('output_data/security_claims.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('security_claims')+ '\n')

        # Loop over the blocks and fill the lines
        for security_claim_block in security_related_claims_per_block:
            security_claim_block_details = security_related_claims_per_block[security_claim_block]
            for claim_year_month in security_claim_block_details['claims_per_month']:
                security_claims_per_block_index = (security_claim_block_details['claims_per_month'][claim_year_month]['nb_claims'] / max_security_related_claims_per_block) * 10
                line_out_elements = [str(i) for i in [security_claim_block_details['block_ID'], security_claim_block_details['administrative_subdivision'], 
                                                      claim_year_month[0], claim_year_month[1], security_claims_per_block_index]]
                filout.write(','.join(line_out_elements) + '\n')
                lines_written_for_security_claims += 1
    
    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines for lighting claims: {lines_written_for_lighting_claims}')
    print(f'Written lines for security claims: {lines_written_for_security_claims}')

    #return security_related_claims_per_block






# Module execution: launch main method
if __name__ == '__main__':
    
    get_claims_geodata(config.city_claims_input_file)

