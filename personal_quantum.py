
# app.py
import pennylane as qml
from pennylane import numpy as np
########################################################################
########################  CENSORED #####################################
########################################################################

# --- Quantum Setup ---
n_qubits = 2
dev = qml.device("default.qubit", wires=n_qubits)

@qml.qnode(dev, interface="torch")
########################################################################
########################  CENSORED #####################################
########################################################################

n_layers = 3
weight_shapes = {"weights": (n_layers, n_qubits, 3)}
qlayer = qml.qnn.TorchLayer(quantum_circuit, weight_shapes)
model_q = torch.nn.Sequential(qlayer)

# --- Classical Setup ---
class ClassicalBaseline(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(2, 4),
            nn.ReLU(),
 ########################################################################
########################  CENSORED #####################################
########################################################################

model_c = ClassicalBaseline()

# ==========================================
# 2. CARICAMENTO PESI E DATI
# ==========================================

########################################################################
########################  CENSORED #####################################
########################################################################


# ==========================================
# 3. LOGICA DI INFERENZA & CONFRONTO
# ==========================================

OUTLIER_THRESHOLD = 0.8 

def get_dynamic_background(n_samples, noise_level):
    """
    Genera dati sintetici al volo per simulare diversi scenari storici.
    """
    # Genera dati raw
    X, Y = sklearn.datasets.make_moons(n_samples=n_samples, noise=noise_level, random_state=42)
    
    # Scala i dati usando lo scaler originale (fondamentale per coerenza con i modelli)
    X_scaled = feature_scaler.transform(X)
    
    # Prepara label (-1, 1)
    Y_scaled = Y * 2 - np.ones(len(Y))
    
    # Converti in tensori
    X_t = torch.tensor(X_scaled).float()
   ########################################################################
########################  CENSORED #####################################
########################################################################

def generate_plot(input_scaled_coords, X_bg, y_bg, nearest_label, is_outlier=False):
    plt.figure(figsize=(6, 4))
    
    # Converti tensori in numpy per il plot
    X_np = X_bg.numpy()
    y_np = y_bg.numpy()
    
    # Plot Dati Simulati (Background)
    plt.scatter(X_np[y_np == -1][:, 0], X_np[y_np == -1][:, 1], c='green', alpha=0.3, s=15, label='Storici Simulati: Normali')
 ########################################################################
########################  CENSORED #####################################
########################################################################
        label_text = 'Input Utente'
        marker_style = '*'

    plt.scatter(input_scaled_coords[0][0], input_scaled_coords[0][1], 
                c=user_color, s=250, marker=marker_style, edgecolors='black', linewidth=1.5, label=label_text)
    
    # Cerchio soglia outlier
    if is_outlier:
        circle = plt.Circle((input_scaled_coords[0][0], input_scaled_coords[0][1]), OUTLIER_THRESHOLD, color='gray', fill=False, linestyle='--', alpha=0.5)
        plt.gca().add_patch(circle)

    plt.title("Density analysis (dynamic data)")
    plt.legend(loc='lower right', fontsize='small')
    plt.grid(True, linestyle='--', alpha=0.5)
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Image.open(buf)

def get_quantum_explanation(packet_size, arrival_time):
    weights = model_q[0].weights
    input_data = np.array([[packet_size, arrival_time]])
    input_scaled = feature_scaler.transform(input_data)
    inputs = torch.tensor(input_scaled).float()
    
########################################################################
########################  CENSORED #####################################
########################################################################
    
    explanation = f"""
    ### Quantum Encoding
    * Feature 1 $\\rightarrow$ Rotazione $\\theta_1$: **{theta_1:.2f} rad**
    * Feature 2 $\\rightarrow$ Rotazione $\\theta_2$: **{theta_2:.2f} rad**
    """
    return fig, explanation

def compare_prediction(packet_size, arrival_time, n_points, noise_level):
    # 1. Preprocessing Input Utente
    input_data = np.array([[packet_size, arrival_time]])
    input_scaled = feature_scaler.transform(input_data)
    input_tensor = torch.tensor(input_scaled).float()
    
  ########################################################################
########################  CENSORED #####################################
########################################################################
    
    # 4. Check Outlier (rispetto ai dati generati ora)
    distance, nearest_label = check_outlier(input_tensor, X_bg, y_bg)
    is_outlier = distance > OUTLIER_THRESHOLD
    
########################################################################
########################  CENSORED #####################################
########################################################################
    
    # --- LOGICA VERDETTO SEMPLIFICATA ---
    if is_outlier:
        verdict = f"OUTLIER DETECTED (Dist: {distance:.2f})"
        verdict += "\nThe data point is too far from the simulated historical distribution."
    else:
        if lbl_q_val == lbl_c_val:
########################################################################
########################  CENSORED #####################################
########################################################################
    return txt_q, conf_q, txt_c, conf_c, verdict, plot_img, circuit_plot, explain_text

# ==========================================
# 4. INTERFACCIA
# ==========================================

css_style = ".verdict-box {font-weight: bold; font-size: 1.2em; padding: 10px; border-radius: 5px; background-color: #f0f0f0;}"

with gr.Blocks() as demo:
    gr.Markdown("## Hybrid Quantum-Classical Intrusion Detection System (simulator)")

    gr.Markdown(
            "#### Disagreement example: **Packet size anomaly index = 1,5** | **Inter-arrival time index = 0,5** | **Historical sample size (points) = 170** | **Noise = 0,15**"
        )
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("### 1. Input (simulation)")
            s1 = gr.Slider(minimum=0, maximum=5, step=0.1, value=1.5, label="Packet size anomaly index")
            s2 = gr.Slider(minimum=0, maximum=5, step=0.1, value=3.0, label="Inter-arrival time index")
            
            gr.Markdown("### 2. Environment parameters")
########################################################################
########################  CENSORED #####################################
########################################################################
            
            btn = gr.Button("Scenario analysis", variant="primary")
        
        with gr.Column():
            with gr.Row():
                with gr.Column():
                    gr.Markdown("**Quantum**")
           ########################################################################
########################  CENSORED #####################################
########################################################################
         out_plot = gr.Image(label="Visualizzazione Dinamica")

    with gr.Accordion("Quantum internals", open=False):
        with gr.Row():
            out_circuit = gr.Plot(label="Circuit")
            out_explanation = gr.Markdown()

    btn.click(
        fn=compare_prediction, 
        inputs=[s1, s2, s_points, s_noise], 
        outputs=[out_lbl_q, out_conf_q, out_lbl_c, out_conf_c, out_verdict, out_plot, out_circuit, out_explanation]
    )

if __name__ == "__main__":
########################################################################
########################  CENSORED #####################################
########################################################################