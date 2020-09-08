import math
import utils

import get_accidents_geodata
import get_hotel_geodata


# Main method
def extract_lighting_index():

    # Input files - this can be replaced by cache
    input_file_hotels = 'hotel_locations.csv'
    input_file_accidents = 'csv_incidenti_merge_20192020.csv'

    hotel_rooms_per_block = get_hotel_geodata.get_hotel_geodata(input_file_hotels)
    accidents_per_block = get_accidents_geodata.get_accidents_geodata(input_file_accidents)

    # TODO combine the datasets

    return




# Module execution: launch main method
if __name__ == '__main__':
    
    extract_lighting_index()

