import pandas as pd
import numpy as np
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import interp1d
import json

# ================= CONFIGURATION =================
INPUT_CSV = 'imu_samples_0.csv'
OUTPUT_NPY = 'imu0_resampled.npy'
TARGET_FREQ = 200.0

# Calibration Biases (from your calibration.json snippet)
ACCEL_BIAS = np.array([0.053046, -0.325644, -0.129551])
GYRO_BIAS = np.array([-0.000073, -0.000595, -0.001119])
# =================================================

print(f"Reading {INPUT_CSV}...")
df = pd.read_csv(INPUT_CSV)
df.columns = df.columns.str.strip()

# 1. EXTRACT AND CLEAN RAW DATA
# Convert ns -> us (Your JSON uses microseconds)
t_raw_us = df['#timestamp [ns]'].values / 1000.0

gyro_raw = df[['w_RS_S_x [rad s^-1]', 'w_RS_S_y [rad s^-1]', 'w_RS_S_z [rad s^-1]']].values
accel_raw = df[['a_RS_S_x [m s^-2]', 'a_RS_S_y [m s^-2]', 'a_RS_S_z [m s^-2]']].values

# Apply Bias Correction
gyro_clean = gyro_raw - GYRO_BIAS
accel_clean = accel_raw - ACCEL_BIAS

# 2. UPSAMPLE TO 200Hz
print(f"Upsampling to {TARGET_FREQ} Hz...")
t_start = t_raw_us[0]
t_end = t_raw_us[-1]
duration_sec = (t_end - t_start) / 1e6

num_samples = int(duration_sec * TARGET_FREQ)
t_new_us = np.linspace(t_start, t_end, num_samples)

# Interpolate
f_gyro = interp1d(t_raw_us, gyro_clean, axis=0, kind='linear', fill_value="extrapolate")
f_accel = interp1d(t_raw_us, accel_clean, axis=0, kind='linear', fill_value="extrapolate")

gyro_new = f_gyro(t_new_us)
accel_new = f_accel(t_new_us)

# 3. COMPUTE ORIENTATION (ALIGN GRAVITY TO Z)
# Your gravity is on Y (~9.37). We need a rotation that moves Y to Z.
print("Aligning Gravity to World Z...")

# Estimate initial gravity vector from first 50 samples
acc_static_mean = np.mean(accel_new[:50], axis=0)
print(f"  Detected Initial Gravity Vector: {acc_static_mean}")

# Target: Gravity should be [0, 0, 9.81] (or just +Z direction)
target_z = np.array([0, 0, 1])
acc_dir = acc_static_mean / np.linalg.norm(acc_static_mean)

# Calculate Rotation Matrix (Device -> World)
# Find rotation that maps acc_dir to target_z
axis = np.cross(acc_dir, target_z)
axis_len = np.linalg.norm(axis)
if axis_len < 1e-6:
    # Already aligned
    q_init = R.from_quat([0,0,0,1])
else:
    axis = axis / axis_len
    angle = np.arccos(np.clip(np.dot(acc_dir, target_z), -1.0, 1.0))
    q_init = R.from_rotvec(axis * angle)

print(f"  Computed Initial Tilt: {np.degrees(angle):.2f} degrees")

# 4. INTEGRATE GYRO
dt = np.diff(t_new_us, prepend=t_new_us[0]) * 1e-6 # us -> seconds
rotations = R.from_rotvec(gyro_new * dt[:, None])

# Accumulate orientation: q_world(t) = q_init * q_integrated(t)
q_integrated = R.from_quat([0,0,0,1])
quats = []
for i in range(num_samples):
    r_step = R.from_rotvec(gyro_new[i] * dt[i])
    q_integrated = q_integrated * r_step
    # Combine with initial alignment
    q_final = q_init * q_integrated
    quats.append(q_final.as_quat())

quats = np.array(quats) # [x, y, z, w]

# 5. ROTATE SENSOR DATA TO WORLD FRAME
# The model expects "compensated_rotated_in_World"
# So we must rotate the body frame data by the orientation we just calculated.
print("Rotating sensor data to World Frame...")
r_all = R.from_quat(quats)
accel_world = r_all.apply(accel_new)
gyro_world = r_all.apply(gyro_new)

# 6. SAVE
output = np.zeros((num_samples, 17))
output[:, 0] = t_new_us      # Time (us)
output[:, 1:4] = gyro_world  # Gyro (World Frame)
output[:, 4:7] = accel_world # Accel (World Frame)
output[:, 7:11] = quats      # Orientation
output[:, 11:14] = 0.0       # Pos (Zero)
output[:, 14:17] = 0.0       # Vel (Zero)

np.save(OUTPUT_NPY, output)

# 7. PRINT JSON
t_end_safe = t_new_us[-1] - 100000.0 # 0.1s Safety buffer

print("\nSUCCESS. COPY THIS INTO YOUR JSON:")
print("-" * 40)
print(f'"num_rows": {num_samples},')
print(f'"approximate_frequency_hz": {TARGET_FREQ},')
print(f'"t_start_us": {t_new_us[0]},')
print(f'"t_end_us": {t_end_safe}')
print("-" * 40)