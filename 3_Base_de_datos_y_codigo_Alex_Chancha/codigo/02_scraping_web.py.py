# Nombres y apellidos: Chancha Santiago Alex Omar
# Código de matrícula: 2024200492K
# Tema N.º 88: Restricción financiera y acceso al crédito de la micro y pequeña empresa peruana
# Fecha de extracción: 2026-11-23

import os
import time
import requests

# Parámetros congelados
FECHA_INICIO = "2018-01"
FECHA_CORTE = "2025-12"
CODIGO_REPORTE = "C-1234"      # Créditos directos y depósitos por oficina - Cajas Municipales
PAUSA_SEG = 1
HEADERS = {"User-Agent": "Mozilla/5.0 (investigacion academica UNCP - Finanzas I - Chancha Santiago Alex Omar - 2024200492K)"}

MESES = {1: ("Enero", "en"), 2: ("Febrero", "fe"), 3: ("Marzo", "ma"), 4: ("Abril", "ab"),
         5: ("Mayo", "my"), 6: ("Junio", "jn"), 7: ("Julio", "jl"), 8: ("Agosto", "ag"),
         9: ("Setiembre", "se"), 10: ("Octubre", "oc"), 11: ("Noviembre", "no"), 12: ("Diciembre", "di")}

# Rutas relativas: este script está en /codigo, los datos van en /datos_crudos
DIR_CODIGO = os.path.dirname(os.path.abspath(__file__))
DIR_BASE = os.path.dirname(DIR_CODIGO)
DESTINO = os.path.join(DIR_BASE, "datos_crudos", "cajas_municipales")
RUTA_LOG = os.path.join(DIR_BASE, "log_ejecucion.txt")
os.makedirs(DESTINO, exist_ok=True)

# Lista de meses entre FECHA_INICIO y FECHA_CORTE
a, m = map(int, FECHA_INICIO.split("-"))
a_fin, m_fin = map(int, FECHA_CORTE.split("-"))
meses = []
while (a, m) <= (a_fin, m_fin):
    meses.append((a, m))
    m += 1
    if m == 13:
        a, m = a + 1, 1

ok = fallidos = ya_existian = 0
with open(RUTA_LOG, "a", encoding="utf-8") as log:
    log.write(f"\n=== {time.strftime('%Y-%m-%d %H:%M:%S')} | {CODIGO_REPORTE} | {FECHA_INICIO} a {FECHA_CORTE} ===\n")
    for anio, mes in meses:
        nombre_mes, abrev = MESES[mes]
        archivo = f"{CODIGO_REPORTE}-{abrev}{anio}.XLS"
        ruta = os.path.join(DESTINO, archivo)
        if os.path.exists(ruta):
            ya_existian += 1
            continue
        url = f"https://intranet2.sbs.gob.pe/estadistica/financiera/{anio}/{nombre_mes}/{archivo}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            marca = time.strftime("%Y-%m-%d %H:%M:%S")
            if r.status_code == 200:
                with open(ruta, "wb") as f:
                    f.write(r.content)
                ok += 1
                print(f"OK     {anio}-{mes:02d} | HTTP 200 | {len(r.content)} bytes")
                log.write(f"{marca} | {url} | HTTP 200 | {len(r.content)} bytes\n")
            else:
                fallidos += 1
                print(f"FALLO  {anio}-{mes:02d} | HTTP {r.status_code}")
                log.write(f"{marca} | {url} | HTTP {r.status_code} | FALLO\n")
        except requests.RequestException as e:
            fallidos += 1
            print(f"ERROR  {anio}-{mes:02d} | {e}")
            log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {url} | ERROR: {e}\n")
        time.sleep(PAUSA_SEG)
    resumen = f"RESUMEN: {ok} descargados, {ya_existian} ya existían, {fallidos} fallidos de {len(meses)} meses"
    print(resumen)
    log.write(resumen + "\n")
    
    # ---------------------------------------------------------------------
# BLOQUE B - INEI: PBI por departamentos 2007-2024 (PDF oficial)
# ---------------------------------------------------------------------
URL_INEI_PBI = "https://cdn.www.gob.pe/uploads/document/file/9219775/7567597-peru-producto-bruto-interno-por-departamentos-2007-2024.pdf?v=1771442357"
DESTINO_PBI = os.path.join(DIR_BASE, "datos_crudos", "inei_pbi")
os.makedirs(DESTINO_PBI, exist_ok=True)
ruta_pbi = os.path.join(DESTINO_PBI, "inei_pbi_departamentos_2007_2024.pdf")

if os.path.exists(ruta_pbi):
    print("INEI PBI: el PDF ya existe, no se vuelve a descargar")
else:
    r = requests.get(URL_INEI_PBI, headers=HEADERS, timeout=120)
    marca = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(RUTA_LOG, "a", encoding="utf-8") as log:
        log.write(f"{marca} | {URL_INEI_PBI} | HTTP {r.status_code} | {len(r.content)} bytes\n")
    if r.status_code == 200:
        with open(ruta_pbi, "wb") as f:
            f.write(r.content)
        print("INEI PBI descargado:", ruta_pbi)
    else:
        print("INEI PBI FALLO | HTTP", r.status_code)
    time.sleep(PAUSA_SEG)
    
    # ---------------------------------------------------------------------
# BLOQUE C - INEI: Población por departamento 1995-2030 (Boletín N.º 39)
# ---------------------------------------------------------------------
URL_INEI_POBLACION = "https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1702/libro.pdf"
DESTINO_POB = os.path.join(DIR_BASE, "datos_crudos", "inei_poblacion")
os.makedirs(DESTINO_POB, exist_ok=True)
ruta_pob = os.path.join(DESTINO_POB, "inei_poblacion_departamentos_1995_2030.pdf")

if os.path.exists(ruta_pob):
    print("INEI población: el PDF ya existe, no se vuelve a descargar")
else:
    r = requests.get(URL_INEI_POBLACION, headers=HEADERS, timeout=120)
    marca = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(RUTA_LOG, "a", encoding="utf-8") as log:
        log.write(f"{marca} | {URL_INEI_POBLACION} | HTTP {r.status_code} | {len(r.content)} bytes\n")
    if r.status_code == 200:
        with open(ruta_pob, "wb") as f:
            f.write(r.content)
        print("INEI población descargado:", ruta_pob)
    else:
        print("INEI población FALLO | HTTP", r.status_code)
    time.sleep(PAUSA_SEG)