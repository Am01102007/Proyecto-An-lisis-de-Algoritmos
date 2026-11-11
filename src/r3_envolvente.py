"""Requerimiento 3. Experimento de la envolvente convexa: Quickhull propio contra SciPy.

Ejecutar desde la raíz:  python src/r3_envolvente.py
"""
import csv
import json
import random

import numpy as np
from pyproj import Transformer
from scipy.spatial import ConvexHull

from config import COMPONENTE, CRS_UTM, RESULTADOS, SEMILLA
from envolvente import envolvente_convexa
from medicion import guardar_maquina, medir

TAMANOS = [1_000, 10_000, 50_000]
LADO_M = 1_000_000   # cuadrado de 1 000 km de lado, en metros enteros


def puntos_de_la_red():
    """Nodos de la componente en UTM 18N, redondeados al entero y sin repetidos."""
    import osmnx as ox
    G = ox.load_graphml(COMPONENTE)
    a_utm = Transformer.from_crs("EPSG:4326", CRS_UTM, always_xy=True)
    xs, ys = a_utm.transform([d["x"] for _, d in G.nodes(data=True)],
                             [d["y"] for _, d in G.nodes(data=True)])
    return sorted({(int(round(x)), int(round(y))) for x, y in zip(xs, ys)})


def puntos_al_azar(n):
    rng = random.Random(SEMILLA)
    puntos = set()
    while len(puntos) < n:
        puntos.add((rng.randint(0, LADO_M), rng.randint(0, LADO_M)))
    return sorted(puntos)


def envolvente_scipy(arreglo):
    return ConvexHull(arreglo)


def experimento(nombre, puntos):
    arreglo = np.array(puntos, dtype=np.float64)   # preparación: fuera de la medición
    ms_propio, propio = medir(envolvente_convexa, puntos)
    ms_scipy, hull = medir(envolvente_scipy, arreglo)
    vertices_scipy = {puntos[i] for i in hull.vertices}
    assert set(propio) == vertices_scipy, f"{nombre}: los vértices no coinciden"
    print(f"  {nombre}: n = {len(puntos)}, {len(propio)} vértices, "
          f"propio {ms_propio:.2f} ms, SciPy {ms_scipy:.2f} ms")
    return {"conjunto": nombre, "n": len(puntos), "vertices": len(propio),
            "tiempo_propio_ms": round(ms_propio, 3), "tiempo_scipy_ms": round(ms_scipy, 3),
            "cociente": round(ms_propio / ms_scipy, 2)}


def main():
    guardar_maquina()
    red = puntos_de_la_red()
    filas = [experimento("Nodos de la red", red)]
    for n in TAMANOS:
        filas.append(experimento(f"Cuadrado, {n:,} puntos".replace(",", " "), puntos_al_azar(n)))
    with open(RESULTADOS / "r3_envolvente.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    # Vértices de la envolvente de la red, en lat/lon, para dibujarla en la aplicación
    a_geo = Transformer.from_crs(CRS_UTM, "EPSG:4326", always_xy=True)
    vertices = envolvente_convexa(red)
    lon, lat = a_geo.transform([p[0] for p in vertices], [p[1] for p in vertices])
    (RESULTADOS / "r3_envolvente_red.json").write_text(
        json.dumps([[la, lo] for la, lo in zip(lat, lon)]), encoding="utf-8")


if __name__ == "__main__":
    main()
