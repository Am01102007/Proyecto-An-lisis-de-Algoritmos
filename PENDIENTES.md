# Pendientes del proyecto

## Catálogo (`datos/catalogo.csv`)

- [ ] **L15 Valle de Cocora:** queda a 1 046 m de la red vial. El nodo más cercano es una vía rural en 4.643277, -75.481252.
  - Si ese punto es la entrada o el parqueadero, se cambia la coordenada.
  - Si no, se deja y se explica en la sección 2.4 que el último tramo es un sendero peatonal.
- [ ] **L23 Reserva Peñas Blancas:** queda a 741 m. El nodo más cercano es una vía rural en 4.481402, -75.634683. Se decide igual que Cocora.
- [ ] **L34 Finca Hotel Nuevo Futuro:** confirmar que el municipio es Circasia; queda cerca del límite con Armenia.
- [ ] **L35 a L40:** cambiar las filas "POR DEFINIR" por una finca y 5 centros de acopio o trilladoras reales.
- [ ] Revisar las duraciones de visita de los atractivos y anotar la fuente o el criterio.
- [ ] Volver a correr `python src/r1_red.py` después de cada cambio del catálogo.

## Mediciones (en el computador de Maryam)

- [x] R1 con la red real (descargada el 2026-11-07)
- [ ] R3 `python src/r3_envolvente.py`
- [ ] R2 `python src/r2_caminos.py` (después de cerrar el catálogo)
- [ ] R4 `python src/r4_ruta.py`
- [ ] Gráficas `python src/graficas.py`
- [ ] App `streamlit run src/app.py`

## Documento técnico

- [ ] Llenar los [LLENAR] con `resultados/tablas.md` y escribir las discusiones
- [ ] Anexo de uso de IA
- [ ] Exportar a PDF
