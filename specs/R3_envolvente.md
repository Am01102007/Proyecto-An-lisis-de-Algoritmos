# Spec R3. Envolvente convexa

**Entrada:** lista de puntos enteros (UTM 18N redondeado), sin repetidos.

**Comportamiento esperado**
- `envolvente_convexa(puntos)` (Quickhull, divide y vencerás) devuelve los vértices de la envolvente.
- Los puntos alineados sobre un lado no son vértices.
- Da el mismo conjunto de vértices que `scipy.spatial.ConvexHull(...).vertices`.

**Casos de prueba**
- Cuadrícula de 11 × 11 → exactamente las 4 esquinas.
- 200 conjuntos al azar, con muchos puntos alineados → los mismos vértices que SciPy.
- Nodos de la red y cuadrados de 1 000, 10 000 y 50 000 puntos (semilla 2026) → los mismos vértices que SciPy.
