import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import filedialog, simpledialog
import pandas as pd

# === STEP 1: Load image via dialog ===
root = tk.Tk()
root.withdraw()
img_path = filedialog.askopenfilename(title="Select Graph Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])

if not img_path:
    raise Exception("No image file selected.")

img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Image not found at path: {img_path}")

print("Loaded image from:", img_path)

# === STEP 2: Ask user to click reference points ===
print("\nClick on the image in this order:")
print("1. Origin (bottom-left corner of the graph area)")
print("2. X-axis max (right-bottom corner of graph area)")
print("3. Y-axis max (top-left corner of graph area)")

plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
plt.title("Click 3 points: Origin, X-max, Y-max")
pts = plt.ginput(3, timeout=0)
plt.close()

if len(pts) != 3:
    raise Exception("You must click exactly 3 points.")

(pixel_origin, pixel_xmax, pixel_ymax) = pts
ox, oy = pixel_origin
xmax_px, _ = pixel_xmax
_, ymax_py = pixel_ymax

# Bounding box for graph area
x_min_box = int(min(ox, xmax_px))
x_max_box = int(max(ox, xmax_px))
y_min_box = int(min(oy, ymax_py))
y_max_box = int(max(oy, ymax_py))

# === STEP 3: Ask user for actual axis values ===
x_min_val = float(simpledialog.askstring("Axis Input", "Enter x-axis minimum value:"))
x_max_val = float(simpledialog.askstring("Axis Input", "Enter x-axis maximum value:"))
y_min_val = float(simpledialog.askstring("Axis Input", "Enter y-axis minimum value:"))
y_max_val = float(simpledialog.askstring("Axis Input", "Enter y-axis maximum value:"))

# === STEP 4: Preprocessing for white background only ===
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# === STEP 5: Find contours ===
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# === STEP 6: Convert pixel coords to graph coords ===
def pixel_to_graph(x_pix, y_pix):
    x = x_min_val + (x_max_val - x_min_val) * (x_pix - ox) / (xmax_px - ox)
    y = y_min_val + (y_max_val - y_min_val) * (oy - y_pix) / (oy - ymax_py)
    return round(x, 2), round(y, 2)

# === STEP 7: Filter and convert points ===
real_coords = []
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 5:  # Ignore tiny dots or noise
        continue
    M = cv2.moments(cnt)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        if x_min_box < cx < x_max_box and y_min_box < cy < y_max_box:
            gx, gy = pixel_to_graph(cx, cy)
            real_coords.append((gx, gy))

print(f"\n{len(real_coords)} points extracted.")

# === STEP 8: Save to Excel file ===
df = pd.DataFrame(real_coords)
excel_output = os.path.join(os.getcwd(), "extracted_coordinates.xlsx")
df.to_excel(excel_output, index=False, header=False)
print(f"\nDone! Coordinates saved to '{excel_output}'")


# === Optional: Visual preview ===
img_copy = img.copy()
for cnt in contours:
    area = cv2.contourArea(cnt)
    if area < 5:
        continue
    M = cv2.moments(cnt)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        if x_min_box < cx < x_max_box and y_min_box < cy < y_max_box:
            cv2.circle(img_copy, (cx, cy), 5, (0, 255, 0), -1)

cv2.imshow("Detected Dots", img_copy)
cv2.waitKey(0)
cv2.destroyAllWindows()
