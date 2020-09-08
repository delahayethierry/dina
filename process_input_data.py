import get_accidents_geodata
import get_hotel_geodata


# Processes all of the input data. Some of the inputs require getting additional data from APIs (typically geocoding)
def process_input_data():

    input_file_accidents = 'input_data/csv_incidenti_merge_20192020.csv'
    get_accidents_geodata.get_accidents_geodata(input_file_accidents)
    
    input_file_hotels = 'input_data/hotel_locations.csv'
    get_hotel_geodata.get_hotel_geodata(input_file_hotels)

    return


# Module execution: launch main method
if __name__ == '__main__':
    
    process_input_data()




