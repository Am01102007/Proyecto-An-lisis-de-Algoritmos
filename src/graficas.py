"""Genera las gráficas (PNG) y las tablas (Markdown) a partir de los CSV de resultados.

Ejecutar desde la raíz, al final:  python src/graficas.py
"""
import csv
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from config import GRAFICAS, RESULTADOS


def leer(nombre):
    with open(RESULTADOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def tabla(titulo, columnas, filas):
    lineas = [f"### {titulo}", "", "| " + " | ".join(columnas) + " |",
              "|" + "---|" * len(columnas)]
    lineas += ["| " + " | ".join(str(c) for c in fila) + " |" for fila in filas]
    return "\n".join(lineas) + "\n\n"


def r1():
    res = json.loads((RESULTADOS / "r1_resumen.json").read_text(encoding="utf-8"))
    md = tabla("R1. Tamaño de la red", ["Red", "Nodos", "Aristas"], [
        ["Red descargada", res["red_descargada"]["nodos"], res["red_descargada"]["aristas"]],
        ["Componente fuertemente conexa", res["componente"]["nodos"], res["componente"]["aristas"]]])
    m = res["memoria_red_descargada"]
    md += tabla("R1. Memoria estimada (red descargada)", ["Representación", "MB"], [
        ["Matriz (float64, 8 B por celda)", f"{m['matriz_float64_mb']:,.1f}"],
        ["Matriz (1 B por celda)", f"{m['matriz_1byte_mb']:,.1f}"],
        ["Listas de adyacencia", f"{m['listas_mb']:,.2f}"]])
    filas = leer("r1_tiempos_componente.csv")
    md += tabla("R1. Tiempo de obtener la componente (ms)", ["Red", "V", "E", "V+E", "Tiempo (ms)"],
                [[f["red"], f["V"], f["E"], f["V+E"], f["tiempo_ms"]] for f in filas])
    x = [int(f["V+E"]) for f in filas]
    y = [float(f["tiempo_ms"]) for f in filas]
    plt.figure(figsize=(6, 4))
    plt.plot(x, y, "o-")
    plt.xlabel("V + E")
    plt.ylabel("Tiempo (ms)")
    plt.title("Componente fuertemente conexa: tiempo frente a V + E")
    plt.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig(GRAFICAS / "r1_componente.png", dpi=150)
    plt.close()
    return md


def r2():
    filas = leer("r2_dijkstra.csv")
    plt.figure(figsize=(6, 4))
    for version, marca in (("cola_prioridad", "o"), ("lineal", "s")):
        sel = [f for f in filas if f["version"] == version]
        plt.scatter([int(f["nodos_explorados"]) for f in sel], [float(f["tiempo_ms"]) for f in sel],
                    marker=marca, label=version.replace("_", " "))
    plt.xlabel("Nodos explorados")
    plt.ylabel("Tiempo (ms)")
    plt.yscale("log")
    plt.legend()
    plt.title("Dijkstra: tiempo frente a nodos explorados")
    plt.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig(GRAFICAS / "r2_dijkstra.png", dpi=150)
    plt.close()
    c = json.loads((RESULTADOS / "r2_cocientes.json").read_text(encoding="utf-8"))
    md = tabla("R2. Mediciones de Dijkstra (ms)", list(filas[0].keys()), [list(f.values()) for f in filas])
    md += tabla("R2. Cociente lineal / cola de prioridad (10 pares)", ["Mediana", "Mínimo", "Máximo"],
                [[f"{c['mediana']:.1f}", f"{c['minimo']:.1f}", f"{c['maximo']:.1f}"]])
    return md


def r3():
    filas = leer("r3_envolvente.csv")
    return tabla("R3. Envolvente convexa (ms)",
                 ["Conjunto de puntos", "n", "Vértices de la envolvente", "Tiempo propio (ms)",
                  "Tiempo SciPy (ms)", "Cociente"], [list(f.values()) for f in filas])


def r4():
    filas = leer("r4_exactos.csv")
    plt.figure(figsize=(6, 4))
    for col, nombre in (("tiempo_fuerza_bruta_ms", "Fuerza bruta"), ("tiempo_held_karp_ms", "Held-Karp")):
        pts = [(int(f["k"]), float(f[col])) for f in filas if f[col] != "no completada"]
        plt.plot([p[0] for p in pts], [p[1] for p in pts], "o-", label=nombre)
    plt.xlabel("k (lugares a visitar)")
    plt.ylabel("Tiempo (ms)")
    plt.yscale("log")
    plt.legend()
    plt.title("Viajante: tiempo frente a k")
    plt.grid(alpha=.3)
    plt.tight_layout()
    plt.savefig(GRAFICAS / "r4_exactos.png", dpi=150)
    plt.close()
    md = tabla("R4. Soluciones exactas (ms)", ["k", "Tiempo fuerza bruta (ms)", "Tiempo Held-Karp (ms)",
                                                 "Memoria Held-Karp (KB)"],
               [[f["k"], f["tiempo_fuerza_bruta_ms"], f["tiempo_held_karp_ms"], f["memoria_held_karp_kb"]]
                for f in filas])
    cal = leer("r4_calidad_resumen.csv")
    md += tabla("R4. Calidad de la heurística", ["k", "Instancias", "Brecha promedio (%)", "Brecha máxima (%)"],
                [list(f.values()) for f in cal])
    it = leer("r4_itinerario.csv")
    res = json.loads((RESULTADOS / "r4_itinerario.json").read_text(encoding="utf-8"))
    md += tabla(f"R4. Itinerario de un día (partida: {res['partida']})",
                ["Orden", "Lugar", "Desplazamiento desde el anterior (min)", "Visita (min)",
                 "Tiempo acumulado (h)"], [list(f.values()) for f in it])
    md += (f"\nTiempo total de visitas: {res['visitas_h']} h · desplazamientos: {res['desplazamientos_h']} h · "
           f"jornada: {res['jornada_h']} h. Atractivos quitados: "
           f"{', '.join(q['nombre'] for q in res['quitados']) or 'ninguno'}.\n")
    return md


def main():
    partes = []
    for nombre, f in (("R1", r1), ("R2", r2), ("R3", r3), ("R4", r4)):
        try:
            partes.append(f())
        except FileNotFoundError as e:
            print(f"{nombre}: falta {e.filename}; corra primero su script")
    (RESULTADOS / "tablas.md").write_text("\n".join(partes), encoding="utf-8")
    print("Listo: resultados/tablas.md y graficas/*.png")


if __name__ == "__main__":
    main()
