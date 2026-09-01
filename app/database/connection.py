import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv


# Buscar el directorio raíz del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Cargar las variables de entorno desde config/.env.
ENV_FILE = PROJECT_ROOT / "config" / ".env"
load_dotenv(ENV_FILE)


def get_connection():
    """
    Crea y devuelve una conexión a SQL Server utilizando
    las variables definidas en config/.env.
    """

    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = os.getenv("DB_DRIVER")
    trust_certificate = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "no")

    required_variables = {
        "DB_SERVER": server,
        "DB_NAME": database,
        "DB_USER": username,
        "DB_PASSWORD": password,
        "DB_DRIVER": driver,
    }

    missing_variables = [
        name for name, value in required_variables.items()
        if not value
    ]

    if missing_variables:
        raise RuntimeError(
            "Faltan variables de entorno: "
            + ", ".join(missing_variables)
        )

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"TrustServerCertificate={trust_certificate};"
    )

    return pyodbc.connect(connection_string)