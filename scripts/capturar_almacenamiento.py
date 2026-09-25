"""Captura periódica de almacenamiento. Lo ejecuta el Programador de tareas de Windows."""

import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "app"))

from database.queries.almacenamiento import registrar_medicion  # noqa: E402

LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "captura_almacenamiento.log"


def escribir_log(mensaje):
    LOG_DIR.mkdir(exist_ok=True)
    linea = f"{datetime.now():%Y-%m-%d %H:%M:%S} | {mensaje}"
    with open(LOG_FILE, "a", encoding="utf-8") as archivo:
        archivo.write(linea + "\n")
    print(linea)


def main():
    try:
        filas = registrar_medicion(origen="programado")
    except Exception as error:
        escribir_log(f"ERROR | {type(error).__name__}: {error}")
        return 1

    if not filas:
        escribir_log("ERROR | El procedimiento no devolvió filas; no se confirmó la medición.")
        return 1

    detalle = "; ".join(
        f"{f['nombre_logico']} ({f['tipo_archivo']}): "
        f"{f['espacio_usado_mb']:.2f}/{f['tamano_asignado_mb']:.2f} MB"
        for f in filas
    )
    escribir_log(f"OK | {filas[0]['base_datos']} | {detalle}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
