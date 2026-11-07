# Spec R4. Ruta óptima de recorrido

**Entrada:** matriz M (asimétrica), lugar de inicio y lista de k lugares por visitar.

**Comportamiento esperado**
- `fuerza_bruta`, `held_karp` y `vecino_mas_cercano` devuelven `(tiempo_total_s, recorrido)`, con recorrido = [inicio, …, inicio] y cada lugar una sola vez.
- `fuerza_bruta` lanza `TiempoAgotado` si pasa de 5 minutos.
- Held-Karp da el mismo tiempo que la fuerza bruta.
- Itinerario: si visitas + desplazamientos > 11 h, se quita el atractivo cuya salida más reduce la duración y se recalcula.

**Casos de prueba**
- 100 instancias al azar con k ≤ 7: Held-Karp = fuerza bruta.
- Matriz de 4 lugares de `tests/`: voraz 0-1-2-3-0 = 23 y óptimo 0-3-2-1-0 = 10.
