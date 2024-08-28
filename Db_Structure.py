import numpy as np
import psycopg2
from psycopg2 import OperationalError
import pandas as pd
from sqlalchemy import create_engine
import csv

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
    CREATE TABLE laboratory(
        Time_Start_of_Stage INTEGER,
        Shear_Induced_PWP NUMERIC,
        Axial_Strain NUMERIC,
        Vol_Strain NUMERIC,
        Induced_PWP NUMERIC,
        "p'" NUMERIC,
        q NUMERIC,
        e NUMERIC,
        Soil_Classification TEXT,
        Soil_Properties TEXT,
        Test_Classification TEXT,
        Test_Properties TEXT
        )
"""  
)

connection.commit()
connection.close()

connection2 = create_connection(db_database, db_user, db_password, db_host, db_port)
cur2 = connection2.cursor()

with open('cleaned.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)

    for row in reader:
        try:
            cur2.execute("""
                INSERT INTO public.laboratory(Time_Start_of_Stage, Shear_Induced_PWP, Axial_Strain, Vol_Strain, Induced_PWP, "p'", q, e, Soil_Classification, Soil_Properties, Test_Classification, Test_Properties) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                row
            )
        except Exception as e:
            print("Error:", e)

connection2.commit()
connection2.close()
#extract csv file

# df = pd.read_csv("cleaned.csv")
# print(df)