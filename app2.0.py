import math
import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บ Streamlit ให้แสดงผลแบบเต็มหน้าจอและตั้งชื่อแท็บ
st.set_page_config(
    page_title="เครื่องคำนวณสปริงสตริปเปอร์",
    page_icon="⚙️",
    layout="wide"
)

# ----------------------------------------------------------------------
# ฐานข้อมูลวัสดุและสเปกสปริง (อิงตามลอจิกเดิมของคุณ)
# ----------------------------------------------------------------------
MATERIALS = [
    ("เหล็กเหนียวรีดเย็น (SPCC / Mild steel)", 350.0, 5.0),
    ("สแตนเลส (SUS304)",                        450.0, 8.0),
    ("อะลูมิเนียม (Al 5052)",                    170.0, 3.0),
    ("ทองแดง (Copper)",                          220.0, 4.0),
    ("ทองเหลือง (Brass)",                        280.0, 4.0),
]

ODS = [10, 13, 16, 20, 25, 32, 40, 50]
LENGTHS = [25, 32, 38, 51, 64, 76, 102, 127]
BASE_RATE_AT25 = {10: 60, 13: 90, 16: 140, 20: 220, 25: 340, 32: 520, 40: 780, 50: 1150}

DUTIES = [
    {"key": "L",  "name": "เบา (Light)",            "color_name": "เหลือง", "mult": 1.0, "max_pct": 0.45},
    {"key": "M",  "name": "กลาง (Medium)",           "color_name": "น้ำเงิน", "mult": 1.6, "max_pct": 0.40},
    {"key": "H",  "name": "หนัก (Heavy)",            "color_name": "แดง",    "mult": 2.4, "max_pct": 0.35},
    {"key": "XH", "name": "หนักพิเศษ (Extra Heavy)", "color_name": "เขียว",  "mult": 3.4, "max_pct": 0.30},
]

def spring_rate(od, length, duty):
    return BASE_RATE_AT25[od] * (25 / length) * duty["mult"]

def max_deflection(length, duty):
    return length * duty["max_pct"]

def best_for_duty(duty, x_req, f_design, cap_springs):
    best = None
    for od in ODS:
        valid_lengths = [l for l in LENGTHS if max_deflection(l, duty) >= x_req]
        if not valid_lengths:
            continue
        length = min(valid_lengths)
        k = spring_rate(od, length, duty)
        f_spring = k * x_req
        n = math.ceil(f_design / f_spring) if f_spring > 0 else float("inf")
        total = n * f_spring
        candidate = {
            "duty": duty["name"], "color": duty["color_name"], "od": od, "length": length, "k": k,
            "max_def": max_deflection(length, duty), "f_spring": f_spring, "n": n, "total": total,
        }
        if n <= cap_springs:
            return candidate
        if best is None or n < best["n"]:
            best = candidate
    return best

def recommend_springs(x_req, f_design, cap_springs):
    results = []
    for duty in DUTIES:
        cand = best_for_duty(duty, x_req, f_design, cap_springs)
        if cand:
            results.append(cand)
    results.sort(key=lambda r: (r["n"] > cap_springs, r["n"], r["od"]))
    return results

# ========================================================================
# หน้าจอเว็บแอป UI ของ Streamlit
# ========================================================================
st.title("เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด ⚙️")
st.caption("คำนวณแรงตัด แรงสตริป แรงกดรวม และแนะนำสเปกสปริงมาตรฐาน (ISO 10243)")

# แบ่งหน้าจอเป็น 2 ฝั่ง ซ้าย (ฝั่งรับข้อมูลเข้า) และ ขวา (ฝั่งแสดงผลคำนวณ)
col_input, col_result = st.columns([1, 1.5], gap="large")

with col_input:
    st.subheader("📥 ค่าที่ป้อน")
    
    # ดึงรายชื่อวัสดุมาทำเป็นตัวเลือก Dropdown
    mat_names = [m[0] for m in MATERIALS] + ["กำหนดเอง..."]
    selected_mat_name = st.selectbox("วัสดุแผ่นงาน (Workpiece)", mat_names)
    
    # กำหนดค่าเริ่มต้นของแรงเฉือนและ K-stripper ตามวัสดุที่เลือก
    if selected_mat_name != "กำหนดเอง...":
        mat_data = next(m for m in MATERIALS if m[0] == selected_mat_name)
        default_tau = mat_data[1]
        default_kstrip = mat_data[2]
    else:
        default_tau = 350.0
        default_kstrip = 5.0

    # ฟอร์มรับข้อมูลตัวเลขสำหรับการคำนวณ
    tau = st.number_input("แรงเฉือนของวัสดุ (Shear Strength, MPa)", value=default_tau, step=10.0)
    thickness = st.number_input("ความหนาแผ่นงาน (Thickness, mm)", value=1.2, step=0.1)
    perimeter = st.number_input("ความยาวเส้นรอบรูปขอบตัดรวม (Perimeter, mm)", value=220.0, step=10.0)
    kstrip = st.number_input("เปอร์เซ็นต์แรงสตริปเปอร์ (K-stripper, %)", value=default_kstrip, step=0.5)
    sf = st.number_input("ตัวคูณเผื่อความปลอดภัย (Safety Factor)", value=1.3, step=0.1)
    
    st.markdown("---")
    st.subheader("⚙️ ข้อจำกัดของสปริง")
    x_req = st.number_input("ระยะยุบตัวที่ต้องการ (Required Deflection, mm)", value=5.0, step=0.5)
    cap_springs = st.number_input("จำนวนสปริงสูงสุดที่ติดตั้งได้ (Max Springs)", value=8, step=1)

with col_result:
    st.subheader("📊 ผลการคำนวณ")
    
    # 💥 ลอจิกการคำนวณทางวิศวกรรม
    f_cutting = (perimeter * thickness * tau) / 1000  # หน่วย: กิโลนิวตัน (kN)
    f_stripping = f_cutting * (kstrip / 100)
    f_design = f_stripping * sf
    
    # แสดงตัวเลขสรุปผลแบบการ์ด 3 ช่องหลัก
    c1, c2, c3 = st.columns(3)
    c1.metric("แรงตัดรวม (F_cut)", f"{f_cutting:.2f} kN")
    c2.metric("แรงถอนที่ต้องการ (F_strip)", f"{f_stripping:.2f} kN")
    c3.metric("แรงออกแบบรวม (F_design)", f"{f_design:.2f} kN", delta=f"SF {sf}")
    
    st.markdown("---")
    st.subheader("💡 ตารางสปริงที่แนะนำ (ISO 10243)")
    
    # ทำการแปลงแรงออกแบบหน่วย kN ไปเป็นหน่วยที่แมตช์กับฟังก์ชันแนะนำสปริงเดิม
    # (เนื่องจากในฟังก์ชันดั้งเดิมเปรียบเทียบค่าแรงในสเกลที่สัมพันธ์กัน)
    recs = recommend_springs(x_req, f_design * 1000, cap_springs) 
    
    if recs:
        data_table = []
        for r in recs:
            # คำนวณหาแรงกดรวมของชุดสปริงให้ออกมาเป็นหน่วย kN
            total_kn = (r["total"] / 1000) 
            status = "✅ ผ่าน (จำนวนพอดี)" if r["n"] <= cap_springs else "⚠️ จำนวนสปริงเกินเป้า"
            
            data_table.append({
                "ระดับงาน (Duty)": r["duty"],
                "สีมาตรฐาน": r["color"],
                "ขนาด OD (mm)": r["od"],
                "ความยาว (mm)": r["length"],
                "จำนวนที่ต้องใช้ (ตัว)": r["n"],
                "แรงกดรวม (kN)": f"{total_kn:.2f}",
                "สถานะตรวจสอบ": status
            })
            
        df = pd.DataFrame(data_table)
        # แสดงผลลัพธ์เป็นตาราง Interactive บนหน้าเว็บ
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error("❌ ไม่พบสเปกสปริงที่เหมาะสมกับระยะยุบตัวและแรงที่ต้องการในระบบ")
