# Install Folium beforehands: pip install folium, pip install pandas
import calendar
import datetime
import folium
import numpy as np
import ogr
import os
import pandas as pd
import pyproj
import sys
import webbrowser
import create_indexes
from math import ceil
from folium import (FeatureGroup, LayerControl, Map, Marker, plugins)

# Local imports
import config as config
import utils

# Read the city grid config

def createHeatMapWithTimeFromIndexFile(indexFile, period_for_heatmap_parameter,heatmap_name):
    print("Generating HeatMap from " + indexFile)
    needs_index_df = pd.read_csv(indexFile)
    
    # Filter file to display 2019 and above and relevant
    needs_index_df = needs_index_df[needs_index_df['Year']>=2019]
    needs_index_df = needs_index_df[needs_index_df['Month']>0]
    needs_index_df = needs_index_df[needs_index_df['block_ID']>-1]    
    needs_index_df = needs_index_df[needs_index_df['administrative_subdivision']>0]
    

    # Convert some columns       
    needs_index_df['Year'] = needs_index_df['Year'].astype(str)
    needs_index_df['Month'] = needs_index_df['Month'].astype(str)
    needs_index_df['period'] = needs_index_df[['Year', 'Month']].agg('-'.join, axis=1)
    needs_index_df['period'] = pd.to_datetime(needs_index_df['period'], errors='coerce', format='%Y-%m')
    needs_index_df['Index'] = needs_index_df['Index'].astype(float)

    #print('Number of rows in datafile before the association between block IDs and latitude/longitude: ', str(needs_index_df.count))
    # Use the city grid file to append the latitude/longitude of the centre of each block (useful for heatmaps) using a look-up
    heatmap_index_df = pd.merge(left=needs_index_df, right=utils.get_city_blocks_dataframe(), how='left', on='block_ID')
   
    skipped_rows = len(needs_index_df.index) - len(heatmap_index_df.index)
    print('Number of rows skipped in datafile after the association between block IDs and latitude/longitude: ', str(skipped_rows))

    # Remove null rows
    heatmap_index_df = heatmap_index_df.dropna(axis=0, subset=['centroid_latitude','centroid_longitude'])
    #print('Number of rows in datafile after removing the missing longitude/latitude: ', str(heatmap_index_df.count))

    # Sort values by period
    heatmap_index_df['period']=heatmap_index_df['period'].sort_values(ascending=True)
    
    # Initialize the heatmap data
    heat_data = []
    heatmap_label = []
    
    # Month case: group by month and don't care about the year

        
    if period_for_heatmap_parameter == 'month':
        heatmap_index_df['Month'] = heatmap_index_df['Month'].astype(int)
        grouped_by_df = heatmap_index_df.sort_values(by=['Month']).groupby(by='Month')
        for _, d in grouped_by_df:
            heat_data.append([[row['centroid_latitude'], row['centroid_longitude'], row['Index']] for _, row in d.iterrows()])
        
        print(heatmap_index_df['Month'])        
        for m in heatmap_index_df['Month'].unique().astype(int):
            heatmap_label.append(str(m) + " - " + calendar.month_name[m])
        
    # Year-Month case: group by period (i.e. YEAR-MONTH like 2019-02)
    else:
        
        for _, d in heatmap_index_df.sort_values(by=['period']).groupby('period'):
            heat_data.append([[row['centroid_latitude'], row['centroid_longitude'], row['Index']] for _, row in d.iterrows()])
        for p in np.sort(heatmap_index_df['period'].unique()):
            ts = pd.to_datetime(str(p)) 
            heatmap_label.append(ts.strftime("%Y-%m"))
    
    # Generate the heatmap
    heatmap_from_index = plugins.HeatMapWithTime(heat_data, name = heatmap_name + " per " + period_for_heatmap_parameter, index = heatmap_label, auto_play=False, min_opacity = 0.00, 
                                                 radius = 120, max_opacity=0.5, use_local_extrema = True, gradient={0.0: 'lime', 0.7: 'orange', 1: 'red'})
    
    
    return heatmap_from_index


def get_file_name(file_extension,map_type,index_name, period_for_heatmap_parameter):
    filename = 'DINA_' + config.city_name + '_' + config.country_name + '_' +  str(config.block_width) + 'mX' + str(config.block_height) + 'm_' + index_name + '_per_' + period_for_heatmap_parameter + '_' + map_type + '.' + file_extension
    return filename

# Creates the heatmap
def create_heatmap(mapname, index_input_file,period_for_heatmap_parameter):
    
    # Info: print the version of folium
    print("Folium Version: " + folium.__version__)
    
    # Get the lower-left and upper-right bounds from the Municipi shapes to center the map
    administrative_subdivision_shape_bounds = folium.GeoJson(config.administrative_subdivision_geojson_file).get_bounds()
    city_coords = [
        administrative_subdivision_shape_bounds[0][0]+(administrative_subdivision_shape_bounds[1]
                                      [0]-administrative_subdivision_shape_bounds[0][0])/2,
        administrative_subdivision_shape_bounds[0][1]+(administrative_subdivision_shape_bounds[1]
                                      [1]-administrative_subdivision_shape_bounds[0][1])/2
    ]
    print('Boundaries of the map are {}'.format(administrative_subdivision_shape_bounds))
    print('Centre of the map of {} is {}'.format(config.city_name, city_coords))

    # Prepare the choropleth for the administrative subdivisions (e.g. Roma Municipi)
    choropleth = folium.Choropleth(
        geo_data=config.administrative_subdivision_geojson_file,
        name=config.city_name + ' Administrative Subdivisions',
        columns=['nome'],
        key_on='feature.properties.nome',
        fill_color='YlGn',
        fill_opacity=0,
        line_opacity=0.5,
        legend_name='{} Administrative Subdivisions'.format(config.city_name)
    )

    # Prepares the grid for city blocks
    map_grid = folium.Choropleth(
        geo_data='./input_data/city_grid.geojson',
        name=config.city_name + ' City Grid',
        columns=['administrative_subdivision','block_ID'],
        fill_color='RdPu',
        fill_opacity=0,
        line_opacity=0.1,
        line_color='blue',
        show=False
    )
    
    # Adds a tooltip
    #choropleth.geojson.add_child( folium.features.GeoJsonTooltip(['administrative_subdivision']))
    map_grid.geojson.add_child( folium.features.GeoJsonTooltip(['administrative_subdivision','block_ID'], aliases=['Administrative Subdivision','Block Identifier']))

    # Creates the city map
    city_map = folium.Map(location=city_coords, zoom_start=12,
                          min_zoom=10, max_zoom=15, control_scale=True)
    
    # Adds different map layers
    folium.TileLayer('cartodbpositron').add_to(city_map)
    folium.TileLayer('cartodbdark_matter').add_to(city_map)
    
    # Adds the administrative subdivisions and city grid
    choropleth.add_to(city_map)
    map_grid.add_to(city_map)
    
    # Creates the heatmap correspinding to the index file provided as argument and adds it to the map
    heatmap_with_time = createHeatMapWithTimeFromIndexFile(index_input_file,period_for_heatmap_parameter, mapname).add_to(city_map)
    folium.LayerControl(collapsed=False).add_to(city_map)
    

    # Save the map and display it using a web browser
    mapFileName = os.path.join('map', get_file_name('html','Heatmap',mapname.replace(" ","_"),period_for_heatmap_parameter ))
    city_map.save(mapFileName)
    print("Saving the generated map in: " + mapFileName)
    webbrowser.open(mapFileName, new=2)

def create_all_maps():
    create_indexes.create_indexes()
    # Create a set of maps with data grouped by months (whatever the year is: 2019 or 2020)
    create_heatmap ('Security Needs', config.security_needs_index_file,'month')
    create_heatmap ('Lighting Needs', config.lighting_needs_index_file,'month')
    create_heatmap ('Connectivity Needs', config.connectivity_needs_index_file, 'month')
    
    #Create a set of maps with data grouped by year-month (less data per time period but provides a better view of history)
    create_heatmap ('Security Needs', config.security_needs_index_file, 'year-month')
    create_heatmap ('Lighting Needs', config.lighting_needs_index_file, 'year-month')
    create_heatmap ('Connectivity Needs', config.connectivity_needs_index_file, 'year-month')

# Module execution: launch main method
if __name__ == '__main__':
    create_all_maps()
    