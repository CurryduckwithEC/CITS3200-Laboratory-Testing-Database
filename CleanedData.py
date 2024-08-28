import pandas as pd
import openpyxl

# Reading Excel file, returning DataFrame of specified sheet
def read_excel(file_name, sheet_name):
    return pd.read_excel(file_name, sheet_name, header = None)
    
# Find the starting index where data begins and the columns indices of the wanted columns in the data frame
# Returns Dicionary with column of indices and wanted values and starting index
def organising_columns(dataframe, wanted_columns):
    index_start = int(dataframe.index[dataframe.iloc[:, 0] == 'Stage no.'][0]) #determines where to start pulling data from - hardcoded as all future csv files are same structure
    headers = index_start + 1 # specifys headers row location 
    starting_data_val = index_start + 2 #specify start of data

    visited = {} #dictionary will be used to determine whether the wanted column has already been visited or not - due to duplicate columns in the data (can update index instead of column)
    for i in range(0, len(wanted_columns)):
        visited[wanted_columns[i]] = False

    value_to_col_idx = {}
    file_counter = 0

    # Iterate from index_start to headers rowsm, and all columns in dataframe
    for row_idx in range(index_start, headers + 1):
        for col_idx in range(0,dataframe.shape[1]):
            cell_value = dataframe.iloc[row_idx, col_idx]

            # if wanted value has already been visited, just update its column index - alternative: only grab first column that appears and ignore all after - however have to manage csv file structure 
            if cell_value in wanted_columns and visited[cell_value] == True: #updates to latest index as multiple rows duplicates exist
                value_to_col_idx[cell_value] = int(col_idx)

            # if wanted value hasnt been visited, add to dictionary of wanted values with its column index
            if cell_value in wanted_columns and visited[cell_value] == False: #searching each cell within specified col and row range
                value_to_col_idx[cell_value] = int(col_idx)
                visited[cell_value] = True  

    # Sort the dictionary by column index
    sorted_dict = {key: value_to_col_idx[key] for key in sorted(value_to_col_idx, key=value_to_col_idx.get)}

    return sorted_dict, starting_data_val

# Extracts wanted columns and all their data entries based on tehe sorted dictionary of the columns indices
def clean_dataframe(df, sorted_dict, starting_data_val):
    return df.iloc[starting_data_val:, list(sorted_dict.values())] #pulling wanted columns based on wanted values from dictionary

# Saves the cleaned Dataframe to a csv file with specified file name
def save_to_csv(df_clean, wanted_values, file_name="cleaned.csv"):
    return df_clean.to_csv(file_name, index = False, header = wanted_values)

def main():
     # Specify file and sheet names
    file_name = 'CSL_1_U.xlsx'
    sheet_name = "03 - Shearing"

    # List of wanted column values
    wanted_values = ["Time start of stage ", "Shear induced PWP", "Axial strain", "Vol strain", "Induced PWP", "p'", "q", "e"]

    # Read Excel file
    df = read_excel(file_name, sheet_name)

    # Find headers and column indices
    sorted_dict, starting_data_val = organising_columns(df, wanted_values)

    # Clean DataFrame
    df_clean = clean_dataframe(df, sorted_dict, starting_data_val)

    # Save cleaned DataFrame to CSV
    save_to_csv(df_clean, wanted_values)

# Run the main function
if __name__ == "__main__":
    main()
