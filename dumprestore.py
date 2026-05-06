import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

host_name = "localhost"
user_name = "root"
user_password = os.getenv("MYSQL_ROOT_PASSWORD")

if __name__ == "__main__":
    with open("dump.sql", "r", encoding="utf-8") as sql:
        connection = mysql.connector.connect(
            host=host_name, user=user_name, passwd=user_password
        )
        command = (
            """
        RESET BINARY LOGS AND GTIDS;
        DROP DATABASE IF EXISTS test;
        CREATE DATABASE IF NOT EXISTS test;
        USE test;
        """
            + sql.read()
        )

        with connection.cursor() as cur:
            cur.execute(command)
            for _, result_set in cur.fetchsets():  # drain all result sets
                pass

        connection.commit()
        connection.close()
