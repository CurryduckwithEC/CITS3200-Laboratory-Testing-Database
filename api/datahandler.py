from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

import pandas as pd
import os

from models import Entry, Test, TestValues, SampleValues, Base

# In array to allow changing of value in function
PATH = [""]

def get_path():
    return "sqlite:///" + os.path.normpath(PATH[0])

# Takes new path and name of database
def change_path(new_path: str):
    
    PATH[0] = new_path
    print(f"Path to database is now {get_path()}")




# Takes the specs dict defined within parsing
# Returns an object which is ready to be .add() into database
def sample_values_object(specs: dict) -> SampleValues:

    # Create sample_value object to input into database
    sample_values = SampleValues(
        density_type = specs["density"],
        plasticity_type = specs["plasticity"],
        psd_type = specs["psd"]
    )

    return sample_values

def test_values_object(specs: dict) -> TestValues:

    if specs["availability"] == "public":
        availability = True
    elif specs["availability"] == "private":
        availability = False
    # If a typo/misinput default to False
    else:
        availability == False

    test_values = TestValues(
        drainage_type = specs["drainage"],
        shearing_type = specs["shearing"],
        availability_type = availability
    )

    return test_values

def test_object(specs: dict, sample_values: SampleValues, test_values: TestValues, file_name: str) -> Test:

    # Make sure to commit any foreign key dependencies first
    test = Test(
        test_value_id = test_values.test_value_id,
        sample_value_id = sample_values.sample_value_id,

        consolidation = specs["consolidation"],
        anisotropy = specs["anisotropy"],

        test_file_name = file_name
    )

    return test

# Returns array of entry objects
def entry_objects(df: pd.DataFrame, test: Test):

    def row_to_entry(row):
        return Entry(
            test_id = test.test_id,

            time_start_of_stage = row["time start of stage"],
            axial_strain = row["axial strain"],
            vol_strain = row["volumetric strain"],
            excess_pwp = row["excess pwp"],
            p = row["p'"],
            deviator_stress = row["deviator stress"],
            void_ratio = row["void ratio"],
            shear_induced_pwp = row["shear induced pwp"] 
        )
    
    return df.apply(row_to_entry, axis=1).tolist()


# Function that takes the data of a new entry and commits to database
# The ordering matters of the commit due to foreign key dependencies
# Takes absolute path to database
def commit_new_entry(specs: dict, df: pd.DataFrame, file_name: str):

    sample_values = sample_values_object(specs)
    test_values = test_values_object(specs)
    test = test_object(specs, sample_values, test_values, file_name)

    entries = entry_objects(df, test)

    test.entries.extend(entries)
    sample_values.test = test
    test_values.test = test

    engine = create_engine(get_path(), echo=True)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(sample_values)
        session.add(test_values)
        session.add(test)
        session.add_all(entries)

        session.commit()


# Shouldn't really be used
# Retrieves all entry data and returns them as list of dataframes
def retrieve_entry_data():
    
    engine = create_engine(get_path(), echo=True) #replace sqlite:///.api/test with get_path()

    with Session(engine) as session:
        df = pd.read_sql(session.query(Entry).statement, session.bind)

    # split dataframe into list of dataframes by test id
    split_df = [group for _, group in df.groupby("test_id")]

    return df #split_df
    

# Returns a dataframe of specs
def retrieve_test_specs():

    engine = create_engine(get_path(), echo=True)

    with Session(engine) as session:
        query = (
            session.query(Test, TestValues, SampleValues)
            .join(TestValues, Test.test_value_id == TestValues.test_value_id)
            .join(SampleValues, Test.sample_value_id == SampleValues.sample_value_id)
        )

        df = pd.read_sql(query.statement, session.bind)

    return df


def retrieve_filtered_data(drainage_types=None, shearing_types=None, anisotropy_range=None, consolidation_range=None, availability_types=None, density_types=None, plasticity_types = None, psd_types = None):
    engine = create_engine(get_path(), echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        query = session.query(Entry).join(Test).join(TestValues).join(SampleValues)
    

        if drainage_types:
            drainage_map = {'Drained': "drained", 'Undrained':"undrained"}
            drainage_types = [drainage_map[atype] for atype in drainage_types]
            query = query.filter(TestValues.drainage_type.in_(drainage_types))

        if shearing_types:
            shearing_map = {'Compression': 'compression', 'Extension': 'extension'}
            shearing_types = [shearing_map[atype] for atype in shearing_types]
            query = query.filter(TestValues.shearing_type.in_(shearing_types))

        # Apply anisotropy filter
        if anisotropy_range:
            query = query.filter(Test.anisotropy.between(anisotropy_range[0], anisotropy_range[1])) #this works!!

        # Apply consolidation filter
        if consolidation_range:
            query = query.filter(Test.consolidation.between(consolidation_range[0], consolidation_range[1]))

        # Apply availability filter
        if availability_types:
            availability_map = {'Public': True, 'Confidential': False}
            availability_types = [availability_map[atype] for atype in availability_types]
            query = query.filter(TestValues.availability_type.in_(availability_types))

        if density_types:
            density_map = {'Loose':'loose', 'Dense':'dense'}
            density_types = [density_map[atype] for atype in density_types]
            query = query.filter(SampleValues.density_type.in_(density_types))

        if plasticity_types:
            plasticity_map = {"Plastic":"plastic", "Non-plastic" :"non-plastic", "Unknown" : "unknown"} #dash doesnt have dash in nonplastic
            plasticity_types = [plasticity_map[atype] for atype in plasticity_types]
            query = query.filter(SampleValues.plasticity_type.in_(plasticity_types))
        
        
        if psd_types:
            psd_map = {"Clay":"clay", "Silt":"silt", "Sand":"sand"}
            psd_types = [psd_map[atype] for atype in psd_types]
            query = query.filter(SampleValues.psd_type.in_(psd_types))
        result = query.all()
        print(f"Retrieved {len(result)} entries after filtering")
        return result

    finally:
        session.close()


# used to find specific test by either test_id or test_file_name and remove it from the database
def delete_entry_by_test(test_id=None, test_file_name=None):
    engine = create_engine(get_path(), echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Build the query to join Entry and Test tables
        query = session.query(Entry).join(Test, Entry.test_id == Test.test_id)
        
        # Filter by test_id if provided
        if test_id:
            query = query.filter(Entry.test_id == test_id)
        
        # Filter by test_file_name if provided
        if test_file_name:
            query = query.filter(Test.test_file_name == test_file_name)
        
        # Retrieve the matched entries
        entries_to_delete = query.all()

        if not entries_to_delete:
            print("No entries found with the given test_id or test_file_name.")
            return

        # Delete the entries
        for entry in entries_to_delete:
            session.delete(entry)
            print(f"Deleted entry with ID {entry.entry_id} for test_id {entry.test_id}")

        session.commit()
        print("Entries successfully deleted.")

    except Exception as e:
        session.rollback()
        print(f"Error occurred: {e}")

    finally:
        session.close()