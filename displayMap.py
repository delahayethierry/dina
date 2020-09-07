# Install Folium beforehands: pip install folium, pip install pandas
import os
import folium
import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
from folium import FeatureGroup, LayerControl, Map, Marker, plugins

print(folium.__version__)

#Define coordinates of where we want to center our map (here, Roma in Italy)
boulder_coords = [41.902782,  12.496366]

#Read all the data files generated by the DINA Open Data Ingestion module for the city of Roma, Italy
data_file_security_needs_index = pd.read_csv('security_needs_index.csv', dtype=object)
data_file_connectivity_needs_index = pd.read_csv('connectivity_needs_index.csv', dtype=object)
data_file_lighting_needs_index = pd.read_csv('lighting_needs_index.csv', dtype=object)

print(data_file_security_needs_index.head(5))

#Create the map
city_map = folium.Map(location = boulder_coords, zoom_start = 13)

#Add different layers (feature group) to the map: our 3 indexes
feature_group_security_needs = FeatureGroup(name='Security Needs Index')
feature_group_connectivity_needs = FeatureGroup(name='Connectivity Needs Index')
feature_group_lighting_needs = FeatureGroup(name='Lighting Needs Index')


# Ensure you're handing it floats
data_file_security_needs_index['Latitude'] = data_file_security_needs_index['Latitude'].astype(float)
data_file_security_needs_index['Longitude'] = data_file_security_needs_index['Longitude'].astype(float)

data_file_connectivity_needs_index['Latitude'] = data_file_security_needs_index['Latitude'].astype(float)
data_file_connectivity_needs_index['Longitude'] = data_file_security_needs_index['Longitude'].astype(float)

data_file_lighting_needs_index['Latitude'] = data_file_security_needs_index['Latitude'].astype(float)
data_file_lighting_needs_index['Longitude'] = data_file_security_needs_index['Longitude'].astype(float)


# Filter the data file for rows, then columns

#Security Index
heatmap_data_file_security_needs_index = data_file_security_needs_index[data_file_security_needs_index['Year']=='2020'] 
heatmap_data_file_security_needs_index = heatmap_data_file_security_needs_index[['Latitude', 'Longitude']]

#Lighting Index
heatmap_data_file_lighting_needs_index = data_file_lighting_needs_index[data_file_lighting_needs_index['Year']=='2020'] 
heatmap_data_file_lighting_needs_index = heatmap_data_file_lighting_needs_index[['Latitude', 'Longitude']]

#Connectivity Index
heatmap_data_file_connectivity_needs_index = data_file_connectivity_needs_index[data_file_connectivity_needs_index['Year']=='2020'] 
heatmap_data_file_connectivity_needs_index = heatmap_data_file_lighting_needs_index[['Latitude', 'Longitude']]


# Create weight column, using date
# ---- Security Index ---- 
heatmap_data_file_security_needs_index['Weight'] = data_file_security_needs_index['Month']
heatmap_data_file_security_needs_index['Weight'] = heatmap_data_file_security_needs_index['Weight'].astype(float)
heatmap_data_file_security_needs_index = heatmap_data_file_security_needs_index.dropna(axis=0, subset=['Latitude','Longitude', 'Weight'])

heat_data_security = [[[row['Latitude'],row['Longitude']] for index, row in heatmap_data_file_security_needs_index[heatmap_data_file_security_needs_index['Weight'] == i].iterrows()] for i in range(0,13)]
# Plot it on the map
hm_security = plugins.HeatMapWithTime(heat_data_security,auto_play=True,max_opacity=0.8)
#hm_security.add_to(feature_group_security_needs)
hm_security.add_to(city_map)

# ---- lighting Index ---- 
heatmap_data_file_lighting_needs_index['Weight'] = data_file_lighting_needs_index['Month']
heatmap_data_file_lighting_needs_index['Weight'] = heatmap_data_file_lighting_needs_index['Weight'].astype(float)
heatmap_data_file_lighting_needs_index = heatmap_data_file_lighting_needs_index.dropna(axis=0, subset=['Latitude','Longitude', 'Weight'])

heat_data_lighting = [[[row['Latitude'],row['Longitude']] for index, row in heatmap_data_file_lighting_needs_index[heatmap_data_file_lighting_needs_index['Weight'] == i].iterrows()] for i in range(0,13)]
# Plot it on the map
hm_lighting = plugins.HeatMapWithTime(heat_data_lighting,auto_play=True,max_opacity=0.8)
hm_lighting.add_to(feature_group_lighting_needs)
#hm_lighting.add_to(city_map)

# ---- connectivity Index ---- 
heatmap_data_file_connectivity_needs_index['Weight'] = data_file_connectivity_needs_index['Month']
heatmap_data_file_connectivity_needs_index['Weight'] = heatmap_data_file_connectivity_needs_index['Weight'].astype(float)
heatmap_data_file_connectivity_needs_index = heatmap_data_file_connectivity_needs_index.dropna(axis=0, subset=['Latitude','Longitude', 'Weight'])

heat_data_connectivity = [[[row['Latitude'],row['Longitude']] for index, row in heatmap_data_file_connectivity_needs_index[heatmap_data_file_connectivity_needs_index['Weight'] == i].iterrows()] for i in range(0,13)]
# Plot it on the map
hm_connectivity = plugins.HeatMapWithTime(heat_data_connectivity,auto_play=True,max_opacity=0.8)
hm_connectivity.add_to(feature_group_connectivity_needs)
#hm_connectivity.add_to(city_map)

#Example of market that we could add for security inded (but the best is to have a heatmap)
#Marker(location=[41.902782,  12.496366],
#       popup='Security Index 2/10').add_to(feature_group_security_needs)


feature_group_security_needs.add_to(city_map)
feature_group_connectivity_needs.add_to(city_map)
feature_group_lighting_needs.add_to(city_map)
LayerControl().add_to(city_map)

#Save the map
city_map.save(os.path.join('map', 'CityMap.html'))