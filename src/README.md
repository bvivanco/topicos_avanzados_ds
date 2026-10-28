# Práctica: pipeline ETL con Git

Tres scripts que forman un pipeline de datos de ventas:

| Archivo | Qué hace |
|---|---|
| `extraer.py` | Genera ventas con errores y las guarda en `data/raw/ventas.csv` |
| `transformar.py` | Limpia los datos y calcula IGV y total → `data/processed/ventas_limpias.csv` |
| `cargar.py` | Guarda los datos en SQLite (`data/ventas.db`) y muestra un resumen por región |

Requisito: Python 3 con `pandas` (`pip install pandas`).

## 1. Clonar y ejecutar

```bash
git clone https://github.com/bvivanco/topicos_avanzados_ds.git
cd topicos_avanzados_ds

python src/extraer.py
python src/transformar.py
python src/cargar.py
```

## 2. Ignorar los datos generados

```bash
git status                 # aparece la carpeta data/
echo "data/" > .gitignore
git status                 # data/ ya no aparece
git add .gitignore
git commit -m "Ignorar datos generados"
```

## 3. Modificar un archivo y hacer commit

En `extraer.py` cambia `N_REGISTROS = 200` por `N_REGISTROS = 500`.

```bash
git diff                   # ver el cambio
python src/extraer.py      # comprobar que funciona
git add src/extraer.py
git commit -m "Extraer 500 registros"
git log --oneline
```

## 4. Trabajar en una rama

```bash
git switch -c nueva-region
```

En `extraer.py` agrega `"Chiclayo"` a la lista `REGIONES`. Ejecuta los tres scripts y verifica que Chiclayo aparece en el resumen.

```bash
git add src/extraer.py
git commit -m "Agregar región Chiclayo"
git switch main
git merge nueva-region
```

## 5. Reto: resolver un conflicto

Dos ramas cambian la misma línea `TASA_IGV` de `transformar.py`:

```bash
git switch -c igv-a
# en transformar.py cambia TASA_IGV = 0.18 por TASA_IGV = 0.10
git commit -am "IGV 10%"

git switch main
git switch -c igv-b
# en transformar.py cambia TASA_IGV = 0.18 por TASA_IGV = 0.19
git commit -am "IGV 19%"

git switch main
git merge igv-a
git merge igv-b            # CONFLICT
```

Abre `transformar.py`, borra los marcadores `<<<<<<<`, `=======`, `>>>>>>>` y deja `TASA_IGV = 0.18`. Luego:

```bash
python src/transformar.py
git add src/transformar.py
git commit -m "Resolver conflicto de IGV"
```
