import streamlit as st

# 1. ตั้งค่าหน้าตาแอปพลิเคชัน
st.set_page_config(
    page_title="Universal Stamping Die App",
    page_icon="⚙️",
    layout="centered"
)

# ฐานข้อมูลวัสดุแผ่นโลหะ (Shear Strength สำหรับงานกดตัด)
MATERIAL_DATA = {
    "เหล็กแผ่นทั่วไป (Mild Steel / SS400)": {"E": 207000.0, "YS": 250.0, "SS": 320.0},
    "เหล็กกล้ากำลังสูง (High-Strength Steel)": {"E": 210000.0, "YS": 550.0, "SS": 480.0},
    "อลูมิเนียมแผ่น (Aluminum AL5052)": {"E": 70000.0, "YS": 195.0, "SS": 150.0},
    "สแตนเลสแผ่น (Stainless SUS304)": {"E": 193000.0, "YS": 290.0, "SS": 420.0}
}

# ส่วนหัวของแอปพลิเคชัน
st.caption("⚙️ โปรแกรมวิศวกรรมแม่พิมพ์กดตัดเฉือนอเนกประสงค์ (Blanking & Piercing Die App)")
st.title("Stamping Shearing Calculator")
st.write("แอปพลิเคชันคำนวณแม่พิมพ์กดตัดแผ่นโลหะ: คำนวณแรงกดเครื่องจักร ขนาดสปริง และค่าชดเชยผิวสปริงตัว")
st.markdown("---")

# --- โซนอินพุต 1: ข้อมูลสเปกวัสดุ ---
st.header("📋 1. ข้อมูลวัสดุและความหนา")
mat_choice = st.selectbox("เลือกชนิดวัสดุแผ่นโลหะ:", list(MATERIAL_DATA.keys()))
sheet_t = st.selectbox("เลือกความหนาชิ้นงาน, t (mm):", [0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0], index=5)

shear_strength = MATERIAL_DATA[mat_choice]["SS"]
st.caption(f"ดัชนีวัสดุ -> Shear Strength (τ_s): {shear_strength} MPa")

# --- โซนอินพุต 2: ขนาดมิติแนวตัด (เปลี่ยนเป็นความยาวเส้นรอบวงตามคำขอ) ---
st.header("📐 2. มิติแนวตัดและระยะชักแม่พิมพ์")

total_perimeter = st.number_input(
    "ระบุความยาวเส้นรอบวง / เส้นรอบรูปแนวตัดรวม, L (mm):", 
    min_value=1.0, 
    value=100.0, 
    step=10.0,
    help="ใส่ค่าความยาวรวมของเส้นแนวตัดทั้งหมด (เช่น ถ้าเจาะรูทรงกลม ให้ใส่ค่าเส้นรอบวงของรูเจาะนั้น)"
)

stroke = st.number_input("ระยะกดชักของแผ่นปลดชิ้นงาน (Stripper Stroke), mm:", min_value=1.0, value=10.0, step=1.0)
st.markdown("---")

# --- โซนประมวลผลคำนวณทางวิศวกรรมแม่พิมพ์ตัด ---
if total_perimeter > 0:
    # 1. คำนวณแรงตัดสุทธิ (Shearing Force) = ความยาวเส้นรอบรูปแนวตัดรวม x ความหนา x ค่าแรงเฉือนวัสดุ
    force_N = total_perimeter * sheet_t * shear_strength
    force_tons = force_N / 9806.65 # แปลงนิวตันเป็นตัน
    
    # แรงปลดชิ้นงานออกจากพั้นช์ (Stripping Force) เผื่อไว้ 10% ของแรงตัดเพื่อใช้คำนวณโหลดสปริง
    stripping_force_tons = force_tons * 0.10
    # ขนาดเครื่องปั๊มที่แนะนำ (Safety Factor เผื่อแรงกระแทกกระดอนย้อนกลับ 30%)
    recommended_press = force_tons * 1.30

    # 2. คำนวณสปริงปลดชิ้นงาน (Stripper Spring Selection)
    load_index = sheet_t * shear_strength
    if load_index <= 200:
        color_label, color_code, compress_ratio = "สีเขียว (Light Load)", "#10B981", 0.40
        reason_text = "ภาระงานตัดเบา ชิ้นงานบาง แรงบีบติดพั้นช์น้อย สปริงขยับตัวได้ไว เหมาะกับรอบปั๊มสูง"
    elif load_index <= 450:
        color_label, color_code, compress_ratio = "สีน้ำเงิน (Medium Load)", "#2563EB", 0.32
        reason_text = "ภาระงานปานกลาง เหมาะสำหรับงานกดตัดแผ่นเหล็กทั่วไป ทนรอบรอบการปั๊มต่อเนื่องได้ดี"
    elif load_index <= 750:
        color_label, color_code, compress_ratio = "สีแดง (Heavy Load)", "#DC2626", 0.24
        reason_text = "ภาระงานกดตัดหนัก แผ่นโลหะหนา มีแรงบีบรัดตัวพั้นช์สูง ต้องใช้สปริงแรงดันปลดสูงเพื่อป้องกันแผ่นติด"
    else:
        color_label, color_code, compress_ratio = "สีเหลือง (Extra Heavy Load)", "#F59E0B", 0.20
        reason_text = "งานกดตัดแผ่นโลหะหนาพิเศษหรือเหล็กแข็งกำลังสูง (HSS) สปริงหนาทนแรงกระแทกกระดอนย้อนกลับสูงสุด"
    
    calculated_L0 = stroke / compress_ratio

    # 3. คำนวณค่าชดเชยขนาดจากผลกระทบ Springback แนวรัศมี (Radial Elastic Recovery ~0.05%)
    radial_recovery_ratio = 0.0005

    # --- โซนแสดงผลลัพธ์บนหน้าต่างแอปพลิเคชัน ---
    st.header("📊 3. ผลการวิเคราะห์และการเลือกสเปกเครื่องจักร")
    
    # 3.1 กำลังของเครื่องจักรที่ต้องใช้
    st.subheader("🏭 กำลังแรงกดของเครื่องปั๊ม (Press Tonnage)")
    col_f1, col_f2 = st.columns(2)
    col_f1.metric("แรงกดตัดเฉือนสุทธิ (Net Blanking Force)", f"{force_tons:.2f} Tons")
    col_f2.metric("ขนาดเครื่องปั๊มแนะนำ (+Safety 30%)", f"{recommended_press:.1f} Tons", delta="ปลอดภัยหน้างาน")
    st.caption(f"📊 แรงที่แผ่นปลดต้องใช้ดึงแผ่นโลหะออกจากพั้นช์ (Stripping Force): {stripping_force_tons:.2f} Tons")

    # 3.2 ค่าผลกระทบ Springback ในงานกดตัด
    st.markdown(" ")
    st.subheader("📐 ผลกระทบจาก Springback ในแนวรัศมี (Radial Elastic Recovery)")
    st.info("ในงานกดตัดเฉือนโลหะแผ่น (Blanking/Piercing) แรงบีบอัดสไลด์จะทำให้เกิดการสปริงตัวกลับในแนวรัศมีประมาณ **0.05%**")
    
    col_m1, col_m2 = st.columns(2)
    col_m1.markdown(f"**กรณีงานเจาะรูชิ้นงาน (Piercing):**\nรูเจาะจะ **หดตัวเล็กลง** ควรออกแบบขนาดพั้นช์ (Punch) ให้ **โตขึ้นกว่าขนาดชิ้นงานจริงประมาณ +0.05%** เพื่อชดเชยการหดตัว")
    col_m2.markdown(f"**กรณีงานตัดขอบนอกชิ้นงาน (Blanking):**\nแผ่นงานจะ **ขยายโตขึ้น** ควรออกแบบขนาดดาย (Die) ให้ **เล็กกว่าขนาดชิ้นงานจริงประมาณ -0.05%** เพื่อชดเชยการขยายตัว")

    # 3.3 สเปกสปริงปลดชิ้นงาน
    st.markdown(" ")
    st.subheader("🔩 สเปกสปริงแผ่นปลดชิ้นงาน (Stripper Spring)")
    st.markdown(
        f"<div style='background-color:{color_code}; padding:12px; border-radius:6px; text-align:center; margin-bottom:15px.'>"
        f"<h3 style='color:white; margin:0px; font-weight:bold;'>สปริงแม่พิมพ์ที่แนะนำ: {color_label}</h3>"
        f"</div>", 
        unsafe_allow_html=True
    )
    st.info(f"💡 **เหตุผลอ้างอิงเชิงวิศวกรรม:** {reason_text}")
    st.success(f"📏 **ขนาดความยาวอิสระของสปริงปลดที่ควรเลือกใช้ (Free Length - L0):** {calculated_L0:.2f} mm")

st.markdown("---")
st.caption("พัฒนาโดย: โปรเจกต์วิศวกรรมแอปพลิเคชันคำนวณแม่พิมพ์ปั๊มขึ้นรูปใช้งานได้จริงหน้างาน")
