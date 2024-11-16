import psycopg2
import pandas as pd
from psycopg2 import OperationalError
file_path = 'movie_merged_output.csv'  # Cập nhật đường dẫn tới file của bạn
movie_data = pd.read_csv(file_path)
movie_data = movie_data.drop_duplicates(subset=['Name of movie', 'Year of release'])
def create_connection():
    try:
        # Sử dụng connection string của bạn, thay thế `your_password_here` bằng mật khẩu thực tế
        connection = psycopg2.connect(
            "postgresql://moviedb_owner:BA7XeptPqFR3@ep-yellow-firefly-a5.us-east-2.aws.neon.tech/moviedb?sslmode=require"
        )
        print("Connection to PostgreSQL DB successful")
        return connection
    except OperationalError as e:
        print(f"The error '{e}' occurred")
        return None

# Thử kết nối
connection = create_connection()

# Đóng kết nối sau khi xong
if connection:
    connection.close()
    print("Connection closed")

import psycopg2
from psycopg2 import sql

def create_movie_table(connection):
    create_table_query = '''
    CREATE TABLE IF NOT EXISTS movies (
        name_of_movie VARCHAR(255) NOT NULL,
        year_of_release INT NOT NULL,
        watchtime INT NOT NULL,
        genre VARCHAR(255),
        classification VARCHAR(50),
        movie_rating FLOAT,
        metascore FLOAT,
        votes BIGINT,
        gross_collection BIGINT,
        des TEXT,
        id BIGINT,
        keywords TEXT,
        link VARCHAR(255),
        img_src VARCHAR(255),
        director VARCHAR(255),
        stars TEXT,
        PRIMARY KEY (name_of_movie, year_of_release)
    );
    '''
    try:
        cursor = connection.cursor()
        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        print("Table 'movies' created successfully with primary key (name_of_movie, year_of_release)")
    except Exception as e:
        print(f"An error occurred: {e}")

# Kết nối và tạo bảng
connection = create_connection()
if connection:
    create_movie_table(connection)
    connection.close()


# Hàm chèn dữ liệu vào bảng movies
def insert_movie_data(connection, data):
    insert_query = '''
    INSERT INTO movies (
        name_of_movie, year_of_release, watchtime, genre, classification, 
        movie_rating, metascore, votes, gross_collection, des, id, keywords, 
        link, img_src, director, stars
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    '''

    cursor = connection.cursor()

    # Chèn từng dòng vào bảng
    for _, row in data.iterrows():
        values = (
            row['Name of movie'],
            row['Year of release'],
            row['Watchtime'],
            row['Genre'],
            row['Classification'] if pd.notnull(row['Classification']) else None,
            row['Movie Rating'],
            row['Metascore'] if pd.notnull(row['Metascore']) else None,
            int(row['Votes'].replace(',', '')) if pd.notnull(row['Votes']) else None,
            int(row['Gross collection'].replace(',', '')) if pd.notnull(row['Gross collection']) else None,
            row['Des'],
            int(row['id']) if pd.notnull(row['id']) else None,
            row['keywords'] if pd.notnull(row['keywords']) else None,
            row['Link'],
            row['img_src'],
            row['Director'],
            row['Stars']
        )
        cursor.execute(insert_query, values)

    connection.commit()
    cursor.close()
    print("Data inserted successfully")


# Kết nối và chèn dữ liệu
connection = create_connection()
if connection:
    insert_movie_data(connection, movie_data)
    connection.close()
