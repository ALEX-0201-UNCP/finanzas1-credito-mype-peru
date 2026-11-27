# Nombres y apellidos: Chancha Santiago Alex Omar
# Código de matrícula: 2024200492K
# Tema N.º 88: Restricción financiera y acceso al crédito de la micro y pequeña empresa peruana
# Fecha de extracción: 2026-11-25  (actualizar si se vuelve a extraer)

# 03_limpieza_datos.py
# Lee los datos crudos (Excel de la SBS y PDF del INEI) y construye el panel
# 25 departamentos x meses, que se guarda en /datos_procesados.
#
# Variables del panel:
#   credito_miles_soles     (endógena)  SBS: créditos directos de las entidades microfinancieras
#   depositos_miles_soles   (exógena)   SBS: depósitos totales (no incluye empresas de créditos)
#   pbi_miles_soles_2007    (exógena)   INEI: PBI departamental, precios constantes de 2007
#   poblacion               (exógena)   INEI: población al 30 de junio, estimaciones y proyecciones
#   credito_per_capita_soles (derivada) crédito / población

import os
import re
import glob
import hashlib
import unicodedata
import pandas as pd
import pdfplumber

# ---------------------------------------------------------------------------
# 1. PARÁMETROS CONGELADOS
# ---------------------------------------------------------------------------
CODIGO_MATRICULA = "2024200492K"
FECHA_INICIO = "2017-01"
FECHA_CORTE = "2024-12"       # el PBI departamental del INEI llega hasta 2024

ENTIDADES = ["cajas_municipales", "cajas_rurales", "empresas_financieras", "empresas_de_creditos"]

# Páginas de los PDF del INEI donde están las tablas
PAG_PBI = 101                  # Cuadro N.º 1: PBI por departamentos 2007-2024
PAGS_POBLACION = {             # Cuadro 3.68, repartido en 3 páginas (orden de columnas)
    125: ["peru", "amazonas", "ancash", "apurimac", "arequipa", "ayacucho", "cajamarca", "callao", "cusco"],
    126: ["huancavelica", "huanuco", "ica", "junin", "lalibertad", "lambayeque", "lima", "loreto", "madrededios"],
    127: ["moquegua", "pasco", "piura", "puno", "sanmartin", "tacna", "tumbes", "ucayali"],
}
UMBRAL_HUECO = 5.0             # separación (pt) que distingue "miles" de "otra columna"

# ---------------------------------------------------------------------------
# 2. RUTAS RELATIVAS
# ---------------------------------------------------------------------------
def obtener_directorio_base():
    try:
        dir_actual = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        dir_actual = os.getcwd()
    if os.path.basename(dir_actual).lower() == "codigo":
        return os.path.dirname(dir_actual)
    return dir_actual

DIR_BASE = obtener_directorio_base()
DIR_CRUDOS = os.path.join(DIR_BASE, "datos_crudos")
DIR_PROC = os.path.join(DIR_BASE, "datos_procesados")
RUTA_SALIDA = os.path.join(DIR_PROC, f"datos_procesados_{CODIGO_MATRICULA}.csv")
RUTA_PBI = os.path.join(DIR_CRUDOS, "inei_pbi", "inei_pbi_departamentos_2007_2024.pdf")
RUTA_POB = os.path.join(DIR_CRUDOS, "inei_poblacion", "inei_poblacion_departamentos_1995_2030.pdf")

# ---------------------------------------------------------------------------
# 3. CÓDIGOS UBIGEO (INEI) Y NORMALIZACIÓN DE NOMBRES
# ---------------------------------------------------------------------------
def clave(texto):
    """Solo letras, minúsculas y sin tildes: 'San Martín' -> 'sanmartin'."""
    t = unicodedata.normalize("NFKD", str(texto))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"[^a-z]", "", t.lower())

NOMBRES = {
    "01": "Amazonas", "02": "Áncash", "03": "Apurímac", "04": "Arequipa", "05": "Ayacucho",
    "06": "Cajamarca", "07": "Callao", "08": "Cusco", "09": "Huancavelica", "10": "Huánuco",
    "11": "Ica", "12": "Junín", "13": "La Libertad", "14": "Lambayeque", "15": "Lima",
    "16": "Loreto", "17": "Madre de Dios", "18": "Moquegua", "19": "Pasco", "20": "Piura",
    "21": "Puno", "22": "San Martín", "23": "Tacna", "24": "Tumbes", "25": "Ucayali",
}
UBIGEO = {clave(n): u for u, n in NOMBRES.items()}
UBIGEO.update({"provconstdelcallao": "07", "provinciaconstitucionaldelcallao": "07"})

# ---------------------------------------------------------------------------
# 4. SBS: LECTURA DE LOS EXCEL (detecta las columnas por su encabezado)
# ---------------------------------------------------------------------------
ABREV_A_MES = {"en": 1, "fe": 2, "ma": 3, "ab": 4, "my": 5, "jn": 6,
               "jl": 7, "ag": 8, "se": 9, "oc": 10, "no": 11, "di": 12}

def fecha_desde_nombre(ruta):
    """C-1234-fe2026.XLS -> '2026-02'."""
    sufijo = os.path.splitext(os.path.basename(ruta))[0].split("-")[-1]
    return f"{sufijo[2:]}-{ABREV_A_MES[sufijo[:2]]:02d}"

def leer_xls_sbs(ruta, avisos):
    """Devuelve crédito y depósitos por departamento de un Excel de la SBS.
    El crédito total es la última columna; los depósitos son la columna 'Total Depósitos'
    (las empresas de créditos no la tienen)."""
    nombre = os.path.basename(ruta)
    crudo = pd.read_excel(ruta, header=None)
    # El encabezado puede venir como "Empresa" o "Empresa*" (con asterisco)
    filas_enc = crudo.index[crudo[0].astype(str).str.strip().str.lower().str.rstrip("*").str.strip() == "empresa"]
    if len(filas_enc) == 0:
        avisos.append(f"{nombre}: no se encontró la fila de encabezado 'Empresa'")
        return None
    r = filas_enc[0]
    enc = (crudo.iloc[r].fillna("").astype(str) + " " + crudo.iloc[r + 1].fillna("").astype(str)).str.strip()
    col_cred = max(i for i, t in enumerate(enc) if t)
    col_dep = next((i for i, t in enumerate(enc) if re.search(r"total\s*dep", t, re.I)), None)

    datos = crudo.iloc[r + 2:].copy()
    primera = datos[0].astype(str).str.strip().str.lower()
    fila_total = datos[primera.str.startswith("total general")]
    # Solo se excluyen "Total general" y las notas. Ojo: hay empresas cuyo nombre empieza
    # con "Total" (ej. TOTAL SERVICIOS) y esas SÍ deben sumarse.
    datos = datos[~(primera.str.startswith("total general") | primera.str.startswith("nota"))].copy()
    datos[1] = datos[1].ffill()                                   # celdas combinadas
    datos["cred"] = pd.to_numeric(datos[col_cred], errors="coerce").fillna(0)
    datos["dep"] = pd.to_numeric(datos[col_dep], errors="coerce").fillna(0) if col_dep is not None else 0.0

    # Control de integridad contra el "Total general" publicado por la SBS
    if len(fila_total):
        tc = pd.to_numeric(fila_total[col_cred], errors="coerce").iloc[0]
        if abs(datos["cred"].sum() - tc) > 1:
            avisos.append(f"{nombre}: el crédito no coincide con 'Total general'")
        if col_dep is not None:
            td = pd.to_numeric(fila_total[col_dep], errors="coerce").iloc[0]
            if abs(datos["dep"].sum() - td) > 1:
                avisos.append(f"{nombre}: los depósitos no coinciden con 'Total general'")
    else:
        avisos.append(f"{nombre}: sin fila 'Total general' para verificar")

    g = datos.groupby(datos[1].astype(str), as_index=False)[["cred", "dep"]].sum()
    g["ubigeo"] = g[1].map(lambda x: UBIGEO.get(clave(x)))
    malos = g[g["ubigeo"].isna() & ((g["cred"] != 0) | (g["dep"] != 0))]
    if len(malos):
        avisos.append(f"{nombre}: departamentos sin ubigeo: {malos[1].tolist()}")
    g = g.dropna(subset=["ubigeo"])
    g["fecha"] = fecha_desde_nombre(ruta)
    g["tiene_depositos"] = col_dep is not None
    return g[["ubigeo", "fecha", "cred", "dep", "tiene_depositos"]]

def construir_sbs(avisos, fecha_inicio, fecha_corte):
    partes = []
    for ent in ENTIDADES:
        rutas = sorted(glob.glob(os.path.join(DIR_CRUDOS, ent, "*.XLS")))
        print(f"{ent}: {len(rutas)} archivos")
        for ruta in rutas:
            fecha = fecha_desde_nombre(ruta)
            if not (fecha_inicio <= fecha <= fecha_corte):
                continue
            g = leer_xls_sbs(ruta, avisos)
            if g is not None:
                partes.append(g)
    if not partes:
        raise FileNotFoundError("No hay Excel en datos_crudos. Ejecutar antes 02_scraping_web.py")
    todo = pd.concat(partes, ignore_index=True)
    return (todo.groupby(["ubigeo", "fecha"], as_index=False)[["cred", "dep"]].sum()
                .rename(columns={"cred": "credito_miles_soles", "dep": "depositos_miles_soles"}))

# ---------------------------------------------------------------------------
# 5. INEI: LECTURA DE LOS PDF (PBI y población)
# ---------------------------------------------------------------------------
def lineas_pdf(pagina):
    """Agrupa las palabras de una página en líneas (misma altura), ordenadas de izquierda a derecha."""
    palabras = sorted(pagina.extract_words(x_tolerance=1.5), key=lambda w: (w["top"], w["x0"]))
    lineas, actual, top = [], [], None
    for w in palabras:
        if top is None or abs(w["top"] - top) <= 2:
            actual.append(w)
            top = w["top"] if top is None else top
        else:
            lineas.append(sorted(actual, key=lambda x: x["x0"]))
            actual, top = [w], w["top"]
    if actual:
        lineas.append(sorted(actual, key=lambda x: x["x0"]))
    return lineas

def agrupar_numeros(palabras):
    """Une los trozos de un número separados por espacio de miles ('1 778 775' -> 1778775).
    Un hueco pequeño entre trozos es de miles; un hueco grande es otra columna."""
    valores, actual, x_prev = [], "", None
    for w in palabras:
        if not w["text"].isdigit():
            continue
        if actual and (w["x0"] - x_prev) < UMBRAL_HUECO:
            actual += w["text"]
        else:
            if actual:
                valores.append(int(actual))
            actual = w["text"]
        x_prev = w["x1"]
    if actual:
        valores.append(int(actual))
    return valores

def leer_pbi(avisos):
    """PBI por departamento, 2007-2024 (miles de soles, precios de 2007). Devuelve {ubigeo: {año: valor}}."""
    filas = {}
    with pdfplumber.open(RUTA_PBI) as pdf:
        for linea in lineas_pdf(pdf.pages[PAG_PBI - 1]):
            nombre = clave("".join(w["text"] for w in linea if not w["text"].isdigit()))
            valores = agrupar_numeros(linea)
            if nombre and len(valores) == 18:
                filas[nombre] = valores
    anios = list(range(2007, 2025))
    # En esta tabla "Lima" incluye al Callao: Lima (ubigeo 15) = Región Lima + Provincia de Lima
    filas["lima"] = [a + b for a, b in zip(filas["regionlima"], filas["provinciadelima"])]
    filas["callao"] = filas["provconstdelcallao"]
    pbi = {}
    for nombre, u in UBIGEO.items():
        if nombre in filas and u not in pbi:
            pbi[u] = dict(zip(anios, filas[nombre]))
    if len(pbi) != 25:
        avisos.append(f"PBI: se leyeron {len(pbi)} departamentos (se esperaban 25)")
    # Control: la suma de departamentos debe igualar el 'Valor agregado bruto' nacional
    if "valoragregadobruto" in filas:
        for i, a in enumerate(anios):
            if sum(v[a] for v in pbi.values()) != filas["valoragregadobruto"][i]:
                avisos.append(f"PBI {a}: la suma de departamentos no coincide con el total nacional")
    return pbi

def leer_poblacion(avisos):
    """Población al 30 de junio, 1995-2030. Devuelve {ubigeo: {año: valor}}."""
    tabla = {}
    with pdfplumber.open(RUTA_POB) as pdf:
        for pag, columnas in PAGS_POBLACION.items():
            for linea in lineas_pdf(pdf.pages[pag - 1]):
                if not re.fullmatch(r"(19|20)\d\d", linea[0]["text"]):
                    continue
                anio = int(linea[0]["text"])
                valores = agrupar_numeros(linea[1:])
                if len(valores) != len(columnas):
                    avisos.append(f"Población {anio} (pág. {pag}): {len(valores)} valores, se esperaban {len(columnas)}")
                    continue
                for c, v in zip(columnas, valores):
                    tabla.setdefault(anio, {})[c] = v
    pob = {}
    for anio, fila in tabla.items():
        if sum(v for k, v in fila.items() if k != "peru") != fila["peru"]:
            avisos.append(f"Población {anio}: la suma de departamentos no coincide con el total del Perú")
        for c, v in fila.items():
            if c != "peru":
                pob.setdefault(UBIGEO[c], {})[anio] = v
    return pob

# ---------------------------------------------------------------------------
# 6. PANEL FINAL
# ---------------------------------------------------------------------------
def lista_meses(fecha_inicio, fecha_corte):
    a, m = map(int, fecha_inicio.split("-"))
    a2, m2 = map(int, fecha_corte.split("-"))
    meses = []
    while (a, m) <= (a2, m2):
        meses.append(f"{a}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return meses

def construir_panel(fecha_inicio=FECHA_INICIO, fecha_corte=FECHA_CORTE):
    avisos = []
    sbs = construir_sbs(avisos, fecha_inicio, fecha_corte)
    pbi, pob = leer_pbi(avisos), leer_poblacion(avisos)

    # Malla completa: 25 departamentos x todos los meses
    malla = pd.MultiIndex.from_product([sorted(NOMBRES), lista_meses(fecha_inicio, fecha_corte)],
                                       names=["ubigeo", "fecha"]).to_frame(index=False)
    panel = malla.merge(sbs, on=["ubigeo", "fecha"], how="left")
    sin_dato = int(panel["credito_miles_soles"].isna().sum())
    if sin_dato:
        avisos.append(f"{sin_dato} celdas ubigeo-mes sin oficinas en la SBS (se completan con 0)")
    panel[["credito_miles_soles", "depositos_miles_soles"]] = panel[["credito_miles_soles", "depositos_miles_soles"]].fillna(0)

    panel["anio"] = panel["fecha"].str[:4].astype(int)
    panel["pbi_miles_soles_2007"] = [pbi[u][a] for u, a in zip(panel["ubigeo"], panel["anio"])]
    panel["poblacion"] = [pob[u][a] for u, a in zip(panel["ubigeo"], panel["anio"])]
    panel["credito_per_capita_soles"] = (panel["credito_miles_soles"] * 1000 / panel["poblacion"]).round(2)
    panel["departamento"] = panel["ubigeo"].map(NOMBRES)
    columnas = ["ubigeo", "departamento", "fecha", "credito_miles_soles", "depositos_miles_soles",
                "pbi_miles_soles_2007", "poblacion", "credito_per_capita_soles"]
    return panel[columnas].sort_values(["ubigeo", "fecha"]).reset_index(drop=True), avisos

def sha256_archivo(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(8192), b""):
            h.update(bloque)
    return h.hexdigest()
# ---------------------------------------------------------------------------
# 7. VISTA EN EXCEL (solo para leer el panel con comodidad; NO reemplaza al CSV)
# ---------------------------------------------------------------------------
def guardar_vista_excel(panel):
    """Guarda una copia ordenada del panel en /salidas/panel_vista.xlsx.
    El archivo oficial sigue siendo el CSV de /datos_procesados (el hash es del CSV)."""
    from openpyxl.utils import get_column_letter
    from openpyxl.styles import Font, PatternFill, Alignment
    os.makedirs(DIR_PROC, exist_ok=True)
    ruta = os.path.join(DIR_PROC, f"datos_procesados_{CODIGO_MATRICULA}_vista.xlsx")
    with pd.ExcelWriter(ruta, engine="openpyxl") as escritor:
        panel.to_excel(escritor, sheet_name="Panel", index=False)
        hoja = escritor.sheets["Panel"]
        hoja.freeze_panes = "D2"
        hoja.auto_filter.ref = hoja.dimensions
        for celda in hoja[1]:
            celda.font = Font(bold=True, color="FFFFFF")
            celda.fill = PatternFill("solid", fgColor="1F4E78")
            celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        for i, col in enumerate(panel.columns, start=1):
            ancho = max(len(str(col)), panel[col].astype(str).str.len().max()) + 3
            hoja.column_dimensions[get_column_letter(i)].width = min(ancho, 28)
            if col in ("credito_miles_soles", "depositos_miles_soles", "pbi_miles_soles_2007",
                       "poblacion", "credito_per_capita_soles"):
                for fila in range(2, len(panel) + 2):
                    hoja.cell(row=fila, column=i).number_format = "#,##0.00" if "per_capita" in col else "#,##0"
    print("Vista en Excel guardada:", ruta)

if __name__ == "__main__":
    os.makedirs(DIR_PROC, exist_ok=True)
    panel, avisos = construir_panel()
    panel.to_csv(RUTA_SALIDA, index=False, encoding="utf-8", lineterminator="\n")
    guardar_vista_excel(panel)
    print("\n=== AVISOS ===")
    for a in avisos[:40]:
        print("AVISO:", a)
    if len(avisos) > 40:
        print(f"... y {len(avisos) - 40} avisos más")
    print(f"\nPanel guardado: {RUTA_SALIDA}")
    print("Filas:", len(panel), "| departamentos:", panel["ubigeo"].nunique(), "| meses:", panel["fecha"].nunique())
    print("SHA-256:", sha256_archivo(RUTA_SALIDA))
