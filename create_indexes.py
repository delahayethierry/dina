import math
import pandas as pd
import config 
import utils


# Main method to create indexes from the data sources
def create_indexes():

    # Loop over indexes and build the index from the existing data
    for index in config.indexes_calculation_parameters:
        print(f'Calculating indexes for {index}')
        index_values = pd.DataFrame(columns=utils.get_index_headers())
        for data_source in config.indexes_calculation_parameters[index]:
            file_name = f'output_data/{data_source}.csv'
            data_source_content = pd.read_csv(file_name)
            print(f'Reading file {file_name} to create index')
            index_values = index_values.merge(data_source_content, how='outer', on=utils.get_index_headers())
            index_values.to_csv(f'map/{index}_needs_index__temp.csv', index=False)
        # Merge the datasources into the index
        index_values = index_values.fillna(value=0)
        print('Weights to apply to index: ')
        print(config.indexes_calculation_parameters[index])
        #index_values['Index'] = index_values.dot(pd.Series(config.indexes_calculation_parameters[index]).reindex(index_values.columns, fill_value=0))
        index_values['Index'] = index_values.dot(pd.Series(config.indexes_calculation_parameters[index]).reindex(index_values.columns, fill_value=0))

        # Write the index to the map file
        print(f'Writing index file for {index}')
        index_values.to_csv(f'map/{index}_needs_index.csv', index=False)

    return



# Module execution: launch main method
if __name__ == '__main__':
    
    create_indexes()

