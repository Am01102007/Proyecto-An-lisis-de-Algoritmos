"""Requerimiento 2. Mediciones de Dijkstra y matriz de tiempos entre lugares.

Ejecutar desde la raíz:  python src/r2_caminos.py
Ojo: la versión lineal puede tardar varios minutos en total.
"""
import csv
import json
import math
import random
import statistics

from config import MATRIZ, RESULTADOS, SEMILLA
from dijkstra import INF, dijkstra_cola, dijkstra_lineal
from grafo import cargar_grafo, cargar_lugares
from medicion import guardar_maquina, medir

PARES_LINEAL = 10
PARES_COLA = 20


def distancia_recta_km(a, b):
    """Haversine, solo para escoger pares cercanos (no es parte del algoritmo medido)."""
    la1, lo1, la2, lo2 = map(math.radians, (float(a["latitud"]), float(a["longitud"]),
                                            float(b["latitud"]), float(b["longitud"])))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def escoger_pares(lugares):
    """10 pares cercanos (para ambas versiones) + 10 pares al azar (solo cola de prioridad)."""
    todos = [(a, b) for a in lugares for b in lugares
             if a["id"] < b["id"] and a["nodo"] != b["nodo"]]
    todos.sort(key=lambda p: distancia_recta_km(*p))
    cercanos = todos[:PARES_LINEAL]
    resto = todos[PARES_LINEAL:]
    random.Random(SEMILLA).shuffle(resto)
    return cercanos, cercanos + resto[:PARES_COLA - PARES_LINEAL]


def medir_consultas(g, cercanos, pares_cola):
    filas = []
    for version, funcion, pares in (("cola_prioridad", dijkstra_cola, pares_cola),
                                    ("lineal", dijkstra_lineal, cercanos)):
        for a, b in pares:
            ms, (t, ruta, explorados) = medir(funcion, g, a["indice"], b["indice"])
            assert ruta and ruta[0] == a["indice"] and ruta[-1] == b["indice"]
            filas.append({"origen": a["id"], "destino": b["id"], "version": version,
                          "tiempo_viaje_s": round(t, 3), "nodos_explorados": explorados,
                          "tiempo_ms": round(ms, 3)})
            print(f"  {version:15s} {a['id']}->{b['id']}: {t:8.1f} s de viaje, "
                  f"{explorados:6d} explorados, {ms:10.2f} ms")
    return filas


def verificar_y_cocientes(filas):
    """Las dos versiones deben dar el mismo tiempo; cociente lineal / cola en los 10 pares."""
    por_par = {}
    for f in filas:
        por_par.setdefault((f["origen"], f["destino"]), {})[f["version"]] = f
    cocientes = []
    for par, v in por_par.items():
        if "lineal" in v:
            assert abs(v["lineal"]["tiempo_viaje_s"] - v["cola_prioridad"]["tiempo_viaje_s"]) < 1e-6, par
            cocientes.append(v["lineal"]["tiempo_ms"] / v["cola_prioridad"]["tiempo_ms"])
    return {"pares_verificados": len(cocientes), "mismos_tiempos": True,
            "mediana": statistics.median(cocientes), "minimo": min(cocientes), "maximo": max(cocientes)}


def matriz_tiempos(g, lugares):
    """Un Dijkstra con cola desde cada lugar, sin destino: O(L (V + E) log V)."""
    matriz = []
    for a in lugares:
        dist, _, _ = dijkstra_cola(g, a["indice"])
        fila = [dist[b["indice"]] for b in lugares]
        assert all(t < INF for t in fila), f"{a['id']} no alcanza a todos (¿componente?)"
        matriz.append(fila)
    return matriz


def main():
    guardar_maquina()
    g = cargar_grafo()
    lugares = cargar_lugares(g)
    print(f"Grafo: V = {g.n}, E = {sum(len(a) for a in g.ady)}; {len(lugares)} lugares")

    cercanos, pares_cola = escoger_pares(lugares)
    filas = medir_consultas(g, cercanos, pares_cola)
    with open(RESULTADOS / "r2_dijkstra.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    resumen = verificar_y_cocientes(filas)
    (RESULTADOS / "r2_cocientes.json").write_text(json.dumps(resumen, indent=2), encoding="utf-8")
    print(resumen)

    print("Matriz de tiempos...")
    matriz = matriz_tiempos(g, lugares)
    with open(MATRIZ, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([""] + [l["id"] for l in lugares])
        for l, fila in zip(lugares, matriz):
            w.writerow([l["id"]] + [round(t, 3) for t in fila])
    print(f"Matriz {len(lugares)} x {len(lugares)} guardada en {MATRIZ}")


if __name__ == "__main__":
    main()
