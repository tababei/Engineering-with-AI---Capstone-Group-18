import numpy as np
import pandas as pd

def generate_realistic_tlio(motion_type="running"):
    num_rows = 59851
    freq = 200.0
    dt = 1.0 / freq
    t_start_us = 692679546.0
    
    # Setup Timestamps
    t_us = t_start_us + np.arange(num_rows) * (1e6 / freq)
    t_sec = np.arange(num_rows) * dt

    # DEFINING NOISE 
    # Typical values for a smartphone IMU
    acc_sigma = 0.012  # m/s^2
    gyr_sigma = 0.0015 # rad/s
    acc_bias_drift = 0.0005 # m/s^2 per sample

    # Generate Clean Motion Signals
    acc_clean = np.zeros((num_rows, 3))
    gyr_clean = np.zeros((num_rows, 3))
    
    if motion_type == "running":
        # --- SWAPPED AXES FOR Y-GRAVITY ---
        # 1. Vertical bounce (Impacts) -> NOW ON Y (Index 1)
        # We also add the impact harmonic here.
        acc_clean[:, 1] = 5.0 * np.sin(2 * np.pi * 3 * t_sec) + 1.5 * np.sin(2 * np.pi * 6 * t_sec)
        
        # 2. Forward thrust -> NOW ON Z (Index 2)
        # (Assuming the device is held upright, Z is often "Forward" relative to the screen)
        acc_clean[:, 2] = 2.0 * np.abs(np.sin(2 * np.pi * 1.5 * t_sec))
        
        # 3. Lateral sway (Roll) -> KEEPS ON X (Index 0)
        # Rotating the device around X doesn't change X-axis logic.
        gyr_clean[:, 0] = 0.15 * np.cos(2 * np.pi * 1.5 * t_sec)

    # 4. SENSOR REALISM LAYER
    # Add White Noise
    acc_noise = np.random.normal(0, acc_sigma, (num_rows, 3))
    gyr_noise = np.random.normal(0, gyr_sigma, (num_rows, 3))
    
    # Add Bias Random Walk (Slow drift)
    acc_bias = np.cumsum(np.random.normal(0, acc_bias_drift, (num_rows, 3)), axis=0)
    
    # 5. FINAL ASSEMBLY (Crucial: Add Gravity)
    # TLIO needs gravity (9.81) to orient itself!
    acc_final = acc_clean + acc_noise + acc_bias
    acc_final[:, 1] += 9.81 
    
    gyr_final = gyr_clean + gyr_noise

    # 6. Formatting for the 17-parameter requirement
    headers = ["ts_us", "gyr_x", "gyr_y", "gyr_z", "acc_x", "acc_y", "acc_z", 
               "q_x", "q_y", "q_z", "q_w", "pos_x", "pos_y", "pos_z", "vel_x", "vel_y", "vel_z"]
    
    data = np.zeros((num_rows, 17))
    data[:, 0] = t_us
    data[:, 1:4] = gyr_final
    data[:, 4:7] = acc_final
    data[:, 10] = 1.0 # Initial Quaternion W
    
    # Simple integration for Pos/Vel Ground Truth
    # Note: We integrate acc_clean (movement only), NOT acc_final (which has gravity)
    vel_gt = np.cumsum(acc_clean, axis=0) * dt
    pos_gt = np.cumsum(vel_gt, axis=0) * dt
    data[:, 11:14] = pos_gt
    data[:, 14:17] = vel_gt

    filename = f"realistic_{motion_type}_Y_gravity.csv"
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(filename, index=False)
    print(f"Generated {filename}")

if __name__ == "__main__":
    generate_realistic_tlio("running")
