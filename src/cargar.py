"""
Paso 3 del pipeline ETL: CARGAR.

Lee data/processed/ventas_limpias.csv y lo carga en una base de datos SQLite
(data/ventas.db) junto con una tabla resumen por región.

Ejecutar (después de transformar.py):
    python src/cargar.py
"""

import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVO_PROCESADO = BASE_DIR / "data" / "processed" / "ventas_limpias.csv"
BASE_DATOS = BASE_DIR / "data" / "ventas.db"

TABLA_VENTAS = "ventas"
TABLA_RESUMEN = "resumen_region"


def leer(ruta=ARCHIVO_PROCESADO):
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Ejecuta primero: python src/transformar.py"
        )
    return pd.read_csv(ruta, parse_dates=["fecha"])


def resumir(df):
    """Total vendido y número de ventas por región."""
    return (
        df.groupby("region", as_index=False)
        .agg(n_ventas=("id_venta", "count"), total=("total", "sum"))
        .round({"total": 2})
        .sort_values("total", ascending=False)
    )


def cargar(df, ruta_bd=BASE_DATOS):
    """Escribe las tablas en SQLite (las reemplaza si ya existen)."""
    ruta_bd.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(ruta_bd) as conexion:
        df.to_sql(TABLA_VENTAS, conexion, if_exists="replace", index=False)
        resumir(df).to_sql(TABLA_RESUMEN, conexion, if_exists="replace", index=False)
    return ruta_bd


def consultar(sql, ruta_bd=BASE_DATOS):
    with sqlite3.connect(ruta_bd) as conexion:
        return pd.read_sql_query(sql, conexion)


def main():
    df = leer()
    ruta = cargar(df)
    print(f"[CARGAR] {len(df)} registros cargados en {ruta.relative_to(BASE_DIR)}")
    print(f"[CARGAR] Tabla '{TABLA_RESUMEN}':")
    print(consultar(f"SELECT * FROM {TABLA_RESUMEN}").to_string(index=False))


if __name__ == "__main__":
    main()
