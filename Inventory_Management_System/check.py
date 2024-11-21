# check.py
import cx_Oracle
import config

try:
    connection = cx_Oracle.connect(
        config.ORACLE_USERNAME,
        config.ORACLE_PASSWORD,
        config.ORACLE_DSN
    )
    cursor = connection.cursor()
    print("Connected to the database successfully")
    # Your code to interact with the database goes here

except cx_Oracle.DatabaseError as e:
    print(f"There was an error connecting to the database: {e}")

finally:
    # Close the cursor and connection only if they were created
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection:
        connection.close()
