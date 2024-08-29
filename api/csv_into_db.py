import pandas as pd
import openpyxl
import numpy as np
from sqlalchemy import create_engine, text
from psycopg2 import OperationalError
import psycopg2

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



def find_categories(dataframe, starting_val="drainage"):
    column_index = dataframe.columns.get_loc(dataframe.columns[(dataframe.iloc[0] == 'drainage')][0])
    extracted_values = dataframe.iloc[0:7, column_index+1]
    return extracted_values

# Extracts wanted columns and all their data entries based on tehe sorted dictionary of the columns indices
def clean_dataframe(df, sorted_dict, starting_data_val, wanted_values):
    cleaned_df = df.iloc[starting_data_val:, list(sorted_dict.values())] #pulling wanted columns based on wanted values from dictionary
    cleaned_df.columns = wanted_values
    return cleaned_df

# # Saves the cleaned Dataframe to a csv file with specified file name
# def save_to_csv(df_clean, wanted_values, file_name="cleaned.csv"):
#     return df_clean.to_csv(file_name, index = False, header = wanted_values)
def create_connection(db_name, db_user, db_password, db_host, db_port):
    connection = None
    try:
        connection = psycopg2.connect(
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port,
        )
        print("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        print(f"The error '{e}' occurred")
    return connection

def fetch_test_ids(test_vals, engine):
    test_pd = pd.read_sql_query("SELECT * FROM public.test_values", engine)

    drainage_type = test_vals.iloc[0]
    shearing_type = test_vals.iloc[1]
    anisotropy_type = test_vals.iloc[2]
    availability_type = test_vals.iloc[3]
    
    # Filter the DataFrame based on the values
    matched_df = test_pd[
        (test_pd['drainage_type'] == drainage_type) &
        (test_pd['shearing_type'] == shearing_type) &
        (test_pd['anisotropy_type'] == anisotropy_type) &
        (test_pd['availability_type'] == availability_type)
    ]
    return matched_df['test_value_id'].iloc[0]


def fetch_sample_ids(sample_vals, engine):
    test_pd = pd.read_sql_query("SELECT * FROM public.sample_values", engine)

    density_type = sample_vals.iloc[0]
    plasticity_type = sample_vals.iloc[1]
    psd_type = sample_vals.iloc[2]
    
    
    # Filter the DataFrame based on the values
    matched_df = test_pd[
        (test_pd['density_type'] == density_type) &
        (test_pd['plasticity_type'] == plasticity_type) &
        (test_pd['psd_type'] == psd_type)
    ]
    return matched_df['sample_value_id'].iloc[0]


def populate_test_and_return_test_id(sample_key, test_key, connection, consolidation=0, anisotropic=0):
    data = {
        'test_value_id': int(test_key),  # Ensure the type is int
        'sample_value_id': int(sample_key),  # Ensure the type is int
        'consolidation': int(consolidation),  # Ensure the type is int
        'anisotropic': int(anisotropic)  # Ensure the type is int
    }
    
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame([data])

    insert_query = """
    INSERT INTO test (test_value_id, sample_value_id, consolidation, anisotropic)
    VALUES (%s, %s, %s, %s)
    RETURNING test_id;
    """

    cursor = connection.cursor()

    for index, row in df.iterrows():
        # Convert row values to native Python types (if not already done)
        cursor.execute(insert_query, (
            int(row['test_value_id']), 
            int(row['sample_value_id']), 
            int(row['consolidation']), 
            int(row['anisotropic'])
        ))
        primary_key = cursor.fetchone()[0]
    
    connection.commit()
    cursor.close()
    connection.close()
    return primary_key

def populate_entry_tbl(dataframe, test_id_key, engine):
    try:
        dataframe['test_id'] = test_id_key
        dataframe.to_sql('entry', engine, if_exists='append',index = False)
    except Exception as e:
        print(f"An Error occured: {e}")

def main():
    # Specify file and sheet names
    file_name = 'CSL_1_U.xlsx'
    sheet_name = "03 - Shearing"

    # List of wanted column values
    wanted_values = ["Time start of stage ", "Shear induced PWP", "Axial strain", "Vol strain", "Induced PWP", "p'", "q", "e"]
    new_col_names = ["time_start_of_stage", "shear_induced_pwp", "axial_strain", "vol_strain", "induced_pwp", "p'", "q", "e"]
    # Read Excel file
    df = read_excel(file_name, sheet_name)

    # Find headers and column indices
    sorted_dict, starting_data_val = organising_columns(df, wanted_values)
    categories = find_categories(df)
    test_vals = categories[:4]
    sample_vals = categories[4:]

    #Clean DataFrame
    df_clean = clean_dataframe(df, sorted_dict, starting_data_val, new_col_names)


    db_database="Project"
    db_user="postgres"
    db_password="Kpgg3677!" #change this to sys.argv[i]
    db_host = "localhost"
    db_port="55000"

    connection_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"
    engine = create_engine(connection_url)
    connection = create_connection(db_database, db_user, db_password, db_host, db_port)
    sample_values_id = fetch_sample_ids(sample_vals, engine)
    test_values_id = fetch_test_ids(test_vals, engine)
    test_id  = populate_test_and_return_test_id(sample_values_id, test_values_id, connection,  consolidation=0, anisotropic=0)
    populate_entry_tbl(df_clean, test_id, engine)




    # Save cleaned DataFrame to CSV
    # save_to_csv(df_clean, wanted_values)

# Run the main function
if __name__ == "__main__":
    main()
