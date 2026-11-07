# Guía detallada, paso a paso

Sigan los pasos en orden. Cada paso dice **quién** lo hace, **cuánto tarda** y **qué debería ver**. Los comandos se copian tal cual en la Terminal.

- **Mac:** use `python3` y `pip3`, como dicen los comandos.
- **Windows:** cambie `python3` por `py` y `pip3` por `py -m pip`, y abra la terminal "PowerShell".

---

## PASO 1. Instalar lo necesario (cada una en su computador, 20 min)

1. **Python 3.10 o más nuevo.** En la Terminal escriba `python3 --version`.
   - Si dice 3.10, 3.11, 3.12 o 3.13, está bien.
   - Si no, descárguelo de https://www.python.org/downloads/. En Windows, marque la casilla **"Add Python to PATH"** al instalar.
2. **GitHub Desktop**, para hacer commits sin pelear con la terminal: https://desktop.github.com/. Ábralo e inicie sesión con su cuenta de GitHub.
3. **VS Code**, para abrir y editar archivos: https://code.visualstudio.com/.

---

## PASO 2. Crear el repositorio (Maryam, 15 min)

1. Descargue `proyecto_final.zip` de este chat y descomprímalo en Documentos. Cámbiele el nombre a la carpeta, por ejemplo `rutas-cafeteras`.
2. En GitHub Desktop vaya a **File → Add local repository** y elija esa carpeta.
   - Le dirá que no es un repositorio. Haga clic en **"create a repository"** y luego en **Create repository**.
3. Haga clic en **Publish repository**.
   - Deje marcado **"Keep this code private"** si quiere que sea privado.
   - Publish.
4. En el navegador, abra el repo en github.com y vaya a **Settings → Collaborators → Add people**. Agregue a:
   - Helen
   - Valentina
   - **el profesor**
5. Mande el enlace del repo por el chat del grupo.

**Qué debería ver:** en github.com, el repo con las carpetas `src`, `datos`, `docs`, `specs` y `tests`.

---

## PASO 3. Que Helen y Valentina descarguen el repo (cada una, 5 min)

1. Acepten la invitación que les llega al correo.
2. En GitHub Desktop vayan a **File → Clone repository**, elijan el repo y luego **Clone**.

---

## PASO 4. Preparar el ambiente de Python (las 3, 10 min)

Abra la Terminal **dentro de la carpeta del repo**. En GitHub Desktop: **Repository → Open in Terminal** (o "Open in Command Prompt" en Windows). Luego:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
```

- En Windows, la segunda línea es `.venv\Scripts\activate`.
- Si PowerShell no lo deja, corra primero `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y responda `S`.
- **Qué debería ver:** al inicio de la línea de la terminal aparece `(.venv)`, y la instalación termina sin letras rojas que digan `ERROR`.

Pruebe que todo quedó bien:

```bash
python3 -m pytest tests
```

**Qué debería ver:** `6 passed`. Si sale eso, el código funciona en su computador.

> **Cada vez que abran una terminal nueva** hay que volver a activar el ambiente con `source .venv/bin/activate` (o `.venv\Scripts\activate` en Windows).

---

## PASO 5. Verificar el catálogo de lugares (las 3, por turnos, 1–2 h)

El archivo es `datos/catalogo.csv`. Ábranlo en VS Code; en Excel se pueden dañar las tildes y los decimales.

**Para no pisarse los cambios, háganlo por turnos: Maryam, luego Helen, luego Valentina.** Antes de empezar su turno, cada una hace clic en **Fetch origin / Pull** en GitHub Desktop.

| Quién | Filas |
|---|---|
| Maryam | L01–L12 (cabeceras) y L36–L40 (acopio) |
| Helen | L13–L27 (atractivos) |
| Valentina | L28–L35 (fincas) |

**Para cada fila:**
1. Busque el lugar en Google Maps. Las cabeceras van en la **plaza principal**.
2. Haga **clic derecho** justo sobre el sitio. El primer renglón del menú son las coordenadas, por ejemplo `4.53389, -75.68111`. Haga clic en ellas para copiarlas.
3. Pegue la primera en `latitud` y la segunda en `longitud`. Use **punto** decimal, no coma.
4. Cambie `no` por `si` en la columna `verificado`.

**Las filas que dicen "POR DEFINIR" hay que cambiarlas por lugares reales.**
- Fincas: busquen en Google Maps "finca cafetera Circasia" o "hotel campestre Montenegro" y escojan una que esté al lado de una carretera.
- Trilladoras y centros de acopio: busquen "trilladora café Armenia", "Cooperativa de Caficultores Calarcá", "Almacafé Armenia", etc.
- Pongan el nombre real y el municipio, y dejen la misma categoría (`finca` o `acopio`).

**Helen (atractivos): revise la columna `duracion_visita_min`** y anote de dónde sale cada duración, porque va al documento (sección 5.5). Por ejemplo, la página oficial del Parque del Café recomienda el día completo. Si no hay fuente, usen un criterio, como 60 min para un mirador, 90 para un museo y 240–360 para un parque temático.

**Al terminar su turno, en GitHub Desktop:**
1. Escriba un resumen, por ejemplo "Verificar coordenadas de cabeceras".
2. Clic en **Commit to main**.
3. Clic en **Push origin**.

---

## PASO 6. Correr las mediciones (un solo computador, 1–3 h, casi todo esperando)

El protocolo exige que todas las mediciones se hagan en la misma máquina. Escojan **el computador más rápido**, conéctenlo al cargador, cierren los demás programas y no lo usen mientras mide. Hagan **Pull** antes de empezar, para tener el catálogo final.

Con el ambiente activado `(.venv)`, corran uno por uno y esperen a que cada uno termine:

### 6.1 R1. Red vial (10–30 min, necesita internet)
```bash
python3 src/r1_red.py
```
- **Qué hace:** descarga el Quindío y las 4 redes de radio alrededor de la plaza de Bolívar, calcula los pesos, mide la componente y ubica los lugares.
- **Qué debería ver:** "Descargando…", luego una línea por cada red con su tiempo y, al final, un resumen con los nodos, las aristas y `lugares_a_mas_de_500m`.
- **Si `lugares_a_mas_de_500m` no está vacío:** revisen esas coordenadas en Google Maps.
  - Si estaban mal, corríjanlas y vuelvan a correr este paso.
  - Si estaban bien (una finca en vía destapada, por ejemplo), déjenlas y anótenlo en la sección 2.4 del documento.
- **Si falla la descarga** (error de conexión o "Overpass"): esperen 5 minutos y repitan. Si sigue fallando, pídanle al profe el archivo GraphML.

### 6.2 R2. Dijkstra y matriz (20–60 min)
```bash
python3 src/r2_caminos.py
```
- **Qué debería ver:** 20 líneas de `cola_prioridad`, que son rápidas, y 10 de `lineal`, que son lentas. Es normal que la lineal se demore. Al final aparecen la mediana de los cocientes y "Matriz 40 x 40 guardada".
- **Si sale `AssertionError … no alcanza a todos`:** un lugar quedó mal ubicado. Revisen su coordenada.

### 6.3 R3. Envolvente convexa (1–2 min)
```bash
python3 src/r3_envolvente.py
```
- **Qué debería ver:** 4 líneas, una por conjunto de puntos, con los tiempos propio y de SciPy.

### 6.4 R4. Viajante (10–20 min)
```bash
python3 src/r4_ruta.py
```
- **Qué debería ver:** una línea por cada k, del 5 al 12.
- En k = 11 o k = 12 la fuerza bruta se demora hasta 5 minutos y luego aparece `no completada`. **Eso es correcto**: el enunciado pide reportarlo así.
- Después aparecen la calidad de la heurística y el itinerario.

### 6.5 Tablas y gráficas (segundos)
```bash
python3 src/graficas.py
```
- **Qué debería ver:** "Listo". Se crean `resultados/tablas.md` y las imágenes en `graficas/`.

**Al terminar todo:** en GitHub Desktop, commit "Resultados de las mediciones" y luego Push.

---

## PASO 7. Probar la aplicación (Maryam, 15 min)

```bash
streamlit run src/app.py
```

Se abre el navegador. La primera carga tarda unos segundos. Revisen las 4 pestañas:
- **Ruta:** elijan Armenia y Salento; debe salir una línea azul por las vías y el tiempo.
- **Envolvente:** debe salir un polígono morado alrededor del departamento.
- **Itinerario:** con 6 a 8 atractivos salen los dos recorridos, sus tiempos y la diferencia.
- **Resultados:** las tablas y las gráficas.

Tomen 2 o 3 capturas de pantalla para la sección 6 del documento. Para cerrar la app, oprima `Ctrl + C` en la terminal.

---

## PASO 8. Llenar el documento técnico (cada una su sección, 3–4 h)

Abran `docs/documento_tecnico.md` en VS Code. Para verlo bonito, oprima `Ctrl+Shift+V` (en Mac `Cmd+Shift+V`).

| Quién | Secciones |
|---|---|
| Maryam | 1 Arquitectura, 2 (R1), 6 (R5), datos de la máquina y fecha de descarga |
| Helen | 3 (R2) y 4 (R3) |
| Valentina | 5 (R4), 7 Conclusiones y el anexo de IA |

**Cómo llenar cada [LLENAR]:**
1. Abran `resultados/tablas.md` y copien la tabla que corresponda en el lugar del [LLENAR].
2. Los datos de la máquina están en `resultados/maquina.json`, y la fecha de descarga, la versión de OSMnx y los lugares lejanos en `resultados/r1_resumen.json`.
3. En cada **Discusión**, el [LLENAR] trae entre corchetes qué comprobar. Hagan esa cuenta con sus números y escriban 4 a 6 líneas que digan si coincide con la teoría y, si no, por qué.
4. **Reescriban con sus propias palabras** lo que ya está escrito: les van a preguntar.

Para no pisarse, también por turnos con Pull, Commit y Push. O escriban cada una en un documento aparte y al final Maryam lo pega todo.

**Exportar a PDF:**
1. En VS Code instalen la extensión **"Markdown PDF"**.
2. Clic derecho en el documento → **Markdown PDF: Export (pdf)**.
3. Revisen que se vean las imágenes.

---

## PASO 9. Revisión final (Maryam, 30 min)

- [ ] El README tiene los nombres de las tres.
- [ ] `python3 -m pytest tests` dice `6 passed`.
- [ ] El repo tiene `resultados/` y `graficas/` con archivos, y `datos/catalogo.csv` con todas las filas en `verificado = si`.
- [ ] Ya no queda ningún "[LLENAR]" ni "POR DEFINIR". Búsquenlos con `Ctrl+F`.
- [ ] El profesor está agregado como colaborador.
- [ ] Las tres tienen commits propios: en github.com, ver la pestaña "Commits".

---

## PASO 10. Preparar la sustentación (las 3 juntas, 2 h)

Cada una le explica su parte a las otras dos, con el código abierto, y las otras le hacen las preguntas de la lista que está al final de `PASOS.md`. Recuerden que **a cualquiera le pueden preguntar cualquier parte**.

---

## Si algo falla

| Error | Qué hacer |
|---|---|
| `command not found: python3` | En Windows use `py`. En Mac, instale Python de python.org |
| `No module named osmnx` (o cualquier otro) | No activó el ambiente: `source .venv/bin/activate` |
| `No such file or directory: src/...` | La terminal no está en la carpeta del repo. Ábrala desde GitHub Desktop: Repository → Open in Terminal |
| `FileNotFoundError ... componente.graphml` | Falta correr `src/r1_red.py` primero |
| `FileNotFoundError ... matriz_tiempos.csv` | Falta correr `src/r2_caminos.py` antes que el R4 |
| Conflicto en GitHub Desktop | Mándenme captura y lo resolvemos |

Para cualquier otro error, **copien el mensaje completo de la terminal** y pásenmelo por aquí.
