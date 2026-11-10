# Rutas del Paisaje Cultural Cafetero: documento técnico

Helen Xiomara Giraldo · Valentina Porras · Maryam Hernández Giraldo
Análisis de Algoritmos, 2026-2

> **Cómo usar esta plantilla.** La teoría (complejidades, recurrencias y argumentos de correctitud) ya está escrita. Lo que está entre corchetes **[LLENAR: …]** se completa con los números de `resultados/tablas.md` después de correr los scripts. Antes de entregar, cada una reescribe sus secciones con sus propias palabras.

**Máquina de las mediciones:** portátil Lenovo con procesador Intel (Family 6 Model 183; [LLENAR: nombre comercial, en Configuración → Sistema → Acerca de]), 16 hilos, 31,7 GB de RAM, Windows 11 y Python 3.14.6. Todas las mediciones se hicieron en esa misma máquina.
**Fecha de descarga de la red:** 7 de noviembre de 2026. Versión de OSMnx: 2.1.1.

---

## 1. Arquitectura de la solución

```
 OpenStreetMap ──► r1_red.py ──► datos/componente.graphml ──┬──► r2_caminos.py ──► resultados/matriz_tiempos.csv ──► r4_ruta.py
 catalogo.csv  ──►   (R1)    ──► datos/lugares_nodos.csv ───┤        (R2)                                            (R4)
                                                            └──► r3_envolvente.py ──► r3_envolvente_red.json
                                                                       (R3)
 resultados/*.csv ──► graficas.py ──► graficas/*.png, resultados/tablas.md
 componente + lugares + matriz + envolvente ──► app.py (R5, Streamlit + Folium)
```

- `config.py` reúne las rutas, la semilla (2026), el número de repeticiones (5) y el límite de tiempo (5 min).
- `medicion.py` aplica el protocolo de la sección 6 del enunciado: mediana de 5 ejecuciones medidas con `time.perf_counter_ns`.
- `grafo.py` convierte la componente de OSMnx en listas de adyacencia con índices 0…V−1. Entre aristas paralelas conserva la de menor tiempo.
- Los algoritmos propios están en `dijkstra.py`, `envolvente.py` y `viajante.py`, sin librerías que resuelvan el problema. Se usan `heapq`, `itertools.permutations`, `min` y `max` como estructuras y operaciones de apoyo. Su costo se incluye en el análisis.

---

## 2. Requerimiento 1. Modelo de la red vial

### 2.1 Representación

Con V nodos y E aristas:

- **Matriz de adyacencia:** V × V = V² celdas, existan o no las vías. Memoria Θ(V²).
- **Listas de adyacencia:** una cabecera por nodo y una entrada por arista, V + E en total. Memoria Θ(V + E).

**Supuestos del cálculo:**
- Celda de la matriz: un `float64` de 8 bytes con el tiempo de viaje. También se reporta la versión mínima de 1 byte por celda, que solo indica si hay vía.
- Cabecera de lista: un puntero de 8 bytes.
- Entrada de lista: el vecino (entero de 8 bytes) más el peso (`float64` de 8 bytes), 16 bytes.

Red descargada: V = 8 807 nodos y E = 20 153 aristas.

| Representación | Fórmula | MB |
|---|---|---|
| Matriz (8 B por celda) | 8·V² / 1024² | 591,8 |
| Matriz (1 B por celda) | V² / 1024² | 74,0 |
| Listas de adyacencia | (8·V + 16·E) / 1024² | 0,37 |

**Elección: listas de adyacencia.** La red vial es dispersa: cada intersección se conecta con 2 a 4 vecinos, así que E ≈ 2,3 · V es muchísimo menor que V². De las V² ≈ 77,6 millones de celdas de la matriz, solo 20 153 (el 0,03 %) tendrían una vía. La matriz necesitaría 591,8 MB, casi todos de celdas vacías, mientras que las listas ocupan 0,37 MB, unas 1 600 veces menos. Además, Dijkstra solo recorre los vecinos de cada nodo. Con listas, recorrer todos los vecinos de todos los nodos cuesta O(V + E); con matriz cuesta O(V²).

### 2.2 Pesos

- `length` (m) viene de OSMnx.
- La velocidad se obtiene con `ox.routing.add_edge_speeds`:
  - Si el tramo tiene la etiqueta `maxspeed` de OpenStreetMap, se usa ese valor.
  - Si no la tiene, se le asigna una velocidad según su tipo de vía (`highway`). Es un criterio del grupo, basado en los límites generales del Código Nacional de Tránsito (Ley 769 de 2002, art. 106, modificado por la Ley 1239 de 2008): `motorway` y `trunk` 80 km/h, `primary` 60, `secondary` 50, `tertiary` 40, `residential` y `unclassified` 30, `service` y `living_street` 20.
  - Si el tipo no está en la tabla, se usan 30 km/h.
- `travel_time` (s) = `length` / (`speed_kph` / 3,6), con `ox.routing.add_edge_travel_times`.

De las 20 153 aristas, solo 1 307 (6,5 %) tenían `maxspeed`, y las otras 18 846 (93,5 %) recibieron una velocidad imputada según su tipo de vía (ver `pesos` en `r1_resumen.json`). Por eso la tabla de velocidades por tipo de vía determina casi todos los tiempos del modelo. El tiempo es una estimación del modelo: no considera tráfico, pendientes ni semáforos.

### 2.3 Componente fuertemente conexa

**Algoritmo interno.**
- `ox.truncate.largest_component(G, strongly=True)` primero llama `nx.is_strongly_connected(G)`. Si la red no es fuertemente conexa, obtiene las componentes con `nx.strongly_connected_components(G)`, se queda con la de más nodos y copia ese subgrafo.
- Según la documentación de NetworkX, `strongly_connected_components` es una versión **no recursiva del algoritmo de Tarjan, con las modificaciones de Nuutila**.
  - Fuentes: código fuente de `osmnx/truncate.py` (OSMnx 2.1.1); documentación de `networkx.algorithms.components.strongly_connected_components`; R. Tarjan, «Depth-first search and linear graph algorithms», *SIAM J. Computing* 1(2), 1972; E. Nuutila y E. Soisalon-Soininen, «On finding the strongly connected components in a directed graph», *Information Processing Letters* 49, 1994.

**Cómo funciona.**
- Hace un recorrido en profundidad y le asigna a cada nodo un número de descubrimiento y un valor `lowlink`, que es el menor número de descubrimiento que puede alcanzar desde su subárbol.
- Los nodos visitados se guardan en una pila.
- Cuando un nodo termina con `lowlink` igual a su propio número, es la raíz de una componente: se sacan de la pila todos los nodos hasta él, y esos forman la componente.

**Complejidad.**
- Tiempo: O(V + E), porque cada nodo y cada arista se procesan un número constante de veces. `is_strongly_connected` y la copia del subgrafo también son O(V + E), así que el total sigue siendo O(V + E).
- Memoria: O(V) para los números, la pila y el conjunto de la componente, más O(V + E) para la copia del subgrafo.

**Resultados** (mediana de 5, en ms):

| Red | V | E | V+E | Tiempo (ms) |
|---|---|---|---|---|
| Radio de 2 km | 1 945 | 4 434 | 6 379 | 34,3 |
| Radio de 5 km | 4 294 | 9 682 | 13 976 | 79,1 |
| Radio de 10 km | 6 156 | 13 900 | 20 056 | 110,9 |
| Radio de 20 km | 8 800 | 20 102 | 28 902 | 159,6 |
| Departamento completo | 8 807 | 20 153 | 28 960 | 159,3 |

![Componente: tiempo frente a V+E](../graficas/r1_componente.png)

**Discusión.** Si la complejidad es O(V + E), el tiempo dividido entre V + E debe ser casi constante. Con los datos medidos:

| Red | Tiempo / (V + E) |
|---|---|
| Radio de 2 km | 5,38 µs |
| Radio de 5 km | 5,66 µs |
| Radio de 10 km | 5,53 µs |
| Radio de 20 km | 5,52 µs |
| Departamento completo | 5,50 µs |

- El cociente se mantiene entre 5,4 y 5,7 µs por elemento, aunque V + E crece 4,5 veces del radio de 2 km al departamento. La gráfica es prácticamente una recta, lo que coincide con O(V + E).
- La pequeña variación se explica por el ruido de la medición y el manejo de memoria de Python. No sigue ninguna tendencia que sugiera un crecimiento mayor, como V log V o V².
- La red de 20 km es casi igual al departamento completo (28 902 contra 28 960): el cuadrado de 40 × 40 km alrededor de Armenia cubre casi toda la red vial del Quindío. Por eso sus tiempos son prácticamente iguales.

**Por qué trabajar solo con la componente.** En la componente fuertemente conexa, desde cualquier nodo se puede llegar a cualquier otro respetando el sentido de las vías. Así:
- Dijkstra siempre encuentra una ruta entre dos lugares.
- La matriz de tiempos no tiene celdas infinitas.
- El viajante siempre tiene recorridos válidos de ida y regreso.

Los nodos que quedan fuera, como calles sin salida de un solo sentido o fragmentos desconectados en el borde del departamento, producirían destinos inalcanzables.

### 2.4 Ubicación de los lugares

- Las coordenadas de los lugares y de los nodos se convierten a UTM zona 18N (EPSG:32618) con `pyproj`.
- Cada lugar se asocia al nodo con menor distancia euclidiana, por recorrido lineal: O(V) por lugar y O(L·V) en total, con L lugares.
- Lugares a más de 500 m de su nodo: en la primera ejecución fueron 7 (PANACA, Valle de Cocora, Reserva Peñas Blancas, el balsaje del río La Vieja y tres fincas). Se revisaron en Google Maps y se corrigieron sus coordenadas, ubicándolas en la entrada o el parqueadero. Quedaron 2: Valle de Cocora (1 045,6 m) y Reserva Peñas Blancas (740,5 m). [CONFIRMAR después de cerrar el catálogo]
- Cómo se trataron: en los dos casos el nodo más cercano es una vía rural (`unclassified`) donde termina la carretera, y el resto del recorrido hasta el atractivo es un sendero peatonal que no hace parte de la red `drive`. Se mantiene ese nodo como origen y destino de las rutas, y se aclara que el último tramo, a pie, no está modelado. [CONFIRMAR]

### 2.5 Grafo procesado

La componente con sus pesos se guarda en `datos/componente.graphml` y las asociaciones de los lugares en `datos/lugares_nodos.csv`.

| Red | Nodos | Aristas |
|---|---|---|
| Red descargada | 8 807 | 20 153 |
| Componente fuertemente conexa | 8 791 | 20 132 |

Al filtrar la componente se pierden solo 16 nodos y 21 aristas (0,2 %): calles de un solo sentido sin salida o tramos en el borde del departamento.

---

## 3. Requerimiento 2. Caminos mínimos

### 3.1 Algoritmo y complejidad

**Dijkstra lineal** (`dijkstra_lineal`).
- En cada iteración recorre los V nodos buscando el no explorado de menor distancia: O(V) por extracción, a lo sumo V extracciones.
- Relajar las aristas cuesta O(E) en total.
- Tiempo: O(V² + E) = O(V²). Memoria: O(V) para `dist`, `pred` y `explorado`.

**Dijkstra con cola de prioridad** (`dijkstra_cola`).
- Usa `heapq`, un montículo binario de Python con `heappush` y `heappop` en O(log n). Fuente: documentación de Python, módulo `heapq`.
- Usa borrado perezoso: en vez de disminuir la clave, inserta una entrada nueva y descarta las viejas al sacarlas. La cola tiene a lo sumo E entradas, y log E ≤ 2 log V.
- Tiempo: O((V + E) log V). Memoria: O(V + E).
- Fuente: T. Cormen, C. Leiserson, R. Rivest y C. Stein, *Introduction to Algorithms*, 4.ª ed., MIT Press, 2022, sección 22.3.

Las dos versiones se detienen al sacar el destino y reconstruyen la ruta siguiendo `pred` desde el destino hasta el origen, en O(longitud de la ruta).

### 3.2 Correctitud

- **Invariante:** al sacar un nodo u de la cola (marcarlo explorado), `dist[u]` es el tiempo mínimo real desde el origen hasta u.
- **Por qué se mantiene:** supongamos que existiera un camino más corto hasta u. Ese camino sale del conjunto de explorados por primera vez en algún nodo y que todavía no está explorado.
  - Por el invariante, el tramo hasta y es mínimo, así que `dist[y]` ≤ largo de ese camino < `dist[u]`.
  - Entonces se habría sacado y antes que u, lo que contradice que se sacó u.
  - Este paso usa que **todos los pesos son ≥ 0**: el resto del camino de y a u no puede «restar» tiempo.
- **Por qué permite detenerse en el destino:** en cuanto se saca el destino, el invariante dice que su distancia ya es definitiva. Ninguna exploración posterior la puede mejorar.
- **Condición de los pesos:** no negativos. Con un peso negativo, un camino que pase por un nodo aún no explorado sí podría mejorar una distancia ya fijada. En este modelo los tiempos de viaje son positivos.

### 3.3 Resultados

Se midió la versión con cola en 20 pares y la lineal en 10 de ellos, los 10 pares de lugares más cercanos en línea recta, todos del mismo municipio o de municipios vecinos. El archivo completo es `resultados/r2_dijkstra.csv`.

![Dijkstra: tiempo frente a nodos explorados](../graficas/r2_dijkstra.png)

| Mediana | Mínimo | Máximo |
|---|---|---|
| [LLENAR] | [LLENAR] | [LLENAR] |

*Cociente = tiempo lineal / tiempo con cola, en ms, en los 10 pares.*

**Discusión.** [LLENAR.
- La versión lineal hace V comparaciones por cada nodo explorado, así que su tiempo crece como (nodos explorados) × V, aunque el destino esté cerca.
- La versión con cola solo paga por lo que explora, con un factor log.
- Por eso el cociente es grande y aumenta con los nodos explorados.
- Comentar si los puntos de la gráfica siguen esa tendencia.]

**Verificación.** En los 10 pares las dos versiones dieron el mismo tiempo de viaje: `mismos_tiempos: true` en `r2_cocientes.json`, comprobado con `assert`. Además, `tests/test_algoritmos.py` compara con el ejemplo a mano y con NetworkX en 50 grafos al azar.

**Matriz de tiempos.** Se ejecutó `dijkstra_cola` sin destino una vez desde cada uno de los L = [LLENAR] lugares: O(L·(V + E) log V). Está en `resultados/matriz_tiempos.csv` y no es simétrica. Ejemplo: [LLENAR un par i→j y j→i con tiempos distintos].

---

## 4. Requerimiento 3. Envolvente convexa

### 4.1 Elección del algoritmo: Quickhull

- Quickhull es de divide y vencerás (Eddy, 1977; Preparata y Shamos, *Computational Geometry: An Introduction*, Springer, 1985):
  1. Toma los puntos extremos A (menor x) y B (mayor x).
  2. Parte el conjunto en los puntos de arriba y los de abajo de la recta AB.
  3. En cada lado busca el punto C más lejano a la recta.
  4. Descarta los puntos dentro del triángulo A-C-B.
  5. Resuelve recursivamente los dos lados que quedan.
- **Por qué conviene con la red vial:** la mayoría de los nodos están concentrados en las cabeceras, en el interior del departamento. Quickhull descarta en cada paso todos los puntos del triángulo, así que esos puntos interiores salen en las primeras divisiones. Las llamadas recursivas trabajan solo con los pocos puntos cercanos al borde.
- Con coordenadas enteras, el giro (producto cruz) es exacto. Los puntos alineados sobre un lado tienen cruz = 0 y se descartan, por eso no se cuentan como vértices.

### 4.2 Complejidad y recurrencia

Sea T(n) el tiempo con n puntos. Cada nivel recorre los puntos para encontrar C y filtrar, con costo b·n:

T(n) = T(n₁) + T(n₂) + b·n, con n₁ + n₂ ≤ n − 1, T(1) = a.

**Caso balanceado** (n₁ = n₂ = n/2, con n = 2ᵐ): T(n) = 2T(n/2) + b·n.
- T(2) = 2a + 2b
- T(4) = 2T(2) + 4b = 4a + b(4 + 4)
- T(8) = 2T(4) + 8b = 8a + b(8 + 8 + 8)
- T(16) = 2T(8) + 16b = 16a + b(16 + 16 + 16 + 16)
- T(n) = n·a + b·(n + n + … + n), con log₂ n sumandos, = n·a + b·n·log₂ n → **O(n log n)**.
- Con el método maestro: a = 2, b = 2, f(n) = n = Θ(n^(log₂ 2)) → caso 2 → Θ(n log n).

**Peor caso** (en cada paso solo se descarta un punto, n₁ = n − 1, n₂ = 0): T(n) = T(n − 1) + b·n.
- T(2) = a + 2b
- T(3) = a + b(2 + 3)
- T(4) = a + b(2 + 3 + 4)
- T(n) = a + b(2 + 3 + … + n): una serie aritmética, igual a a + b(n(n + 1)/2 − 1) → **O(n²)**.
- Pasa, por ejemplo, con todos los puntos sobre una circunferencia, porque todos son vértices.

**Memoria:** O(n) para las listas de cada lado; la recursión tiene profundidad O(h), con h el número de vértices.

### 4.3 SciPy

`scipy.spatial.ConvexHull` llama a la librería **Qhull**, escrita en C, que implementa Quickhull: C. B. Barber, D. P. Dobkin y H. Huhdanpaa, «The Quickhull algorithm for convex hulls», *ACM Trans. Mathematical Software* 22(4), 1996; documentación de `scipy.spatial.ConvexHull`.

### 4.4 Resultados

| Conjunto de puntos | n | Vértices de la envolvente | Tiempo propio (ms) | Tiempo SciPy (ms) | Cociente |
|---|---|---|---|---|---|
| [LLENAR desde tablas.md] ||||||

**Verificación.** En los 4 conjuntos el programa comprueba con `assert` que el conjunto de vértices es igual al de SciPy. En `tests/` además se prueba con 200 conjuntos al azar con muchos puntos alineados, y con una cuadrícula de 11 × 11 cuya envolvente son solo las 4 esquinas.

**Discusión.** [LLENAR.
- Los dos usan el mismo algoritmo, Quickhull, así que la diferencia viene de la implementación: SciPy ejecuta código C compilado sobre arreglos de NumPy, y la versión propia es Python interpretado, con un objeto por punto y listas nuevas en cada división.
- Por eso el cociente es un factor casi constante, de unas [LLENAR] veces, en los cuadrados de 1 000 a 50 000 puntos.
- Al pasar de 10 000 a 50 000 puntos, el tiempo debe crecer un poco más de 5 veces, como corresponde a n log n.
- Comentar también el número de vértices: en puntos uniformes en un cuadrado crece muy despacio, como O(log n).]

---

## 5. Requerimiento 4. Ruta óptima de recorrido

### 5.1 Fuerza bruta

- Prueba las k! permutaciones de los lugares (`itertools.permutations`, que genera cada una en O(k)) y calcula el costo de cada una en O(k).
- Tiempo: Θ(k!·k). Memoria: O(k).

### 5.2 Held-Karp

**Subestructura óptima.**
- Sea un recorrido óptimo que sale de s, pasa por todos los lugares del conjunto S y termina en j, con i el lugar anterior a j.
- Entonces el tramo de s a i, pasando por S − {j}, también es óptimo.
- Si existiera uno más corto, lo cambiaríamos por ese y obtendríamos un recorrido hasta j más corto que el óptimo, lo cual es una contradicción (argumento de «cortar y pegar»).
- Esto no depende de que la matriz sea simétrica.

**Recurrencia.** C(S, j) es el menor tiempo de salir de s, pasar exactamente por los lugares de S y terminar en j ∈ S:

- C({j}, j) = M[s][j]
- C(S, j) = min over i ∈ S − {j} of ( C(S − {j}, i) + M[i][j] )
- Óptimo = min over j of ( C(todos, j) + M[j][s] )

Fuente: M. Held y R. M. Karp, «A dynamic programming approach to sequencing problems», *Journal of the SIAM* 10(1), 1962.

**Complejidad.**
- Hay 2ᵏ·k estados (S, j), y cada uno se calcula en O(k).
- Tiempo: Θ(2ᵏ·k²). Memoria: Θ(2ᵏ·k).
- Para devolver el orden de visita se guarda una segunda tabla de padres del mismo tamaño y se recorre de atrás hacia adelante.

**Estimación de memoria.** Dos tablas de 2ᵏ·k celdas de 8 bytes: 2 · 2ᵏ · k · 8 bytes.
- Con k = 12: 2 · 4 096 · 12 · 8 = 786 432 bytes ≈ 768 KB.
- En Python cada celda es una referencia de 8 bytes a un objeto `float`, que ocupa unos 24 bytes más, así que el consumo real es varias veces mayor. Aun así son pocos MB.

### 5.3 Heurística voraz: vecino más cercano

- Desde el lugar actual siempre se va al lugar no visitado con menor M[actual][j] y, al final, se regresa al inicio.
- Se eligió porque es la elección voraz más natural para este problema, se explica en una línea y cuesta solo O(k²) en tiempo y O(k) en memoria.
- Usa directamente la matriz asimétrica, porque mira M[actual][j] en el sentido del viaje.

### 5.4 Resultados

**Soluciones exactas** (mediana de 5; las ejecuciones de más de 1 minuto, una sola vez):

| k | Tiempo fuerza bruta (ms) | Tiempo Held-Karp (ms) |
|---|---|---|
| [LLENAR desde tablas.md, k = 5 a 12] |||

![Viajante: tiempo frente a k](../graficas/r4_exactos.png)

**Mayor k resuelto:** con fuerza bruta, k = [LLENAR]; con Held-Karp, k = 12.

**Discusión.** [LLENAR.
- Al pasar de k a k + 1, la fuerza bruta debe multiplicar su tiempo por cerca de (k + 1), por ejemplo ×11 de 10 a 11, y Held-Karp por cerca de 2·((k + 1)/k)².
- Comprobar esos cocientes con la tabla.
- En escala logarítmica, Held-Karp se ve casi como una recta (exponencial) y la fuerza bruta se curva hacia arriba (factorial).]

**Verificación.** Para cada k que la fuerza bruta resolvió, el programa comprueba con `assert` que el tiempo óptimo es igual al de Held-Karp. En `tests/` se prueba además con 100 instancias al azar.

**Calidad de la heurística** (brecha = (voraz − óptimo) / óptimo × 100):

| k | Instancias | Brecha promedio (%) | Brecha máxima (%) |
|---|---|---|---|
| [LLENAR desde tablas.md] ||||

[LLENAR: discusión de la brecha. ¿Crece con k? ¿Hay instancias en las que la voraz acierta (brecha 0)?]

### 5.5 Itinerario de un día

- Partida: Armenia (plaza de Bolívar). Atractivos elegidos: [LLENAR desde `r4_itinerario.json`]. Se ordenan con Held-Karp.
- Duración = desplazamientos (matriz del R2) + visitas (columna `duracion_visita_min` del catálogo).
- Criterio de las duraciones: [LLENAR fuente o criterio. Por ejemplo, el tiempo que sugiere la página oficial del parque, o 60 min para miradores, 90 min para museos y 4 a 6 h para parques temáticos].
- Si no cabe en 11 h, se quita el atractivo cuya salida reduce más la duración total (su visita más el desvío que causa) y se recalcula Held-Karp. Se repite hasta que quepa.

[LLENAR: pegar la tabla del itinerario de `tablas.md`, con el total de visitas, el total de desplazamientos y la duración de la jornada. Si se quitaron atractivos, decir cuáles y por qué.]

### 5.6 Voraz frente a óptimo

**Ejemplo** (`tests/test_algoritmos.py`, `M_VORAZ`). Cuatro lugares, inicio en 0; M[i][j] es el tiempo de i a j:

|   | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| 0 | – | 1 | 6 | 5 |
| 1 | 1 | – | 1 | 10 |
| 2 | 20 | 2 | – | 1 |
| 3 | 20 | 10 | 2 | – |

- **Voraz:** 0 → 1 (1) → 2 (1) → 3 (1) → 0 (20) = **23**. Cada paso es el más barato, pero termina en 3, que queda muy lejos del inicio.
- **Óptimo (Held-Karp):** 0 → 3 (5) → 2 (2) → 1 (2) → 0 (1) = **10**.
- Con datos reales: [LLENAR con `resultados/r4_ejemplo_voraz.json`].

**Por qué en Dijkstra lo voraz sí funciona y aquí no.**
- En Dijkstra, la decisión voraz (fijar el nodo de menor distancia) nunca se arrepiente. Por el invariante y porque los pesos no son negativos, ningún camino que se descubra después puede llegar a ese nodo más barato. La decisión solo depende de lo ya explorado, y el problema tiene la propiedad de elección voraz.
- En el viajante, elegir el vecino más cercano compromete todo lo que sigue: qué lugares quedan, en qué orden se visitarán y desde dónde habrá que regresar. Una elección barata ahora puede obligar a pagar mucho después, como el regreso 3 → 0 de 20 en el ejemplo.
- El costo de una decisión depende del recorrido completo y no solo del paso actual. Por eso no hay propiedad de elección voraz y hace falta explorar los subconjuntos (Held-Karp) o todas las permutaciones.

---

## 6. Requerimiento 5. Aplicación

- Se ejecuta con `streamlit run src/app.py` y usa Streamlit con mapas de Folium.
- Tiene cuatro pestañas:
  1. Ruta entre dos lugares: Dijkstra con cola, calculado en el momento.
  2. Envolvente convexa sobre el mapa.
  3. Itinerario de un día: partida y de 6 a 8 atractivos, con los recorridos de Held-Karp y de la voraz, el tiempo total de cada uno y la diferencia. Los tramos se dibujan por las vías con Dijkstra.
  4. Tablas y gráficas de R1 a R4.

[LLENAR: 2 o 3 capturas de pantalla.]

---

## 7. Conclusiones

[LLENAR, de 4 a 6 viñetas. Ideas:
- Las listas de adyacencia fueron indispensables, porque la matriz no cabe de forma razonable en memoria.
- Lo medido para la componente y para Dijkstra coincide con O(V + E) y con O((V + E) log V).
- Quickhull propio es correcto pero [LLENAR] veces más lento que Qhull, por lenguaje y no por algoritmo.
- Held-Karp hace práctico el viajante hasta k = 12, mientras que la fuerza bruta se detiene en k = [LLENAR].
- La voraz es instantánea pero se aleja hasta [LLENAR] % del óptimo.]

---

## Anexo. Uso de inteligencia artificial

| Herramienta | Para qué se usó | Cómo se verificó |
|---|---|---|
| Claude (Anthropic) | Estructura del repositorio, primera versión del código y plantilla de este documento | Pruebas de `tests/` (casos a mano, NetworkX y SciPy); comparación de las dos versiones de Dijkstra y de fuerza bruta contra Held-Karp; revisión de las complejidades en las fuentes citadas; cada integrante leyó, ejecutó y explicó su parte |
| [LLENAR otras herramientas] | | |
