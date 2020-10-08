import get_accidents_geodata
import get_hotels_geodata
import get_wifi_logs_geodata
import config
import utils
import create_indexes
import display_heatmap
import os
import os.path
from os import path
import glob
import pandas as pd
import requests
import csv
import numpy as np
import chardet

# Reads a .txt file containing all the URLs to open data files
def download_open_data_files(filename, foldername):
    datasets_URLs = pd.read_csv(filename,delimiter=';')
    
    for the_URL in datasets_URLs['URL']:
        filepath = './input_data/' + foldername+  '/{}'.format(os.path.basename(the_URL))
        if path.exists(filepath):
            print(the_URL + " already downloaded")
        else: 
            r = requests.get(the_URL, allow_redirects=True)
            r.encoding = r.apparent_encoding
            open(filepath, 'wb').write(r.content)
            print("Downloading "+ the_URL + " and store it here: " + filepath )

    return datasets_URLs
    
def download_and_merge_wifi():
    datasets_df = download_open_data_files(config.wifi_dataset_locations,'wifi_raw_data')
    files_to_aggregate = []
    os.chdir("./input_data/wifi_raw_data")
    for ind in datasets_df.index:
        local_file_name= os.path.basename(datasets_df['URL'][ind])
        print ('Reading ', local_file_name, ' and adding the corresponding year and month')
        wifi_df = pd.read_csv(local_file_name, delimiter=';', encoding = "utf-8", error_bad_lines=False)
        wifi_df['Year'] = str(datasets_df['Date'][ind])[-4:]
        wifi_df['Month'] = str(datasets_df['Date'][ind])[3:5]
        files_to_aggregate.append(wifi_df)
    
    # Convert the above object into a csv file and export
    result_obj = pd.concat(files_to_aggregate)
    result_obj.to_csv("../consolidated_wifi.csv", sep=';', index=False, encoding="utf-8")
    print('consolidated_wifi.csv has been generated')
    os.chdir("../..")
    

def download_and_merge_hotels():
    datasets_df = download_open_data_files(config.hotels_dataset_locations,'hotels_raw_data')
    files_to_aggregate = []
    os.chdir("./input_data/hotels_raw_data")
    for ind in datasets_df.index:
        local_file_name= os.path.basename(datasets_df['URL'][ind])
        print ('Reading ', local_file_name, ' and adding the corresponding year and month')
        
        with open(local_file_name) as src_file:
            print('encoding of ',local_file_name,' = ', src_file.encoding)
        hotels_df = pd.read_csv(local_file_name,delimiter=';', encoding = "ISO-8859-1", error_bad_lines=False)
        hotels_filtered_columns = hotels_df[['INSEGNA','INDIRIZZO','MUNICIPIO','SINGOLE','DOPPIE','TRIPLE', 'QUADRUPLE', 'QUINTUPLE', 'SESTUPLE']]
        
        hotels_filtered_columns['Year'] = str(datasets_df['Date'][ind])[-4:]
        hotels_filtered_columns['Month'] = str(datasets_df['Date'][ind])[3:5]
        hotels_filtered_columns['INSEGNA'].replace('', np.nan, inplace=True)
        files_to_aggregate.append(hotels_filtered_columns.dropna(subset = ['INSEGNA']))
    
    # Convert the above object into a csv file and export
    result_obj = pd.concat(files_to_aggregate)
    result_obj.to_csv("../consolidated_hotels.csv", sep=';', index=False)
    print('consolidated_hotels.csv has been generated')
    os.chdir("../..")

def download_and_merge_claims():
    datasets_df = download_open_data_files(config.claims_dataset_locations,'claims_raw_data')
    files_to_aggregate = []
    os.chdir("./input_data/claims_raw_data")
    for ind in datasets_df.index:
        local_file_name= os.path.basename(datasets_df['URL'][ind])
        print ('Reading ', local_file_name, ' and adding the corresponding year and month')
        claims_df = pd.read_csv(local_file_name, delimiter=';', encoding = "ISO-8859-1", error_bad_lines=False)
        claims_df['Year'] = str(datasets_df['Date'][ind])[-4:]
        claims_df['Month'] = str(datasets_df['Date'][ind])[3:5]
        claims_df['Municipio di riferimento (tramite geo-localizzazione)'].replace('n.a.', np.nan, inplace=True) #removing claims where administrative subdivision is not known
        claims_df.dropna(subset = ['Municipio di riferimento (tramite geo-localizzazione)'], inplace=True)
        files_to_aggregate.append(claims_df)
    
    # Convert the above object into a csv file and export
    result_obj = pd.concat(files_to_aggregate)
    result_obj.to_csv("../consolidated_claims.csv", sep=';', index=False, encoding="utf-8")
    print('consolidated_claims.csv has been generated')
    os.chdir("../..")

# Processes all of the input data. Some of the inputs require getting additional data from APIs (typically geocoding)
def process_input_data():

    
    print("#### Step 1/7:  Generating the city grid ################################################")
    utils.generate_city_grid()
    print("#### Step 3/7:  Generating geolocated accommodations input file #########################")
    get_hotels_geodata.get_hotel_geodata(config.city_hotels_input_file_geolocated)
    print("#### Step 2/7:  Generating geolocated accidents input file ##############################")
    get_accidents_geodata.get_accidents_geodata(config.city_accidents_input_file)
    print("#### Step 4/7:  Generating geolocated wifi input file ###################################")
    get_wifi_logs_geodata.get_wifi_logs_geodata(config.city_wifi_input_file_geolocated)
    print("#### Step 6/7:  Recreating connectivity, lighting, security needs indexes ###############")
    create_indexes.create_indexes()
    print("#### Step 7/7:  Generating and displaying the heatmaps ##################################")
    display_heatmap.create_all_maps()
    


# Module execution: launch main method
if __name__ == '__main__':
    #download_and_merge_claims()
    #download_and_merge_hotels()
    #download_and_merge_wifi()
    process_input_data()




