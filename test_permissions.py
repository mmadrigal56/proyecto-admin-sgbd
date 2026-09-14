import pyodbc
from app.database.connection import get_connection


def main():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                SUSER_SNAME() AS login_actual,
                USER_NAME() AS usuario_actual,
                DB_NAME() AS base_actual;
        """)

        row = cursor.fetchone()

        print("Identidad de la conexión:")
        print(f"Login: {row.login_actual}")
        print(f"Usuario: {row.usuario_actual}")
        print(f"Base: {row.base_actual}")

        print("\nPermisos efectivos:")

        cursor.execute("""
            SELECT permission_name
            FROM fn_my_permissions(NULL, 'DATABASE')
            WHERE permission_name IN (
                'CONNECT',
                'SELECT',
                'VIEW DATABASE STATE',
                'VIEW DEFINITION',
                'CONTROL',
                'ALTER',
                'INSERT',
                'UPDATE',
                'DELETE'
            )
            ORDER BY permission_name;
        """)

        for permission in cursor.fetchall():
            print(f"- {permission.permission_name}")

    finally:
        connection.close()


if __name__ == "__main__":
    main()