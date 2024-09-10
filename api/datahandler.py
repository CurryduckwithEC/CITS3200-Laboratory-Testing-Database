from sqlalchemy import create_engine
from sqlalchemy.orm import Session

import pandas as pd

from models import Entry, Test, TestValues, SampleValues, Base

# In array to allow changing of value in function
PATH = [""]

def get_path():
    return PATH[0]

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

def test_object(specs: dict, sample_values: SampleValues, test_values: TestValues) -> Test:

    # Make sure to commit any foreign key dependencies first
    test = Test(
        test_value_id = test_values.test_value_id,
        sample_value_id = sample_values.sample_value_id,

        consolidation = specs["consolidation"],
        anisotropy = specs["anisotropy"]
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
def commit_new_entry(specs: dict, df: pd.DataFrame):

    sample_values = sample_values_object(specs)
    test_values = test_values_object(specs)
    test = test_object(specs, sample_values, test_values)

    entries = entry_objects(df, test)

    test.entries.extend(entries)
    sample_values.test = test
    test_values.test = test

    engine = create_engine("sqlite:////" + get_path(), echo=True)
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
    
    engine = create_engine("sqlite:///f1.db", echo=True)

    with Session(engine) as session:
        df = pd.read_sql(session.query(Entry).statement, session.bind)

    # split dataframe into list of dataframes by test id
    split_df = [group for _, group in df.groupby("test_id")]

    return split_df
    
