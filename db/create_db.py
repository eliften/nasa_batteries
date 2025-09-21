import psycopg2, os, logging
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import dotenv
dotenv.load_dotenv()

logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )

def ensure_database():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname="postgres",
        user=DB_USER, password=DB_PASSWORD
    )
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (DB_NAME,))
        exists = cur.fetchone() is not None
        if not exists:
            cur.execute(sql.SQL("CREATE DATABASE {} WITH ENCODING 'UTF8' TEMPLATE template0;")
                        .format(sql.Identifier(DB_NAME)))
            print(f"Database created: {DB_NAME}")
    conn.close()


def create_table():
    ensure_database()
    conn = get_connection()
    create_table_query = """
        CREATE TABLE measurements
        (
        id                   int    NOT NULL GENERATED ALWAYS AS IDENTITY UNIQUE,
        cycle_id             int    NOT NULL,
        type                 text  ,
        ambient_temperature  int   ,
        date_time            date  ,
        voltage_measured     float8,
        current_measured     float8,
        temperature_measured float8,
        current_charge       float8,
        voltage_charge       float8,
        time                 float8,
        capacity             float8,
        data_type            text  ,
        dt_s                 float8,
        dQ_Ah                float8,
        Q_cum_Ah             float8,
        dV_dt                float8,
        soc_percent          float8,
        added_date           date  
        );
    """
    if conn:
        cur = conn.cursor()
        try:
            cur.execute(create_table_query)
            conn.commit()
            print(f"{DB_NAME} tablosu başarıyla oluşturuldu veya zaten mevcut.")
        except Exception as e:
            print(f"Tablo oluşturulurken hata oluştu: {e}")
        finally:
            cur.close()
            conn.close()


def insert_dataframe_to_db(df):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            columns = df.columns.tolist()
            values_placeholder = ", ".join(["%s"] * len(columns))
            insert_query = f"INSERT INTO measurements ({', '.join(columns)}) VALUES ({values_placeholder})"

            data_tuples = [tuple(row) for row in df[columns].to_numpy()]

            cur.executemany(insert_query, data_tuples)

        conn.commit()
        print(f"{len(df)} kayıt başarıyla eklendi.")
    except Exception as e:
        conn.rollback()
        print(f"Veri eklenirken hata oluştu: {e}")
    finally:
        conn.close()
