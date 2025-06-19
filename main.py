# Versión adaptada para alternar entre la curva de impacto y el histograma de dispersión de un escenario

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

from scipy.stats import skewnorm
import pandas as pd

# Simulación principal
def simular_tipo_cambio_uip_ppp(S_t, theta, n_sim,
                                i_dom_range, i_for_range,
                                pi_dom_range, pi_for_range,
                                sesgo_tasa_dom=False, skew_params=None):
    i_for = np.random.uniform(*i_for_range, n_sim)
    pi_dom = np.random.uniform(*pi_dom_range, n_sim)
    pi_for = np.random.uniform(*pi_for_range, n_sim)

    if sesgo_tasa_dom:
        if skew_params is None:
            skew_params = {'loc': np.mean(i_dom_range), 'scale': 0.01, 'skew': 5}
        i_dom = skewnorm.rvs(
            a=skew_params['skew'],
            loc=skew_params['loc'],
            scale=skew_params['scale'],
            size=n_sim
        )
    else:
        i_dom = np.random.uniform(*i_dom_range, n_sim)

    delta_e = theta * (i_dom - i_for) + (1 - theta) * (pi_dom - pi_for)
    return S_t * (1 + delta_e)

# Impacto de escenarios
def simular_impacto_noticias(S_t, theta, n_sim,
                              i_dom_range, i_for_range,
                              pi_dom_range, pi_for_range,
                              sesgo_tasa_dom=False, skew_params=None):

    scenarios = {
        'Normal': {},
        'Subida tasas BanRep': {'i_dom_shift': 0.015},
        'Desanclaje inflacionario': {'pi_dom_shift': 0.02},
        'Choque externo': {'i_for_shift': -0.01, 'pi_for_shift': -0.005},
    }

    results = []
    distribuciones = {}
    for name, shifts in scenarios.items():
        i_dom_r = (i_dom_range[0] + shifts.get('i_dom_shift', 0),
                   i_dom_range[1] + shifts.get('i_dom_shift', 0))
        i_for_r = (i_for_range[0] + shifts.get('i_for_shift', 0),
                   i_for_range[1] + shifts.get('i_for_shift', 0))
        pi_dom_r = (pi_dom_range[0] + shifts.get('pi_dom_shift', 0),
                    pi_dom_range[1] + shifts.get('pi_dom_shift', 0))
        pi_for_r = (pi_for_range[0] + shifts.get('pi_for_shift', 0),
                    pi_for_range[1] + shifts.get('pi_for_shift', 0))

        sims = simular_tipo_cambio_uip_ppp(S_t, theta, n_sim,
                                           i_dom_r, i_for_r,
                                           pi_dom_r, pi_for_r,
                                           sesgo_tasa_dom, skew_params)

        distribuciones[name] = sims
        results.append({
            'Escenario': name,
            'Media': np.mean(sims),
            'P5': np.percentile(sims, 5),
            'P95': np.percentile(sims, 95)
        })

    return pd.DataFrame(results), distribuciones

# Interfaz Tkinter
def ejecutar_simulacion():
    S_t = float(entry_S.get())
    theta = float(entry_theta.get())
    n_sim = int(entry_nsim.get())
    i_dom_range = (float(entry_idom_min.get()), float(entry_idom_max.get()))
    i_for_range = (float(entry_ifor_min.get()), float(entry_ifor_max.get()))
    pi_dom_range = (float(entry_pidom_min.get()), float(entry_pidom_max.get()))
    pi_for_range = (float(entry_pifor_min.get()), float(entry_pifor_max.get()))
    sesgo = var_sesgo.get()
    skew_params = {'loc': np.mean(i_dom_range), 'scale': 0.012, 'skew': 6}

    global df_resultados, distribuciones
    df_resultados, distribuciones = simular_impacto_noticias(
        S_t, theta, n_sim,
        i_dom_range, i_for_range,
        pi_dom_range, pi_for_range,
        sesgo_tasa_dom=sesgo,
        skew_params=skew_params
    )
    mostrar_curva_impacto()

def mostrar_curva_impacto():
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(df_resultados))
    ax.errorbar(x, df_resultados['Media'], yerr=[df_resultados['Media'] - df_resultados['P5'], df_resultados['P95'] - df_resultados['Media']],
                fmt='o', capsize=5)
    ax.set_xticks(x)
    ax.set_xticklabels(df_resultados['Escenario'], rotation=45, ha='right')
    ax.set_title("Curva de Impacto de Noticias en Tipo de Cambio")
    ax.set_ylabel("COP/USD")
    ax.grid(True)
    actualizar_grafico(fig)

def mostrar_dispersión():
    escenario = combo_escenario.get()
    datos = distribuciones.get(escenario, [])
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(datos, bins=60, color='skyblue', edgecolor='black')
    ax.set_title(f"Distribución Esperada - {escenario}")
    ax.set_xlabel("COP/USD")
    ax.set_ylabel("Frecuencia")
    ax.grid(True)
    actualizar_grafico(fig)

def actualizar_grafico(fig):
    for widget in frame_plot.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Crear ventana principal
root = tk.Tk()
root.title("Simulación UIP + PPP con Impacto de Noticias")

frame_inputs = ttk.Frame(root)
frame_inputs.pack(padx=10, pady=5)

frame_plot = ttk.Frame(root)
frame_plot.pack(padx=10, pady=10)

# Entradas
labels = [
    ("S_t (spot)", "4000"), ("theta", "0.6"), ("n_sim", "100000"),
    ("i_dom min", "0.08"), ("i_dom max", "0.11"),
    ("i_for min", "0.045"), ("i_for max", "0.055"),
    ("pi_dom min", "0.07"), ("pi_dom max", "0.09"),
    ("pi_for min", "0.025"), ("pi_for max", "0.035")
]
entries = []
for i, (label_text, default) in enumerate(labels):
    ttk.Label(frame_inputs, text=label_text).grid(row=i // 2, column=(i % 2) * 2)
    entry = ttk.Entry(frame_inputs)
    entry.insert(0, default)
    entry.grid(row=i // 2, column=(i % 2) * 2 + 1)
    entries.append(entry)

(
    entry_S, entry_theta, entry_nsim,
    entry_idom_min, entry_idom_max,
    entry_ifor_min, entry_ifor_max,
    entry_pidom_min, entry_pidom_max,
    entry_pifor_min, entry_pifor_max
) = entries

# Checkbox y botón
var_sesgo = tk.BooleanVar(value=True)
ttk.Checkbutton(frame_inputs, text="Sesgo en tasa doméstica", variable=var_sesgo).grid(row=6, column=0, columnspan=2)

# Combo y botones para alternar gráficos
combo_escenario = ttk.Combobox(frame_inputs, values=["Normal", "Subida tasas BanRep", "Desanclaje inflacionario", "Choque externo"])
combo_escenario.set("Normal")
combo_escenario.grid(row=7, column=0, columnspan=2)

ttk.Button(frame_inputs, text="Ver curva impacto", command=mostrar_curva_impacto).grid(row=7, column=2)
ttk.Button(frame_inputs, text="Ver dispersión", command=mostrar_dispersión).grid(row=7, column=3)

root.mainloop()
