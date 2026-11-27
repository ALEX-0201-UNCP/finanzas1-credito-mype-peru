# Restricción financiera y acceso al crédito de la micro y pequeña empresa peruana

**Nombres y apellidos:** Chancha Santiago Alex Omar
**Código de matrícula:** 2024200492K
**Curso:** Finanzas I (055D), Ciclo V. Escuela Profesional de Economía, Facultad de Economía, UNCP
**Docente:** Dr. Ciro Iván Machacuay Meza
**Periodo lectivo:** 2026-II, Unidad II
**Tema N.º 88 del temario**
**Repositorio:** https://github.com/ALEX-0201-UNCP/finanzas1-credito-mype-peru

## Pregunta de investigación
Analizar la evolución del crédito mype y sus determinantes por departamento.

## Panel de datos
- **Unidad:** 25 departamentos (el Callao separado de Lima).
- **Periodo:** enero de 2017 a diciembre de 2024 (`FECHA_INICIO = "2017-01"`, `FECHA_CORTE = "2024-12"`).
- **Tamaño:** 25 x 96 meses = 2 400 observaciones.
- **Llave común:** `ubigeo` (código INEI de 2 dígitos) + `fecha` (AAAA-MM).
- **Fecha de extracción:** 24 y 25 de noviembre de 2026 (ver `log_ejecucion.txt`).

## Vía de extracción
Vía 2: descarga programática de archivos oficiales (Excel de la SBS y PDF del INEI), con los scripts de `/codigo`.
La vía API no se utiliza por indicación del docente en clase para la Unidad II; ver `incidencias_fuente.md`.

## Fuentes y endpoints
| Fuente | Contenido | Formato | Dirección |
|---|---|---|---|
| SBS | Créditos directos y depósitos por oficina, Cajas Municipales (`C-1234`) | XLS mensual | `https://intranet2.sbs.gob.pe/estadistica/financiera/{año}/{Mes}/C-1234-{mes}{año}.XLS` |
| SBS | Íd., Cajas Rurales (`C-2234`) | XLS mensual | `.../C-2234-{mes}{año}.XLS` |
| SBS | Íd., Empresas Financieras (`B-3241`) | XLS mensual | `.../B-3241-{mes}{año}.XLS` |
| SBS | Créditos directos por oficina, Empresas de Créditos (`C-4228`) | XLS mensual | `.../C-4228-{mes}{año}.XLS` |
| INEI | Perú: Producto Bruto Interno por Departamentos 2007-2024 (Cuadro N.º 1, pág. 101) | PDF | `https://cdn.www.gob.pe/uploads/document/file/9219775/7567597-peru-producto-bruto-interno-por-departamentos-2007-2024.pdf?v=1771442357` |
| INEI | Boletín de Análisis Demográfico N.º 39, Cuadro 3.68 (págs. 125 a 127) | PDF | `https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1702/libro.pdf` |

## Orden de ejecución
1. `pip install -r requirements.txt`
2. `python codigo/01_extraccion_api.py` (informa que no se usa vía API)
3. `python codigo/02_scraping_web.py` (descarga a `/datos_crudos`; omite lo ya descargado)
4. `python codigo/03_limpieza_datos.py` (genera `/datos_procesados`)
5. `python codigo/04_analisis.py` (tablas y figuras en `/salidas`)

## Entorno
- Python 3.12.11 (entorno de Spyder 6).
- pandas 3.0.5, numpy 2.5.2, requests 2.34.2, openpyxl 3.1.5, xlrd 2.0.2, pdfplumber 0.11.11, pillow 13.0.0.
- No se requieren claves de API.

## Verificación de integridad
- Archivo: `datos_procesados/datos_procesados_2024200492K.csv`
- **SHA-256:** `15d4e4db49e82de8765e8f930ee313553e9a5f55f03b2911325fcf3daf08c5a8`

Este hash se coteja contra el archivo entregado. Una reejecución puede diferir si la SBS o el INEI revisan sus series.

## Control de calidad en `03_limpieza_datos.py`
- La suma de oficinas de cada Excel se compara con la fila "Total general" publicada por la SBS.
- La suma de los departamentos se compara con el total nacional del INEI (PBI y población).
- Resultado de la última ejecución: 0 avisos.

## Notas metodológicas
- El crédito mype se aproxima con el crédito directo de las entidades microfinancieras (cajas municipales, cajas rurales, empresas financieras y empresas de créditos). La SBS no publica el crédito por tipo de empresa a nivel departamental con frecuencia mensual.
- El cuadro del INEI llamado PBI por departamento suma el valor agregado bruto nacional; los impuestos no se distribuyen por departamento. Los años 2022 a 2024 son cifras preliminares.
- En la tabla del INEI, "Lima" incluye al Callao. Para igualar a la SBS se calcula Lima = Región Lima + Provincia de Lima, y el Callao aparte.
- Las empresas de créditos no publican depósitos, por lo que `depositos_miles_soles` cubre las otras tres entidades.
- La población y el PBI son anuales y se repiten en los 12 meses de cada año. Desde 2020, la población es una proyección.
- Si un departamento no tiene oficinas de una entidad en un mes, su crédito se toma como 0.
