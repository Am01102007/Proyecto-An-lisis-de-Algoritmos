# Spec R5. Aplicación

`streamlit run src/app.py` abre cuatro pestañas:
1. Origen y destino → ruta en el mapa y tiempo (Dijkstra con cola, calculado en el momento).
2. Envolvente convexa sobre el mapa (de `resultados/r3_envolvente_red.json`).
3. Partida (por defecto Armenia) y entre 6 y 8 atractivos → recorridos de Held-Karp y de la voraz, tiempo de cada uno y diferencia.
4. Tablas y gráficas de R1 a R4.

**Casos de prueba:** Armenia → Salento dibuja una ruta continua; con 5 o 9 atractivos se pide elegir entre 6 y 8.
