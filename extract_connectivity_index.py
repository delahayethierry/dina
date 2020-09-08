import math
import utils

import get_hotel_geodata


# Main method
def extract_connectivity_index():

    # Input files - this can be replaced by cache
    input_file_hotels = 'hotel_locations.csv'

    hotel_rooms_per_block = get_hotel_geodata.get_hotel_geodata(input_file_hotels)

    # TODO combine the datasets

    return




# Module execution: launch main method
if __name__ == '__main__':
    
    extract_connectivity_index()

