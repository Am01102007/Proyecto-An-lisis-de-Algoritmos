### R1. Tamaño de la red

| Red | Nodos | Aristas |
|---|---|---|
| Red descargada | 8807 | 20153 |
| Componente fuertemente conexa | 8791 | 20132 |

### R1. Memoria estimada (red descargada)

| Representación | MB |
|---|---|
| Matriz (float64, 8 B por celda) | 591.8 |
| Matriz (1 B por celda) | 74.0 |
| Listas de adyacencia | 0.37 |

### R1. Tiempo de obtener la componente (ms)

| Red | V | E | V+E | Tiempo (ms) |
|---|---|---|---|---|
| Radio de 2 km | 1647 | 3655 | 5302 | 30.279 |
| Radio de 5 km | 4301 | 9712 | 14013 | 74.132 |
| Radio de 10 km | 5916 | 13332 | 19248 | 105.334 |
| Radio de 20 km | 8772 | 20043 | 28815 | 158.827 |
| Departamento completo | 8807 | 20153 | 28960 | 161.136 |


### R2. Mediciones de Dijkstra (ms)

| origen | destino | version | tiempo_viaje_s | nodos_explorados | tiempo_ms |
|---|---|---|---|---|---|
| L06 | L39 | cola_prioridad | 15.969 | 11 | 0.022 |
| L25 | L39 | cola_prioridad | 28.313 | 17 | 0.024 |
| L30 | L31 | cola_prioridad | 1141.823 | 1124 | 0.537 |
| L06 | L25 | cola_prioridad | 44.282 | 60 | 0.044 |
| L36 | L37 | cola_prioridad | 68.607 | 64 | 0.044 |
| L12 | L20 | cola_prioridad | 57.316 | 59 | 0.04 |
| L09 | L40 | cola_prioridad | 60.655 | 105 | 0.062 |
| L06 | L19 | cola_prioridad | 88.216 | 132 | 0.074 |
| L19 | L39 | cola_prioridad | 103.402 | 69 | 0.048 |
| L11 | L24 | cola_prioridad | 180.769 | 332 | 0.148 |
| L21 | L36 | cola_prioridad | 429.45 | 1879 | 0.884 |
| L32 | L39 | cola_prioridad | 4086.695 | 8376 | 5.085 |
| L15 | L19 | cola_prioridad | 3012.977 | 2142 | 1.0 |
| L20 | L39 | cola_prioridad | 1582.598 | 1572 | 0.722 |
| L11 | L25 | cola_prioridad | 1312.116 | 1227 | 0.594 |
| L23 | L35 | cola_prioridad | 2299.761 | 7142 | 3.866 |
| L04 | L34 | cola_prioridad | 197.99 | 432 | 0.203 |
| L05 | L06 | cola_prioridad | 4104.532 | 8553 | 4.726 |
| L18 | L31 | cola_prioridad | 2958.274 | 8169 | 4.403 |
| L17 | L22 | cola_prioridad | 1564.911 | 6460 | 3.291 |
| L06 | L39 | lineal | 15.969 | 11 | 2.289 |
| L25 | L39 | lineal | 28.313 | 17 | 3.951 |
| L30 | L31 | lineal | 1141.823 | 1124 | 231.311 |
| L06 | L25 | lineal | 44.282 | 60 | 12.418 |
| L36 | L37 | lineal | 68.607 | 64 | 13.209 |
| L12 | L20 | lineal | 57.316 | 59 | 12.42 |
| L09 | L40 | lineal | 60.655 | 105 | 22.648 |
| L06 | L19 | lineal | 88.216 | 132 | 27.358 |
| L19 | L39 | lineal | 103.402 | 69 | 14.43 |
| L11 | L24 | lineal | 180.769 | 332 | 69.545 |

### R2. Cociente lineal / cola de prioridad (10 pares)

| Mediana | Mínimo | Máximo |
|---|---|---|
| 305.6 | 104.0 | 469.9 |


### R3. Envolvente convexa (ms)

| Conjunto de puntos | n | Vértices de la envolvente | Tiempo propio (ms) | Tiempo SciPy (ms) | Cociente |
|---|---|---|---|---|---|
| Nodos de la red | 8791 | 14 | 8.223 | 1.315 | 6.25 |
| Cuadrado  1 000 puntos | 1000 | 16 | 1.081 | 0.708 | 1.53 |
| Cuadrado  10 000 puntos | 10000 | 26 | 12.507 | 1.714 | 7.3 |
| Cuadrado  50 000 puntos | 50000 | 25 | 81.171 | 4.381 | 18.53 |


### R4. Soluciones exactas (ms)

| k | Tiempo fuerza bruta (ms) | Tiempo Held-Karp (ms) | Memoria Held-Karp (KB) |
|---|---|---|---|
| 5 | 0.07 | 0.071 | 2.5 |
| 6 | 0.483 | 0.192 | 6.0 |
| 7 | 2.673 | 0.474 | 14.0 |
| 8 | 20.048 | 0.92 | 32.0 |
| 9 | 193.218 | 1.882 | 72.0 |
| 10 | 2047.701 | 4.575 | 160.0 |
| 11 | 24342.652 | 10.631 | 352.0 |
| 12 | no completada | 25.48 | 768.0 |

### R4. Calidad de la heurística

| k | Instancias | Brecha promedio (%) | Brecha máxima (%) |
|---|---|---|---|
| 5 | 5 | 8.06 | 21.1 |
| 8 | 5 | 8.69 | 15.03 |
| 10 | 5 | 6.7 | 12.86 |
| 12 | 5 | 12.72 | 19.93 |

### R4. Itinerario de un día (partida: Armenia (plaza de Bolívar))

| Orden | Lugar | Desplazamiento desde el anterior (min) | Visita (min) | Tiempo acumulado (h) |
|---|---|---|---|---|
| 1 | Jardín Botánico del Quindío | 8.4 | 150 | 2.64 |
| 2 | Calle Real y mirador Alto de la Cruz | 28.0 | 90 | 4.61 |
| 3 | Mirador Encanto Filandia | 26.8 | 60 | 6.05 |
| 4 | Mirador de Filandia | 2.0 | 60 | 7.09 |
| 5 | Museo del Oro Quimbaya | 29.9 | 90 | 9.09 |
| 6 | Parque de la Vida | 4.2 | 60 | 10.16 |
| Regreso | Armenia (plaza de Bolívar) | 4.5 | — | 10.23 |


Tiempo total de visitas: 8.5 h · desplazamientos: 1.73 h · jornada: 10.23 h. Atractivos quitados: Valle de Cocora.
