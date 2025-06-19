"""
Frontend GUI for UIP + PPP Exchange Rate Simulation
Tkinter interface for the exchange rate simulation engine
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
import sys

# Import the simulation engine
from simulation_engine import ExchangeRateSimulator

# Global variables
simulator = ExchangeRateSimulator()
df_resultados = None
distribuciones = {}
current_params = None  # Track current parameters
current_view = 'impacto'  # Track current view: 'impacto', 'dispersión', 'estadisticas'

def get_current_params():
    """Get current parameters from GUI"""
    return {
        'S_t': float(entry_S.get()),
        'theta': float(entry_theta.get()),
        'n_sim': int(entry_nsim.get()),
        'i_dom_range': (float(entry_idom_min.get()), float(entry_idom_max.get())),
        'i_for_range': (float(entry_ifor_min.get()), float(entry_ifor_max.get())),
        'pi_dom_range': (float(entry_pidom_min.get()), float(entry_pidom_max.get())),
        'pi_for_range': (float(entry_pifor_min.get()), float(entry_pifor_max.get())),
        'sesgo': var_sesgo.get()
    }

def params_changed():
    """Check if parameters have changed since last simulation"""
    global current_params
    new_params = get_current_params()
    
    if current_params is None:
        current_params = new_params
        return True
    
    if new_params != current_params:
        current_params = new_params
        return True
    
    return False

def ejecutar_simulacion():
    """Execute simulation using the backend engine"""
    global df_resultados, distribuciones
    
    # Get parameters from GUI
    params = get_current_params()
    S_t = params['S_t']
    theta = params['theta']
    n_sim = params['n_sim']
    i_dom_range = params['i_dom_range']
    i_for_range = params['i_for_range']
    pi_dom_range = params['pi_dom_range']
    pi_for_range = params['pi_for_range']
    sesgo = params['sesgo']
    skew_params = {'loc': np.mean(i_dom_range), 'scale': 0.012, 'skew': 6}

    # Run simulation using backend
    df_resultados, distribuciones = simulator.simulate_news_impact(
        S_t, theta, n_sim,
        i_dom_range, i_for_range,
        pi_dom_range, pi_for_range,
        sesgo_tasa_dom=sesgo,
        skew_params=skew_params
    )
    
    mostrar_curva_impacto()

def mostrar_curva_impacto():
    """Display impact curve chart"""
    global current_view
    current_view = 'impacto'
    
    if df_resultados is None or params_changed():
        ejecutar_simulacion()
        
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(df_resultados))
    ax.errorbar(x, df_resultados['Media'], 
                yerr=[df_resultados['Media'] - df_resultados['P5'], 
                      df_resultados['P95'] - df_resultados['Media']],
                fmt='o', capsize=5)
    ax.set_xticks(x)
    ax.set_xticklabels(df_resultados['Escenario'], rotation=45, ha='right')
    ax.set_title("Curva de Impacto de Noticias en Tipo de Cambio")
    ax.set_ylabel("COP/USD")
    ax.grid(True)
    for label in ax.get_xticklabels():
        label.set_rotation(0)
        label.set_ha('center')

    actualizar_grafico(fig)

def mostrar_dispersión():
    """Display distribution histogram"""
    global current_view
    current_view = 'dispersión'
    
    if df_resultados is None or params_changed():
        ejecutar_simulacion()
        
    escenario = combo_escenario.get()
    datos = distribuciones.get(escenario, [])
    
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.hist(datos, bins=60, color='skyblue', edgecolor='black', alpha=0.7)
    ax.set_title(f"Distribución Esperada - {escenario}")
    ax.set_xlabel("COP/USD")
    ax.set_ylabel("Frecuencia")
    ax.grid(True, alpha=0.3)
    for label in ax.get_xticklabels():
        label.set_rotation(0)
        label.set_ha('center')
    
    # Add percentiles to the plot
    mean_val = np.mean(datos)
    p1_negative_val = np.percentile(datos, 1)
    p5_negative_val = np.percentile(datos, 5)
    p1_positive_val = np.percentile(datos, 99)
    p5_positive_val = np.percentile(datos, 95)
    ax.axvline(mean_val, color='red', linestyle='--', label=f'Media: {mean_val:.2f}')
    ax.axvline(p1_negative_val, color='darkgreen', linestyle='-', linewidth=2, label=f'P1: {p1_negative_val:.2f}')
    ax.axvline(p5_negative_val, color='orange', linestyle='-', linewidth=2, label=f'P5: {p5_negative_val:.2f}')
    ax.axvline(p1_positive_val, color='darkgreen', linestyle='-', linewidth=2, label=f'P99: {p1_positive_val:.2f}')
    ax.axvline(p5_positive_val, color='orange', linestyle='-', linewidth=2, label=f'P95: {p5_positive_val:.2f}')
    ax.legend()
    
    actualizar_grafico(fig)

def mostrar_resumen_completo():
    """Display comprehensive summary with forward rates and VaR"""
    global current_view
    current_view = 'resumen'
    
    if df_resultados is None or params_changed():
        ejecutar_simulacion()
    
    # Get current parameters
    params = get_current_params()
    S_t = params['S_t']
    i_dom = np.mean(params['i_dom_range'])  # Use mean of range
    i_for = np.mean(params['i_for_range'])  # Use mean of range
    
    escenario = combo_escenario.get()
    
    # Get comprehensive summary
    resumen = simulator.get_scenario_summary(escenario, S_t, i_dom, i_for)
    
    if resumen is None:
        return
    
    # Create a new window for comprehensive summary
    summary_window = tk.Toplevel(root)
    summary_window.title(f"Resumen Completo - {escenario}")
    summary_window.geometry("500x400")
    
    # Create text widget to display summary
    text_widget = tk.Text(summary_window, wrap=tk.WORD, padx=10, pady=10, font=("Courier", 10))
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Format and display comprehensive summary
    summary_text = f"RESUMEN COMPLETO - {escenario.upper()}\n"
    summary_text += "=" * 50 + "\n\n"
    summary_text += f"Media: {resumen['Media']:,.2f}\n"
    summary_text += f"P1: {resumen['P1']:,.2f}\n"
    summary_text += f"P5: {resumen['P5']:,.2f}\n"
    summary_text += f"P50: {resumen['P50']:,.2f}\n"
    summary_text += f"P95: {resumen['P95']:,.2f}\n"
    summary_text += f"P99: {resumen['P99']:,.2f}\n"
    summary_text += f"VaR_5pct_COP: {resumen['VaR_5pct_COP']:,.2f}\n"
    summary_text += f"VaR_1pct_COP: {resumen['VaR_1pct_COP']:,.2f}\n"
    summary_text += f"Forward implícito: {resumen['Forward_implicito']:,.2f}\n"
    
    text_widget.insert(tk.END, summary_text)
    text_widget.config(state=tk.DISABLED)

def evaluar_forward():
    """Evaluate forward contract against CIP and UIP+PPP model"""
    global current_view
    current_view = 'evaluacion'
    
    if df_resultados is None or params_changed():
        ejecutar_simulacion()
    
    # Get current parameters
    params = get_current_params()
    S_t = params['S_t']
    i_dom = np.mean(params['i_dom_range'])
    i_for = np.mean(params['i_for_range'])
    
    # Get offered forward price
    try:
        forward_ofrecido = float(entry_forward.get())
    except ValueError:
        messagebox.showerror("Error", "Por favor ingrese un precio forward válido")
        return
    
    escenario = combo_escenario.get()
    
    # Get comprehensive summary
    resumen = simulator.get_scenario_summary(escenario, S_t, i_dom, i_for)
    
    if resumen is None:
        return
    
    # Get key values
    cip_forward = resumen['Forward_implicito']
    spot_esperado = resumen['Media']
    p5 = resumen['P5']
    p95 = resumen['P95']
    
    # Create evaluation window
    eval_window = tk.Toplevel(root)
    eval_window.title(f"Evaluación Forward - {escenario}")
    eval_window.geometry("700x600")
    
    # Create text widget
    text_widget = tk.Text(eval_window, wrap=tk.WORD, padx=15, pady=15, font=("Arial", 10))
    text_widget.pack(fill=tk.BOTH, expand=True)
    
    # Build evaluation text
    eval_text = f"EVALUACIÓN DE CONTRATO FORWARD\n"
    eval_text += "=" * 50 + "\n"
    
    # Current parameters
    eval_text += f"ESCENARIO: {escenario}\n"
    eval_text += f"Spot actual: {S_t:,.2f} COP/USD\n"
    eval_text += f"Forward ofrecido: {forward_ofrecido:,.2f} COP/USD\n\n"
    
    # CIP Analysis
    eval_text += "📊 ANÁLISIS CIP (PARIDAD CUBIERTA)\n"
    eval_text += "-" * 40 + "\n"
    eval_text += f"Forward CIP implícito: {cip_forward:,.2f} COP/USD\n"
    
    if forward_ofrecido <= cip_forward:
        eval_text += "✅ Forward ≤ CIP: CONTRATO JUSTO O FAVORABLE\n"
        cip_favorable = True
    else:
        eval_text += "❌ Forward > CIP: POSIBLE SOBREPRECIO\n"
        cip_favorable = False
    
    eval_text += f"Diferencia: {forward_ofrecido - cip_forward:+,.2f} COP/USD\n\n"
    
    # UIP+PPP Analysis
    eval_text += "📈 ANÁLISIS UIP + PPP (SPOT ESPERADO)\n"
    eval_text += "=" * 50 + "\n"
    eval_text += f"Spot esperado (media): {spot_esperado:,.2f} COP/USD\n"
    eval_text += f"P5: {p5:,.2f} COP/USD\n"
    eval_text += f"P95: {p95:,.2f} COP/USD\n"
    
    # Protection analysis
    if forward_ofrecido < spot_esperado:
        eval_text += "✅ Forward < spot esperado: TE PROTEGE\n"
        protege = True
    else:
        eval_text += "❌ Forward ≥ spot esperado: NO TE PROTEGE\n"
        protege = False
    
    # Uncertainty reduction analysis
    if p5 <= forward_ofrecido <= p95:
        eval_text += "✅ Dentro P5-P95: REDUCE INCERTIDUMBRE RAZONABLEMENTE\n"
        incertidumbre_ok = True
    elif forward_ofrecido > p95:
        eval_text += "⚠️ Mayor que P95: PROBABLEMENTE PAGAS DE MÁS\n"
        incertidumbre_ok = False
    else:
        eval_text += "✅ Menor que P5: MUY CONSERVADOR\n"
        incertidumbre_ok = True
    
    eval_text += f"Diferencia vs spot esperado: {forward_ofrecido - spot_esperado:+,.2f} COP/USD\n\n"
    
    # Final recommendation
    eval_text += "🎯 RECOMENDACIÓN FINAL\n"
    eval_text += "=" * 30 + "\n\n"
    
    # Decision logic
    acepta_condicion1 = forward_ofrecido <= cip_forward
    acepta_condicion2 = forward_ofrecido < spot_esperado
    
    if acepta_condicion1 or acepta_condicion2:
        eval_text += "✅ ACEPTA EL CONTRATO\n\n"
        eval_text += "Razones:\n"
        if acepta_condicion1:
            eval_text += "• Forward ≤ CIP (paridad cubierta)\n"
        if acepta_condicion2:
            eval_text += "• Forward < spot esperado (protección)\n"
    else:
        eval_text += "⚠️ NEGOCIA O RECHAZA\n\n"
        eval_text += "Razones:\n"
        eval_text += "• Forward > CIP (sobreprecio)\n"
        eval_text += "• Forward > spot esperado (sin protección)\n"
    
    eval_text += "\n" + "=" * 50 + "\n"
    eval_text += "Nota: Esta evaluación se basa en el modelo UIP+PPP y paridad cubierta de tasas de interés (CIP)."
    
    # Insert text and configure
    text_widget.insert(tk.END, eval_text)
    text_widget.config(state=tk.DISABLED)
    
    # Add scrollbar
    scrollbar = ttk.Scrollbar(eval_window, orient="vertical", command=text_widget.yview)
    scrollbar.pack(side="right", fill="y")
    text_widget.configure(yscrollcommand=scrollbar.set)

def actualizar_grafico(fig):
    """Update the plot in the GUI"""
    for widget in frame_plot.winfo_children():
        widget.destroy()
    canvas = FigureCanvasTkAgg(fig, master=frame_plot)
    canvas.draw()
    canvas.get_tk_widget().pack()

def on_closing():
    """Handle window closing properly"""
    plt.close('all')  # Close all matplotlib figures
    root.quit()       # Quit the mainloop
    root.destroy()    # Destroy the window
    sys.exit(0)       # Exit the program

# Create main window
root = tk.Tk()
root.title("Simulación UIP + PPP con Impacto de Noticias")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create frames
frame_inputs = ttk.Frame(root)
frame_inputs.pack(padx=10, pady=5)

frame_plot = ttk.Frame(root)
frame_plot.pack(padx=10, pady=10)

# Create input fields
labels = [
    ("TRM (spot)", "4000"), ("theta", "0.6"), ("# Simulaciones", "100000"),
    ("i Minimo Colombiano", "0.08"), ("i Maximo Colombiano", "0.11"),
    ("i Minimo Extranjero", "0.045"), ("i Maximo Extranjero", "0.055"),
    ("Inflacion Minimo Colombiano", "0.07"), ("Inflacion Maximo Colombiano", "0.09"),
    ("Inflacion Minimo Extranjero", "0.025"), ("Inflacion Maximo Extranjero", "0.035")
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

# Create controls
var_sesgo = tk.BooleanVar(value=True)
ttk.Checkbutton(frame_inputs, text="Sesgo en tasa doméstica", 
                variable=var_sesgo).grid(row=6, column=0, columnspan=2)

# Forward price input
ttk.Label(frame_inputs, text="Forward Price (COP/USD):", 
          font=("Arial", 10, "bold")).grid(row=6, column=2, columnspan=2, pady=(5,0))
entry_forward = ttk.Entry(frame_inputs, font=("Arial", 10, "bold"))
entry_forward.insert(0, "4000")
entry_forward.grid(row=7, column=2, columnspan=2, pady=(0,5))

# Scenario selector and buttons
combo_escenario = ttk.Combobox(frame_inputs, 
                               values=["Normal", "Subida tasas BanRep", 
                                      "Desanclaje inflacionario", "Choque externo"])
combo_escenario.set("Normal")
combo_escenario.grid(row=8, column=0, columnspan=2)

ttk.Button(frame_inputs, text="Ver curva impacto", 
           command=mostrar_curva_impacto).grid(row=8, column=2)
ttk.Button(frame_inputs, text="Ver dispersión", 
           command=mostrar_dispersión).grid(row=8, column=3)
ttk.Button(frame_inputs, text="Ver resumen completo", 
           command=mostrar_resumen_completo).grid(row=9, column=2, columnspan=2)
ttk.Button(frame_inputs, text="Evaluar Forward", 
           command=evaluar_forward).grid(row=10, column=2, columnspan=2)

# Auto-execute simulation on startup
root.after(100, mostrar_curva_impacto)

root.mainloop()