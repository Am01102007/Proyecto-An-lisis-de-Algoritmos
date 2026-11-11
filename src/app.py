"""Requerimiento 5. Aplicación demostrativa.

Ejecutar desde la raíz:  streamlit run src/app.py
"""
import json
import re

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from config import GRAFICAS, ID_ARMENIA, RESULTADOS
from dijkstra import dijkstra_cola
from grafo import cargar_grafo, cargar_lugares
from r4_ruta import ITINERARIO, cargar_matriz
from viajante import held_karp, vecino_mas_cercano

st.set_page_config(page_title="Rutas del Paisaje Cultural Cafetero", page_icon=":material/forest:", layout="wide")
CENTRO = [4.53, -75.68]


@st.cache_resource
def datos():
    g = cargar_grafo()
    lugares = cargar_lugares(g)
    ids, M = cargar_matriz()
    return g, lugares, ids, M


def secciones_tablas(texto):
    """Separa tablas.md en secciones (título, DataFrame, notas) para mostrarlas con ancho uniforme."""
    secciones, titulo, filas, notas = [], None, [], []

    def cerrar():
        if titulo and filas:
            df = pd.DataFrame(filas[1:], columns=filas[0])
            secciones.append((titulo, df, " ".join(notas).strip()))

    for linea in texto.splitlines():
        if linea.startswith("### "):
            cerrar()
            titulo, filas, notas = linea[4:].strip(), [], []
        elif linea.strip().startswith("|"):
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            if not all(re.fullmatch(r"-+", c) for c in celdas):
                filas.append(celdas)
        elif linea.strip():
            notas.append(linea.strip())
    cerrar()
    return secciones


def coordenadas(g, ruta):
    return [(g.lat[i], g.lon[i]) for i in ruta]


def dibujar_recorrido(mapa, g, por_id, recorrido_ids, color, nombre):
    """Dibuja el recorrido por las vías, con Dijkstra entre lugares consecutivos."""
    capa = folium.FeatureGroup(name=nombre)
    for a, b in zip(recorrido_ids, recorrido_ids[1:]):
        _, ruta, _ = dijkstra_cola(g, por_id[a]["indice"], por_id[b]["indice"])
        folium.PolyLine(coordenadas(g, ruta), color=color, weight=4, opacity=.8).add_to(capa)
    capa.add_to(mapa)


g, lugares, ids, M = datos()
por_id = {l["id"]: l for l in lugares}
nombre = {l["id"]: f"{l['nombre']} ({l['municipio']})" for l in lugares}

with st.sidebar:
    st.header("Rutas del Paisaje Cultural Cafetero")
    st.caption("Requerimiento 5 · aplicación demostrativa sobre la red vial del Quindío.")
    st.metric("Lugares en el catálogo", len(lugares))
    st.metric("Nodos de la red", len(g.lat))
    st.divider()
    st.caption("Algoritmos: Dijkstra (caminos mínimos), Quickhull (envolvente convexa) "
               "y Held-Karp / vecino más cercano (ruta óptima del viajante).")

st.title("Rutas del Paisaje Cultural Cafetero")
st.caption("Quindío, Colombia · Dijkstra, envolvente convexa y ruta óptima sobre la red vial real")
ruta_tab, envolvente_tab, itinerario_tab, resultados_tab = st.tabs(
    [":material/alt_route: Ruta entre dos lugares", ":material/pentagon: Envolvente convexa",
     ":material/map: Itinerario de un día", ":material/bar_chart: Resultados R1–R4"])

with ruta_tab:
    with st.container(border=True):
        c1, c2 = st.columns(2)
        origen = c1.selectbox("Origen", ids, format_func=nombre.get, index=ids.index(ID_ARMENIA))
        destino = c2.selectbox("Destino", ids, format_func=nombre.get, index=1)
        t, ruta, explorados = dijkstra_cola(g, por_id[origen]["indice"], por_id[destino]["indice"])
        st.metric("Tiempo de viaje (modelo)", f"{t / 60:.1f} min")
        st.caption(f"Dijkstra con cola de prioridad · {explorados} nodos explorados · {len(ruta)} nodos en la ruta")
    mapa = folium.Map(location=CENTRO, zoom_start=10)
    if ruta:
        folium.PolyLine(coordenadas(g, ruta), color="blue", weight=5).add_to(mapa)
    for x, color in ((origen, "green"), (destino, "red")):
        folium.Marker([float(por_id[x]["latitud"]), float(por_id[x]["longitud"])], tooltip=nombre[x],
                      icon=folium.Icon(color=color)).add_to(mapa)
    st_folium(mapa, height=550, use_container_width=True, key="mapa_ruta")

with envolvente_tab:
    archivo = RESULTADOS / "r3_envolvente_red.json"
    if archivo.exists():
        vertices = json.loads(archivo.read_text(encoding="utf-8"))
        mapa = folium.Map(location=CENTRO, zoom_start=9)
        folium.Polygon(vertices, color="purple", fill=True, fill_opacity=.15).add_to(mapa)
        st.badge(f"{len(vertices)} vértices", icon=":material/pentagon:")
        st.caption("Quickhull propio, verificado con SciPy")
        st_folium(mapa, height=550, use_container_width=True, key="mapa_envolvente")
    else:
        st.warning("Primero ejecute src/r3_envolvente.py")

with itinerario_tab:
    atractivos = [l["id"] for l in lugares if l["categoria"] == "atractivo"]
    partida = st.selectbox("Lugar de partida", ids, format_func=nombre.get, index=ids.index(ID_ARMENIA))
    elegidos = st.multiselect("Atractivos (entre 6 y 8)", atractivos, default=[x for x in ITINERARIO if x in atractivos],
                              format_func=nombre.get, max_selections=8)
    if 6 <= len(elegidos) <= 8:
        i0, vis = ids.index(partida), [ids.index(x) for x in elegidos]
        visitas_min = sum(por_id[x]["duracion_visita_min"] for x in elegidos)
        t_hk, rec_hk = held_karp(M, i0, vis)
        t_vz, rec_vz = vecino_mas_cercano(M, i0, vis)
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            c1.metric("Held-Karp (óptimo)", f"{(t_hk / 60 + visitas_min) / 60:.2f} h",
                      help=f"{t_hk / 60:.0f} min de desplazamiento + {visitas_min:.0f} min de visitas")
            c2.metric("Heurística voraz", f"{(t_vz / 60 + visitas_min) / 60:.2f} h",
                      help=f"{t_vz / 60:.0f} min de desplazamiento + {visitas_min:.0f} min de visitas")
            c3.metric("Diferencia", f"{(t_vz - t_hk) / 60:.1f} min", f"{(t_vz - t_hk) / t_hk * 100:.1f} %",
                      delta_color="inverse")
            if (t_hk / 60 + visitas_min) > 11 * 60:
                st.warning("El recorrido óptimo no cabe en una jornada de 11 h.")
            st.write("**Orden Held-Karp:** " + " → ".join(por_id[ids[i]]["nombre"] for i in rec_hk))
            st.write("**Orden voraz:** " + " → ".join(por_id[ids[i]]["nombre"] for i in rec_vz))
        mapa = folium.Map(location=CENTRO, zoom_start=10)
        dibujar_recorrido(mapa, g, por_id, [ids[i] for i in rec_hk], "blue", "Held-Karp")
        dibujar_recorrido(mapa, g, por_id, [ids[i] for i in rec_vz], "orange", "Voraz")
        for x in [partida] + elegidos:
            folium.Marker([float(por_id[x]["latitud"]), float(por_id[x]["longitud"])],
                          tooltip=nombre[x]).add_to(mapa)
        folium.LayerControl().add_to(mapa)
        st_folium(mapa, height=550, use_container_width=True, key="mapa_itinerario")
    else:
        st.info("Elija entre 6 y 8 atractivos.")

with resultados_tab:
    tablas = RESULTADOS / "tablas.md"
    if tablas.exists():
        for titulo, df, notas in secciones_tablas(tablas.read_text(encoding="utf-8")):
            st.subheader(titulo, divider="gray")
            st.dataframe(df, width="stretch", hide_index=True)
            if notas:
                st.caption(notas)
    pngs = sorted(GRAFICAS.glob("*.png"))
    if pngs:
        st.divider()
        for col, png in zip(st.columns(len(pngs)), pngs):
            col.image(str(png), caption=png.stem, alt=png.stem.replace("_", " "))
