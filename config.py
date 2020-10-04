# File where the security indexes will be stored to generate the map 
security_needs_index_file = './map/security_needs_index.csv'
# File where the connectivity indexes will be stored to generate the map
connectivity_needs_index_file = './map/connectivity_needs_index.csv'
# File where the lighting indexes will be stored to generate the map
lighting_needs_index_file = './map/lighting_needs_index.csv'

#Name of the city and country for the proof of concept. Used for display and call to the Here! geocoding API
city_name = "Rome"
country_name = "Italy"

#
# Size of the blocks (grid to map a city): width & length in meters
block_width = 800
block_height = 800
# File where should be generated the city grid geojson file
city_grid_geojson_file='./input_data/city_grid.geojson'
city_grid_csv_file='./input_data/city_grid.csv'
# GeoJson file where the city "town halls"/Municipi shapes are stored
administrative_subdivision_geojson_file = "./input_data/administrative_subdivision.geojson"
# administrative_subdivision_lookup is a csv file which translates the way a municipi is called in various data sources into a unique ID (a number)
administrative_subdivision_lookup = "./input_data/administrative_subdivision_lookup.csv"



#File where we consolidated accidents from the Roma Open Data portal
city_accidents_input_file = 'input_data/csv_incidenti_merge_20192020.csv' 

#File where we consolidated acomodations/hotels from the Roma Open Data portal
city_hotels_input_file_geolocated = 'input_data/hotel_locations_geolocalized.csv'
city_hotels_input_file = 'input_data/hotel_locations.csv'


#File where we consolidated anonimized wifi logs from the Roma Open Data portal
city_wifi_input_file = 'input_data/wifi_geolocated.csv'

#Index calculation. 
# Define the lighting, security and connectivity needs indexes by combining input data sources (here hotels/accomodations, accidents, public wifi logs) with customized weights
# In the example below, we estimate the need for public lighting by combining 3 Open Data sources (city of Rome, Italy):
# - Normalized index per block based on the number of accidents per month, which contributes to 50% of the lighting need index
# - Normalized index per block based on the number of wifi sessions per month (mainly used by tourists), which contributes to 20% of the lighting need index
# - Normalized index per block based on the number of accomodations (mainly used by tourists), which contributes to 30% of the lighting need index
# It is assumed here that tourists are more likely to go back to their hotel later than citizens, and that improved lighting will make the city safer
# and more attractive from their point of view. This is why trouristic-related data sources are used to calculate the lighting needs index
indexes_calculation_parameters = {
    'lighting': {
        'accidents': 0.5,
        'hotels': 0.3,
        'wifi': 0.2
    },
    'connectivity': {
        'hotels': 0.7,
        'wifi': 0.3
    },
    'security': {
        'accidents': 1
    },
}
