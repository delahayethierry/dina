# File where the security indexes will be stored to generate the map 
security_needs_index_file = './map/security_needs_index.csv'
# File where the connectivity indexes will be stored to generate the map
connectivity_needs_index_file = './map/connectivity_needs_index.csv'
# File where the lighting indexes will be stored to generate the map
lighting_needs_index_file = './map/lighting_needs_index.csv'
#GeoJson file where the city "town halls"/Municipi shapes are stored
administrative_subdivision_geojson_file = "./input_data/municipi.geojson"
#municipi_lookup is a csv file which translates the way a municipi is called in various data sources into a unique ID (a number)
municipi_lookup = "./input_data/municipi_lookup.csv"
#Name of the city for the proof of concept
city_name = "Roma"
#Size of the blocks (grid to map a city): width & length in meters
block_width = 1000
block_height = 1000