#!/usr/bin/env python3
import argparse
import json
import os
import shutil
from typing import Iterable, Tuple

import numpy as np


CSV_HEADER = (
    "#timestamp [ns], temperature [degC], w_RS_S_x [rad s^-1], "
    "w_RS_S_y [rad s^-1], w_RS_S_z [rad s^-1], a_RS_S_x [m s^-2], "
    "a_RS_S_y [m s^-2], a_RS_S_z [m s^-2]"
)

RESAMPLED_COLUMNS = [
    "ts_us(1)",
    "gyr_compensated_rotated_in_World(3)",
    "acc_compensated_rotated_in_World(3)",
    "qxyzw_World_Device(4)",
    "pos_World_Device(3)",
    "vel_World(3)",
]


def _load_jsonl(path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    accel_times = []
    accel_vals = []
    gyro_times = []
    gyro_vals = []

    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            sensor = item.get("sensor") or {}
            stype = sensor.get("type")
            values = sensor.get("values")
            t = item.get("time")
            if t is None or values is None:
                continue
            if stype == "accelerometer":
                accel_times.append(float(t))
                accel_vals.append(values)
            elif stype == "gyroscope":
                gyro_times.append(float(t))
                gyro_vals.append(values)

    if not accel_times or not gyro_times:
        raise RuntimeError(f"Missing accel/gyro data in {path}")

    accel_times = np.asarray(accel_times, dtype=np.float64)
    accel_vals = np.asarray(accel_vals, dtype=np.float64)
    gyro_times = np.asarray(gyro_times, dtype=np.float64)
    gyro_vals = np.asarray(gyro_vals, dtype=np.float64)

    accel_order = np.argsort(accel_times)
    gyro_order = np.argsort(gyro_times)
    return (
        accel_times[accel_order],
        accel_vals[accel_order],
        gyro_times[gyro_order],
        gyro_vals[gyro_order],
    )


def _interp_stream(
    times: np.ndarray, values: np.ndarray, target_times: np.ndarray
) -> np.ndarray:
    if len(times) < 2:
        raise RuntimeError("Not enough samples to interpolate")
    out = []
    for axis in range(values.shape[1]):
        out.append(np.interp(target_times, times, values[:, axis]))
    return np.stack(out, axis=1)


def _write_imu_samples_csv(
    path: str,
    target_times: np.ndarray,
    gyro_vals: np.ndarray,
    accel_vals: np.ndarray,
) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(CSV_HEADER + "\n")
        for t, g, a in zip(target_times, gyro_vals, accel_vals):
            ts_ns = int(round(t * 1e9))
            handle.write(
                f"{ts_ns}, 0, {g[0]:.7f}, {g[1]:.7f}, {g[2]:.7f}, "
                f"{a[0]:.7f}, {a[1]:.7f}, {a[2]:.7f}\n"
            )


def _write_resampled(
    out_dir: str,
    target_times: np.ndarray,
    gyro_vals: np.ndarray,
    accel_vals: np.ndarray,
    resample_hz: float,
) -> None:
    ts_us = target_times * 1e6
    q_xyzw = np.tile(np.array([0.0, 0.0, 0.0, 1.0], dtype=np.float64), (len(ts_us), 1))
    pos = np.zeros((len(ts_us), 3), dtype=np.float64)
    vel = np.zeros((len(ts_us), 3), dtype=np.float64)

    data = np.column_stack([ts_us, gyro_vals, accel_vals, q_xyzw, pos, vel])
    np.save(os.path.join(out_dir, "imu0_resampled.npy"), data)

    description = {
        "columns_name(width)": RESAMPLED_COLUMNS,
        "num_rows": int(len(ts_us)),
        "approximate_frequency_hz": float(resample_hz),
        "t_start_us": float(ts_us[0]) if len(ts_us) else 0.0,
        "t_end_us": float(ts_us[-1]) if len(ts_us) else 0.0,
    }
    with open(
        os.path.join(out_dir, "imu0_resampled_description.json"),
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(description, handle, indent=4)
        handle.write("\n")


def _convert_folder(
    source_dir: str,
    output_dir: str,
    calib_template: str,
    resample_hz: float,
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    shutil.copyfile(calib_template, os.path.join(output_dir, "calibration.json"))

    jsonl_path = os.path.join(source_dir, "data.jsonl")
    accel_times, accel_vals, gyro_times, gyro_vals = _load_jsonl(jsonl_path)

    if len(gyro_times) >= len(accel_times):
        target_times = gyro_times
        accel_interp = _interp_stream(accel_times, accel_vals, target_times)
        gyro_interp = gyro_vals
    else:
        target_times = accel_times
        gyro_interp = _interp_stream(gyro_times, gyro_vals, target_times)
        accel_interp = accel_vals

    _write_imu_samples_csv(
        os.path.join(output_dir, "imu_samples_0.csv"),
        target_times,
        gyro_interp,
        accel_interp,
    )

    start_time = max(accel_times[0], gyro_times[0])
    end_time = min(accel_times[-1], gyro_times[-1])
    if end_time <= start_time:
        raise RuntimeError("Invalid time range for resampling")
    step = 1.0 / resample_hz
    resampled_times = np.arange(start_time, end_time, step, dtype=np.float64)
    gyro_resampled = _interp_stream(gyro_times, gyro_vals, resampled_times)
    accel_resampled = _interp_stream(accel_times, accel_vals, resampled_times)
    _write_resampled(output_dir, resampled_times, gyro_resampled, accel_resampled, resample_hz)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert raw folders into example-format IMU outputs."
    )
    parser.add_argument(
        "source_dirs",
        nargs="+",
        help="Source folders containing data.jsonl",
    )
    parser.add_argument(
        "--output-root",
        default="converted_example",
        help="Root folder for converted outputs",
    )
    parser.add_argument(
        "--calib-template",
        default=os.path.join("example", "calibration.json"),
        help="Path to an example-format calibration.json to copy",
    )
    parser.add_argument(
        "--resample-hz",
        type=float,
        default=200.0,
        help="Target frequency for imu0_resampled.npy",
    )
    parser.add_argument(
        "--suffix",
        default="_out",
        help="Suffix to append to output folder names",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not os.path.isfile(args.calib_template):
        raise SystemExit(f"Missing calibration template: {args.calib_template}")
    os.makedirs(args.output_root, exist_ok=True)

    for source_dir in args.source_dirs:
        name = os.path.basename(os.path.normpath(source_dir))
        output_dir = os.path.join(args.output_root, f"{name}{args.suffix}")
        _convert_folder(source_dir, output_dir, args.calib_template, args.resample_hz)
        print(f"Converted {source_dir} -> {output_dir}")


if __name__ == "__main__":
    main()
