"""Requerimiento 2. Dijkstra (implementación propia) en dos versiones.

Invariante: cada vez que un nodo u se saca (se marca explorado), dist[u] es el tiempo mínimo
real desde el origen. Se cumple si todos los pesos son >= 0.
"""
import heapq

INF = float("inf")


def reconstruir_ruta(pred, origen, destino):
    """Sigue los predecesores desde el destino hasta el origen. O(longitud de la ruta)."""
    if destino != origen and pred[destino] == -1:
        return []
    ruta = [destino]
    while ruta[-1] != origen:
        ruta.append(pred[ruta[-1]])
    ruta.reverse()
    return ruta


def dijkstra_lineal(g, origen, destino):
    """Mínimo por recorrido lineal de todos los nodos: O(V^2) tiempo, O(V) memoria extra.

    Devuelve (tiempo_s, ruta, nodos_explorados).
    """
    n = g.n
    dist = [INF] * n
    pred = [-1] * n
    explorado = [False] * n
    dist[origen] = 0.0
    explorados = 0
    for _ in range(n):
        # Recorrido lineal: buscar el nodo no explorado con menor distancia
        u, mejor = -1, INF
        for i in range(n):
            if not explorado[i] and dist[i] < mejor:
                u, mejor = i, dist[i]
        if u == -1:            # los que quedan son inalcanzables
            break
        explorado[u] = True
        explorados += 1
        if u == destino:       # al sacar el destino su distancia ya es definitiva
            break
        for v, w in g.ady[u]:
            if not explorado[v] and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pred[v] = u
    return dist[destino], reconstruir_ruta(pred, origen, destino), explorados


def dijkstra_cola(g, origen, destino=None):
    """Cola de prioridad (heapq, montículo binario): O((V + E) log V) tiempo, O(V + E) memoria.

    Con destino: devuelve (tiempo_s, ruta, nodos_explorados) y se detiene al sacarlo.
    Sin destino (destino=None): recorre todo y devuelve (dist, pred, nodos_explorados).
    Se usa "borrado perezoso": una entrada vieja de la cola se ignora si el nodo ya fue explorado.
    """
    n = g.n
    dist = [INF] * n
    pred = [-1] * n
    explorado = [False] * n
    dist[origen] = 0.0
    cola = [(0.0, origen)]
    explorados = 0
    while cola:
        d, u = heapq.heappop(cola)          # O(log V)
        if explorado[u]:
            continue                        # entrada vieja: no cuenta como explorado
        explorado[u] = True
        explorados += 1
        if u == destino:
            break
        for v, w in g.ady[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                pred[v] = u
                heapq.heappush(cola, (nd, v))   # O(log V)
    if destino is None:
        return dist, pred, explorados
    return dist[destino], reconstruir_ruta(pred, origen, destino), explorados
