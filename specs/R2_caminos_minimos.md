# Spec R2. Caminos mínimos

**Entrada:** componente con peso `travel_time`; índices de origen y destino.

**Comportamiento esperado**
- `dijkstra_lineal` (O(V²)) y `dijkstra_cola` (O((V + E) log V)) devuelven `(tiempo_s, ruta, nodos_explorados)`.
- Se detienen al sacar el destino. Un nodo cuenta como explorado solo la primera vez que sale.
- La ruta empieza en el origen, termina en el destino y su suma de pesos es el tiempo devuelto.
- `dijkstra_cola(g, origen)` sin destino devuelve las distancias a todos (para la matriz).
- Matriz de tiempos L × L en `resultados/matriz_tiempos.csv`, con ids en la primera fila y columna.

**Casos de prueba**
- Ejemplo a mano: 0→1 (1), 0→2 (5), 1→2 (2), 1→3 (6), 2→3 (1). De 0 a 3: tiempo 4 y ruta [0, 1, 2, 3].
- 50 grafos al azar: mismas distancias que `networkx.single_source_dijkstra_path_length`.
- En los 10 pares medidos con las dos versiones, los tiempos coinciden.
