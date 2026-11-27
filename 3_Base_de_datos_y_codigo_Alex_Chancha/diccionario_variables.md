# Diccionario de variables

**Archivo:** `datos_procesados/datos_procesados_2024200492K.csv` (2 400 filas, 8 columnas)
**Autor:** Chancha Santiago Alex Omar (2024200492K)

| Variable | Definición | Unidad | Frecuencia | Fuente exacta | URL o endpoint |
|---|---|---|---|---|---|
| `ubigeo` | Código INEI del departamento (01 a 25). Callao = 07, Lima = 15 | texto (2 dígitos) | - | INEI | https://www.inei.gob.pe |
| `departamento` | Nombre del departamento | texto | - | INEI (codificación) | - |
| `fecha` | Mes de la observación | AAAA-MM | Mensual | SBS | https://intranet2.sbs.gob.pe/estadistica/financiera/ |
| `credito_miles_soles` | Créditos directos de las entidades microfinancieras en el departamento. **Variable endógena** (aproximación al crédito mype) | miles de S/ | Mensual | SBS: reportes C-1234, C-2234, B-3241 y C-4228 | https://intranet2.sbs.gob.pe/estadistica/financiera/{año}/{Mes}/{código}-{mes}{año}.XLS |
| `depositos_miles_soles` | Depósitos totales captados por cajas municipales, cajas rurales y empresas financieras (sin empresas de créditos) | miles de S/ | Mensual | SBS: reportes C-1234, C-2234 y B-3241 | Íd. |
| `pbi_miles_soles_2007` | PBI departamental (valor agregado bruto), a precios constantes de 2007. 2022 a 2024 preliminar | miles de S/ de 2007 | Anual, repetido en los 12 meses | INEI, Perú: PBI por Departamentos 2007-2024, Cuadro N.º 1 | https://cdn.www.gob.pe/uploads/document/file/9219775/7567597-peru-producto-bruto-interno-por-departamentos-2007-2024.pdf?v=1771442357 |
| `poblacion` | Población total al 30 de junio. Estimaciones y proyecciones | habitantes | Anual, repetido en los 12 meses | INEI, Boletín de Análisis Demográfico N.º 39, Cuadro 3.68 | https://www.inei.gob.pe/media/MenuRecursivo/publicaciones_digitales/Est/Lib1702/libro.pdf |
| `credito_per_capita_soles` | Variable derivada: `credito_miles_soles * 1000 / poblacion` | S/ por habitante | Mensual | Cálculo propio (SBS e INEI) | - |

## Rol en el modelo
- **Endógena:** `credito_miles_soles`.
- **Exógenas:** `depositos_miles_soles`, `pbi_miles_soles_2007`, `poblacion`.
- **Derivada:** `credito_per_capita_soles`.

## Tratamiento de datos
- No se imputan datos. Si un departamento no tiene oficinas de una entidad en un mes, su crédito se toma como 0.
- Lima (15) = Región Lima + Provincia de Lima del INEI; el Callao (07) se toma por separado.
