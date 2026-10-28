"""
Paso 1 del pipeline ETL: EXTRAER.

Simula la extracción de ventas desde un sistema de origen y guarda los datos
"tal cual" (sucios) en data/raw/ventas.csv.

Los datos vienen con problemas a propósito (duplicados, nulos, regiones mal
escritas, precios negativos) para que transformar.py tenga algo que limpiar.

Ejecutar:
    python src/extraer.py
"""

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

# Rutas relativas a la raíz del repositorio (funciona desde cualquier carpeta)
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
ARCHIVO_RAW = RAW_DIR / "ventas.csv"

# Parámetros de la extracción
N_REGISTROS = 200
SEMILLA = 42  # misma semilla = mismos datos para todos los alumnos
FECHA_INICIO = date(2026, 1, 1)
DIAS = 180

REGIONES = ["Lima", "Arequipa", "Cusco", "Piura", "Trujillo"]
PRODUCTOS = {
    "Laptop": 3500.0,
    "Monitor": 850.0,
    "Teclado": 120.0,
    "Mouse": 60.0,
    "Audifonos": 250.0,
}


def ensuciar_region(region, rng):
    """Introduce errores típicos de digitación en el nombre de la región."""
    opcion = rng.random()
    if opcion < 0.10:
        return region.upper()
    if opcion < 0.20:
        return f"  {region.lower()} "
    return region


def extraer(n_registros=N_REGISTROS, semilla=SEMILLA):
    """Genera las ventas 'crudas' y las devuelve como DataFrame."""
    rng = random.Random(semilla)
    filas = []

    for i in range(1, n_registros + 1):
        producto = rng.choice(list(PRODUCTOS))
        precio = PRODUCTOS[producto] * rng.uniform(0.9, 1.1)
        cantidad = rng.randint(1, 10)

        # Errores de origen
        if rng.random() < 0.05:
            cantidad = None
        if rng.random() < 0.03:
            precio = -precio

        filas.append({
            "id_venta": i,
            "fecha": (FECHA_INICIO + timedelta(days=rng.randrange(DIAS))).isoformat(),
            "region": ensuciar_region(rng.choice(REGIONES), rng),
            "producto": producto,
            "cantidad": cantidad,
            "precio_unitario": round(precio, 2),
        })

    df = pd.DataFrame(filas)

    # El sistema de origen a veces envía registros repetidos
    duplicados = df.sample(n=max(1, n_registros // 20), random_state=semilla)
    df = pd.concat([df, duplicados], ignore_index=True)
    return df


def guardar(df, ruta=ARCHIVO_RAW):
    ruta.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(ruta, index=False)
    return ruta


def main():
    df = extraer()
    ruta = guardar(df)
    print(f"[EXTRAER] {len(df)} registros guardados en {ruta.relative_to(BASE_DIR)}")
    print(df.head())


if __name__ == "__main__":
    main()
