import math
import streamlit as st
import pandas as pd

# ตั้งค่าหน้าเว็บให้แสดงผลเต็มหน้าจอ
st.set_page_config(
    page_title="เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด",
    page_icon="⚙️",
    layout="wide"
)

# ----------------------------------------------------------------------
# ฐานข้อมูลและโครงสร้างคำนวณ (ถอดจากโค้ดเดิม)
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
BASE_RATE_AT25 = {10: 60.0, 13: 90.0, 16: 140.0, 20: 220.0, 25: 340.0, 32: 520.0, 40: 780.0, 50: 1150.0}

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
                "duty": duty["name"], "color": duty["color_name"], "od": od, "length": length, 
                "k": k, "max_def": max_deflection(length, duty), "n": n, "total": total
            }
            if n <= cap_springs:
                best_for_duty = candidate
                break
            if best_for_duty is None or n < best_for_duty["n"]:
                best_for_duty = candidate
        if best_for_duty:
            results.append(best_for_duty)
            
    # เรียงลำดับผลลัพธ์ตามความเหมาะสม (ให้ตัวที่จำนวนสปริงผ่านและแรงพอดีขึ้นก่อน)
    results.sort(key=lambda x: (x["n"] > cap_springs, x["n"], x["total"]))
    return results

# ========================================================================
# การจัดวางหน้าตาเว็บแอป (UI ตามโครงสร้างรูปภาพ)
# ========================================================================
st.title("เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด")
st.caption("คำนวณแรงตัด แรงสตริป แรงกดรวม และแนะนำสเปกสปริงมาตรฐาน (ISO 10243)")

col_left, col_right = st.columns([1, 2.5], gap="medium")

# --- ฝั่งซ้าย: กล่องป้อนข้อมูล ---
with col_left:
    st.markdown("### **ค่าที่ป้อน**")
    
    mat_names = [m[0] for m in MATERIALS] + ["กำหนดเอง..."]
    selected_mat = st.selectbox("วัสดุแผ่นงาน (workpiece)", mat_names, index=1) # เลือกสแตนเลสเป็นค่าเริ่มต้นตามภาพ
    
    if selected_mat != "กำหนดเอง...":
        mat_data = next(m for m in MATERIALS if m[0] == selected_mat)
        default_tau, default_kstrip = mat_data[1], mat_data[2]
    else:
        default_tau, default_kstrip = 450.0, 8.0

    tau = st.number_input("แรงเฉือนวัสดุ τ (MPa)", value=default_tau, step=10.0)
    thickness = st.number_input("ความหนาแผ่น t (mm)", value=1.0, step=0.1)
    perimeter = st.number_input("เส้นรอบรูปตัดรวม L (mm)", value=220.0, step=10.0)
    kstrip = st.number_input("สัดส่วนแรงถอนแผ่น K_strip (%)", value=default_kstrip, step=0.5)
    sf = st.number_input("ค่าความปลอดภัย Safety Factor (SF)", value=1.3, step=0.1)
    
    st.markdown("---")
    x_travel = st.number_input("ระยะยุบตัวสำหรับการทำงาน (mm)", value=5.2, step=0.1)
    x_preload = st.number_input("ระยะพรีโหลดติดตั้ง preload (mm)", value=3.0, step=0.1)
    cap_springs = st.number_input("จำนวนสปริงสูงสุด", value=4, step=1)

# --- ฝั่งขวา: ผลลัพธ์และการคำนวณ ---
with col_right:
    st.markdown("### **ผลการคำนวณ**")
    
    # คำนวณค่าวิศวกรรม (หน่วยเป็น นิวตัน N)
    f_cut = perimeter * thickness * tau
    f_strip_req = f_cut * (kstrip / 100.0)
    f_design = f_strip_req * sf
    
    x_total = x_travel + x_preload # ระยะยุบรวมที่สปริงได้รับ
    
    # คำนวณสปริงที่แนะนำ
    spring_options = calculate_spring_options(x_total, f_design, cap_springs)
    
    # ดึงตัวเลือกแรกที่แนะนำที่สุดไปโชว์ในช่องสรุปผล
    best_spring = spring_options[0] if spring_options else None
    
    # 1. กล่องแสดงตัวเลขสรุป (กล่องบนตามรูป)
    c1, c2, c3 = st.columns(3)
    c1.metric("แรงตัด F_cut", f"{f_cut:,.0f} N")
    c2.metric("แรงถอนที่ต้องการ", f"{f_strip_req:,.0f} N")
    c3.metric("แรงออกแบบรวม (×SF)", f"{f_design:,.0f} N")
    
    c4, c5, c6 = st.columns(3)
    # คำนวณแรงเครื่องคิดเผื่อเป็นตัน (ประมาณค่าจากแรงตัด + แรงออกแบบ)
    f_total_machine = f_cut + f_design
    tons = f_total_machine / 9806.65 # แปลง N เป็น ตัน
    
    c4.metric("แรงเครื่องรวมโดยประมาณ (N)", f"{f_total_machine:,.0f} N")
    c5.metric("แรงเครื่องรวม (ตัน)", f"{tons:.2f} ตัน")
    if best_spring:
        c6.metric("สเปกแนะนำ (OD × L)", f"Ø{best_spring['od']} × {best_spring['length']} mm")
    else:
        c6.metric("สเปกแนะนำ (OD × L)", "ไม่พบสเปก")

    st.markdown("---")
    
    # 2. บรรทัดไฮไลท์สรุปผลลัพธ์ข้อความสีเขียวกลางหน้าจอ
    if best_spring:
        st.success(
            f"**แนะนำประเมิน:** ระดับงาน **{best_spring['duty']}** "
            f"**Ø{best_spring['od']}×{best_spring['length']} mm** จำนวน **{best_spring['n']} ตัว** "
            f"ให้แรงรวม {best_spring['total']:,.0f} N ≥ แรงออกแบบ {f_design:,.0f} N "
            f"(ระยะยุบใช้งาน {x_travel} mm ไม่เกินระยะยุบสูงสุด {best_spring['max_def']:.1f} mm)"
        )

    st.markdown("### **สปริงมาตรฐานที่แนะนำ (คัดจากผลลัพธ์รวมดีที่สุด)**")
    
    if spring_options:
        table_data = []
        for s in spring_options:
            status = "พอดี" if s["n"] <= cap_springs else "สปริงเกินเป้า"
            table_data.append({
                "ระดับงาน (Duty)": f"{s['duty']} ({s['color']})",
                "ขนาด OD×L": f"Ø{s['od']} × {s['length']} mm",
                "k (N/mm)": f"{s['k']:.1f}",
                "ยุบสูงสุด (mm)": f"{s['max_def']:.1f}",
                "จำนวน": int(s["n"]),
                "ผลรวม (N)": f"{s['total']:,.0f}",
                "สถานะ": status
            })
            
        df = pd.DataFrame(table_table_data if 'table_table_data' in locals() else table_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.error("ไม่พบข้อมูลสปริงที่เหมาะสม")
        
    st.caption("**หมายเหตุ:** ค่าคงที่สปริง (K) เป็นค่าประมาณเชิงวิศวกรรมเพื่อการประเมินเบื้องต้น อ้างอิงตามมาตรฐาน ISO 10243")
