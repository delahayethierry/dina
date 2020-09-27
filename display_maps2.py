# Install Folium beforehands: pip install folium, pip install pandas
import os
import sys
import webbrowser
from math import ceil
import datetime

import folium
import numpy as np
import ogr
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import pyproj
from folium import FeatureGroup, LayerControl, Map, Marker, plugins

import config as config
import utils


def createHeatMapWithTimeFromIndexFile(indexFile):
    print("Generating HeatMap from " + indexFile)

    # Read data files generated by the DINA Open Data Ingestion module for the city of Roma, Italy
    index_df = pd.read_csv(indexFile, dtype=object)
    # print(index_df.head(5)) #print 5 first rows to check in the logs

    # Ensure we are handling Lat/Long as floats
    index_df['Latitude'] = index_df['Latitude'].astype(float)
    index_df['Longitude'] = index_df['Longitude'].astype(float)

    # Filter the data file for rows, then columns to display 2020 data only
    #heatmap_index_df = index_df[index_df['Year']=='2020']
    #heatmap_index_df = index_df[['Latitude', 'Longitude']]

    heatmap_index_df = index_df

    # Prepare the Data Frame to generate the heatmap
    heatmap_index_df['Index'] = heatmap_index_df['Index'].astype(float)
    heatmap_index_df = heatmap_index_df.dropna(
        axis=0, subset=['Latitude', 'Longitude', 'Index'])
    heatmap_index_df['Month'] = heatmap_index_df['Month'].sort_values(
        ascending=True)

    heat_data = []
    for _, d in heatmap_index_df.groupby('Month'):
        heat_data.append(
            [[row['Latitude'], row['Longitude'], row['Index']] for _, row in d.iterrows()])

    # Plot data on the map
    # heatMapIndex = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep'] #we are using 2020 data so datasets stops in Sep 2020
    heatmap_from_index = plugins.HeatMapWithTime(heat_data, auto_play=False, min_opacity=0.05, radius=175,
                                                 max_opacity=0.3, use_local_extrema=True, gradient={0.0: 'lime', 0.7: 'orange', 1.0: 'red'})

    return heatmap_from_index

# Example of market that we could add for security inded (but the best is to have a heatmap)
# Marker(location=[41.902782,  12.496366],
#       popup='Security Index 2/10').add_to(feature_group_security_needs)


def createMap(filename, mapname):
    # Define coordinates of where we want to center our map (here, Roma in Italy)
    city_coords = [41.902782,  12.496366]
    city_map = folium.Map(location=city_coords,
                          zoom_start=14, min_zoom=13, max_zoom=15)
    folium.TileLayer('cartodbpositron').add_to(city_map)
    createHeatMapWithTimeFromIndexFile(filename).add_to(city_map)
    folium.LayerControl().add_to(city_map)

    # Save the map and display it using a web browser
    mapFileName = os.path.join(
        'map', 'DINA_' + mapname.replace(" ", "_") + '.html')
    city_map.save(mapFileName)
    print("Saving the generated map in: " + mapFileName)
    webbrowser.open(mapFileName, new=2)

def generate_blocks_for_hotels():
    hotels_before_df = pd.read_csv(
        './output_data/hotels.csv', names=['Latitude', 'Longitude', 'Year', 'Month', 'Hotels'])
    print(hotels_before_df.head(5))
    block_names = [utils.extract_block(x, y)
                   for x, y in zip(hotels_before_df['Longitude'], hotels_before_df['Latitude'])]
    hotels_after_df = pd.DataFrame(block_names)
    
    hotels_after_df['Year'] = hotels_before_df['Year'].values
    hotels_after_df['Month'] = hotels_before_df['Month'].values
    hotels_after_df['Hotels'] = hotels_before_df['Hotels'].values
    
    print(hotels_after_df.head(5))
    hotels_after_df.to_csv('output_data/hotels2.csv')
    


def generate_blocks_for_hotels2():
    hotels_per_block = {}
    max_hotels_per_block = 0

    # General stats
    lines_read = 0
    lines_written = 0
     # Open the accidents file
    with open('./output_data/hotels.csv') as filin_hotels:

        for line in filin_hotels:
            line_elements = line.split(',')

            # First line: headers
            if lines_read == 0:
                headers = line_elements

            # General case: extract the line and parse the data
            else:
                line_dict = utils.extract_line(headers, line_elements)
                hotels_block_details = utils.extract_block(
                    line_dict['Longitude'], line_dict['Latitude'])
                hotels_block_name = hotels_block_details['name']
                
                try:
                    
                    hotel_year = str(line_dict['Year'])
                    hotel_month = str(line_dict['Month'])
                    hotel_number = str(line_dict['Hotels'])
                except:
                    hotel_year = '-1'
                    hotel_month = '-1'
                    hotel_number = '0'
                hotels_year_month = (hotel_year, hotel_month)

                # Add the hotel to the statistics
                if hotels_block_name not in hotels_per_block:
                    hotels_per_block[hotels_block_name] = {}
                if hotels_year_month not in hotels_per_block[hotels_block_name]:
                    hotels_per_block[hotels_block_name][hotels_year_month] = hotels_block_details
                    hotels_per_block[hotels_block_name][hotels_year_month]['Hotels'] = hotel_number
                

            lines_read += 1


    # Open the output file
    with open('output_data/hotels2.csv', 'w') as filout:

        # Print headers
        filout.write(utils.write_index_headers('hotels') + '\n')

        # Loop over the blocks and fill the lines
        for hotel_block in hotels_per_block:
            for hotels_year_month in hotels_per_block[hotel_block]:
                hotels_block_details = hotels_per_block[hotel_block][hotels_year_month]
                hotels_per_block_index = float(hotels_block_details['Hotels']) 
                line_out_elements = [str(i) for i in [hotels_block_details['block_ID'], hotels_block_details['administrative_subdivision'],
                                                      hotels_year_month[0], hotels_year_month[1], hotels_per_block_index]]
                filout.write(','.join(line_out_elements) + '\n')
                lines_written += 1

    # Print some stats
    print(f'Read lines: {lines_read}')
    print(f'Written lines: {lines_written}')


# Module execution: launch main method
if __name__ == '__main__':
    generate_blocks_for_hotels()
    
    '''
    print("Folium Version: " + folium.__version__)
    

    # Create maps
    #createMap(security_needs_index_file ,'Security Needs Index')
    #createMap(connectivity_needs_index_file ,'Connectivity Needs Index')
    #createMap(lighting_needs_index_file ,'Lighting Needs Index')

    # Get the lower-left and upper-right bounds from the Municipi shapes to center the map
    municipi_shapes_bounds = folium.GeoJson(config.administrative_subdivision_geojson_file).get_bounds()
    city_coords = [
        municipi_shapes_bounds[0][0]+(municipi_shapes_bounds[1]
                                      [0]-municipi_shapes_bounds[0][0])/2,
        municipi_shapes_bounds[0][1]+(municipi_shapes_bounds[1]
                                      [1]-municipi_shapes_bounds[0][1])/2
    ]
    print('Boundaries of the map are {}'.format(municipi_shapes_bounds))
    print('Centre of the map of {} is {}'.format(config.city_name, city_coords))

    choropleth = folium.Choropleth(
        geo_data=config.administrative_subdivision_geojson_file,
        name='Roma Municipi',
        columns=['nome'],
        key_on='feature.properties.nome',
        fill_color='YlGn',
        fill_opacity=0,
        line_opacity=0.5,
        legend_name='{} Municipi'.format(config.city_name)
    )

    map_grid = folium.Choropleth(
        geo_data='./input_data/city_grid.geojson',
        name='City grid',
        columns=['administrative_subdivision'],
        fill_color='RdPu',
        fill_opacity=0,
        line_opacity=0.1,
        line_color='blue',
        show=False
    )

    map_grid.geojson.add_child(
        folium.features.GeoJsonTooltip(['administrative_subdivision'])
    )

    city_map = folium.Map(location=city_coords, zoom_start=10,
                          min_zoom=9, max_zoom=15, control_scale=True)
    city_map.fit_bounds(municipi_shapes_bounds)
    folium.TileLayer('cartodbpositron').add_to(city_map)

    choropleth.add_to(city_map)
    map_grid.add_to(city_map)

    folium.LayerControl().add_to(city_map)

    test_name = 'test map'
    # Save the map and display it using a web browser
    mapFileName = os.path.join(
        'map', 'DINA_' + test_name.replace(" ", "_") + '.html')
    city_map.save(mapFileName)
    print("Saving the generated map in: " + mapFileName)
    webbrowser.open(mapFileName, new=2)
    '''
