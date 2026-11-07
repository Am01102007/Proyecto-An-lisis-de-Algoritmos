"""Requerimiento 3. Envolvente convexa por divide y vencerás: Quickhull (implementación propia).

Trabaja con coordenadas enteras, así el giro (producto cruz) es exacto.
Los puntos alineados sobre un lado no se cuentan como vértices (se descartan con cruz == 0).
"""
import sys

sys.setrecursionlimit(100_000)


def cruz(o, a, b):
    """Producto cruz de (a - o) x (b - o): > 0 si b está a la izquierda de o->a, 0 si alineados."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _quickhull(p, q, puntos):
    """Vértices de la envolvente estrictamente a la izquierda de p->q, en orden de p a q.

    Recurrencia: T(n) = T(n1) + T(n2) + c·n, con n1 + n2 <= n - 1.
    """
    if not puntos:
        return []
    # Dividir: el punto más lejano a la recta pq (empate: el más avanzado en dirección p->q)
    dx, dy = q[0] - p[0], q[1] - p[1]
    c = max(puntos, key=lambda r: (cruz(p, q, r), (r[0] - p[0]) * dx + (r[1] - p[1]) * dy))
    # Los puntos dentro del triángulo p-c-q quedan descartados
    izquierda_pc = [r for r in puntos if cruz(p, c, r) > 0]
    izquierda_cq = [r for r in puntos if cruz(c, q, r) > 0]
    # Vencer y combinar
    return _quickhull(p, c, izquierda_pc) + [c] + _quickhull(c, q, izquierda_cq)


def envolvente_convexa(puntos):
    """Recibe una lista de puntos enteros sin repetidos; devuelve los vértices de la envolvente.

    Tiempo: O(n log n) en promedio, O(n^2) en el peor caso. Memoria: O(n).
    """
    if len(puntos) < 3:
        return list(puntos)
    a = min(puntos)        # el de menor x (y, si empatan, menor y)
    b = max(puntos)        # el de mayor x (y, si empatan, mayor y)
    arriba = [r for r in puntos if cruz(a, b, r) > 0]
    abajo = [r for r in puntos if cruz(a, b, r) < 0]
    return [a] + _quickhull(a, b, arriba) + [b] + _quickhull(b, a, abajo)
