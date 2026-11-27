# Nombres y apellidos: Chancha Santiago Alex Omar
# Código de matrícula: 2024200492K
# Tema N.º 88: Restricción financiera y acceso al crédito de la micro y pequeña empresa peruana
# Fecha de extracción: 2026-11-25  (datos de /datos_procesados)

# 04_analisis.py
# Genera TODAS las tablas y figuras del artículo a partir del panel procesado.
# Salidas en /salidas:
#   tabla_01_descriptivos.csv      tabla_02_correlaciones.csv     tabla_03_ranking_departamentos.csv
#   tabla_04_dispersion_anual.csv  tabla_05_modelos_panel.csv
#   fig_01_evolucion_nacional.png  fig_02_lima_vs_resto.png       fig_03_credito_per_capita_2024.png
#   fig_04_dispersion.png          fig_05_coeficientes.png

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

# ---------------------------------------------------------------------------
# 1. PARÁMETROS
# ---------------------------------------------------------------------------
CODIGO_MATRICULA = "2024200492K"
SEMILLA = 492            # cuatro últimos dígitos de la matrícula (0492); el análisis no usa azar
np.random.seed(SEMILLA)

def obtener_directorio_base():
    try:
        dir_actual = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        dir_actual = os.getcwd()
    if os.path.basename(dir_actual).lower() == "codigo":
        return os.path.dirname(dir_actual)
    return dir_actual

DIR_BASE = obtener_directorio_base()
RUTA_DATOS = os.path.join(DIR_BASE, "datos_procesados", f"datos_procesados_{CODIGO_MATRICULA}.csv")
DIR_SAL = os.path.join(DIR_BASE, "salidas")
os.makedirs(DIR_SAL, exist_ok=True)

plt.rcParams.update({"figure.dpi": 120, "savefig.dpi": 200, "axes.grid": True,
                     "grid.alpha": 0.3, "axes.spines.top": False, "axes.spines.right": False})

def guardar_fig(nombre):
    plt.tight_layout()
    plt.savefig(os.path.join(DIR_SAL, nombre), bbox_inches="tight")
    plt.close()

# ---------------------------------------------------------------------------
# 2. CARGA Y VARIABLES
# ---------------------------------------------------------------------------
df = pd.read_csv(RUTA_DATOS, dtype={"ubigeo": str})
df["fecha_dt"] = pd.to_datetime(df["fecha"] + "-01")
df["anio"] = df["fecha_dt"].dt.year

# Logaritmos (el panel no tiene ceros ni faltantes)
df["ln_credito"] = np.log(df["credito_miles_soles"])
df["ln_depositos"] = np.log(df["depositos_miles_soles"])
df["ln_pbi"] = np.log(df["pbi_miles_soles_2007"])
df["ln_poblacion"] = np.log(df["poblacion"])

# Variables per cápita (soles por habitante) para el modelo de robustez
df["depositos_pc"] = df["depositos_miles_soles"] * 1000 / df["poblacion"]
df["pbi_pc"] = df["pbi_miles_soles_2007"] * 1000 / df["poblacion"]
df["ln_credito_pc"] = np.log(df["credito_per_capita_soles"])
df["ln_depositos_pc"] = np.log(df["depositos_pc"])
df["ln_pbi_pc"] = np.log(df["pbi_pc"])

print(f"Panel: {len(df)} observaciones | {df['ubigeo'].nunique()} departamentos | "
      f"{df['fecha'].nunique()} meses ({df['fecha'].min()} a {df['fecha'].max()})")

# ---------------------------------------------------------------------------
# 3. TABLA 1: ESTADÍSTICOS DESCRIPTIVOS
# ---------------------------------------------------------------------------
VARS = ["credito_miles_soles", "depositos_miles_soles", "pbi_miles_soles_2007",
        "poblacion", "credito_per_capita_soles"]
desc = df[VARS].agg(["count", "mean", "std", "min", "median", "max"]).T.round(2)
desc.to_csv(os.path.join(DIR_SAL, "tabla_01_descriptivos.csv"), encoding="utf-8-sig")

# ---------------------------------------------------------------------------
# 4. TABLA 2: CORRELACIONES (en logaritmos)
# ---------------------------------------------------------------------------
corr = df[["ln_credito", "ln_depositos", "ln_pbi", "ln_poblacion"]].corr().round(3)
corr.to_csv(os.path.join(DIR_SAL, "tabla_02_correlaciones.csv"), encoding="utf-8-sig")

# ---------------------------------------------------------------------------
# 5. TABLA 3: RANKING Y CRECIMIENTO POR DEPARTAMENTO
# ---------------------------------------------------------------------------
f0, f1 = df["fecha"].min(), df["fecha"].max()
a = df[df["fecha"] == f0].set_index("departamento")
b = df[df["fecha"] == f1].set_index("departamento")
anios = (df["fecha_dt"].max() - df["fecha_dt"].min()).days / 365.25
rank = pd.DataFrame({
    "credito_inicial_miles": a["credito_miles_soles"],
    "credito_final_miles": b["credito_miles_soles"],
    "crecimiento_total_pct": ((b["credito_miles_soles"] / a["credito_miles_soles"] - 1) * 100),
    "crecimiento_anual_pct": ((b["credito_miles_soles"] / a["credito_miles_soles"]) ** (1 / anios) - 1) * 100,
    "credito_per_capita_final": b["credito_per_capita_soles"],
}).round(2).sort_values("credito_per_capita_final", ascending=False)
rank["puesto_per_capita"] = range(1, len(rank) + 1)
rank.to_csv(os.path.join(DIR_SAL, "tabla_03_ranking_departamentos.csv"), encoding="utf-8-sig")

# ---------------------------------------------------------------------------
# 6. TABLA 4: DISPERSIÓN ANUAL DEL CRÉDITO PER CÁPITA (coef. de variación entre departamentos)
# ---------------------------------------------------------------------------
disp = (df.groupby(["anio", "ubigeo"])["credito_per_capita_soles"].mean().groupby("anio")
          .agg(media="mean", desviacion="std")
          .assign(coef_variacion=lambda x: x["desviacion"] / x["media"]).round(4))
disp.to_csv(os.path.join(DIR_SAL, "tabla_04_dispersion_anual.csv"), encoding="utf-8-sig")

# ---------------------------------------------------------------------------
# 7. FIGURAS 1 A 4
# ---------------------------------------------------------------------------
# Fig. 1: evolución nacional del crédito y de los depósitos
nac = df.groupby("fecha_dt")[["credito_miles_soles", "depositos_miles_soles"]].sum() / 1e6
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(nac.index, nac["credito_miles_soles"], label="Crédito", lw=2)
ax.plot(nac.index, nac["depositos_miles_soles"], label="Depósitos", lw=2)
ax.set_ylabel("Miles de millones de soles")
ax.set_title("Crédito y depósitos de las entidades microfinancieras, 2017-2024")
ax.legend()
guardar_fig("fig_01_evolucion_nacional.png")

# Fig. 2: Lima frente al resto (índice, enero 2017 = 100)
df["es_lima"] = np.where(df["ubigeo"] == "15", "Lima", "Resto del país")
g = df.groupby(["fecha_dt", "es_lima"])["credito_miles_soles"].sum().unstack()
g = g / g.iloc[0] * 100
fig, ax = plt.subplots(figsize=(8, 4.2))
g.plot(ax=ax, lw=2)
ax.set_ylabel("Índice (enero 2017 = 100)")
ax.set_xlabel("")
ax.set_title("Crecimiento del crédito: Lima y resto del país")
guardar_fig("fig_02_lima_vs_resto.png")

# Fig. 3: crédito per cápita por departamento, último mes
orden = rank["credito_per_capita_final"].sort_values()
fig, ax = plt.subplots(figsize=(7, 7))
ax.barh(orden.index, orden.values)
ax.set_xlabel("Soles por habitante")
ax.set_title(f"Crédito microfinanciero per cápita por departamento ({f1})")
ax.grid(axis="y", alpha=0)
guardar_fig("fig_03_credito_per_capita_2024.png")

# Fig. 4: dispersión (coeficiente de variación) del crédito per cápita
fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(disp.index, disp["coef_variacion"], marker="o", lw=2)
ax.set_ylabel("Coeficiente de variación")
ax.set_title("Dispersión del crédito per cápita entre departamentos")
guardar_fig("fig_04_dispersion.png")

# ---------------------------------------------------------------------------
# 8. MODELOS DE PANEL (errores estándar agrupados por departamento)
# ---------------------------------------------------------------------------
def estimar(formula, datos, nombre):
    m = smf.ols(formula, data=datos).fit(cov_type="cluster", cov_kwds={"groups": datos["ubigeo"]})
    print(f"{nombre}: N = {int(m.nobs)} | R2 = {m.rsquared:.3f}")
    return m

BASE = "ln_credito ~ ln_depositos + ln_pbi + ln_poblacion"
modelos = {
    "(1) MCO agrupado": estimar(BASE, df, "(1)"),
    "(2) EF departamento": estimar(BASE + " + C(ubigeo)", df, "(2)"),
    "(3) EF depto. y mes": estimar(BASE + " + C(ubigeo) + C(fecha)", df, "(3)"),
    "(4) Sin Lima": estimar(BASE + " + C(ubigeo) + C(fecha)", df[df["ubigeo"] != "15"], "(4)"),
    "(5) Per cápita": estimar("ln_credito_pc ~ ln_depositos_pc + ln_pbi_pc + C(ubigeo) + C(fecha)", df, "(5)"),
}

def estrellas(p):
    return "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.10 else ""

NOMBRES_VAR = {"ln_depositos": "ln(Depósitos)", "ln_pbi": "ln(PBI departamental)",
               "ln_poblacion": "ln(Población)", "ln_depositos_pc": "ln(Depósitos per cápita)",
               "ln_pbi_pc": "ln(PBI per cápita)"}
filas = []
for var, etiqueta in NOMBRES_VAR.items():
    fila_c, fila_e = {"Variable": etiqueta}, {"Variable": ""}
    for nom, m in modelos.items():
        if var in m.params.index:
            fila_c[nom] = f"{m.params[var]:.3f}{estrellas(m.pvalues[var])}"
            fila_e[nom] = f"({m.bse[var]:.3f})"
        else:
            fila_c[nom], fila_e[nom] = "", ""
    filas += [fila_c, fila_e]
filas.append({"Variable": "Observaciones", **{n: int(m.nobs) for n, m in modelos.items()}})
filas.append({"Variable": "R2", **{n: round(m.rsquared, 3) for n, m in modelos.items()}})
filas.append({"Variable": "EF departamento", **{n: ("Sí" if "ubigeo" in m.model.formula else "No") for n, m in modelos.items()}})
filas.append({"Variable": "EF mes", **{n: ("Sí" if "fecha" in m.model.formula else "No") for n, m in modelos.items()}})
tabla_modelos = pd.DataFrame(filas)
tabla_modelos.to_csv(os.path.join(DIR_SAL, "tabla_05_modelos_panel.csv"), index=False, encoding="utf-8-sig")

# Fig. 5: coeficientes del modelo (3) con intervalo de confianza al 95 %
m3 = modelos["(3) EF depto. y mes"]
vars3 = ["ln_depositos", "ln_pbi", "ln_poblacion"]
ic = m3.conf_int().loc[vars3]
fig, ax = plt.subplots(figsize=(6.5, 3.5))
ax.errorbar(m3.params[vars3], range(len(vars3)),
            xerr=[m3.params[vars3] - ic[0], ic[1] - m3.params[vars3]], fmt="o", capsize=4)
ax.axvline(0, color="gray", lw=1)
ax.set_yticks(range(len(vars3)))
ax.set_yticklabels([NOMBRES_VAR[v] for v in vars3])
ax.set_xlabel("Coeficiente (elasticidad) e IC 95 %")
ax.set_title("Determinantes del crédito: modelo (3), EF de departamento y mes")
guardar_fig("fig_05_coeficientes.png")

print("\n=== TABLA DE MODELOS ===")
print(tabla_modelos.to_string(index=False))
print("\nListo: tablas y figuras guardadas en", DIR_SAL)

# ---------------------------------------------------------------------------
# 9. ANIMACIONES (GIF) PARA LA EXPOSICIÓN
#    anim_01_depositos_vs_credito.gif : cada burbuja es un departamento; recorre los 96 meses
#    anim_02_ranking_credito_pc.gif   : ranking del crédito per cápita mes a mes
#    Poner GENERAR_ANIMACIONES = False si solo se quieren tablas y figuras (es más rápido).
# ---------------------------------------------------------------------------
GENERAR_ANIMACIONES = True
FPS = 8

if GENERAR_ANIMACIONES:
    from matplotlib.animation import FuncAnimation, PillowWriter
    meses = sorted(df["fecha"].unique())
    por_mes = {m: d.set_index("departamento") for m, d in df.groupby("fecha")}
    deptos = sorted(df["departamento"].unique())
    lim_x = (df["depositos_pc"].min() * 0.85, df["depositos_pc"].max() * 1.15)
    lim_y = (df["credito_per_capita_soles"].min() * 0.85, df["credito_per_capita_soles"].max() * 1.15)

    # --- Animación 1: depósitos per cápita (x) vs crédito per cápita (y), tamaño = población
    fig, ax = plt.subplots(figsize=(8.5, 6))
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlim(lim_x); ax.set_ylim(lim_y)
    ax.set_xlabel("Depósitos per cápita (soles por habitante, escala log)")
    ax.set_ylabel("Crédito per cápita (soles por habitante, escala log)")
    ax.set_title("Depósitos y crédito microfinanciero por departamento")
    reloj = ax.text(0.97, 0.05, "", transform=ax.transAxes, ha="right", fontsize=26,
                    color="gray", alpha=0.6)
    d0 = por_mes[meses[0]].loc[deptos]
    puntos = ax.scatter(d0["depositos_pc"], d0["credito_per_capita_soles"],
                        s=d0["poblacion"] / 12000, alpha=0.6, edgecolor="k")
    etiquetas = [ax.text(0, 0, d, fontsize=7) for d in deptos]

    def actualizar_1(i):
        d = por_mes[meses[i]].loc[deptos]
        puntos.set_offsets(np.c_[d["depositos_pc"], d["credito_per_capita_soles"]])
        puntos.set_sizes(d["poblacion"] / 12000)
        for t, (_, fila) in zip(etiquetas, d.iterrows()):
            t.set_position((fila["depositos_pc"] * 1.02, fila["credito_per_capita_soles"] * 1.02))
        reloj.set_text(meses[i])
        return [puntos, reloj] + etiquetas

    FuncAnimation(fig, actualizar_1, frames=len(meses), blit=False).save(
        os.path.join(DIR_SAL, "anim_01_depositos_vs_credito.gif"), writer=PillowWriter(fps=FPS))
    plt.close(fig)

    # --- Animación 2: ranking del crédito per cápita
    fig, ax = plt.subplots(figsize=(7.5, 8))
    maximo = df["credito_per_capita_soles"].max() * 1.08

    def actualizar_2(i):
        ax.clear()
        d = por_mes[meses[i]]["credito_per_capita_soles"].sort_values()
        colores = ["tab:red" if n == "Junín" else "tab:blue" for n in d.index]   # resalta Junín
        ax.barh(d.index, d.values, color=colores)
        ax.set_xlim(0, maximo)
        ax.set_xlabel("Soles por habitante")
        ax.set_title("Crédito microfinanciero per cápita por departamento")
        ax.text(0.97, 0.05, meses[i], transform=ax.transAxes, ha="right", fontsize=26, color="gray", alpha=0.6)
        ax.grid(axis="y", alpha=0)

    FuncAnimation(fig, actualizar_2, frames=len(meses), blit=False).save(
        os.path.join(DIR_SAL, "anim_02_ranking_credito_pc.gif"), writer=PillowWriter(fps=FPS))
    plt.close(fig)
    print("Animaciones guardadas en", DIR_SAL)