from tkinter import *
from types import SimpleNamespace

import customtkinter
import customtkinter as CTk
from customtkinter import *
from tkinter import ttk, messagebox, filedialog, simpledialog
import tkinter as tk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image, ImageTk
import os
import cv2
import math
import psutil
from openpyxl import Workbook
import win32file


# === USB DETECTION BACH NL9AW ALL DRIVES===
# RESUME DE FOCTION SELECT ALL DRIVES C?B?E... THEN SELECT ONLY REMOVABLE DRIVES AKA REFERED TO WITH 2
def get_usb_mountpoints():
    DRIVE_REMOVABLE = 2
    usb_mounts = []
    for part in psutil.disk_partitions():
        if win32file.GetDriveType(part.device) == DRIVE_REMOVABLE:
            usb_mounts.append(part.mountpoint)
    return usb_mounts


# FIND AND LIST XLSX FILES IN THOSE DRIVES LI JBNAHOM M FONCTION LI FATT
def find_xlsx_files_in_usb():
    xlsx_files = []
    file_paths = []
    usb_drives = get_usb_mountpoints()
    for drive in usb_drives:
        for root, dirs, files in os.walk(drive):
            for file in files:
                if file.lower().endswith(".xlsx"):
                    xlsx_files.append(file)
                    file_paths.append(os.path.join(root, file))
    return xlsx_files, file_paths


def click1():
    filePath = None
    usb_file_paths = []
    new_window = customtkinter.CTkToplevel()
    new_window.attributes('-topmost', 1)
    new_window.geometry("500x600")
    new_window.title('OKUMURA-HATA MODEL GRAPH PLOTTING')
    center_window1(new_window ,500,800)
    customtkinter.CTkLabel(new_window, text="Okumura-Hata Model", font=("Helvetica", 20, "bold"), ).pack(pady=20)

    customtkinter.CTkLabel(new_window, text="frequency", font=("Helvetica", 14, "bold"), ).pack(pady=2)

    freq = customtkinter.CTkEntry(new_window, height=40, width=200, corner_radius=50,
                                  placeholder_text="enter frequency in MHz")
    freq.pack(pady=5)

    customtkinter.CTkLabel(new_window, text="Tx height", font=("Helvetica", 14, "bold"), ).pack(pady=2)
    Txheight = customtkinter.CTkEntry(new_window, height=40, width=200, corner_radius=50,
                                      placeholder_text="enter transmitter height in m")
    Txheight.pack(pady=5)
    customtkinter.CTkLabel(new_window, text="Rx height", font=("Helvetica", 14, "bold"), ).pack(pady=2)
    Rxheight = customtkinter.CTkEntry(new_window, height=40, width=200, corner_radius=50,
                                      placeholder_text="enter receiver height in m")
    Rxheight.pack(pady=5)
    customtkinter.CTkLabel(new_window, text="Distance", font=("Helvetica", 14, "bold"), ).pack(pady=2)
    Distance = customtkinter.CTkEntry(new_window, height=40, width=200, corner_radius=50,
                                      placeholder_text="enter distance in km")
    Distance.pack(pady=4)

    def clearData():
        freq.delete(0, tk.END)
        Txheight.delete(0, tk.END)
        Rxheight.delete(0, tk.END)
        Distance.delete(0, tk.END)
        # slope.delete(0, tk.END)

    def a_medium(hm, f):
        return (1.1 * math.log10(f) - 0.7) * hm - (1.56 * math.log10(f) - 0.8)

    def a_dense(hm, f):
        if f <= 200:
            return 8.29 * (math.log10(1.54 * hm)) ** 2 - 1.1
        elif f >= 400:
            return 3.2 * (math.log10(11.75 * hm)) ** 2 - 4.97
        else:
            # Interpolation linéaire entre 200 et 400 MHz
            a200 = 8.29 * (math.log10(1.54 * hm)) ** 2 - 1.1
            a400 = 3.2 * (math.log10(11.75 * hm)) ** 2 - 4.97
            return a200 + (a400 - a200) * ((f - 200) / 200)

    def compute_curves():
        try:
            frequency = float(freq.get())
            hb = float(Txheight.get())
            hm = float(Rxheight.get())
            distance = float(Distance.get())

            if not (150 <= frequency <= 1500):
                show_error("frenquency error", "Enter frequency (in MHz) where 150 <= frequency <= 1500")
                return
            if not (30 <= hb <= 200):
                show_error("transmitter high  error", "Enter Tx height (30 <= hb <= 200 m)")
                return
            if not (1 <= hm <= 10):
                show_error("receiver high  error", "Enter Rx height (1 <= hm <= 10 m)")
                return
            if not (1 <= distance <= 20):
                show_error("distance error", "Enter distance (1 <= distance <= 20 km)")
                return

        except ValueError:
            show_error("value error", "Invalid value. Please enter numbers only.")
            return

        step = 1
        xs = np.arange(step, distance + step, step)
        ys_medium, ys_dense, ys_open, ys_suburban = [], [], [], []

        for d in xs:
            # Medium city
            a_m = a_medium(hm, frequency)
            l_medium = 69.55 + 26.16 * math.log10(frequency) - 13.82 * math.log10(hb) - a_m + \
                       (44.9 - 6.55 * math.log10(hb)) * math.log10(d)
            ys_medium.append(l_medium)

            # Dense urban
            a_d = a_dense(hm, frequency)
            l_dense = 69.55 + 26.16 * math.log10(frequency) - 13.82 * math.log10(hb) - a_d + \
                      (44.9 - 6.55 * math.log10(hb)) * math.log10(d)
            ys_dense.append(l_dense)

            # Open area
            lopen = l_medium - 4.78 * (math.log10(frequency)) ** 2 + 18.33 * math.log10(frequency) - 40.94
            ys_open.append(lopen)

            # Suburban
            l_suburban = l_medium - 2 * (math.log10(frequency / 28)) ** 2 - 5.4
            ys_suburban.append(l_suburban)

        return xs, ys_medium, ys_dense, ys_open, ys_suburban
    def plot_all_curves():
        result = compute_curves()
        if result is None:
            return
        xs, ys_medium, ys_dense, ys_open, ys_suburban = result

        plt.figure(figsize=(10, 6))
        plt.semilogx(xs, ys_medium, linestyle='--', color='green', label="Urban (Medium city)")
        plt.semilogx(xs, ys_dense, linestyle='-.', color='blue', label="Urban (Dense/Large city)")
        plt.semilogx(xs, ys_open, linestyle=':', color='orange', label="Open area")
        plt.semilogx(xs, ys_suburban, linestyle='-', color='purple', label="Suburban")
        plt.gca().invert_yaxis()  # <- Inversion de l’axe Y
        plt.xlabel("Distance (km) [log scale]")
        plt.ylabel("Path Loss (dB)")
        plt.title("Comparaison des pertes – Modèle Okumura-Hata")
        plt.legend()
        plt.grid(True, which="both", linestyle='--', linewidth=0.5)
        plt.tight_layout()
        def choiceofpc ():
                plt.show()
        choiceofpc()

    
    customtkinter.CTkButton(new_window, text="Generate Plot", command=plot_all_curves, height=30, width=200, corner_radius=50).pack(pady=7)
    customtkinter.CTkButton(new_window, text="Clear", command=clearData, height=30, width=200, corner_radius=50).pack(pady=7)


#################### matochiwch hadi , hadi hiya ta3 error show message """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def show_error(title, message, type="error"):
    current_active = window.focus_get()
    temp = tk.Toplevel()
    temp.attributes('-topmost', True)
    temp.withdraw()
    if type == "error":
        messagebox.showerror(title, message, parent=temp)
    elif type == "warning":
        messagebox.showwarning(title, message, parent=temp)
    elif type == "info":
        messagebox.showinfo(title, message, parent=temp)
    temp.destroy()
    if current_active:
        current_active.focus_force()


##########################################################################################################
def click2():
    option2 = customtkinter.CTkToplevel()
    option2.attributes('-topmost', 1)
    option2.geometry("500x650")
    center_window1(option2, 500, 850)
    option2.title("the three slope model and the cloud point")

    filePath = None
    usb_file_paths = []
    customtkinter.CTkLabel(option2, text="The three slope model and the cloud point",
                           font=("Helvetica", 20, "bold"), ).pack(pady=5)

    customtkinter.CTkLabel(option2, text="frequency", font=("Helvetica", 14, "bold"), ).pack(pady=2)
    freq = customtkinter.CTkEntry(option2, height=40, width=200, corner_radius=50, placeholder_text="enter frequency in (MHz)")
    freq.pack(pady=2)
    customtkinter.CTkLabel(option2, text="Tx height", font=("Helvetica", 14, "bold"), ).pack(pady=2)
    Txheight = customtkinter.CTkEntry(option2, height=40, width=200, corner_radius=50, placeholder_text="enter transmitter height in (m)")
    Txheight.pack(pady=2)
    customtkinter.CTkLabel(option2, text="Rx height", font=("Helvetica", 14, "bold"), ).pack(pady=2)
    Rxheight = customtkinter.CTkEntry(option2, height=40, width=200, corner_radius=50, placeholder_text="enter receiver height in (m)")
    Rxheight.pack(pady=2)
    customtkinter.CTkLabel(option2, text="Salop", font=("Helvetica", 14, "bold"), ).pack(pady=2)
    salop = customtkinter.CTkEntry(option2, height=40, width=200, corner_radius=50, placeholder_text="enter salop (n) ")
    salop.pack(pady=2)
    customtkinter.CTkLabel(option2, text=" enter the distance range in (km) ", font=("Helvetica", 14, "bold"), ).pack(pady=2)
    MinDistance = customtkinter.CTkEntry(option2, height=40, width=200, corner_radius=50, placeholder_text="from ")
    MinDistance.pack(pady=2)
    MaxDistance = customtkinter.CTkEntry(option2, height=40, width=200, corner_radius=50, placeholder_text="to ")
    MaxDistance.pack(pady=2)

    def clearData():
        freq.delete(0, tk.END)
        Txheight.delete(0, tk.END)
        Rxheight.delete(0, tk.END)
        salop.delete(0, tk.END)
        MinDistance.delete(0, tk.END)
        MaxDistance.delete(0, tk.END)

    def openFile():
        nonlocal filePath
        filePath = filedialog.askopenfilename(
            parent=option2,
            title="Sélectionner un fichier Excel",
            filetypes=[("Excel files", "*.xlsx")])

    def read_excel_data(file_name):
        ext = os.path.splitext(file_name)[1].lower()

        try:
            if ext == ".xlsx":
                df = pd.read_excel(file_name, engine="openpyxl")
            elif ext == ".xls":
                df = pd.read_excel(file_name, engine="xlrd")
            else:
                raise show_error("error", "Unsupported file type. Please select a .xls or .xlsx file.")
        except Exception as e:
            raise show_error("error", f"Failed to read Excel file: {str(e)}")

        if df.shape[1] < 2:
            return show_error("error", "The Excel file must contain at least two columns.")

        distances = df.iloc[:, 0].values
        losses = df.iloc[:, 1].values
        return distances, losses

    def compute_k(f_mhz):
        c = 3e8
        return 20 * np.log10((4 * np.pi * f_mhz * 1e6) / c)

    def compute_thresholds(h_tx, h_rx):
        return 3 + 0.02 * h_tx, 8 + 0.1 * h_rx

    def compute_a(h_tx, h_rx):
        return 5 + (h_tx + h_rx) / 60

    def S1(d, a, d1):
        return 1 / (1 + np.exp(-a * (d - d1)))

    def S2(d, a, d2):
        return 1 / (1 + np.exp(-a * (d - d2)))

    def Lp(d, k, a, d1, d2):
        return k + 10 * np.log10((d ** 2) / (1 + S1(d, a, d1) + S2(d, a, d2)))

    def detect_env(p):
        if p > 5: return "Urban Area"
        if p > 3: return "Small City"
        if p > 1.5: return "Suburban"
        if p > 0.5: return "Open Environment"
        return "Large City / Rural"

    def analyze_and_plot(f, h_tx, h_rx, slope_threshold, d_user, loss_user):
        k = compute_k(f)
        a = compute_a(h_tx, h_rx)
        d1, d2 = compute_thresholds(h_tx, h_rx)
        lp_model = Lp(d_user, k, a, d1, d2)
        slopes = np.gradient(lp_model, d_user)

        segments, envs, start_idx = [], [], 0
        for i in range(1, len(d_user) - 1):
            slope = abs(slopes[i])
            env = detect_env(slope)
            if slope > slope_threshold and (len(envs) == 0 or env != envs[-1]):
                segments.append((start_idx, i))
                envs.append(env)
                start_idx = i

        segments.append((start_idx, len(d_user) - 1))
        envs.append(envs[-1] if envs else "Large City / Rural")

        plt.figure(figsize=(12, 6))
        colors = ['blue', 'green', 'orange', 'purple', 'magenta', 'brown']
        for i, (s, e) in enumerate(segments):
            plt.plot(d_user[s:e], lp_model[s:e], color=colors[i % len(colors)], label=f"{envs[i]} ({s}-{e})")

        if len(loss_user) > 0:
            plt.scatter(d_user, loss_user, color='red', label='Experimental Data')

        plt.xscale('log')
        plt.xlabel("Distance (km)")
        plt.ylabel("Path Loss (dB)")
        plt.gca().invert_yaxis()
        plt.title("Dynamic Multi-slope Model")
        plt.grid(True, which="both", linestyle='--', linewidth=0.5)
        plt.legend()
        formula = r"$L_p(d) = k + 10 \log_{10}\left(\frac{d^2}{1 + S_1(d) + S_2(d)}\right)$"
        plt.text(0.5, 0.95, formula, transform=plt.gca().transAxes,
                 fontsize=12, verticalalignment='top', bbox=dict(facecolor='white', alpha=0.8))
        if len(loss_user) > 0:
            lp_interp = np.interp(d_user, d_user, lp_model)
            mse = np.mean((loss_user - lp_interp) ** 2)
            plt.text(0.5, 0.88, f"MSE: {mse:.2f} dB²", transform=plt.gca().transAxes,
                     fontsize=12, verticalalignment='top', color='red', bbox=dict(facecolor='white', alpha=0.8))

        plt.tight_layout()
        plt.show()

    def sumbitData():
        try:
            f = float(freq.get())
            h_tx = float(Txheight.get())
            h_rx = float(Rxheight.get())
            slope_threshold = float(salop.get())
            if f <= 0:
                return show_error("frequency error", "La fréquence doit être strictement positive")
            if not ( h_tx >= 0):
                return show_error("transmitter height error")
            if not ( h_rx >= 0):
                return show_error("receiver height error")
            if not filePath:
                return show_error("Excel Required", "Please select an Excel file to load experimental data.")
            d_user, loss_user = read_excel_data(filePath)
            analyze_and_plot(f, h_tx, h_rx, slope_threshold, d_user, loss_user)

        except Exception as e:
            show_error("Error", str(e))


    be = customtkinter.CTkButton(option2, text="Browse Excel", command=openFile, height=40, width=200, corner_radius=50)
    be.pack(pady=2)
    customtkinter.CTkLabel(option2, text="Choose Excel from USB:", font=("Helvetica", 14)).pack(pady=2)
    usb_combo = customtkinter.CTkComboBox(option2, values=[], width=250, height=40, corner_radius=50)
    usb_combo.pack(pady=4)
    lfu = customtkinter.CTkButton(option2, text="Load from USB", command=lambda: None, height=40, width=200, corner_radius=50)
    lfu.pack(pady=2)
    sf = customtkinter.CTkButton(option2, text="Use Selected USB File", command=lambda: None, height=40, width=200, corner_radius=50)
    sf.pack(pady=2)
    customtkinter.CTkButton(option2, text="Generate Plot", command=sumbitData, height=40, width=200, corner_radius=50).pack(pady=2)
    customtkinter.CTkButton(option2, text="Clear", command=clearData, height=40, width=200, corner_radius=50).pack(pady=2)

def click3():
    ################### same balako touchiwha ##################
    option3 = customtkinter.CTkToplevel()
    option3.title("Manual Point Selector")
    option3.geometry("700x800")
    center_window1(option3, 700, 800)
    option3.attributes('-topmost', 1)

    global set_axis_btn, save_btn, clear_last_btn, clear_all_btn

    state = SimpleNamespace(
        image=None,
        tk_image=None,
        image_path="",
        points=[],
        axis_points={},
        axis_limits={},
        axis_index=0,
        setting_axis=False
    )

    axis_labels = ["x_min", "x_max", "y_min", "y_max"]

    def upload_image():
        state.image_path = filedialog.askopenfilename(parent=option3, title="Select Image",
                                                      filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if state.image_path:
            state.image = cv2.imread(state.image_path)
            state.image = cv2.cvtColor(state.image, cv2.COLOR_BGR2RGB)
            state.points.clear()
            state.axis_points.clear()
            state.axis_index = 0
            state.setting_axis = False
            display_image()
            set_axis_btn.configure(state="normal")
            save_btn.configure(state="normal")
            clear_last_btn.configure(state="normal")
            clear_all_btn.configure(state="normal")

    def display_image():
        img = Image.fromarray(state.image)
        state.tk_image = ImageTk.PhotoImage(img)
        canvas.config(width=img.width, height=img.height)
        canvas.create_image(0, 0, anchor=tk.NW, image=state.tk_image)
        redraw_points()

    def redraw_points():
        for x, y in state.points:
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="red")
        for label in axis_labels[:state.axis_index]:
            x, y = state.axis_points[label]
            canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill="blue")

    def safe_eval(prompt):
        def on_submit():
            value = entry.get()
            try:
                if not value:
                    raise ValueError("No input.")
                expr = value.replace("^", "**")
                if any(c not in "0123456789.+-*/eE() " for c in expr):
                    raise ValueError("Invalid characters.")
                result = float(eval(expr, {"__builtins__": None}, {}))
                user_input.set(result)
                dialog.destroy()
            except Exception:
                messagebox.showerror("Invalid Input", f"Could not interpret: {value}", parent=dialog)

        dialog = customtkinter.CTkToplevel(option3)
        dialog.title("Enter Axis Value")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        dialog.attributes('-topmost', 1)
        dialog.grab_set()  # modal
        center_window(dialog)

        label = customtkinter.CTkLabel(dialog, text=prompt, font=("Helvetica", 20))
        label.pack(pady=(30, 10))

        entry = customtkinter.CTkEntry(dialog, font=("Helvetica", 18), width=300)
        entry.pack(pady=10, ipadx=10, ipady=10)
        entry.focus()

        submit_button = customtkinter.CTkButton(dialog, text="Submit", command=on_submit,
                                                font=("Helvetica", 16), corner_radius=20)
        submit_button.pack(pady=20)

        user_input = tk.DoubleVar(value=float('nan'))
        dialog.wait_window()
        val = user_input.get()
        return None if math.isnan(val) else val

    def set_axis_limits():
        messagebox.showinfo("Set Axis Points", "Click image in order: X Min, X Max, Y Min, Y Max\nRight click to undo.",
                            parent=option3)
        state.setting_axis = True
        state.axis_index = 0
        state.points.clear()
        state.axis_points.clear()
        display_image()

    def on_click(event):
        x, y = event.x, event.y
        r = 4

        if state.setting_axis:
            if state.axis_index < len(axis_labels):
                label = axis_labels[state.axis_index]
                state.axis_points[label] = (x, y)
                canvas.create_oval(x - r, y - r, x + r, y + r, fill="blue")
                state.axis_index += 1

            if state.axis_index == len(axis_labels):
                state.setting_axis = False
                x_min_val = safe_eval("Enter X axis minimum value:")
                x_max_val = safe_eval("Enter X axis maximum value:")
                    
                while  x_max_val<x_min_val or x_max_val is None:
                    show_error("enter a valid value" , "max should be greater then min")
                    x_max_val = safe_eval("Enter X axis maximum value:")

                y_min_val = safe_eval("Enter Y axis minimum value:")
                y_max_val = safe_eval("Enter Y axis maximum value:")
                
                while y_max_val< y_min_val or y_max_val is None:
                    
                    show_error("enter a valid value" , "max should be greater then min")
                    y_max_val = safe_eval("Enter Y axis maximum value:")
        
                if None in [x_min_val, x_max_val, y_min_val, y_max_val]:
                    return

                state.axis_limits = {
                    "x_min": x_min_val,
                    "x_max": x_max_val,
                    "y_min": y_min_val,
                    "y_max": y_max_val
                }
                messagebox.showinfo("Axis Set", "Axis points and limits have been set.", parent=option3)
        else:
            state.points.append((x, y))
            canvas.create_oval(x - r, y - r, x + r, y + r, fill="red")

    def undo_point(event=None):
        clear_last_point()

    def clear_last_point():
        if state.setting_axis and state.axis_index > 0:
            state.axis_index -= 1
            state.axis_points.pop(axis_labels[state.axis_index], None)
        elif not state.setting_axis and state.points:
            state.points.pop()
        display_image()

    def clear_all_points():
        if state.setting_axis:
            state.axis_index = 0
            state.axis_points.clear()
        state.points.clear()
        display_image()

    def save_to_excel():
        if not state.axis_limits or len(state.axis_points) != 4:
            show_error("Missing Axis", "Set axis points and limits before saving.")
            return
        if not state.points:
            show_error("No Points", "No points selected.")
            return

        x_min_pix, _ = state.axis_points["x_min"]
        x_max_pix, _ = state.axis_points["x_max"]
        _, y_min_pix = state.axis_points["y_min"]
        _, y_max_pix = state.axis_points["y_max"]

        x_min_val = state.axis_limits["x_min"]
        x_max_val = state.axis_limits["x_max"]
        y_min_val = state.axis_limits["y_min"]
        y_max_val = state.axis_limits["y_max"]

        log_x = x_min_val > 0 and x_max_val > 0
        log_y = y_min_val > 0 and y_max_val > 0

        if log_x:
            log_x_min = math.log10(x_min_val)
            log_x_max = math.log10(x_max_val)
        if log_y:
            log_y_min = math.log10(y_min_val)
            log_y_max = math.log10(y_max_val)

        transformed_points = []
        for x_pix, y_pix in state.points:
            if log_x:
                x_log = log_x_min + ((x_pix - x_min_pix) / (x_max_pix - x_min_pix)) * (log_x_max - log_x_min)
                x_val = 10 ** x_log
            else:
                x_val = x_min_val + ((x_pix - x_min_pix) / (x_max_pix - x_min_pix)) * (x_max_val - x_min_val)

            if log_y:
                y_log = log_y_max - ((y_pix - y_max_pix) / (y_min_pix - y_max_pix)) * (log_y_max - log_y_min)
                y_val = 10 ** y_log
            else:
                y_val = y_max_val - ((y_pix - y_max_pix) / (y_min_pix - y_max_pix)) * (y_max_val - y_min_val)

            transformed_points.append((x_val, y_val))

        wb = Workbook()
        ws = wb.active
        ws.title = "Selected Points"
        ws.append(["X", "Y"])
        for x_val, y_val in transformed_points:
            ws.append([x_val, y_val])

        ws2 = wb.create_sheet("Axis Info")
        ws2.append(["Label", "Pixel X", "Pixel Y"])
        for label, (x, y) in state.axis_points.items():
            ws2.append([label, x, y])
        ws2.append([])
        ws2.append(["Axis Limits"])
        for k, v in state.axis_limits.items():
            ws2.append([k, v])

        save_path = filedialog.asksaveasfilename(parent=option3, defaultextension=".xlsx",
                                                 filetypes=[("Excel files", "*.xlsx")])
        if save_path:
            wb.save(save_path)
            messagebox.show_info("Saved", f" Data saved to {save_path}" , parent=option3)
        else:
            show_error("Cancelled", "Save operation cancelled.")

        def center_window(window):
            window.update_idletasks()
            width = window.winfo_width()
            height = window.winfo_height()
            screen_width = window.winfo_screenwidth()
            screen_height = window.winfo_screenheight()
            x = (screen_width // 2) - (width // 2)
            y = (screen_height // 2) - (height // 2)
            window.geometry(f"{width}x{height}+{x}+{y}")

    # GUI setup
    canvas = tk.Canvas(option3, cursor="cross")
    canvas.pack(fill=tk.BOTH, expand=True)
    canvas.bind("<Button-1>", on_click)
    canvas.bind("<Button-3>", undo_point)

    upload_btn = customtkinter.CTkButton(option3, text="Upload Image", command=upload_image, height=30, width=200,
                                         font=("Helvetica", 24), hover_color="green", corner_radius=50)
    upload_btn.pack(pady=4, ipadx=20)
    set_axis_btn = customtkinter.CTkButton(option3, text="set axis limit", command=set_axis_limits, height=30,
                                           width=200,
                                           font=("Helvetica", 24), hover_color="green", corner_radius=50,
                                           state="disabled")
    set_axis_btn.pack(pady=4, ipadx=20)
    save_btn = customtkinter.CTkButton(option3, text="save to excel", command=save_to_excel, height=30, width=200,
                                       font=("Helvetica", 24), hover_color="green", corner_radius=50, state="disabled")
    save_btn.pack(pady=4, ipadx=20)
    clear_last_btn = customtkinter.CTkButton(option3, text="clear last point ", command=clear_last_point, height=30,
                                             width=200,
                                             font=("Helvetica", 24), hover_color="green", corner_radius=50,
                                             state="disabled")
    clear_last_btn.pack(pady=4, ipadx=20)
    clear_all_btn = customtkinter.CTkButton(option3, text="clear all points", command=clear_all_points, height=30,
                                            width=200,
                                            font=("Helvetica", 24), hover_color="green", corner_radius=50,
                                            state="disabled")
    clear_all_btn.pack(pady=4, ipadx=20)



def center_window(window):
    """Centre une fenêtre sur l'écran"""
    window.update_idletasks()  # Mise à jour pour obtenir la taille actuelle
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width - width) // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def center_window1(window, width, height):
    ##center the main window
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = int((screen_width - width) / 2)
    y = int((screen_height - height) / 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

import tkinter as tk

class ToolTip:
    def __init__(self, widget, text='Tooltip text'):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, justify='left',
                         background="#333", foreground="white", relief='solid', borderwidth=1,
                         font=("Helvetica", 10))
        label.pack(ipadx=5, ipady=2)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

# Main window
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
window = customtkinter.CTk()
window.geometry("1000x1200")
center_window1(window, 1000, 850)
window.title("projet pluridisciplinaire")
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
my_label = customtkinter.CTkLabel(window, text=" Welcome to our PP project", font=("Helvetica", 20, "bold"))
my_label.pack(pady=30)
btn1 =customtkinter.CTkButton(window, text="OPTION 1", height=70, width=200, font=("Helvetica", 24), hover_color="green",
                        corner_radius=50, command=click1)
btn1.pack(pady=50, ipadx=20)

ToolTip(btn1, "OKUMURA-HATA MODEL GRAPH PLOTTING")

btn2 = customtkinter.CTkButton(window, text=" OPTION 2", height=70, width=200, font=("Helvetica", 24), hover_color="green",
                        corner_radius=50, command=click2)
btn2.pack(pady=50, ipadx=20)
ToolTip(btn2, "the three slope model and the cloud point")

btn3 = customtkinter.CTkButton(window, text="OPTION 3", height=70, width=200, font=("Helvetica", 24), hover_color="green",
                        corner_radius=50, command=click3)
btn3.pack(pady=50, ipadx=20)
ToolTip(btn3, "Manual Point Selector")



window.mainloop()