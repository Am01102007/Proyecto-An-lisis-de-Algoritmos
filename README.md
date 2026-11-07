# Rutas del Paisaje Cultural Cafetero

Proyecto final de Análisis de Algoritmos (2026-2). Integrantes: Helen Xiomara Giraldo, Valentina Porras y Maryam Hernández Giraldo.

Sistema de planificación de rutas sobre la red vial del Quindío (OpenStreetMap), con análisis teórico y experimental de Dijkstra, la envolvente convexa (Quickhull), la fuerza bruta, Held-Karp y una heurística voraz para el viajante asimétrico.

## Estructura

| Carpeta | Contenido |
| --- | --- |
| `specs/` | Especificación de cada requerimiento (comportamiento esperado y casos de prueba) |
| `src/` | Código. Los algoritmos propios están en `dijkstra.py`, `envolvente.py` y `viajante.py` |
| `tests/` | Pruebas de los algoritmos propios contra casos a mano, NetworkX y SciPy |
| `datos/` | Catálogo de lugares, red descargada y componente procesada |
| `resultados/` | CSV y JSON de los experimentos, `tablas.md` y `maquina.json` |
| `graficas/` | Gráficas en PNG generadas desde los CSV |
| `docs/` | Documento técnico |

## Cómo reproducir

Requiere Python 3.10 o superior. Todo se ejecuta desde la raíz del repositorio, en este orden:

```bash
python -m venv .venv
source .venv/bin/activate          # en Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m pytest tests             # 1. verificar los algoritmos (debe decir "6 passed")
python src/r1_red.py               # 2. R1: descarga la red, pesos, componente, lugares (necesita internet)
python src/r2_caminos.py           # 3. R2: Dijkstra y matriz de tiempos (la versión lineal tarda)
python src/r3_envolvente.py        # 4. R3: envolvente convexa contra SciPy
python src/r4_ruta.py              # 5. R4: fuerza bruta, Held-Karp, voraz e itinerario (hasta ~15 min)
python src/graficas.py             # 6. tablas y gráficas desde los CSV
streamlit run src/app.py           # 7. R5: aplicación en el navegador
```

Después del paso 2 ya no hace falta internet: la componente queda guardada en `datos/componente.graphml`.

## Protocolo experimental

Cada medición se repite 5 veces y se reporta la mediana en milisegundos (`time.perf_counter_ns`). Si la primera ejecución pasa de un minuto, se mide una sola vez. Una ejecución de más de 5 minutos se detiene y se reporta como «no completada». Solo se mide la llamada al algoritmo: la lectura de archivos y la preparación de datos quedan por fuera. La semilla de todos los datos aleatorios es 2026 (`src/config.py`). Los datos de la máquina quedan en `resultados/maquina.json`.
