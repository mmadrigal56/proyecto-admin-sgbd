import os
from pathlib import Path

import pyodbc
from dotenv import load_dotenv


# Buscar el directorio raíz del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Cargar las variables de entorno desde config/.env.
ENV_FILE = PROJECT_ROOT / "config" / ".env"
load_dotenv(ENV_FILE)


def _conectar(username, password, etiqueta_usuario):
    """
    Construye la cadena de conexión y devuelve una conexión pyodbc.

    etiqueta_usuario se usa solo para que los mensajes de error
    indiquen con cuál credencial (consultiva o administrativa) falló
    la conexión, sin exponer la contraseña.
    """

    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    driver = os.getenv("DB_DRIVER")
    trust_certificate = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "no")

    required_variables = {
        "DB_SERVER": server,
        "DB_NAME": database,
        "DB_DRIVER": driver,
        f"usuario ({etiqueta_usuario})": username,
        f"contraseña ({etiqueta_usuario})": password,
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


def get_connection():
    """
    Crea y devuelve una conexión a SQL Server utilizando el usuario
    CONSULTIVO (DB_USER / DB_PASSWORD en config/.env). Esta conexión
    solo puede leer información; no puede ejecutar operaciones de
    mantenimiento.
    """
    return _conectar(
        os.getenv("DB_USER"),
        os.getenv("DB_PASSWORD"),
        "consultivo",
    )


def get_admin_connection():
    """
    Crea y devuelve una conexión a SQL Server utilizando el usuario
    ADMINISTRATIVO (DB_ADMIN_USER / DB_ADMIN_PASSWORD en config/.env).

    Esta conexión es la única autorizada para ejecutar operaciones
    reales de mantenimiento (Módulo 6). Nunca debe usarse para las
    páginas de solo consulta de los demás módulos.

    Si las variables administrativas no están configuradas, lanza un
    error explícito y comprensible en vez de fallar de forma confusa
    más adelante.
    """
    return _conectar(
        os.getenv("DB_ADMIN_USER"),
        os.getenv("DB_ADMIN_PASSWORD"),
        "administrativo",
    )
