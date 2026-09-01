from app.database.connection import get_connection


def main():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                @@SERVERNAME AS servidor,
                @@VERSION AS version_sql_server,
                DB_NAME() AS base_actual;
        """)

        row = cursor.fetchone()

        print("Conexión exitosa.")
        print(f"Servidor: {row.servidor}")
        print(f"Base actual: {row.base_actual}")
        print("Versión:")
        print(row.version_sql_server)

    finally:
        connection.close()


if __name__ == "__main__":
    main()