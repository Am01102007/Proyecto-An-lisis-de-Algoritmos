"""Requerimiento 4. Viajante asimétrico (implementación propia).

Convención: M es la matriz de tiempos (M[i][j] = segundos de i a j, no necesariamente igual a
M[j][i]). El recorrido sale de 'inicio', visita cada lugar de 'visitas' una vez y regresa.
Todas las funciones devuelven (tiempo_total_s, recorrido), con recorrido = [inicio, ..., inicio].
"""
import itertools
import time

from config import LIMITE_S


class TiempoAgotado(Exception):
    """La ejecución pasó el límite de tiempo del protocolo (5 minutos)."""


def costo(M, recorrido):
    return sum(M[a][b] for a, b in zip(recorrido, recorrido[1:]))


def fuerza_bruta(M, inicio, visitas, limite_s=LIMITE_S):
    """Prueba las k! permutaciones. Tiempo O(k! · k), memoria O(k)."""
    t0 = time.perf_counter()
    mejor, mejor_orden = float("inf"), None
    for contador, orden in enumerate(itertools.permutations(visitas)):
        if contador & 0xFFFF == 0 and time.perf_counter() - t0 > limite_s:
            raise TiempoAgotado()
        total = M[inicio][orden[0]] + M[orden[-1]][inicio]
        for a, b in zip(orden, orden[1:]):
            total += M[a][b]
        if total < mejor:
            mejor, mejor_orden = total, orden
    return mejor, [inicio, *mejor_orden, inicio]


def held_karp(M, inicio, visitas):
    """Programación dinámica sobre subconjuntos. Tiempo O(2^k · k^2), memoria O(2^k · k).

    C[S][j] = menor tiempo de salir de 'inicio', pasar exactamente por los lugares del
    subconjunto S (máscara de bits) y terminar en el lugar j (j en S):
        C[{j}][j] = M[inicio][j]
        C[S][j]   = min_{i en S, i != j} ( C[S - {j}][i] + M[i][j] )
    Óptimo = min_j ( C[todos][j] + M[j][inicio] ).
    """
    k = len(visitas)
    INF = float("inf")
    C = [[INF] * k for _ in range(1 << k)]
    padre = [[-1] * k for _ in range(1 << k)]
    for j in range(k):
        C[1 << j][j] = M[inicio][visitas[j]]
    for S in range(1, 1 << k):              # en orden creciente: S - {j} < S ya está calculado
        for j in range(k):
            if not S & (1 << j) or S == 1 << j:
                continue
            anterior = S ^ (1 << j)
            vj = visitas[j]
            for i in range(k):
                if anterior & (1 << i):
                    valor = C[anterior][i] + M[visitas[i]][vj]
                    if valor < C[S][j]:
                        C[S][j] = valor
                        padre[S][j] = i
    todos = (1 << k) - 1
    mejor, ultimo = min((C[todos][j] + M[visitas[j]][inicio], j) for j in range(k))
    # Reconstrucción del recorrido siguiendo los padres hacia atrás
    orden, S, j = [], todos, ultimo
    while j != -1:
        orden.append(visitas[j])
        S, j = S ^ (1 << j), padre[S][j]
    return mejor, [inicio, *reversed(orden), inicio]


def memoria_held_karp_bytes(k, bytes_por_celda=8):
    """Tamaño de las dos tablas (costos y padres): 2 · 2^k · k celdas."""
    return 2 * (1 << k) * k * bytes_por_celda


def vecino_mas_cercano(M, inicio, visitas):
    """Heurística voraz: siempre ir al lugar no visitado más cercano. Tiempo O(k^2), memoria O(k)."""
    pendientes = list(visitas)
    recorrido = [inicio]
    while pendientes:
        actual = recorrido[-1]
        siguiente = min(pendientes, key=lambda j: M[actual][j])
        pendientes.remove(siguiente)
        recorrido.append(siguiente)
    recorrido.append(inicio)
    return costo(M, recorrido), recorrido
