import streamlit as st

# 1. ตั้งค่าหน้าตาแอปพลิเคชัน
st.set_page_config(
    page_title="Advanced Springback & Tonnage App",
    page_icon="⚙️",
    layout="centered"
)

# ฐานข้อมูลพารามิเตอร์วัสดุทางวิศวกรรม (เพิ่มค่า Ultimate Tensile Strength: UTS เพื่อคำนวณแรงกด)
MATERIAL_DATA = {
    "เหล็กแผ่นทั่วไป (Mild Steel / SS400)": {"E": 207000.0, "YS": 250.0, "UTS": 400.0},
    "เหล็กกล้ากำลังสูง (High-Strength Steel)": {"E": 210000.0, "YS": 550.0, "UTS": 700.0},
    "อลูมิเนียมแผ่น (Aluminum AL5052)": {"E": 70000.0, "YS": 195.0, "UTS": 230.0},
    "สแตนเลสแผ่น (Stainless SUS304)": {"E": 193000.0, "YS": 290.0, "UTS": 520.0}
}

# ส่วนหัวของแอปพลิเคชัน
st.caption("⚙️ โปรแกรมคำนวณงานวิศวกรรมแม่พิมพ์ (Die & Stamping Pro Suite)")
st.title("Springback & Press Tonnage Calculator")
st.write("ระบบคำนวณการดีดกลับผิวโลหะ ขนาดความยาวสปริง และขนาดแรงกดตันของเครื่องปั๊ม")
st.markdown("---")

# --- โซนอินพุต 1: ข้อมูลชิ้นงาน ---
st.header("📋 1. ข้อมูลสเปกวัสดุชิ้นงาน")
mat_choice = st.selectbox("เลือกชนิดวัสดุ:", list(MATERIAL_DATA.keys()))
sheet_t = st.selectbox("เลือกความหนาของแผ่นชิ้นงาน, t (mm):", [0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0], index=5)

# ดึงข้อมูลพารามิเตอร์ภายใน
modulus_E = MATERIAL_DATA[mat_choice]["E"]
yield_YS = MATERIAL_DATA[mat_choice]["YS"]
uts_val = MATERIAL_DATA[mat_choice]["UTS"]
st.caption(f"ดัชนีวัสดุ -> E: {modulus_E} MPa | σ_y: {yield_YS} MPa | Tensile Strength: {uts_val} MPa")

# --- โซนอินพุต 2: ขนาดแม่พิมพ์และระยะกดชัก ---
st.header("📐 2. พารามิเตอร์ขนาดแม่พิมพ์และระยะชัก")
punch_R = st.number_input("รัศมีปลายพั้นช์ดัดงอ, R_i (mm):", min_value=0.1, value=4.0, step=0.1)

# ติ๊กเลือกมุมมาตรฐาน 90 องศา
lock_90 = st.checkbox("ใช้มุมพับมาตรฐาน 90 องศา (Standard 90° V-Bend)", value=True)
if lock_90:
    target_angle = 90.0
    st.info("🔒 ระบบล็อกมุมดัดพับไว้ที่ 90.0 องศาอัตโนมัติ")
else:
    target_angle = st.number_input("ระบุมุมพับชิ้นงานที่ต้องการกำหนดเอง (องศา °):", min_value=1.0, max_value=180.0, value=90.0, step=1.0)

die_stroke = st.number_input("ระยะกดชักของแม่พิมพ์, Stroke (mm):", min_value=0.1, value=15.0, step=1.0)

# ช่องอินพุตคำนวณแรงกดเครื่องพับที่เพิ่มเข้ามาใหม่
st.markdown(" ")
st.subheader("🏭 ส่วนคำนวณแรงกดดันเครื่องจักร (Tonnage Parameters)")
bend_length = st.number_input("ระบุความยาวของแนวพับชิ้นงาน, L (mm):", min_value=1.0, value=100.0, step=10.0)
st.markdown("---")

# --- โซนประมวลผลคำนวณทางวิศวกรรม ---
calc_factor = (punch_R * yield_YS) / (modulus_E * sheet_t)
springback_factor_Ks = 1 - 3 * calc_factor + 4 * (calc_factor ** 3)

if springback_factor_Ks > 1 or springback_factor_Ks < 0:
    st.error("⚠️ ข้อผิดพลาด: พารามิเตอร์อินพุตอยู่นอกขอบเขตการคำนวณตามทฤษฎี กรุณาตรวจสอบสัดส่วนความหนาชิ้นงาน")
else:
    # 1. คำนวณค่ามุมและสปริงแบ็ค
    final_angle_tf = target_angle * springback_factor_Ks
    compensation_punch = target_angle * (2 - springback_factor_Ks)
    
    # 2. คำนวณสีสปริงและ Free Length
    load_index = sheet_t * yield_YS
    if load_index <= 250:
        color_label, color_code, compress_ratio = "สีเขียว (Light Load)", "#10B981", 0.40
        reason_text = "ภาระงานเบา ชิ้นงานบาง แรงสปริงแบ็คต่ำ สปริงขยับตัวได้ดี ยืดอายุแผ่นพิมพ์"
    elif load_index <= 500:
        color_label, color_code, compress_ratio = "สีน้ำเงิน (Medium Load)", "#2563EB", 0.32
        reason_text = "ภาระงานปานกลาง เหมาะสำหรับงานแผ่นเหล็กทั่วไป ทนรอบปั๊มได้สูง"
    elif load_index <= 800:
        color_label, color_code, compress_ratio = "สีแดง (Heavy Load)", "#DC2626", 0.24
        reason_text = "ภาระงานหนัก วัสดุหนา/แข็ง ต้องใช้แรงกดสูงเพื่อต้านการดีดตัวกลับ"
    else:
        color_label, color_code, compress_ratio = "สีเหลือง (Extra Heavy Load)", "#F59E0B", 0.20
        reason_text = "ภาระงานหนักพิเศษ สำหรับงานเหล็กโครงสร้างหนา ต้านแรงกดกระแทกสูงสุด"
    calculated_L0 = die_stroke / compress_ratio

    # 3. คำนวณแรงกดพับแม่พิมพ์ (Bending Force) ในหน่วยกิโลนิวตัน (kN) และแปลงเป็นตัน (Tons)
    # อ้างอิงมาตรฐานร่องเปิด Die Opening width (V) = 8 * ความหนาแผ่น (t)
    v_die_opening = 8.0 * sheet_t
    force_kN = (1.42 * uts_val * bend_length * (sheet_t ** 2)) / v_die_opening
    force_tons = force_kN / 9.80665  # แปลงค่าจาก kN เป็น Metric Tons
    
    # เผื่อค่า Safety Factor 20% เพื่อความปลอดภัยหน้างานจริง ไม่ให้เครื่องทำงานหนักเกิน 100%
    recommended_press_tonnage = force_tons * 1.20

    # --- โซนแสดงผลลัพธ์บนหน้าต่างแอปพลิเคชัน ---
    st.header("📊 3. ผลการวิเคราะห์หน้างานและการเลือกเครื่องจักร")
    
    # แสดงค่ามุมสปริงแบ็ค
    st.subheader("📐 มิติมุมและการชดเชยแม่พิมพ์")
    col1, col2, col3 = st.columns(3)
    col1.metric("สัมประสิทธิ์ Ks", f"{springback_factor_Ks:.3f}")
    col2.metric("มุมที่จะได้จริง (θ_f)", f"{final_angle_tf:.2f} °")
    col3.metric("มุมพั้นช์ที่ต้องออกแบบ", f"{compensation_punch:.2f} °")
    
    # แสดงสเปกแรงกดของเครื่องปั๊ม (Feature ใหม่โดดเด่นโดนใจอาจารย์)
    st.markdown(" ")
    st.subheader("🏭 การประเมินขนาดแรงกดเครื่องปั๊มพับ (Press Tonnage Requirement)")
    col_f1, col_f2 = st.columns(2)
    col_f1.metric("แรงกดดัดงอสุทธิ (Net Force)", f"{force_tons:.2f} Tons")
    col_f2.metric("ขนาดเครื่องปั๊มที่แนะนำ (+Safety 20%)", f"{recommended_press_tonnage:.1f} Tons", delta="ปลอดภัยหน้างาน")
    
    # แสดงสเปกสปริงแม่พิมพ์
    st.markdown(" ")
    st.subheader("🔩 สเปกสปริงแม่พิมพ์ที่แนะนำ (Die Spring)")
    st.markdown(
        f"<div style='background-color:{color_code}; padding:12px; border-radius:6px; text-align:center; margin-bottom:15px.'>"
        f"<h3 style='color:white; margin:0px; font-weight:bold;'>สปริงแม่พิมพ์ที่แนะนำ: {color_label}</h3>"
        f"</div>", 
        unsafe_allow_html=True
    )
    st.info(f"💡 **เหตุผลอ้างอิงเชิงวิศวกรรม:** {reason_text}")
    st.success(f"📏 **ขนาดความยาวอิสระของสปริงที่ควรเลือกใช้ (Free Length - L0):** {calculated_L0:.2f} mm")

st.markdown("---")
st.caption("พัฒนาโดย: โปรเจกต์วิศวกรรมแอปพลิเคชันคำนวณแม่พิมพ์ปั๊มขึ้นรูปใช้งานได้จริงหน้างาน")
