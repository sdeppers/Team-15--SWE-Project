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

        # Insert sample data
        cursor.execute('''
            INSERT INTO players (id, codename)
            VALUES (%s, %s);
        ''', (player_id, codename))

        # Commit the changes
        conn.commit()

        # # Fetch and display data from the table
        # cursor.execute("SELECT * FROM players;")
        # rows = cursor.fetchall()
        # for row in rows:
        #     print(row)

    except Exception as error:
        print(f"Error connecting to PostgreSQL database: {error}")

    finally:
        # Close the cursor and connection
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


# code to test if it worked
# ran the test with: python3 sql/python-pg.py
# ran this to delete row: psql -U student -d photon -c "DELETE FROM players WHERE id = 1;"
# if __name__ == "__main__":
#     add_player(1001, "EshaanTest1")
#     add_player(1002, "EshaanTest2")
#     print("Insert 2 players")