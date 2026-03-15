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
        # Execute query and retrieve the first element from it
        #query="SELECT codename FROM players WHERE id = " + player_id
        #cursor.execute(query)
        cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
        existing_id=cursor.fetchone()
        # If the query result is empty, add (id, codename) to DB
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
# For given player_id, searches DB for record where id = player_id
# If one exists, return the CODENAME for that record
# Otherwise, return ''
def id_exists(player_id):
    connection_params = {
        'dbname': 'photon',
        'user': 'student',
    }

    conn = None
    cursor = None
    # Prevents crash if user bails out of the try block (using mouseClicked)
    output = ''

    try:
        conn = psycopg2.connect(**connection_params)
        cursor = conn.cursor()
        # Retrieve codename for record where id = player_id (should be only 1)
        #query="SELECT codename FROM players WHERE id = " + player_id
        #cursor.execute(query)
        cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
        existing_codename=cursor.fetchone()
        # If there is an existing codename, join it to output, and return output
        if existing_codename:
            output = ''.join(existing_codename)

    except Exception as error:
        print(f"Error connecting to PostgreSQL database: {error}")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    # Return either '' or codename in same record as id = player_id
    return output
# Not in use
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