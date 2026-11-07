# Spec R1. Modelo de la red vial

**Entrada:** red `drive` del Quindío (OSMnx) y `datos/catalogo.csv` (≥ 40 lugares).

**Comportamiento esperado**
- Reporta V y E de la red descargada y estima los MB como matriz (V² celdas) y como listas (V + E entradas).
- Cada arista tiene `length` (m), `speed_kph` y `travel_time` (s) = length / (speed_kph / 3,6). Tramos sin `maxspeed`: velocidad según su tipo de vía (tabla `VELOCIDAD_POR_TIPO`), y si el tipo no está, 30 km/h.
- Mide `ox.truncate.largest_component(G, strongly=True)` en radios de 2, 5, 10 y 20 km y en el departamento (mediana de 5).
- Cada lugar se asocia al nodo más cercano en UTM 18N; se listan los que quedan a más de 500 m.
- Guarda `datos/componente.graphml`, `datos/lugares_nodos.csv` y `resultados/r1_*.{csv,json}`.

**Casos de prueba**
- V = 3, E = 4 → matriz 9 celdas; listas 3 + 4 = 7.
- La componente tiene ≤ nodos que la red descargada y, desde cualquier nodo, se alcanzan todos (`nx.is_strongly_connected`).
- La plaza de Bolívar queda a menos de 100 m de su nodo.
