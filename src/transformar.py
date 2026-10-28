"""
Paso 2 del pipeline ETL: TRANSFORMAR.

Lee data/raw/ventas.csv, limpia los datos y agrega columnas calculadas.
El resultado se guarda en data/processed/ventas_limpias.csv.

Ejecutar (después de extraer.py):
    python src/transformar.py
"""

from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVO_RAW = BASE_DIR / "data" / "raw" / "ventas.csv"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
ARCHIVO_PROCESADO = PROCESSED_DIR / "ventas_limpias.csv"

# Reglas de negocio
TASA_IGV = 0.18


def leer(ruta=ARCHIVO_RAW):
    if not ruta.exists():
        raise FileNotFoundError(
            f"No existe {ruta}. Ejecuta primero: python src/extraer.py"
        )
    return pd.read_csv(ruta)


def limpiar(df):
    """Elimina duplicados, nulos y valores inválidos; normaliza textos."""
    df = df.drop_duplicates(subset="id_venta")
    df = df.dropna(subset=["cantidad"])
    df = df[df["precio_unitario"] > 0]
    df = df.assign(
        region=df["region"].str.strip().str.title(),
        cantidad=df["cantidad"].astype(int),
        fecha=pd.to_datetime(df["fecha"]),
    )
    return df


def agregar_columnas(df):
    """Calcula montos y columnas de fecha útiles para el análisis."""
    subtotal = (df["cantidad"] * df["precio_unitario"]).round(2)
    igv = (subtotal * TASA_IGV).round(2)
    return df.assign(
        subtotal=subtotal,
        igv=igv,
        total=(subtotal + igv).round(2),
        mes=df["fecha"].dt.strftime("%Y-%m"),
    )


def transformar(df):
    df_limpio = limpiar(df)
    df_final = agregar_columnas(df_limpio)
    return df_final.sort_values("fecha").reset_index(drop=True)


def guardar(df, ruta=ARCHIVO_PROCESADO):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    return ruta


def main():
    df_raw = leer()
    df = transformar(df_raw)
    ruta = guardar(df)
    print(f"[TRANSFORMAR] {len(df_raw)} registros leídos -> {len(df)} registros limpios")
    print(f"[TRANSFORMAR] Guardado en {ruta.relative_to(BASE_DIR)}")
    print(df.head())


if __name__ == "__main__":
    main()
