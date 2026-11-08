"""Requerimiento 1. Modelo de la red vial.

Ejecutar desde la raíz del repositorio:  python src/r1_red.py
Descarga las redes (necesita internet), así que es el único paso que tarda por la red.
"""
import csv
import json
import time
from datetime import date

import numpy as np
import osmnx as ox
from pyproj import Transformer

from config import (CATALOGO, COMPONENTE, CRS_UTM, DATOS, LUGAR, LUGARES_NODOS, PLAZA_BOLIVAR,
                    RED_COMPLETA, RESULTADOS)
from medicion import guardar_maquina, medir

RADIOS_KM = [2, 5, 10, 20]
UMBRAL_LEJANO_M = 500

# Velocidad por tipo de vía para los tramos sin "maxspeed" (km/h). Criterio del grupo,
# basado en los límites generales del Código Nacional de Tránsito (Ley 769 de 2002, art. 106,
# modificado por la Ley 1239 de 2008): 80 km/h en vías nacionales y 30–60 km/h en zonas urbanas.
VELOCIDAD_POR_TIPO = {
    "motorway": 80, "trunk": 80, "primary": 60, "secondary": 50, "tertiary": 40,
    "unclassified": 30, "residential": 30, "living_street": 20, "service": 20,
}
VELOCIDAD_RESPALDO = 30

# Servidores de Overpass: si el principal está saturado, se prueba el espejo
SERVIDORES_OVERPASS = ["https://overpass-api.de/api", "https://overpass.kumi.systems/api"]


# ---------- Descarga con reintentos ----------

def descargar(funcion, *args, **kwargs):
    """Llama a una función de descarga de OSMnx; si Overpass está saturado, espera y reintenta.

    Espera 30, 60, 120 y 240 s (espera exponencial) y alterna entre los servidores.
    """
    espera = 30
    for intento in range(1, 6):
        ox.settings.overpass_url = SERVIDORES_OVERPASS[(intento - 1) % len(SERVIDORES_OVERPASS)]
        try:
            return funcion(*args, **kwargs)
        except Exception as e:   # errores de red o de Overpass (502, 504, 429, respuesta vacía...)
            if intento == 5:
                raise
            print(f"    falló la descarga ({type(e).__name__}); reintento {intento}/4 en {espera} s...")
            time.sleep(espera)
            espera *= 2


def red_guardada(ruta, funcion, *args, **kwargs):
    """Si la red ya está guardada en datos/, la lee; si no, la descarga y la guarda."""
    if ruta.exists():
        return ox.load_graphml(ruta)
    G = descargar(funcion, *args, **kwargs)
    ox.save_graphml(G, ruta)
    return G


# ---------- 1. Representación ----------

def estimar_memoria(V, E):
    """MB que ocuparía la red como matriz y como listas de adyacencia (supuestos en el informe)."""
    mb = 1024 ** 2
    return {
        # Matriz: V*V celdas; cada celda guarda el tiempo de viaje como float64 (8 bytes)
        "matriz_float64_mb": V * V * 8 / mb,
        # Matriz mínima: 1 byte por celda (solo "hay vía o no")
        "matriz_1byte_mb": V * V * 1 / mb,
        # Listas: V cabeceras (puntero de 8 bytes) + E entradas (vecino int64 + peso float64 = 16 bytes)
        "listas_mb": (V * 8 + E * 16) / mb,
    }


# ---------- 2. Pesos ----------

def agregar_pesos(G):
    """Agrega speed_kph y travel_time (s) a cada arista. La distancia (length, en m) ya viene de OSMnx."""
    con_velocidad = sum(1 for *_, d in G.edges(data=True) if d.get("maxspeed"))
    G = ox.routing.add_edge_speeds(G, hwy_speeds=VELOCIDAD_POR_TIPO, fallback=VELOCIDAD_RESPALDO)
    G = ox.routing.add_edge_travel_times(G)   # travel_time = length / (speed_kph / 3.6)
    return G, {"aristas": G.number_of_edges(), "con_maxspeed": con_velocidad,
               "imputadas": G.number_of_edges() - con_velocidad}


# ---------- 3. Componente fuertemente conexa ----------

def componente(G):
    return ox.truncate.largest_component(G, strongly=True)


def medir_componentes(G_departamento):
    """Tiempo de largest_component en redes de tamaño creciente (tabla del anexo)."""
    redes = []
    for r in RADIOS_KM:
        print(f"  red de radio {r} km...")
        redes.append((f"Radio de {r} km",
                      red_guardada(DATOS / f"red_radio_{r}km.graphml", ox.graph_from_point,
                                   PLAZA_BOLIVAR, dist=r * 1000, network_type="drive")))
    redes.append(("Departamento completo", G_departamento))

    filas = []
    for nombre, G in redes:
        V, E = G.number_of_nodes(), G.number_of_edges()
        ms, _ = medir(componente, G)
        filas.append({"red": nombre, "V": V, "E": E, "V+E": V + E, "tiempo_ms": round(ms, 3)})
        print(f"  {nombre}: V+E = {V + E}, {ms:.1f} ms")
    return filas


# ---------- 4. Ubicación de los lugares ----------

def leer_catalogo():
    with open(CATALOGO, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def asociar_lugares(G, lugares):
    """Nodo de la componente más cercano en línea recta (distancia euclidiana en UTM 18N)."""
    a_utm = Transformer.from_crs("EPSG:4326", CRS_UTM, always_xy=True)
    ids = list(G.nodes)
    xs, ys = a_utm.transform([G.nodes[n]["x"] for n in ids], [G.nodes[n]["y"] for n in ids])
    xs, ys = np.array(xs), np.array(ys)
    filas = []
    for lugar in lugares:
        lx, ly = a_utm.transform(float(lugar["longitud"]), float(lugar["latitud"]))
        d = np.hypot(xs - lx, ys - ly)        # recorrido lineal: O(V) por lugar
        i = int(np.argmin(d))
        filas.append({**lugar, "nodo": ids[i], "distancia_nodo_m": round(float(d[i]), 1)})
    return filas


# ---------- 5. Grafo procesado ----------

def guardar_csv(ruta, filas):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)


def main():
    guardar_maquina()
    print("Red del departamento (si ya está en datos/, no se descarga otra vez)...")
    if not RED_COMPLETA.exists():
        (RESULTADOS / "fecha_descarga.txt").write_text(str(date.today()))
    G = red_guardada(RED_COMPLETA, ox.graph_from_place, LUGAR, network_type="drive")
    archivo_fecha = RESULTADOS / "fecha_descarga.txt"
    fecha = archivo_fecha.read_text() if archivo_fecha.exists() else str(date.today())
    resumen = {"fecha_descarga": fecha, "osmnx": ox.__version__,
               "red_descargada": {"nodos": G.number_of_nodes(), "aristas": G.number_of_edges()}}

    print("Pesos...")
    G, resumen["pesos"] = agregar_pesos(G)

    print("Componente fuertemente conexa en redes crecientes...")
    guardar_csv(RESULTADOS / "r1_tiempos_componente.csv", medir_componentes(G))
    C = componente(G)
    resumen["componente"] = {"nodos": C.number_of_nodes(), "aristas": C.number_of_edges()}

    resumen["memoria_red_descargada"] = estimar_memoria(G.number_of_nodes(), G.number_of_edges())
    resumen["memoria_componente"] = estimar_memoria(C.number_of_nodes(), C.number_of_edges())

    print("Asociando lugares...")
    lugares = asociar_lugares(C, leer_catalogo())
    guardar_csv(LUGARES_NODOS, lugares)
    resumen["lugares_a_mas_de_500m"] = [
        {"id": l["id"], "nombre": l["nombre"], "distancia_m": l["distancia_nodo_m"]}
        for l in lugares if l["distancia_nodo_m"] > UMBRAL_LEJANO_M]

    ox.save_graphml(C, COMPONENTE)
    (RESULTADOS / "r1_resumen.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False))
    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
