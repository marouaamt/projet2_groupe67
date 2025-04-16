from tkinter import *
from tkinter import ttk
import tkinter as tk
import math
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
from tkinter import filedialog
import pandas as pd


def click1():
    new_window = Tk()
    new_window.geometry("400x400")
    new_window.title('Option 1')

    ttk.Label(new_window,
              text=" Okumura-Hata Model",
              font=("Helvetica", 20, "bold"),
              background="#f0f4f8",
              foreground="#333").grid(row=0, column=0, columnspan=2, pady=10)

    freq = ttk.Entry(new_window)
    Txheight = ttk.Entry(new_window)
    Rxheight = ttk.Entry(new_window)
    Distance = ttk.Entry(new_window)
    slope = ttk.Entry(new_window)
    def clearData():
        freq.delete(0, tk.END)
        Txheight.delete(0, tk.END)
        Rxheight.delete(0, tk.END)
        slope.delete(0, tk.END)
        Distance.delete(0, tk.END)

    def sumbitData():
        try:
            frequency = float(freq.get())
            hb = float(Txheight.get())
            hm = float(Rxheight.get())
            distance = float(Distance.get())

            if not (150 <= frequency <= 1500):
                print("Enter frequency (in MHz) where 150 <= frequency <= 1500")
                return
            if not (30 <= hb <= 200):
                print("Enter Tx height (30 <= hb <= 200 m)")
                return
            if not (1 <= hm <= 10):
                print("Enter Rx height (1 <= hm <= 10 m)")
                return
            if not (1 <= distance <= 20):
                print("Enter distance (1 <= distance <= 20 km)")
                return

        except ValueError:
            print("Invalid value. Please enter numbers only.")
            return

        step = 1  # step constante 1 km
        xs = np.arange(step, distance + step, step)
        a = (1.1 * math.log10(frequency) - 0.7) * hm - (1.56 * math.log10(frequency) - 0.8)

        ys = []
        ys2 = []

        for d in xs:
            lurban = 69.55 + 26.16 * math.log10(frequency) - 13.82 * math.log10(hb) - a + \
                     (44.9 - 6.55 * math.log10(hb)) * math.log10(d)
            ys.append(lurban)

            lopen = lurban - 4.78 * (math.log10(frequency)) ** 2 + 18.33 * math.log10(frequency) - 40.94
            ys2.append(lopen)

        plt.plot(xs, ys, c="green", linestyle="--", label="Urban")
        plt.plot(xs, ys2, c="orange", linestyle="-.", label="Open")
        plt.xlabel("Distance (km)")
        plt.ylabel("Path Loss (dB)")
        plt.title("Okumura-Hata Path Loss")
        plt.legend()
        plt.grid(True)
        plt.show()

    # labels
    ttk.Label(new_window, text="Frequency (MHz):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    freq.grid(row=1, column=1)

    ttk.Label(new_window, text="Tx Height (m):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    Txheight.grid(row=2, column=1)

    ttk.Label(new_window, text="Rx Height (m):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    Rxheight.grid(row=3, column=1)

    ttk.Label(new_window, text="Distance (km):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    Distance.grid(row=4, column=1)

    ttk.Button(new_window, text="Generate Plot", command=sumbitData).grid(row=5, column=1, padx=10, pady=10)
    ttk.Button(new_window, text="Clear", command=clearData).grid(row=5, column=0, padx=10, pady=10)


def click2():
    option2 = Tk()
    option2.geometry("500x400")
    option2.title('Option 2')

    

    freq = ttk.Entry(option2)
    Txheight = ttk.Entry(option2)
    Rxheight = ttk.Entry(option2)
    salop = ttk.Entry(option2)
    MinDistance = ttk.Entry(option2)
    MaxDistance = ttk.Entry(option2)

    def clearData():
        freq.delete(0, tk.END)
        Txheight.delete(0, tk.END)
        Rxheight.delete(0, tk.END)
        salop.delete(0, tk.END)
        MinDistance.delete(0, tk.END)
        MaxDistance.delete(0, tk.END)

    def sumbitData():
        try:
            f = float(freq.get())
            h_tx = float(Txheight.get())
            h_rx = float(Rxheight.get())
            d_min = float(MinDistance.get())
            d_max = float(MaxDistance.get())
            slope_threshold = float(salop.get())

            if d_min >= d_max:
                messagebox.showerror("Invalid range. Minimum distance must be less than maximum distance.")
                return
        except ValueError:
            messagebox.showerror("Invalid value. Please enter numbers only.")
            return

        d_user, loss_user = read_excel_data(filePath)
        analyze_and_plot(f, h_tx, h_rx, slope_threshold, d_user, loss_user, d_min, d_max)

    # === Lecture Excel ===

    def openFile():
        global filePath
        filePath = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )

    def read_excel_data(file_name="donnees.xlsx"):
        df = pd.read_excel(file_name)
        return df['distance'].values, df['perte_mesuree'].values

    # === Formule exacte de k ===
    def compute_k(f_mhz):
        f_hz = f_mhz * 1e6
        c = 3e8  # Vitesse de la lumière en m/s
        return 20 * np.log10((4 * np.pi * f_hz) / c)

    # === Calcul des seuils dynamiques et a ===
    def compute_thresholds(h_tx, h_rx):
        d1 = 3 + 0.02 * h_tx
        d2 = 8 + 0.1 * h_rx
        return d1, d2

    def compute_a(h_tx, h_rx):
        return 5 + (h_tx + h_rx) / 60

    # === Sigmoïdes dynamiques ===
    def S1(d, a, d1):
        return 1 / (1 + np.exp(-a * (d - d1)))

    def S2(d, a, d2):
        return 1 / (1 + np.exp(-a * (d - d2)))

    # === Modèle de perte ===
    def Lp(d, k, a, d1, d2):
        return k + 10 * np.log10((d ** 2) / (1 + S1(d, a, d1) + S2(d, a, d2)))

    # === Détection d'environnement ===
    def detect_env(pente):
        if pente > 5:
            return "Urban Area"
        elif pente > 3:
            return "Small City"
        elif pente > 1.5:
            return "Suburban"
        elif pente > 0.5:
            return "Open Environment"
        else:
            return "Large City / Rural"

    # === Analyse et tracé ===
    def analyze_and_plot(f, h_tx, h_rx, slope_threshold, d_user, loss_user, d_min, d_max):
        d_plot = np.logspace(np.log10(d_min), np.log10(d_max), 500)

        k = compute_k(f)
        a = compute_a(h_tx, h_rx)
        d1, d2 = compute_thresholds(h_tx, h_rx)

        lp_model = Lp(d_plot, k, a, d1, d2)

        segments = []
        environnements = []
        start_idx = 0

        for i in range(1, len(d_plot) - 1):
            d1_i, d2_i = d_plot[i - 1], d_plot[i + 1]
            l1, l2 = lp_model[i - 1], lp_model[i + 1]
            pente = abs((l2 - l1) / (d2_i - d1_i))

            if pente > slope_threshold:
                end_idx = i
                segments.append((start_idx, end_idx))
                env = detect_env(pente)
                environnements.append(env)

                print(f"\n📍 Segment {len(segments)} détecté")
                print(f"🗺️ Environnement : {env}")
                print("💠 Fonction utilisée : Lp(d) = k + 10·log10(d² / (1 + S1 + S2))")
                start_idx = end_idx

        segments.append((start_idx, len(d_plot) - 1))
        environnements.append("Large City / Rural")

        # Tracé
        plt.figure(figsize=(12, 6))
        colors = ['blue', 'green', 'orange', 'purple', 'magenta', 'brown']

        for idx, (start, end) in enumerate(segments):
            d_seg = d_plot[start:end]
            lp_seg = lp_model[start:end]
            plt.plot(d_seg, lp_seg, color=colors[idx % len(colors)], linewidth=2,
                     label=f"{environnements[idx]} ({start}-{end})")

        plt.scatter(d_user, loss_user, color='red', zorder=5, label='Données expérimentales')
        plt.axvline(x=d1, color='gray', linestyle='--', label=f'Transition d1 ≈ {d1:.1f} km')
        plt.axvline(x=d2, color='gray', linestyle=':', label=f'Transition d2 ≈ {d2:.1f} km')

        # Affichage des équations
        eq_k = rf"$k = 20 \log_{{10}}\left(\frac{{4\pi f}}{{c}}\right) = {k:.2f} \, \mathrm{{dB}}$"
        eq_lp = r"$L_p(d) = k + 10\log_{10}\left(\frac{d^2}{1 + S_1(d) + S_2(d)}\right)$"
        eq_s1 = rf"$S_1(d) = \frac{{1}}{{1 + e^{{-{a:.2f}(d - {d1:.2f})}}}}$"
        eq_s2 = rf"$S_2(d) = \frac{{1}}{{1 + e^{{-{a:.2f}(d - {d2:.2f})}}}}$"

        plt.text(d_min * 1.1, max(lp_model) * 0.98, eq_k, fontsize=11)
        plt.text(d_min * 1.1, max(lp_model) * 0.93, eq_lp, fontsize=11)
        plt.text(d_min * 1.1, max(lp_model) * 0.88, eq_s1, fontsize=11)
        plt.text(d_min * 1.1, max(lp_model) * 0.83, eq_s2, fontsize=11)

        plt.xscale('log')
        plt.xlabel("Distance (km)")
        plt.ylabel("Perte de trajet (dB)")
        plt.title("Modèle à 3 pentes avec transitions dynamiques")
        plt.grid(True, which="both", linestyle='--', linewidth=0.5)
        plt.legend()
        plt.tight_layout()
        plt.show()

    # === Interface ===

    # labels
    ttk.Label(option2, text="Frequency (MHz):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    freq.grid(row=1, column=1)

    ttk.Label(option2, text="Tx Height (m):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
    Txheight.grid(row=2, column=1)

    ttk.Label(option2, text="Rx Height (m):").grid(row=3, column=0, padx=10, pady=5, sticky="e")
    Rxheight.grid(row=3, column=1)

    ttk.Label(option2, text="Salop (n):").grid(row=4, column=0, padx=10, pady=5, sticky="e")
    salop.grid(row=4, column=1)

    # distance
    ttk.Label(option2, text="Distance Range (km):").grid(row=5, column=0, padx=10, pady=5, sticky="e")
    MinDistance.grid(row=5, column=1, padx=5, pady=5)
    ttk.Label(option2, text="to").grid(row=5, column=2, padx=5, pady=5)
    MaxDistance.grid(row=5, column=3, padx=5, pady=5)

    ##buttons

    ttk.Button(option2, text="Load Excel Data", command=openFile).grid(row=6, column=1, padx=10, pady=10)
    ttk.Button(option2, text="Generate Plot", command=sumbitData).grid(row=7, column=1, padx=10, pady=10)
    ttk.Button(option2, text="Clear", command=clearData).grid(row=7, column=0, padx=10, pady=10)


def click3():
    print("Go to option 3")


# Main window
window = Tk()
window.geometry("600x500")
window.title("Projet PP")
window.configure(bg="#f0f4f8")

# Styling
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton",
                font=("Helvetica", 16),
                padding=10,
                relief="flat",
                background="#4CAF50",
                foreground="white")
style.map("TButton", background=[("active", "#45a049")])

ttk.Label(window,
          text=" Welcome to our PP project",
          font=("Helvetica", 20, "bold"),
          background="#f0f4f8",
          foreground="#333").pack(pady=30)

# Button frame
button_frame = Frame(window, bg="#f0f4f8")
button_frame.pack(pady=20)

ttk.Button(button_frame, text=" Option 1", command=click1).pack(pady=10, ipadx=20)
ttk.Button(button_frame, text=" Option 2", command=click2).pack(pady=10, ipadx=20)
ttk.Button(button_frame, text=" Option 3", command=click3).pack(pady=10, ipadx=20)

ttk.Label(window,
          text="Select an option to continue...",
          font=("Helvetica", 12),
          background="#f0f4f8",
          foreground="black").pack(side="bottom", pady=20)

window.mainloop()