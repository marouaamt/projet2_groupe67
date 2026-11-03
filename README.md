# Radio Propagation and Graph Analysis

A Windows desktop application for exploring radio path-loss models and
extracting data points from plotted graphs. The project was developed as a
group school project for the **Pluridisciplinaire** module.

> **Project milestone:** the group received **16.5/20** after the project
> presentation. The module has a **coefficient of 6**.

The application combines telecommunications concepts, mathematical modelling,
data visualization, image processing, spreadsheet input/output, and a
graphical user interface.

## Project goals

- Compare predicted path loss for several propagation environments.
- Plot a smooth multi-slope model alongside measured data loaded from Excel.
- Digitize values from an existing graph by mapping image pixels to axis values.
- Export manually selected graph points and their calibration information to
  an Excel workbook.

## Features

The current application entry point, [`final_final.py`](./final_final.py),
opens a dark-themed desktop interface with three options.

### Option 1 — Okumura–Hata model

Enter carrier frequency, transmitter height, receiver height, and the maximum
distance. The application calculates and plots four path-loss curves:

- Urban, medium city
- Urban, dense/large city
- Open area
- Suburban

The plot uses a logarithmic distance axis and inverts the path-loss axis, as
implemented in the application.

The calculation uses the Okumura–Hata form:

```text
L_urban = 69.55 + 26.16 log10(f) - 13.82 log10(hb)
          - a(hm, f) + (44.9 - 6.55 log10(hb)) log10(d)
```

Here `f` is frequency in MHz, `hb` is transmitter height in metres, `hm` is
receiver height in metres, and `d` is distance in kilometres. The receiver
correction `a(hm, f)` varies by city size. The dense-city correction uses
different expressions below 200 MHz and above 400 MHz, with linear
interpolation between those frequencies.

The open-area and suburban curves are corrections applied to the medium-city
curve:

```text
L_open     = L_urban - 4.78(log10(f))^2 + 18.33 log10(f) - 40.94
L_suburban = L_urban - 2(log10(f / 28))^2 - 5.4
```

The interface validates the inputs against the ranges used by the program:
frequency 150–1500 MHz, transmitter height 30–200 m, receiver height 1–10 m,
and distance 1–20 km.

### Option 2 — Dynamic multi-slope model and measured data

Enter:

- Frequency in MHz
- Transmitter height in metres
- Receiver height in metres
- **Salop**, used by the program as a slope threshold

Then select an Excel workbook containing measured data. The first worksheet's
first two columns are read as distance (km) and measured path loss (dB),
respectively. Column headers are optional; the application uses the column
positions rather than the header names.

The model calculates:

```text
k  = 20 log10(4 pi (f × 10^6) / c)   (f in MHz; c = 3 × 10^8 m/s)
a  = 5 + (h_tx + h_rx) / 60
d1 = 3 + 0.02 h_tx
d2 = 8 + 0.1 h_rx

S1(d) = 1 / (1 + exp(-a(d - d1)))
S2(d) = 1 / (1 + exp(-a(d - d2)))

Lp(d) = k + 10 log10(d^2 / (1 + S1(d) + S2(d)))
```

The app evaluates the model at the distances from the workbook, estimates its
slope, and labels plot segments with environment names using slope thresholds.
Measured data is shown as red points, and the plot displays a mean squared
error (MSE) value.

**Workbook format:** use an `.xlsx` workbook with numeric values in columns A
and B of the first worksheet. Keep distances positive and in ascending order,
and avoid blank or non-numeric cells in the data range. An example workbook,
[`option2_test_data.xlsx`](./option2_test_data.xlsx), is included in the
project folder if available.

The USB-selection controls are displayed in this option, but in the current
`final_final.py` they are placeholders and are not connected to USB loading.
Use **Browse Excel** to choose a workbook directly.

### Option 3 — Manual graph digitizer

Upload a PNG, JPG, or JPEG graph. Calibrate its axes by clicking four points on
the image in this order:

1. X minimum (left end of the horizontal axis)
2. X maximum (right end of the horizontal axis)
3. Y minimum (bottom end of the vertical axis)
4. Y maximum (top end of the vertical axis)

After each click, enter the corresponding numerical value. Once calibration
is complete, click data points on the graph; the selected points are marked
in red. Right-click to undo the most recent point. Use **Clear all points** to
remove selections.

**Save to Excel** writes a workbook with:

- **Selected Points** — the selected points converted from image pixels into
  axis values (`X`, `Y`)
- **Axis Info** — clicked calibration pixel coordinates and the axis limits

When both limits on an axis are positive, the pixel-to-value conversion is
logarithmic for that axis; otherwise, it is linear. Select calibration points
carefully and ensure that they correspond to the entered minimum and maximum
values.

A sample image, [`option3_test_graph.png`](./option3_test_graph.png), can be
used to try this option. Its suggested axis limits are X: 0 to 10 and Y: 40
to 120.

## Technology

- **Python** — application logic
- **CustomTkinter** and **Tkinter** — desktop interface
- **Matplotlib** — plots
- **NumPy** — numerical calculations
- **Pandas** and **OpenPyXL** — reading and writing Excel workbooks
- **Pillow** and **OpenCV** — image loading and display
- **psutil** and **pywin32** — removable-drive detection helpers

The current program imports `win32file`, so the application is intended to run
on **Windows**. Tkinter is part of many standard Python distributions; the
remaining packages are installed with pip.

## Setup

Open PowerShell in the project directory and create a virtual environment:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install customtkinter matplotlib numpy pandas Pillow opencv-python psutil openpyxl pywin32
```

If PowerShell blocks activation, run the interpreter and pip directly instead:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install customtkinter matplotlib numpy pandas Pillow opencv-python psutil openpyxl pywin32
```

Tkinter normally comes with the Windows Python installation. If `tkinter`
cannot be imported, use a Python installation that includes Tcl/Tk support.

## Run

From the project directory:

```powershell
.\.venv\Scripts\python.exe .\final_final.py
```

The main window offers **Option 1**, **Option 2**, and **Option 3**. Each
option opens its own input window.

## Repository contents

| File/folder | Purpose |
|---|---|
| `final_final.py` | Current runnable application and its three GUI options |
| `fullcodeop.txt` | Text copy of a project code version; it includes additional draft code that is not wired into the current application entry point |
| `option2_test_data.xlsx` | Sample Excel input for Option 2, if present |
| `option3_test_graph.png` | Sample graph image for Option 3, if present |
| `final_final.spec` | PyInstaller build configuration, if present |
| `build/` | Generated packaging/build files, if present |

Generated test files and build outputs may not be included in every copy of the
repository.

## Scope and limitations

- This is an educational project and should not be treated as a calibrated
  radio-planning or engineering tool.
- The Option 2 environment labels are heuristics based on the calculated
  model slope; they are not a validated land-use classification.
- Option 2 expects usable numeric distances and measurements in the first two
  columns of the first worksheet. It does not provide comprehensive workbook
  validation.
- Option 3 digitization is approximate: accuracy depends on image quality,
  axis calibration, and where the user clicks.
- The application displays **Options 1–3** in its current main window.
  Additional code in `fullcodeop.txt` should not be assumed to be available
  from the current GUI.
- USB workbook discovery/loading is not implemented in the current Option 2
  controls.

## Academic context

This work was completed as a group project for the **Pluridisciplinaire**
module. Its presentation brought together the telecommunications model,
numerical implementation, interactive plotting, spreadsheet data handling,
and graph digitization. The project received a group-reported mark of
**16.5/20** after the presentation; the module coefficient is **6**.
