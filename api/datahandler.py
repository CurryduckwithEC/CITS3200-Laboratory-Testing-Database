from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
import pandas as pd
import os
from models import Entry, Test, TestValues, SampleValues, Base
from Cryptodome.Cipher import AES
from hashlib import sha256
import random
import math

# Constants
WORD_FOR_KEY = "apple"  # Example word for AES key generation
AES_KEY_SIZE = 256  # Key size (128, 192, or 256 bits)

# In array to allow changing of value in function, this function is merged and may not be needed
PATH = [""]

def get_path():
    return "sqlite:///" + os.path.normpath(PATH[0])

# Takes new path and name of database
def change_path(new_path: str):
    
    PATH[0] = new_path
    print(f"Path to database is now {get_path()}")

# Encryption functions
def word_to_aes_key(word: str, key_size: int = 256) -> bytes:
    if key_size not in [128, 192, 256]:
        raise ValueError("Invalid key size. Choose from 128, 192, or 256 bits.")
    word_bytes = word.encode('utf-8')
    hash_bytes = sha256(word_bytes).digest()
    return hash_bytes[:key_size // 8]

def generate_encryption_parameters(aes_key: bytes) -> tuple:
    random.seed(aes_key)
    amplitude = random.uniform(0.5, 2.0)
    frequency = random.uniform(0.1, 1.0)
    phase = random.uniform(0, 2 * math.pi)
    shift = random.uniform(-10, 10)
    return amplitude, frequency, phase, shift

def encrypt_data(value: float, amplitude: float, frequency: float, phase: float, shift: float) -> float:
    return round(value + amplitude * math.sin(frequency * value + phase) + shift * value, 6)

def decrypt_data(value: float, amplitude: float, frequency: float, phase: float, shift: float) -> float:
    x = value / (1 + shift)  # A rough estimate for initial guess
    for _ in range(10):  # 10 iterations for convergence
        dynamic_shift = shift * x
        fx = x + amplitude * math.sin(frequency * x + phase) + dynamic_shift - value
        dfx = 1 + amplitude * frequency * math.cos(frequency * x + phase) + shift
        x = x - fx / dfx
    return round(x, 6)

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

def entry_objects(df: pd.DataFrame, test: Test, encrypt_params: tuple):
    amplitude, frequency, phase, shift = encrypt_params
    def row_to_entry(row):
        return Entry(
            test_id = test.test_id,
            time_start_of_stage = row["time start of stage"],
            axial_strain = encrypt_data(row["axial strain"], *encrypt_params),
            vol_strain = encrypt_data(row["volumetric strain"], *encrypt_params),
            excess_pwp = encrypt_data(row["excess pwp"], *encrypt_params),
            p = encrypt_data(row["p'"], *encrypt_params),
            deviator_stress = encrypt_data(row["deviator stress"], *encrypt_params),
            void_ratio = encrypt_data(row["void ratio"], *encrypt_params),
            shear_induced_pwp = encrypt_data(row["shear induced pwp"], *encrypt_params)
        )
    return df.apply(row_to_entry, axis=1).tolist()


# Function that takes the data of a new entry and commits to database
# The ordering matters of the commit due to foreign key dependencies
# Takes absolute path to database
def commit_new_entry(specs: dict, df: pd.DataFrame, file_name: str):
    aes_key = word_to_aes_key(WORD_FOR_KEY, AES_KEY_SIZE)
    encrypt_params = generate_encryption_parameters(aes_key)

    sample_values = sample_values_object(specs)
    test_values = test_values_object(specs)
    test = test_object(specs, sample_values, test_values, file_name)
    entries = entry_objects(df, test, encrypt_params)

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
    aes_key = word_to_aes_key(WORD_FOR_KEY, AES_KEY_SIZE)
    decrypt_params = generate_encryption_parameters(aes_key)
    
    engine = create_engine(get_path(), echo=True)

    with Session(engine) as session:
        df = pd.read_sql(session.query(Entry).statement, session.bind)

    # Decrypt the data
    for column in ['axial_strain', 'vol_strain', 'excess_pwp', 'p', 'deviator_stress', 'void_ratio', 'shear_induced_pwp']:
        df[column] = df[column].apply(lambda x: decrypt_data(x, *decrypt_params))

    return df
    

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
