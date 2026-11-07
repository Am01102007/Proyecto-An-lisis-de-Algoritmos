# Plan de 2 días: qué hacer, en orden

El código ya está hecho y probado con una red de prueba. Falta correrlo con la red real, verificar el catálogo y escribir la discusión de los resultados.

## Reparto sugerido

Cada una es dueña de una parte y hace sus propios commits, porque el profe revisa el historial.

| | Maryam | Helen | Valentina |
|---|---|---|---|
| Código | `r1_red.py`, `grafo.py`, `app.py` | `dijkstra.py`, `r2_caminos.py`, `envolvente.py`, `r3_envolvente.py` | `viajante.py`, `r4_ruta.py` |
| Documento | Secciones 1, 2 (R1) y 6 (R5) | Secciones 3 (R2) y 4 (R3) | Sección 5 (R4) y conclusiones |
| Catálogo | Cabeceras (12) + acopio (5) | Atractivos (15) y su duración | Fincas (8) |

## Día 1: datos y mediciones

1. **Repo (Maryam, 15 min).**
   - Crear el repo en GitHub, compartirlo con el profe y con Helen y Valentina.
   - Copiar todo el contenido de esta carpeta, hacer el primer commit y que las otras dos lo clonen.
2. **Ambiente (cada una, 15 min).**
   - `python -m venv .venv`, activar el ambiente y correr `pip install -r requirements.txt`.
   - Probar con `python -m pytest tests`; debe decir **6 passed**.
3. **Catálogo (las 3, 1–2 h).** Abrir `datos/catalogo.csv`.
   - Buscar cada lugar en Google Maps. Clic derecho sobre el sitio exacto copia latitud y longitud; las cabeceras van en la plaza principal.
   - Corregir las coordenadas y poner `si` en `verificado`.
   - **Reemplazar las filas que dicen POR DEFINIR** por fincas y trilladoras reales.
   - Revisar las duraciones de visita y anotar la fuente o el criterio.
   - Hacer un commit cada una con su parte.
4. **Mediciones (en un solo computador, el más rápido; 1–2 h, casi todo esperando).**
   - **No usar el computador para otra cosa mientras mide.** Desde la raíz del repo:
     ```
     python src/r1_red.py
     python src/r2_caminos.py
     python src/r3_envolvente.py
     python src/r4_ruta.py
     python src/graficas.py
     ```
   - Si `r1_red.py` reporta lugares a más de 500 m, revisar esas coordenadas y volver a correrlo.
   - Si la descarga falla, pedirle al profe el GraphML.
5. **Probar la app:** `streamlit run src/app.py`. Commit con `resultados/`, `graficas/` y `datos/`.

## Día 2: documento y sustentación

6. **Documento (cada una, su sección, 3–4 h).** Abrir `docs/documento_tecnico.md`.
   - Llenar cada **[LLENAR]** con los números de `resultados/tablas.md` y escribir el párrafo de discusión.
   - Reescribir con sus propias palabras.
   - Exportarlo a PDF, por ejemplo abriéndolo en VS Code o Typora y exportando.
7. **README:** revisar que los comandos funcionen en un computador limpio.
8. **Sustentación (las 3 juntas, 2 h).** Cada una le explica a las otras su parte, con las preguntas de abajo. La nota se multiplica por la sustentación y preguntan de todo.

## Preguntas que les pueden hacer

- ¿Por qué listas y no matriz? (V² contra V + E; la red es dispersa).
- ¿Cómo funciona Tarjan y por qué es O(V + E)?
- ¿Cuál es el invariante de Dijkstra, por qué se puede detener en el destino y por qué falla con pesos negativos?
- ¿Por qué la versión lineal es tan lenta aunque el destino esté cerca? (cada extracción recorre los V nodos).
- Recurrencia de Quickhull: T(n) = 2T(n/2) + bn da O(n log n) (caso 2 del maestro); T(n) = T(n−1) + bn da una serie aritmética y O(n²).
- ¿Por qué SciPy es más rápido si usa el mismo algoritmo? (Qhull en C contra Python interpretado).
- Recurrencia de Held-Karp, subestructura óptima, por qué es O(2ᵏ k²) y cuánta memoria usa.
- ¿Por qué la fuerza bruta no llega a k = 12? (12! ≈ 479 millones de recorridos).
- ¿Por qué el vecino más cercano falla? (el ejemplo de 4 lugares) y ¿por qué en Dijkstra lo voraz sí funciona?
