"""
สคริปต์ฝึกโมเดล Machine Learning (Neural Network) สำหรับแอปคำนวณสปริง
=====================================================================
รันสคริปต์นี้ครั้งเดียวเพื่อสร้างไฟล์โมเดล (models/*.joblib) ที่แอป
streamlit_app.py จะโหลดไปใช้ทำนายผลคู่ขนานกับสูตรวิศวกรรม

วิธีรัน:
    python train_model.py

แนวคิดเดียวกับการทดลองก่อนหน้า (generate_experiment.py) คือ:
  1) สร้างข้อมูลจำลองจากสูตรวิศวกรรม/กฎ ISO 10243 เดิม (ground truth)
  2) ฝึก Neural Network (MLP) ให้เรียนรู้เลียนแบบการตัดสินใจ
  3) บันทึกโมเดลที่ฝึกแล้วเป็นไฟล์ เพื่อให้แอปเรียกใช้งานได้ทันทีโดยไม่ต้อง
     ฝึกใหม่ทุกครั้งที่เปิดแอป (โหลดไฟล์เร็วกว่าฝึกใหม่มาก)
"""

import math
import os
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier, MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score

RNG = np.random.default_rng(42)

# ----------------------------------------------------------------------
# สูตรวิศวกรรมเดิม (เหมือนใน streamlit_app.py) ใช้สร้างข้อมูลจำลอง
# ----------------------------------------------------------------------
ODS = [10, 13, 16, 20, 25, 32, 40, 50]
LENGTHS = [25, 32, 38, 51, 64, 76, 102, 127]
BASE_RATE_AT25 = {10: 60.0, 13: 90.0, 16: 140.0, 20: 220.0, 25: 340.0,
                   32: 520.0, 40: 780.0, 50: 1150.0}

DUTIES = [
    {"key": "L",  "name": "เบา (Light)",            "mult": 1.0, "max_pct": 0.45},
    {"key": "M",  "name": "กลาง (Medium)",           "mult": 1.6, "max_pct": 0.40},
    {"key": "H",  "name": "หนัก (Heavy)",            "mult": 2.4, "max_pct": 0.35},
    {"key": "XH", "name": "หนักพิเศษ (Extra Heavy)", "mult": 3.4, "max_pct": 0.30},
]
DUTY_NAMES = [d["name"] for d in DUTIES]


def spring_rate(od, length, duty):
    return BASE_RATE_AT25[od] * (25 / length) * duty["mult"]


def max_deflection(length, duty):
    return length * duty["max_pct"]


def calculate_spring_options(x_total, f_design, cap_springs):
    results = []
    for duty in DUTIES:
        best_for_duty = None
        for od in ODS:
            valid_lengths = [l for l in LENGTHS if max_deflection(l, duty) >= x_total]
            if not valid_lengths:
                continue
            length = min(valid_lengths)
            k = spring_rate(od, length, duty)
            f_spring = k * x_total
            n = math.ceil(f_design / f_spring) if f_spring > 0 else 1
            total = n * f_spring
            candidate = {
                "duty_idx": DUTIES.index(duty), "duty": duty["name"],
                "od": od, "length": length, "k": k,
                "max_def": max_deflection(length, duty), "n": n, "total": total
            }
            if n <= cap_springs:
                best_for_duty = candidate
                break
            if best_for_duty is None or n < best_for_duty["n"]:
                best_for_duty = candidate
        if best_for_duty:
            results.append(best_for_duty)
    results.sort(key=lambda x: (x["n"] > cap_springs, x["n"], x["total"]))
    return results


# ----------------------------------------------------------------------
# 1) สร้างข้อมูลจำลอง
# ----------------------------------------------------------------------
N_SAMPLES = 6000
tau = RNG.uniform(150, 500, N_SAMPLES)
thickness = RNG.uniform(0.3, 4.0, N_SAMPLES)
perimeter = RNG.uniform(50, 800, N_SAMPLES)
kstrip = RNG.uniform(2.0, 12.0, N_SAMPLES)
sf = RNG.uniform(1.1, 1.8, N_SAMPLES)
x_travel = RNG.uniform(1.0, 15.0, N_SAMPLES)
x_preload = RNG.uniform(0.5, 8.0, N_SAMPLES)
cap_springs = RNG.integers(2, 9, N_SAMPLES)

rows = []
for i in range(N_SAMPLES):
    f_cut = perimeter[i] * thickness[i] * tau[i]
    f_strip_req = f_cut * (kstrip[i] / 100.0)
    f_design = f_strip_req * sf[i]
    x_total = x_travel[i] + x_preload[i]
    options = calculate_spring_options(x_total, f_design, int(cap_springs[i]))
    if not options:
        continue
    best = options[0]
    rows.append({
        "tau": tau[i], "thickness": thickness[i], "perimeter": perimeter[i],
        "kstrip": kstrip[i], "sf": sf[i], "x_travel": x_travel[i],
        "x_preload": x_preload[i], "cap_springs": cap_springs[i],
        "f_design": f_design, "x_total": x_total,
        "duty_idx": best["duty_idx"], "n_springs": best["n"],
    })

df = pd.DataFrame(rows)
print(f"สร้างข้อมูลจำลอง {len(df)} แถว")

FEATURES = ["tau", "thickness", "perimeter", "kstrip", "sf",
            "x_travel", "x_preload", "cap_springs", "f_design", "x_total"]
X = df[FEATURES].values
y_duty = df["duty_idx"].values
y_n = df["n_springs"].values

X_train, X_test, yduty_train, yduty_test, yn_train, yn_test = train_test_split(
    X, y_duty, y_n, test_size=0.2, random_state=42
)

# ----------------------------------------------------------------------
# 2) ฝึกโมเดล (ใช้ Pipeline เพื่อรวม StandardScaler + MLP ไว้ในไฟล์เดียว)
# ----------------------------------------------------------------------
pipe_duty = Pipeline([
    ("scaler", StandardScaler()),
    ("mlp", MLPClassifier(hidden_layer_sizes=(32, 16), activation="relu",
                           max_iter=2000, random_state=42)),
])
pipe_duty.fit(X_train, yduty_train)
acc = accuracy_score(yduty_test, pipe_duty.predict(X_test))

pipe_n = Pipeline([
    ("scaler", StandardScaler()),
    ("mlp", MLPRegressor(hidden_layer_sizes=(32, 16), activation="relu",
                          max_iter=2000, random_state=42)),
])
pipe_n.fit(X_train, yn_train)
yn_pred = pipe_n.predict(X_test)
mae = mean_absolute_error(yn_test, yn_pred)
r2 = r2_score(yn_test, yn_pred)

print(f"Model A (ระดับงานสปริง) Accuracy = {acc*100:.1f}%")
print(f"Model B (จำนวนสปริง)   MAE = {mae:.3f} ตัว, R^2 = {r2:.3f}")

# ----------------------------------------------------------------------
# 3) บันทึกโมเดล
# ----------------------------------------------------------------------
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

joblib.dump(pipe_duty, os.path.join(MODELS_DIR, "pipe_duty.joblib"))
joblib.dump(pipe_n, os.path.join(MODELS_DIR, "pipe_n.joblib"))

meta = {
    "features": FEATURES,
    "duty_names": DUTY_NAMES,
    "duty_accuracy": acc,
    "n_mae": mae,
    "n_r2": r2,
    "n_samples": len(df),
}
joblib.dump(meta, os.path.join(MODELS_DIR, "meta.joblib"))

print(f"\nบันทึกโมเดลที่ {MODELS_DIR}/ เรียบร้อย")
print("ไฟล์: pipe_duty.joblib, pipe_n.joblib, meta.joblib")
