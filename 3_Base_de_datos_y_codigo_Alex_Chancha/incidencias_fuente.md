# Registro de incidencias de fuente y decisiones metodológicas

**Autor:** Chancha Santiago Alex Omar (2024200492K)
**Tema N.º 88:** Restricción financiera y acceso al crédito de la micro y pequeña empresa peruana
**Unidad II, periodo 2026-II**

## 1. Vía API no utilizada
Por indicación del docente en clase, la Unidad II no exige la vía API. El trabajo usa solo la vía 2
(descarga programática de archivos oficiales de la SBS y del INEI).
Constancia escrita en ADESA o en el grupo del curso: **completar con fecha y enlace o captura**.

## 2. No se encontró el crédito mype por departamento con frecuencia mensual
El temario indica como fuente "SBS: créditos directos por tipo y departamento". Al revisar el portal de la SBS:

| Reporte revisado | Qué contiene | Por qué no sirve para el panel |
|---|---|---|
| B-2349, Estructura de los Créditos Directos por Departamento (banca múltiple) | Porcentaje de cada banco por departamento, todos los tipos de crédito juntos | No separa microempresa ni pequeña empresa |
| Créditos Directos y Depósitos por Oficina (cajas municipales, cajas rurales, financieras) | Crédito total y depósitos por oficina | No separa por tipo de crédito, pero sí es mensual y por departamento |
| CIIF-0001, Reporte de Indicadores de Inclusión Financiera | Indicadores MYPE por departamento | Es semestral y en PDF con gráficos |
| Series Estadísticas (aplicativo web de la SBS) | Crédito por tipo y crédito por zona geográfica, por separado | La descarga exige escribir un captcha, por lo que no puede automatizarse |

**Decisión:** aproximar el crédito mype con el crédito directo de las entidades microfinancieras
(cajas municipales, cajas rurales, empresas financieras y empresas de créditos), que son las entidades
especializadas en microfinanzas. La aproximación se declara en el artículo.
Confirmación del docente: **pendiente**.

## 3. Variables del temario que no se incluyeron
- **Tasa mype:** el BCRP la publica a nivel nacional, no por departamento, y su fuente es una API (vía 1).
- **Número de deudores:** solo disponible de forma semestral y en PDF con gráficos (CIIF-0001).
- **Morosidad:** no se encontró por departamento y por mes en fuentes oficiales descargables.

**Variable añadida:** depósitos por departamento (SBS), medidos en los mismos archivos que el crédito.
Confirmación del docente: **pendiente**.

## 4. Cobertura de datos
- **Periodo:** enero de 2017 a diciembre de 2024 (96 meses). El PBI departamental del INEI llega solo hasta 2024.
- **Empresas de créditos:** no publican depósitos; la variable de depósitos cubre las otras tres entidades.
- **PBI y población:** anuales, repetidos en los 12 meses de cada año.

## 5. Ética de rastreo
- Solo información pública, sin datos personales (Ley N.º 29733).
- Pausa de 1 segundo entre solicitudes y User-Agent identificable en `02_scraping_web.py`.
