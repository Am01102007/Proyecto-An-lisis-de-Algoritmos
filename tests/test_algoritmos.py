"""Verificación de los algoritmos propios. Ejecutar desde la raíz:  python -m pytest tests"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import networkx as nx
import numpy as np
from scipy.spatial import ConvexHull

from dijkstra import dijkstra_cola, dijkstra_lineal
from envolvente import envolvente_convexa
from grafo import Grafo
from viajante import costo, fuerza_bruta, held_karp, vecino_mas_cercano

# Ejemplo resuelto a mano (también está en el documento técnico): 0 -> 3 mínimo = 0-1-2-3 = 4
#   0->1 (1), 0->2 (5), 1->2 (2), 1->3 (6), 2->3 (1)
EJEMPLO = [(0, 1, 1), (0, 2, 5), (1, 2, 2), (1, 3, 6), (2, 3, 1)]

# Viajante asimétrico de 4 lugares donde la voraz falla: voraz 0-1-2-3-0 = 23, óptimo 0-3-2-1-0 = 10
M_VORAZ = [[0, 1, 6, 5],
           [1, 0, 1, 10],
           [20, 2, 0, 1],
           [20, 10, 2, 0]]


def grafo(n, aristas):
    g = Grafo(n)
    for u, v, w in aristas:
        g.agregar_arista(u, v, w)
    return g


def test_dijkstra_a_mano():
    g = grafo(4, EJEMPLO)
    for f in (dijkstra_lineal, dijkstra_cola):
        t, ruta, _ = f(g, 0, 3)
        assert t == 4 and ruta == [0, 1, 2, 3]


def test_dijkstra_contra_networkx():
    rng = random.Random(1)
    for _ in range(50):
        n = rng.randint(2, 60)
        aristas = [(rng.randrange(n), rng.randrange(n), rng.uniform(1, 100)) for _ in range(4 * n)]
        g, G = grafo(n, aristas), nx.DiGraph()
        G.add_nodes_from(range(n))
        for u, v, w in aristas:
            if not G.has_edge(u, v) or G[u][v]["weight"] > w:
                G.add_edge(u, v, weight=w)
        esperado = nx.single_source_dijkstra_path_length(G, 0)
        dist, _, _ = dijkstra_cola(g, 0)
        for v in range(n):
            if v in esperado:
                assert abs(dist[v] - esperado[v]) < 1e-9
                assert abs(dijkstra_lineal(g, 0, v)[0] - esperado[v]) < 1e-9


def test_envolvente_contra_scipy():
    rng = random.Random(2)
    for _ in range(200):
        lado = rng.choice([5, 30, 10_000])     # lados pequeños: muchos puntos alineados
        pts = sorted({(rng.randint(0, lado), rng.randint(0, lado)) for _ in range(rng.randint(10, 500))})
        hull = ConvexHull(np.array(pts, dtype=float))
        assert set(envolvente_convexa(pts)) == {pts[i] for i in hull.vertices}


def test_envolvente_alineados_no_son_vertices():
    cuadricula = [(x, y) for x in range(11) for y in range(11)]
    assert set(envolvente_convexa(cuadricula)) == {(0, 0), (0, 10), (10, 0), (10, 10)}


def test_held_karp_igual_a_fuerza_bruta():
    rng = random.Random(3)
    for _ in range(100):
        n = rng.randint(2, 8)
        M = [[0 if i == j else rng.randint(1, 100) for j in range(n)] for i in range(n)]
        t_fb, _ = fuerza_bruta(M, 0, list(range(1, n)))
        t_hk, rec = held_karp(M, 0, list(range(1, n)))
        assert t_fb == t_hk == costo(M, rec)
        assert rec[0] == rec[-1] == 0 and sorted(rec[1:-1]) == list(range(1, n))


def test_voraz_no_siempre_es_optima():
    assert vecino_mas_cercano(M_VORAZ, 0, [1, 2, 3]) == (23, [0, 1, 2, 3, 0])
    assert held_karp(M_VORAZ, 0, [1, 2, 3]) == (10, [0, 3, 2, 1, 0])
