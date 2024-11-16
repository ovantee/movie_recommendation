from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd

def extract_data(ti, file_path):
    """
    Extracts data from a CSV file.
    """
    data = pd.read_csv(file_path)
    ti.xcom_push(key='raw_data', value=data.to_json())  # Push raw data to XCom

from io import StringIO

def transform_data(ti, method='mean'):
    """
    Transforms the data by cleaning null values, converting data types,
    and handling missing values based on the specified method.
    Ensures compatibility with the PostgreSQL table schema.
    """
    # Pulling raw data from XCom, then read it with StringIO to avoid FutureWarning
    data_json = ti.xcom_pull(key='raw_data', task_ids='extract_data')
    data = pd.read_json(StringIO(data_json))

    # Ensure the data types match the database schema:
    # 'Votes' and 'Gross collection' are extracted from strings that might include commas or dollar signs.
    data['Votes'] = data['Votes'].astype(str).str.replace(',', '').astype(int)
    data['Gross collection'] = data['Gross collection'].astype(str).str.replace(',', '').str.replace('$', '').astype(float)

    # Handle 'Metascore' based on the method argument
    if method == 'mean':
        data['Metascore'] = data['Metascore'].fillna(data['Metascore'].mean())
    elif method == 'drop':
        data = data.dropna(subset=['Metascore'])

    # Fill in missing values for 'Classification' with a default value
    data['Classification'] = data['Classification'].fillna('Not Classified')

    # Push the transformed data to XCom as a JSON string
    ti.xcom_push(key='transformed_data', value=data.to_json())

def safe_convert_to_bigint(value, default=9223372036854775807):
    try:
        value = int(value)
        if value > 9223372036854775807 or value < -9223372036854775808:
            return default
        return value
    except (ValueError, TypeError):
        return default

def insert_movie_data(ti):
    """
    Inserts movie data into the 'movies' table in PostgreSQL.
    """
    data_json = ti.xcom_pull(key='transformed_data', task_ids='transform_data')
    data = pd.read_json(data_json)

    hook = PostgresHook(postgres_conn_id='postgres_connection_neon')
    connection = hook.get_conn()
    cursor = connection.cursor()
    
    insert_query = '''
    INSERT INTO movies (
        name_of_movie, year_of_release, watchtime, genre, classification, 
        movie_rating, metascore, votes, gross_collection, des, id, keywords, 
        link, img_src, director, stars
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''

    # Chèn từng dòng vào bảng
    for _, row in data.iterrows():
        try:
            values = (
                row['Name of movie'],
                int(row['Year of release']),
                int(row['Watchtime']),
                row['Genre'],
                row['Classification'],
                float(row['Movie Rating']) if pd.notnull(row['Movie Rating']) else None,
                float(row['Metascore']) if pd.notnull(row['Metascore']) else None,
                safe_convert_to_bigint(row['Votes']),
                safe_convert_to_bigint(row['Gross collection']),
                row['Des'],
                safe_convert_to_bigint(row['id']),
                row['keywords'],
                row['Link'],
                row['img_src'],
                row['Director'],
                row['Stars']
            )
            cursor.execute(insert_query, values)
        except:
            print("Tồn tại dữ liệu này")

    connection.commit()
    cursor.close()
    print("Data inserted successfully into the 'movies' table.")

with DAG(
    'movie_pipeline',
    default_args={
        'owner': 'airflow',
        'start_date': datetime(2024, 10, 5),
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='A simple movie data ETL pipeline using Python, PostgreSQL, and Apache Airflow',
    schedule_interval=timedelta(minutes=5),
    catchup=False
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_data,
        op_kwargs={'file_path': '/Users/mac/airflow/dags/data_date/output_7_Nov.csv'}
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
        op_kwargs={'method': 'mean'}
    )

    load_task = PythonOperator(
        task_id='load_data',
        python_callable=insert_movie_data
    )

    extract_task >> transform_task >> load_task
