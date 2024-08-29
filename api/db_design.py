import psycopg2
from psycopg2 import OperationalError
import itertools

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
CREATE TABLE IF NOT EXISTS "test_values" (
	"test_value_id" SERIAL PRIMARY KEY,
	"drainage_type" varchar(255) NOT NULL,
	"shearing_type" varchar(255) NOT NULL,
	"anisotropy_type" varchar(255) NOT NULL,
	"availability_type" varchar(255) NOT NULL
    )
"""
)

cur.execute("""           
CREATE TABLE IF NOT EXISTS "sample_values" (
	"sample_value_id" SERIAL PRIMARY KEY,
	"density_type" varchar(255) NOT NULL,
	"plasticity_type" varchar(255) NOT NULL,
	"psd_type" varchar(255) NOT NULL
    )
"""
)

cur.execute("""
CREATE TABLE IF NOT EXISTS "test" (
	"test_id" SERIAL PRIMARY KEY,
	"test_value_id" INTEGER NOT NULL,
	"sample_value_id" INTEGER NOT NULL,
	"consolidation" INTEGER NOT NULL,
	"anisotropic" numeric(10,0) NOT NULL,
    FOREIGN KEY (test_value_id) REFERENCES test_values(test_value_id),
    FOREIGN KEY (sample_value_id) REFERENCES sample_values(sample_value_id)
    )
"""
)

cur.execute("""
CREATE TABLE IF NOT EXISTS "entry" (
	"entry_id" SERIAL PRIMARY KEY,
	"test_id" INTEGER NOT NULL,
	"time_start_of_stage" INTEGER NOT NULL,
	"shear_induced_pwp" double precision NOT NULL,
	"axial_strain" varchar(255) NOT NULL,
	"vol_strain" INTEGER NOT NULL,
	"induced_pwp" double precision NOT NULL,
	"p'" varchar(255) NOT NULL,
	"q" varchar(255) NOT NULL,
	"e" varchar(255) NOT NULL,
    FOREIGN KEY (test_id) REFERENCES test(test_id)
    )
"""
)

data_properties = {
    "drainage": ["drained", "undrained"],
    "shearing": ["compression", "extension"],
    "anisotropic": ["isotropic", "anisotropic"],
    "availability": ["public", "confidential"]
}

combinations = itertools.product(
    data_properties["drainage"],
    data_properties["shearing"],
    data_properties["anisotropic"],
    data_properties["availability"]
)

for combination in combinations:
        sql = f"""
        INSERT INTO test_values (drainage_type, shearing_type, anisotropy_type, availability_type)
        VALUES (%s, %s, %s, %s)
        """
        cur.execute(sql, combination)

soil_properties = {
        "density": ["loose", "dense"],
        "plasticity": ["plastic", "non-plastic", "unknown"],
        "psd": ["clay", "silt", "sand"]
        }

combinations2 = itertools.product(
    soil_properties["density"],
    soil_properties["plasticity"],
    soil_properties["psd"]
)

for combination in combinations2:
        sql = f"""
        INSERT INTO sample_values (density_type, plasticity_type, psd_type)
        VALUES (%s, %s, %s)
        """
        cur.execute(sql, combination)
connection.commit()
cur.close()
connection.close()


