#all needed librarys
import numpy as np
import psycopg2
from psycopg2 import OperationalError
import csv
import pandas as pd
from sqlalchemy import create_engine

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

db_database="Project"
db_user="postgres"
db_password="Kpgg3677!" #change this to sys.argv[i]
db_host = "localhost"
db_port="55000"

connection = create_connection(db_database, db_user, db_password, db_host, db_port)
cur= connection.cursor()

cur.execute("""
    CREATE TABLE dim_drainage(
        test_drainage_id INTEGER PRIMARY KEY,    
        drainage_type TEXT            
    )
"""
)

cur.execute("""
    CREATE TABLE dim_shearing(
        test_shearing_id INTEGER PRIMARY KEY, 
        shearing_type TEXT            
    )
"""
)

cur.execute("""
    CREATE TABLE dim_anisotropic(
        test_anisotropic_id INTEGER PRIMARY KEY,   
        anisotropic_type TEXT            
    )
"""
)

cur.execute("""
    CREATE TABLE dim_availability(
        test_availability_id INTEGER PRIMARY KEY,    
        availability_type TEXT            
    )
"""
)

cur.execute("""
    CREATE TABLE dim_density(
        sample_density_id INTEGER PRIMARY KEY,    
        density_type TEXT            
    )
"""
)

cur.execute("""
    CREATE TABLE dim_plasticity(
        sample_plasticity_id INTEGER PRIMARY KEY,    
        plasticity_type TEXT            
    )
"""
)

cur.execute("""
    CREATE TABLE dim_psd(
        sample_psd_id INTEGER PRIMARY KEY,
        psd_type TEXT            
    )
"""
)

cur.execute("""
    CREATE TABLE fact_soil(
        sample_test_id INTEGER PRIMARY KEY,
        test_drainage_id INTEGER,
        test_shearing_id INTEGER,
        test_anisotropic_id INTEGER, 
        test_availability_id INTEGER,
        sample_density_id INTEGER,
        sample_plasticity_id INTEGER,
        sample_psd_id INTEGER,
        time_start_of_stage INTEGER,
        shear_induced_pwp REAL,
        axial_strain DOUBLE PRECISION,
        vol_strain INTEGER,
        induced_pwp REAL,
        "p'" DOUBLE PRECISION,
        q DOUBLE PRECISION,
        e DOUBLE PRECISION, 
        FOREIGN KEY (test_drainage_id) REFERENCES dim_drainage(test_drainage_id),
        FOREIGN KEY (test_shearing_id) REFERENCES dim_shearing(test_shearing_id),
        FOREIGN KEY (test_anisotropic_id) REFERENCES dim_anisotropic(test_anisotropic_id),
        FOREIGN KEY (test_availability_id) REFERENCES dim_availability(test_availability_id),
        FOREIGN KEY (sample_density_id) REFERENCES dim_density(sample_density_id), 
        FOREIGN KEY (sample_plasticity_id) REFERENCES dim_plasticity(sample_plasticity_id), 
        FOREIGN KEY (sample_psd_id) REFERENCES dim_psd(sample_psd_id)
    )
"""
)


#currentyl hard coding in insertion of dimension tables - quick word around - looking into dynamic approach
data_properties = {
    "drainage": ["drained", "undrained"],
    "shearing": ["compression", "extension"],
    "anisotropic": ["isotropic", "anisotropic"],
    "availability": ["public", "confidential"]
}

# Iterate through each key-value pair

for key, values in data_properties.items():
    # Create dimension table name based on the key
    table_name = f"dim_{key.lower()}"
    
    # Insert values into the dimension table
    for idx, value in enumerate(values, start=1):
        # Construct the SQL INSERT statement
        sql = f"""
        INSERT INTO {table_name} (test_{key}_id, {key}_type)
        VALUES (%s, %s)
        """
        
        # Execute the SQL statement with the appropriate values
        cur.execute(sql, (idx, value))

soil_properties = {
        "Density": ["loose", "dense"],
        "Plasticity": ["plastic", "non-plastic", "unknown"],
        "PSD": ["clay", "silt", "sand"]
        }

for key, values in soil_properties.items():
    # Create dimension table name based on the key
    table_name = f"dim_{key.lower()}"
    
    # Insert values into the dimension table
    for idx, value in enumerate(values, start=1):
        # Construct the SQL INSERT statement
        sql = f"""
        INSERT INTO {table_name} (sample_{key}_id, {key}_type)
        VALUES (%s, %s)
        """
        
        # Execute the SQL statement with the appropriate values
        cur.execute(sql, (idx, value))

connection.commit()
cur.close()
connection.close()