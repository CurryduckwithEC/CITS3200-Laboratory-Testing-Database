"""
This script sets up an SQLite database, creates tables, and inserts sample data.

1. Connects to an SQLite database (creates one if it doesn't exist).
2. Creates four tables: `test_values`, `sample_values`, `test`, and `entry`.
3. Inserts predefined combinations of data into the `test_values` and `sample_values` reference tables.
4. Tests if reference tables are populated: Fetches and prints all rows from the `sample_values` reference table.

Dependencies:
- sqlite3: Standard Python library for SQLite databases.
- itertools: Standard Python library for creating iterators for efficient looping.

"""

import sqlite3
import itertools

# Connect to an SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('soil_tests.db')

# Create a cursor object using the cursor() method
cur = conn.cursor()

# Create the 'test_values' table if it doesn't already exist
cur.execute("""
CREATE TABLE IF NOT EXISTS test_values (
    test_value_id INTEGER PRIMARY KEY AUTOINCREMENT,
    drainage_type TEXT NOT NULL,
    shearing_type TEXT NOT NULL,
    anisotropic_type TEXT NOT NULL,
    availability_type TEXT NOT NULL
)
""")

# Create the 'sample_values' table if it doesn't already exist
cur.execute("""
CREATE TABLE IF NOT EXISTS sample_values (
    sample_value_id INTEGER PRIMARY KEY AUTOINCREMENT,
    density_type TEXT NOT NULL,
    plasticity_type TEXT NOT NULL,
    psd_type TEXT NOT NULL
)
""")

# Create the 'test' table if it doesn't already exist
cur.execute("""
CREATE TABLE IF NOT EXISTS test (
    test_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_value_id INTEGER NOT NULL,
    test_name TEXT NOT NULL,
    sample_value_id INTEGER NOT NULL,
    consolidation INTEGER NOT NULL,
    anisotropicy REAL NOT NULL,
    FOREIGN KEY (test_value_id) REFERENCES test_values(test_value_id),
    FOREIGN KEY (sample_value_id) REFERENCES sample_values(sample_value_id)
)
""")

# Create the 'entry' table if it doesn't already exist
cur.execute("""
CREATE TABLE IF NOT EXISTS entry (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id INTEGER NOT NULL,
    time_start_of_stage INTEGER NOT NULL,
    shear_induced_pwp REAL NOT NULL,
    axial_strain TEXT NOT NULL,
    vol_strain INTEGER NOT NULL,
    induced_pwp REAL NOT NULL,
    p TEXT NOT NULL,
    q TEXT NOT NULL,
    e TEXT NOT NULL,
    FOREIGN KEY (test_id) REFERENCES test(test_id)
)
""")

# Define data properties for test values
data_properties = {
    "drainage": ["drained", "undrained"],
    "shearing": ["compression", "extension"],
    "anisotropic": ["isotropic", "anisotropic"],
    "availability": ["public", "confidential"]
}

# Generate combinations of test values
combinations = itertools.product(
    data_properties["drainage"],
    data_properties["shearing"],
    data_properties["anisotropic"],
    data_properties["availability"]
)

# Insert generated combinations into 'test_values' table
for combination in combinations:
    sql = """
    INSERT INTO test_values (drainage_type, shearing_type, anisotropic_type, availability_type)
    VALUES (?, ?, ?, ?)
    """
    cur.execute(sql, combination)

# Define soil properties for sample values
soil_properties = {
    "density": ["loose", "dense"],
    "plasticity": ["plastic", "non-plastic", "unknown"],
    "psd": ["clay", "silt", "sand"]
}

# Generate combinations of sample values
combinations2 = itertools.product(
    soil_properties["density"],
    soil_properties["plasticity"],
    soil_properties["psd"]
)

# Insert generated combinations into 'sample_values' table
for combination in combinations2:
    sql = """
    INSERT INTO sample_values (density_type, plasticity_type, psd_type)
    VALUES (?, ?, ?)
    """
    cur.execute(sql, combination)

# Commit changes to the database and close the cursor
conn.commit()
cur.close()
conn.close()

#Following code is just to verify that reference tables are populated correctly, by connecting and reading all records from 'sample_values' table
# Reconnect to the SQLite database
connection_obj = sqlite3.connect('soil_tests.db')

# Create a cursor object for querying
cursor_obj = connection_obj.cursor()

# Define SQL statement to select all data from 'sample_values' table
statement = 'SELECT * FROM sample_values'

# Execute the SQL statement
cursor_obj.execute(statement)

# Print all the data retrieved from 'sample_values' table
print("All the data")
output = cursor_obj.fetchall()
for row in output:
    print(row)

# Commit changes (not necessary here as there are no changes) and close the connection
connection_obj.commit()
connection_obj.close()