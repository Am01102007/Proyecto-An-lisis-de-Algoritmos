"""Rutas y constantes compartidas por todos los requerimientos."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
RESULTADOS = RAIZ / "resultados"
GRAFICAS = RAIZ / "graficas"
for carpeta in (DATOS, RESULTADOS, GRAFICAS):
    carpeta.mkdir(exist_ok=True)

LUGAR = "Quindío, Colombia"
CATALOGO = DATOS / "catalogo.csv"
RED_COMPLETA = DATOS / "red_quindio.graphml"        # red descargada, sin filtrar
COMPONENTE = DATOS / "componente.graphml"           # componente fuertemente conexa con pesos
LUGARES_NODOS = DATOS / "lugares_nodos.csv"         # cada lugar con su nodo más cercano
MATRIZ = RESULTADOS / "matriz_tiempos.csv"

# Plaza de Bolívar de Armenia: centro de las redes de radio creciente y punto de partida del R4
PLAZA_BOLIVAR = (4.532066, -75.673104)   # misma coordenada que L01 en el catálogo
ID_ARMENIA = "L01"

CRS_UTM = "EPSG:32618"   # UTM zona 18N, en metros
SEMILLA = 2026           # semilla fija de todos los datos aleatorios
REPETICIONES = 5         # cada medición se repite 5 veces y se reporta la mediana
LIMITE_S = 300           # 5 minutos: una ejecución que lo pase se reporta como no completada
JORNADA_H = 11           # duración máxima del itinerario de un día
