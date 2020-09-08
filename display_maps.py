# Install Folium beforehands: pip install folium, pip install pandas
import os
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import folium
from folium import FeatureGroup, LayerControl, Map, Marker, plugins
import webbrowser


#Define the name of the files containing the aggregated indexes per geographical location,
#following the processing by the DINA Data Ingestion module

security_needs_index_file = './map/security_needs_index.csv'
connectivity_needs_index_file = './map/connectivity_needs_index.csv'
lighting_needs_index_file = './map/lighting_needs_index.csv'

def createHeatMapWithTimeFromIndexFile(indexFile):
    print("Generating HeatMap from " + indexFile)

    #Read data files generated by the DINA Open Data Ingestion module for the city of Roma, Italy
    index_df = pd.read_csv(indexFile, dtype=object)
    #print(index_df.head(5)) #print 5 first rows to check in the logs

    # Ensure we are handling Lat/Long as floats
    index_df['Latitude'] = index_df['Latitude'].astype(float)
    index_df['Longitude'] = index_df['Longitude'].astype(float)

    # Filter the data file for rows, then columns to display 2020 data only
    heatmap_index_df = index_df[index_df['Year']=='2020'] 
    #heatmap_index_df = index_df[['Latitude', 'Longitude']]



    #Prepare the Data Frame to generate the heatmap
    heatmap_index_df['Index'] = heatmap_index_df['Index'].astype(float)
    heatmap_index_df = heatmap_index_df.dropna(axis=0, subset=['Latitude','Longitude', 'Index'])
    heatmap_index_df['Month']=heatmap_index_df['Month'].sort_values(ascending=True)
    
    heat_data = []
    for _, d in heatmap_index_df.groupby('Month'):
        heat_data.append([[row['Latitude'], row['Longitude'], row['Index']] for _, row in d.iterrows()])
    
    print(heat_data)
    # Plot data on the map
    #heatMapIndex = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep'] #we are using 2020 data so datasets stops in Sep 2020
    heatmap_from_index = plugins.HeatMapWithTime(heat_data,auto_play=False,min_opacity = 0.05, max_opacity=0.3, use_local_extrema = True, gradient={0.5: 'lightcyan', 0.7: 'lime', 0.9: 'red'}, radius = 150)
  

    return heatmap_from_index

#Example of market that we could add for security inded (but the best is to have a heatmap)
#Marker(location=[41.902782,  12.496366],
#       popup='Security Index 2/10').add_to(feature_group_security_needs)

def createMap(filename, mapname):
    #Define coordinates of where we want to center our map (here, Roma in Italy)
    city_coords = [41.902782,  12.496366] 
    city_map = folium.Map(location = city_coords, zoom_start = 13)
    createHeatMapWithTimeFromIndexFile(filename).add_to(city_map)
    folium.LayerControl().add_to(city_map)

    #Save the map and display it using a web browser
    mapFileName = os.path.join('map', 'DINA_' + mapname.replace(" ","_") + '.html')
    city_map.save(mapFileName)
    print ("Saving the generated map in: " + mapFileName)
    webbrowser.open(mapFileName, new=2)

# Module execution: launch main method
if __name__ == '__main__':
    print("Folium Version: " + folium.__version__)
        
    #Create maps
    createMap(security_needs_index_file ,'Security Needs Index')  
    createMap(connectivity_needs_index_file ,'Connectivity Needs Index')  
    createMap(lighting_needs_index_file ,'Lighting Needs Index')  
