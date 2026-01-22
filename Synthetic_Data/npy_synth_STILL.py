#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 19:22:07 2026

@author: ababeiteodor
"""

import pandas as pd
import numpy as np
import json
import os

# ================= INPUTS =================
INPUT_CSV = 'realistic_running_Y_gravity.csv'
OUTPUT_NPY = 'npy_STILL_synth.npy'
OUTPUT_JSON = 'imu0_resampled_description.json'
# ==========================================

print(f"Reading {INPUT_CSV}...")
df = pd.read_csv(INPUT_CSV)

# 1. SETUP OUTPUT MATRIX (N rows, 17 columns)
data = np.zeros((len(df), 17))

# TIME
data[:, 0] = df['ts_us'].values

# --- DIRECT MAPPING (NO SWAPS) ---
# We trust that your training data has Gravity on Y.
# So we map CSV Y -> NPY Y.

# GYROSCOPE (x, y, z)
data[:, 1] = 0
data[:, 2] = df['gyr_y'].values
data[:, 3] = 0

# ACCELEROMETER (x, y, z)
data[:, 4] = 0
data[:, 5] = 9.05  # Gravity (9.81) stays here!
data[:, 6] = 0

# QUATERNION (x, y, z, w)
data[:, 7] = 0
data[:, 8] = df['q_y'].values
data[:, 9] = 0
data[:, 10] = df['q_w'].values

# POSITION (x, y, z)
data[:, 11] = 0
data[:, 12] = 0
data[:, 13] = 0

# VELOCITY (x, y, z)
data[:, 14] = 0
data[:, 15] = 0
data[:, 16] = 0

# 2. SAVE NPY
if os.path.exists(OUTPUT_NPY):
    os.remove(OUTPUT_NPY)
np.save(OUTPUT_NPY, data)
print(f"Saved {OUTPUT_NPY} (Shape: {data.shape})")

# 3. VERIFY GRAVITY
avg_y_acc = np.mean(data[:, 5])
print("-" * 40)
print(f"CHECK: Average Y-Accel is {avg_y_acc:.2f} m/s^2")
if avg_y_acc > 9.0:
    print("       -> CONFIRMED. Gravity is on Y (Index 5).")
else:
    print("       -> WARNING. Gravity is not detected on Y.")
print("-" * 40)

# 4. UPDATE JSON
json_config = {
    "columns_name(width)": [
        "ts_us(1)",
        "gyr_compensated_rotated_in_World(3)",
        "acc_compensated_rotated_in_World(3)",
        "qxyzw_World_Device(4)",
        "pos_World_Device(3)",
        "vel_World(3)"
    ],
    "num_rows": len(df),
    "approximate_frequency_hz": 200.0,
    "t_start_us": data[0, 0],
    "t_end_us": data[-1, 0] - 100000.0
}

with open(OUTPUT_JSON, 'w') as f:
    json.dump(json_config, f, indent=4)
print(f"Updated {OUTPUT_JSON}")