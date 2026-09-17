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
# ฐานข้อมูลมาตรฐานสปริง ISO 10243
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

# ----------------------------------------------------------------------
# ฟังก์ชันคำนวณทางวิศวกรรมสปริง
# ----------------------------------------------------------------------
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
    results.sort(key=lambda x: (x["n"] > cap_springs, x["n"], x["total"]))
    return results

# ========================================================================
# การจัดวางหน้าจอเว็บ (UI ของ Streamlit)
# ========================================================================
st.title("เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด ⚙️")
st.caption("คำนวณแรงตัด แรงสตริป แรงกดรวม และแนะนำสเปกสปริงมาตรฐาน (ISO 10243)")

# --- เพิ่มคำอธิบายความหมายของแต่ละตัวแปรในส่วนสูตรคำนวณตามรูปภาพ ---
with st.expander("📘 คลิกเพื่อดูสูตรการคำนวณทางวิศวกรรมที่ใช้ในระบบ (Formula Details)"):
    st.markdown("### **สูตรและที่มาของการคำนวณ**")
    st.markdown("ระบบจะประมวลผลตามลำดับสูตรคำนวณมาตรฐานสากลของแม่พิมพ์กดตัด พร้อมความหมายตัวแปรดังนี้:")
    
    st.latex(r"1.\quad F_{cut} = L \times t \times \tau")
    st.markdown("""
    *   $F_{cut}$ = แรงตัดชิ้นงานรวม (นิวตัน, N)
    *   $L$ = เส้นรอบรูปขอบตัดรวมทั้งหมด (mm)
    *   $t$ = ความหนาของแผ่นวัสดุ (mm)
    *   $\\tau$ = ค่าความต้านทานแรงเฉือนของวัสดุ (Shear Strength, MPa หรือ N/mm²)
    """)
    st.markdown("---")
    
    st.latex(r"2.\quad F_{strip} = F_{cut} \times \left(\frac{K_{strip}}{100}\right)")
    st.markdown("""
    *   $F_{strip}$ = แรงถอนชิ้นงานที่จำเป็น (นิวตัน, N)
    *   $K_{strip}$ = เปอร์เซ็นต์สัดส่วนแรงถอนแผ่นงาน (Stripping Force Factor, %)
    """)
    st.markdown("---")
    
    st.latex(r"3.\quad F_{design} = F_{strip} \times SF")
    st.markdown("""
    *   $F_{design}$ = แรงออกแบบรวมสำหรับสปริงหลังจากเผื่อค่าความปลอดภัยแล้ว (นิวตัน, N)
    *   $SF$ = ตัวคูณเผื่อความปลอดภัย (Safety Factor)
    """)
    st.markdown("---")
    
    st.latex(r"4.\quad X_{total} = X_{travel} + X_{preload}")
    st.markdown("""
    *   $X_{total}$ = ระยะยุบตัวรวมสะสมที่เกิดขึ้นกับสปริง (mm)
    *   $X_{travel}$ = ระยะยุบตัวจากการช่วงชักทำงานจริง (Working Stroke, mm)
    *   $X_{preload}$ = ระยะยุบตัวจากการกดพรีโหลดตั้งต้นตอนประกอบ (Preload, mm)
    """)
    st.markdown("---")
    
    st.latex(r"5.\quad n = \lceil \frac{F_{design}}{K \times X_{total}} \rceil")
    st.markdown("""
    *   $n$ = จำนวนสปริงที่จำเป็นต้องใช้ติดตั้ง (ตัว) โดยปัดเศษขึ้นเป็นจำนวนเต็มเสมอ ($\\lceil \\rceil$)
    *   $K$ = ค่าคงที่สปริง 1 ตัว (Spring Rate, N/mm) อ้างอิงตามสเปกมาตรฐาน ISO 10243
    """)
    st.markdown("---")
    
    st.latex(r"6.\quad F_{machine} = F_{cut} + F_{design}")
    st.markdown("""
    *   $F_{machine}$ = แรงรวมทั้งหมดที่กดลงเครื่องปั๊มโดยประมาณ (นิวตัน, N) เป็นแรงกระทำร่วมระหว่างแรงตัดชิ้นงานและแรงต้านจากสปริงสตริปเปอร์
    """)
    st.markdown("---")
    
    st.latex(r"7.\quad \text{Tons} = \frac{F_{machine}}{9806.65}")
    st.markdown("""
    *   $\text{Tons}$ = ขนาดแรงรวมกดลงเครื่องปั๊มเมื่อแปลงหน่วยจาก นิวตัน (N) เป็น **ตันแรง (Metric Tons)**
    *   $9806.65$ = ค่าคงที่แรงโน้มถ่วงมาตรฐานเพื่อใช้ในการแปลงหน่วยแรง ($1\text{ kgf} \approx 9.80665\text{ N}$)
    """)

st.markdown("---")

col_left, col_right = st.columns([1, 2.5], gap="medium")

# --- ฝั่งซ้าย: กล่องป้อนข้อมูลดิบ ---
with col_left:
    st.markdown("### **ค่าที่ป้อน**")
    
    mat_names = [m for m in MATERIALS] + ["กำหนดเอง..."]
    selected_mat = st.selectbox("วัสดุแผ่นงาน (workpiece)", mat_names, index=1)
    st.caption("💡 ชนิดของแผ่นโลหะที่จะนำมาปั๊มตัด ระบบจะดึงค่าแรงเฉือนมาตรฐานมาให้เบื้องต้น")
    
    if selected_mat != "กำหนดเอง...":
        mat_data = next(m for m in MATERIALS if m == selected_mat)
        default_tau = float(mat_data)
        default_kstrip = float(mat_data)
    else:
        default_tau = 450.0
        default_kstrip = 8.0

    st.markdown("") 
    tau = st.number_input("แรงเฉือนวัสดุ τ (MPa)", value=default_tau, step=10.0)
    st.caption("💡 Shear Strength: ค่าความต้านทานแรงเฉือนของวัสดุ หาได้จากตารางสเปกโลหะหรือคู่มือวิศวกรรม")
    
    thickness = st.number_input("ความหนาแผ่น t (mm)", value=1.0, step=0.1)
    st.caption("💡 Sheet Thickness: ความหนาของแผ่นเหล็กหรือแผ่นงานจริงที่จะถูกกดตัด")
    
    perimeter = st.number_input("เส้นรอบรูปตัดรวม L (mm)", value=220.0, step=10.0)
    st.caption("💡 Total Cutting Perimeter: ความยาวเส้นรอบขอบของชิ้นงานตรงบริเวณที่ถูกใบมีด/พั้นช์ตัดทั้งหมดรวมกัน")
    
    kstrip = st.number_input("สัดส่วนแรงถอนแผ่น K_strip (%)", value=default_kstrip, step=0.5)
    st.caption("💡 Stripping Force Factor: สัดส่วนแรงต้านที่จะดึงเศษชิ้นงานหรือแผ่นงานออกจากพั้นช์ตัด")
    
    sf = st.number_input("ค่าความปลอดภัย Safety Factor (SF)", value=1.3, step=0.1)
    st.caption("💡 ค่าเผื่อความปลอดภัยทางวิศวกรรม เพื่อป้องกันปัญหาสปริงล้าหรือแรงกดไม่พอในระยะยาว")
    
    st.markdown("---")
    st.markdown("### **ข้อมูลระยะชักสปริง**")
    
    x_travel = st.number_input("ระยะยุบตัวสำหรับการทำงาน (mm)", value=5.2, step=0.1)
    st.caption("💡 Working Stroke: ระยะที่แผ่นสปริงจะต้องยุบลงไปจริงๆ ตอนที่กลไกแม่พิมพ์กดลงมาทำงาน")
    
    x_preload = st.number_input("ระยะพรีโหลดติดตั้ง preload (mm)", value=3.0, step=0.1)
    st.caption("💡 Preload: ระยะที่สปริงถูกกดบีบไว้ตั้งแต่ตอนประกอบชุดแม่พิมพ์ เพื่อให้สปริงมีแรงกดตั้งต้นส่งผลทันที")
    
    cap_springs = st.number_input("จำนวนสปริงสูงสุด", value=4, step=1)
    st.caption("💡 Maximum Springs: ข้อจำกัดของพื้นที่ในแม่พิมพ์ ว่าสามารถใส่สปริงลงไปได้มากที่สุดกี่ตัว")

# --- ฝั่งขวา: คำนวณสูตรและแสดงผลลัพธ์ ---
with col_right:
    st.markdown("### **ผลการคำนวณ**")
    
    f_cut = perimeter * thickness * tau
    f_strip_req = f_cut * (kstrip / 100.0)
    f_design = f_strip_req * sf
    x_total = x_travel + x_preload 
    
    spring_options = calculate_spring_options(x_total, f_design, cap_springs)
    best_spring = spring_options if spring_options else None
    
    f_total_machine = f_cut + f_design
    tons = f_total_machine / 9806.65 
    
    c1, c2, c3 = st.columns(3)
    c1.metric("แรงตัด F_cut", f"{f_cut:,.0f} N")
    c2.metric("แรงถอนที่ต้องการ", f"{f_strip_req:,.0f} N")
    c3.metric("แรงออกแบบรวม (×SF)", f"{f_design:,.0f} N")
    
    c4, c5, c6 = st.columns(3)
    c4.metric("แรงเครื่องรวมโดยประมาณ (N)", f"{f_total_machine:,.0f} N")
    c5.metric("แรงเครื่องรวม (ตัน)", f"{tons:.2f} ตัน")
    if best_spring:
        c6.metric("สเปกแนะนำ (OD × L)", f"Ø{best_spring['od']} × {best_spring['length']} mm")
    else:
        c6.metric("สเปกแนะนำ (OD × L)", "ไม่พบสเปก")

    st.markdown("---")
    
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
