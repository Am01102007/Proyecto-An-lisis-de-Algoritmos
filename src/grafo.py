"""Carga la componente procesada (R1) como listas de adyacencia con índices 0..V-1."""
import csv

from config import COMPONENTE, LUGARES_NODOS


class Grafo:
    """Listas de adyacencia: ady[u] = [(v, tiempo_s), ...]. Memoria O(V + E)."""

    def __init__(self, n):
        self.n = n
        self.ady = [[] for _ in range(n)]
        self.osmid = []      # índice -> id de OpenStreetMap
        self.indice = {}     # id de OpenStreetMap -> índice
        self.lat = []
        self.lon = []

    def agregar_arista(self, u, v, peso):
        self.ady[u].append((v, peso))


def desde_networkx(G, peso="travel_time"):
    """Convierte un MultiDiGraph de OSMnx. Entre aristas paralelas u->v se queda la de menor peso."""
    g = Grafo(G.number_of_nodes())
    for i, (nodo, datos) in enumerate(G.nodes(data=True)):
        g.osmid.append(nodo)
        g.indice[nodo] = i
        g.lat.append(float(datos["y"]))
        g.lon.append(float(datos["x"]))
    mejor = {}
    for u, v, datos in G.edges(data=True):
        clave = (g.indice[u], g.indice[v])
        w = float(datos[peso])
        if clave not in mejor or w < mejor[clave]:
            mejor[clave] = w
    for (u, v), w in mejor.items():
        g.agregar_arista(u, v, w)
    return g


def cargar_grafo():
    import osmnx as ox
    return desde_networkx(ox.load_graphml(COMPONENTE))


def cargar_lugares(g=None):
    """Lugares del catálogo con su nodo; si se da el grafo, agrega 'indice' (posición en g)."""
    with open(LUGARES_NODOS, encoding="utf-8") as f:
        lugares = list(csv.DictReader(f))
    for l in lugares:
        l["distancia_nodo_m"] = float(l["distancia_nodo_m"])
        l["duracion_visita_min"] = float(l["duracion_visita_min"] or 0)
        if g is not None:
            l["indice"] = g.indice[int(l["nodo"])]
    return lugares
