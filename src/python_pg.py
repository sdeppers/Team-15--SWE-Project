import psycopg2
from psycopg2 import sql

def add_player(player_id, codename):
    # Define connection parameters
    connection_params = {
        'dbname': 'photon',
        'user': 'student',
        #'password': 'student',
        #'host': 'localhost',
        #'port': '5432'
    }

    # safe gaurd so no confusing errors if it never connects
    conn = None
    cursor = None
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        # # Execute a query
        # cursor.execute("SELECT version();")

        # # Fetch and display the result
        # version = cursor.fetchone()
        # print(f"Connected to - {version}")

        # Example: creating a table
        #cursor.execute('''
        #    CREATE TABLE IF NOT EXISTS employees (
        #        id SERIAL PRIMARY KEY,
        #        name VARCHAR(100),
        #        department VARCHAR(50),
        #        salary DECIMAL
        #    );
        #''')
        query="SELECT codename FROM players WHERE id = " + player_id
        cursor.execute(query)
        existing_id=cursor.fetchone()

        if not existing_id:
            cursor.execute('''
                INSERT INTO players (id, codename)
                VALUES (%s, %s);'''
                , (player_id, codename))

            # Commit the changes
            conn.commit()

    except Exception as error:
        print(f"Error connecting to PostgreSQL database: {error}")

    finally:
        # Close the cursor and connection
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

def id_exists(player_id):
# Define connection parameters
    connection_params = {
        'dbname': 'photon',
        'user': 'student',
    }

    conn = None
    cursor = None
    # Prevents crash if user bails out of the try block
    output = ''

    try:
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        query="SELECT codename FROM players WHERE id = " + player_id
        cursor.execute(query)
        existing_codename=cursor.fetchone()
        if existing_codename:
            output = ''.join(existing_codename)

    except Exception as error:
        print(f"Error connecting to PostgreSQL database: {error}")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return output

def delete_database():
    connection_params = {
        'dbname': 'photon',
        'user': 'student',
    }

    conn = None
    cursor = None
    try:
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM players")
        conn.commit()

    except Exception as error:
        print(f"Error connecting to PostgreSQL database: {error}")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()