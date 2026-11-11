"""Requerimiento 4. Experimentos del viajante e itinerario de un día.

Ejecutar desde la raíz (después de r2_caminos.py):  python src/r4_ruta.py
"""
import csv
import json
import random

from config import ID_ARMENIA, JORNADA_H, MATRIZ, RESULTADOS, SEMILLA
from grafo import cargar_lugares
from medicion import guardar_maquina, medir
from viajante import (TiempoAgotado, costo, fuerza_bruta, held_karp, memoria_held_karp_bytes,
                      vecino_mas_cercano)

KS_EXACTOS = range(5, 13)
KS_CALIDAD = [5, 8, 10, 12]
INSTANCIAS = 5
# Itinerario por defecto: 7 atractivos (se pueden cambiar). Ver datos/catalogo.csv
ITINERARIO = ["L15", "L16", "L17", "L19", "L20", "L21", "L25"]


def cargar_matriz():
    with open(MATRIZ, encoding="utf-8") as f:
        filas = list(csv.reader(f))
    ids = filas[0][1:]
    M = [[float(x) for x in fila[1:]] for fila in filas[1:]]
    return ids, M


def instancia(ids, k, semilla):
    """Armenia + k lugares al azar del catálogo (todas las categorías), con semilla fija."""
    otros = [i for i, x in enumerate(ids) if x != ID_ARMENIA]
    return ids.index(ID_ARMENIA), random.Random(semilla).sample(otros, k)


def guardar_csv(nombre, filas):
    with open(RESULTADOS / nombre, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)


def soluciones_exactas(ids, M):
    filas, fb_activa = [], True
    for k in KS_EXACTOS:
        inicio, visitas = instancia(ids, k, SEMILLA + k)
        ms_hk, (t_hk, rec_hk) = medir(held_karp, M, inicio, visitas)
        fila = {"k": k, "tiempo_fuerza_bruta_ms": "no completada", "tiempo_held_karp_ms": round(ms_hk, 3),
                "optimo_s": round(t_hk, 3), "memoria_held_karp_kb": memoria_held_karp_bytes(k) / 1024}
        if fb_activa:
            try:
                ms_fb, (t_fb, _) = medir(fuerza_bruta, M, inicio, visitas)
                assert abs(t_fb - t_hk) < 1e-6, f"k={k}: fuerza bruta {t_fb} != Held-Karp {t_hk}"
                fila["tiempo_fuerza_bruta_ms"] = round(ms_fb, 3)
            except TiempoAgotado:
                fb_activa = False       # para k mayores tampoco terminaría
        print(f"  k={k}: {fila}")
        filas.append(fila)
    guardar_csv("r4_exactos.csv", filas)


def calidad_heuristica(ids, M):
    filas, ejemplo = [], None
    for k in KS_CALIDAD:
        for n in range(INSTANCIAS):
            inicio, visitas = instancia(ids, k, SEMILLA * 100 + k * 10 + n)
            t_opt, rec_opt = held_karp(M, inicio, visitas)
            t_vor, rec_vor = vecino_mas_cercano(M, inicio, visitas)
            brecha = (t_vor - t_opt) / t_opt * 100
            filas.append({"k": k, "instancia": n, "optimo_s": round(t_opt, 3),
                          "voraz_s": round(t_vor, 3), "brecha_pct": round(brecha, 3)})
            if ejemplo is None and brecha > 0 and k == 5:
                ejemplo = {"optimo": [ids[i] for i in rec_opt], "optimo_s": t_opt,
                           "voraz": [ids[i] for i in rec_vor], "voraz_s": t_vor}
    guardar_csv("r4_calidad.csv", filas)
    resumen = []
    for k in KS_CALIDAD:
        b = [f["brecha_pct"] for f in filas if f["k"] == k]
        resumen.append({"k": k, "instancias": len(b), "brecha_promedio_pct": round(sum(b) / len(b), 2),
                        "brecha_maxima_pct": round(max(b), 2)})
    guardar_csv("r4_calidad_resumen.csv", resumen)
    (RESULTADOS / "r4_ejemplo_voraz.json").write_text(json.dumps(ejemplo, indent=2), encoding="utf-8")
    print(resumen)


def duracion_total_s(M, recorrido, visita_s):
    return costo(M, recorrido) + sum(visita_s[i] for i in recorrido[1:-1])


def itinerario(ids, M, lugares, elegidos=ITINERARIO, partida=ID_ARMENIA):
    """Ordena los atractivos con Held-Karp; si no caben en 11 h, quita atractivos uno a uno.

    Criterio para quitar: el atractivo cuya salida reduce más la duración total
    (su visita más el desvío que causa). Se recalcula Held-Karp después de cada salida.
    """
    por_id = {l["id"]: l for l in lugares}
    visita_s = {ids.index(x): por_id[x]["duracion_visita_min"] * 60 for x in ids}
    inicio = ids.index(partida)
    visitas = [ids.index(x) for x in elegidos]
    quitados = []
    _, rec = held_karp(M, inicio, visitas)
    while duracion_total_s(M, rec, visita_s) > JORNADA_H * 3600 and len(visitas) > 1:
        def sin(x):
            resto = [v for v in visitas if v != x]
            return duracion_total_s(M, held_karp(M, inicio, resto)[1], visita_s)
        sale = min(visitas, key=sin)
        quitados.append({"id": ids[sale], "nombre": por_id[ids[sale]]["nombre"],
                         "duracion_antes_h": round(duracion_total_s(M, rec, visita_s) / 3600, 2)})
        visitas.remove(sale)
        _, rec = held_karp(M, inicio, visitas)

    filas, acumulado = [], 0.0
    for orden, (a, b) in enumerate(zip(rec, rec[1:]), start=1):
        acumulado += M[a][b] + (visita_s[b] if b != inicio else 0)
        filas.append({"orden": orden if b != inicio else "Regreso",
                      "lugar": por_id[ids[b]]["nombre"],
                      "desplazamiento_min": round(M[a][b] / 60, 1),
                      "visita_min": round(visita_s[b] / 60) if b != inicio else "—",
                      "acumulado_h": round(acumulado / 3600, 2)})
    guardar_csv("r4_itinerario.csv", filas)
    total_visitas = sum(visita_s[i] for i in rec[1:-1])
    resumen = {"partida": por_id[partida]["nombre"], "elegidos": elegidos, "quitados": quitados,
               "visitas_h": round(total_visitas / 3600, 2),
               "desplazamientos_h": round(costo(M, rec) / 3600, 2),
               "jornada_h": round((total_visitas + costo(M, rec)) / 3600, 2)}
    (RESULTADOS / "r4_itinerario.json").write_text(json.dumps(resumen, indent=2, ensure_ascii=False), encoding="utf-8")
    print(resumen)


def main():
    guardar_maquina()
    ids, M = cargar_matriz()
    lugares = cargar_lugares()
    print("Soluciones exactas (la fuerza bruta con k grande puede tardar hasta 5 minutos)...")
    soluciones_exactas(ids, M)
    print("Calidad de la heurística...")
    calidad_heuristica(ids, M)
    print("Itinerario de un día...")
    itinerario(ids, M, lugares)


if __name__ == "__main__":
    main()
