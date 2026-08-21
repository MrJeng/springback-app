import streamlit as st
import math

# 1. ตั้งค่าหน้าตาแอปพลิเคชัน
st.set_page_config(
    page_title="Washer Stamping Die App",
    page_icon="⚙️",
    layout="centered"
)

# ฐานข้อมูลวัสดุแผ่นโลหะ (เพิ่มค่า Shear Strength: SS สำหรับงานกดตัดโดยเฉพาะ)
MATERIAL_DATA = {
    "เหล็กแผ่นทั่วไป (Mild Steel / SS400)": {"E": 207000.0, "YS": 250.0, "SS": 320.0},
    "เหล็กกล้ากำลังสูง (High-Strength Steel)": {"E": 210000.0, "YS": 550.0, "SS": 480.0},
    "อลูมิเนียมแผ่น (Aluminum AL5052)": {"E": 70000.0, "YS": 195.0, "SS": 150.0},
    "สแตนเลสแผ่น (Stainless SUS304)": {"E": 193000.0, "YS": 290.0, "SS": 420.0}
}

# ส่วนหัวของแอปพลิเคชัน
st.caption("⚙️ โปรแกรมวิศวกรรมแม่พิมพ์ตัดเฉือน (Piercing & Blanking Die App)")
st.title("Washer Stamping Calculator")
st.write("ระบบคำนวณแม่พิมพ์กดตัดแหวนรองน็อต: คำนวณแรงกดเครื่องจักร ขนาดสปริง และค่าชดเชยผิวสปริงตัว")
st.markdown("---")

# --- โซนอินพุต 1: ข้อมูลสเปกชิ้นงานแหวน ---
st.header("📋 1. ข้อมูลวัสดุและความหนา")
mat_choice = st.selectbox("เลือกชนิดวัสดุแผ่นโลหะ:", list(MATERIAL_DATA.keys()))
sheet_t = st.selectbox("เลือกความหนาชิ้นงาน, t (mm):", [0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0], index=5)

shear_strength = MATERIAL_DATA[mat_choice]["SS"]
st.caption(f"ดัชนีวัสดุ -> Shear Strength (τ_s): {shear_strength} MPa")

st.header("📐 2. ขนาดมิติของแหวนรองน็อต")
col_d1, col_d2 = st.columns(2)
d_inner = col_d1.number_input("ขนาดรูในของแหวน, d (mm):", min_value=1.0, value=10.0, step=0.5)
d_outer = col_d2.number_input("ขนาดขอบนอกของแหวน, D (mm):", min_value=2.0, value=20.0, step=0.5)

if d_inner >= d_outer:
    st.error("⚠️ ข้อผิดพลาด: ขนาดรูในต้องเล็กกว่าขนาดขอบนอกชิ้นงาน")
else:
    stroke = st.number_input("ระยะกดชักของแผ่นปลดชิ้นงาน (Stripper Stroke), mm:", min_value=1.0, value=10.0, step=1.0)
    st.markdown("---")

    # --- โซนประมวลผลคำนวณทางวิศวกรรมแม่พิมพ์ตัด ---
    # 1. คำนวณแรงตัดสุทธิ (Shearing Force) = เส้นรอบวงรวม x ความหนา x ค่าแรงเฉือน
    perimeter_inner = math.pi * d_inner
    perimeter_outer = math.pi * d_outer
    total_perimeter = perimeter_inner + perimeter_outer
    
    force_N = total_perimeter * sheet_t * shear_strength
    force_tons = force_N / 9806.65 # แปลงนิวตันเป็นตัน
    
    # แรงปลดชิ้นงาน (Stripping Force) เผื่อไว้ 10% ของแรงตัดเพื่อเลือกสปริง
    stripping_force_tons = force_tons * 0.10
    # ขนาดเครื่องปั๊มที่แนะนำ (Safety Factor เผื่อแรงกระแทกกระดอน 30%)
    recommended_press = force_tons * 1.30

    # 2. คำนวณสปริงปลดชิ้นงาน (Stripper Spring Selection)
    # ในแม่พิมพ์ตัด แหวนหนาหรือวัสดุแข็งจะเกิดแรงต้านการติดพั้นช์สูงขึ้น
    load_index = sheet_t * shear_strength
    if load_index <= 200:
        color_label, color_code, compress_ratio = "สีเขียว (Light Load)", "#10B981", 0.40
        reason_text = "ชิ้นงานบาง แรงเฉือนต่ำ แรงดีดติดพั้นช์น้อย สปริงตัวได้ดีในระยะชักไว"
    elif load_index <= 450:
        color_label, color_code, compress_ratio = "สีน้ำเงิน (Medium Load)", "#2563EB", 0.32
        reason_text = "ภาระงานปานกลาง เหมาะสำหรับงานกดตัดแหวนเหล็กทั่วไป ทนรอบปั๊มต่อเนื่องสูง"
    elif load_index <= 750:
        color_label, color_code, compress_ratio = "สีแดง (Heavy Load)", "#DC2626", 0.24
        reason_text = "ภาระงานกดตัดหนัก แผ่นโลหะหนา มีแรงบีบอัดพั้นช์สูง ต้องใช้สปริงแรงดันปลดสูงป้องกันชิ้นงานติดขัด"
    else:
        color_label, color_code, compress_ratio = "สีเหลือง (Extra Heavy Load)", "#F59E0B", 0.20
        reason_text = "งานกดตัดแผ่นเหล็กหนาพิเศษหรือเหล็กแข็ง High-Strength สปริงต้านแรงกระแทกย้อนกลับสูงสุด"
    
    calculated_L0 = stroke / compress_ratio

    # 3. คำนวณขนาด Springback เผื่อระยะ Clearance ของแม่พิมพ์ตัด (อ้างอิง Radial Elastic Recovery ~0.05%)
    # รูเจาะในจะหดตัวลงเล็กน้อย ส่วนขอบนอกชิ้นงานจะขยายตัวขึ้นเล็กน้อยหลังหลุดจากแม่พิมพ์
    shrinkage = d_inner * 0.0005
    expansion = d_outer * 0.0005
    recommended_punch = d_inner + shrinkage
    recommended_die = d_outer - expansion

    # --- โซนแสดงผลลัพธ์บนหน้าต่างแอปพลิเคชัน ---
    st.header("📊 3. ผลการวิเคราะห์และการเลือกสเปกแม่พิมพ์")
    
    # 3.1 ขนาดกำลังเครื่องจักร
    st.subheader("🏭 กำลังแรงกดเครื่องปั๊มตัด (Press Tonnage)")
    col_f1, col_f2 = st.columns(2)
    col_f1.metric("แรงกดตัดรวมสุทธิ (Net Blanking Force)", f"{force_tons:.2f} Tons")
    col_f2.metric("ขนาดเครื่องปั๊มแนะนำ (+Safety 30%)", f"{recommended_press:.1f} Tons", delta="ปลอดภัยจากแรงกระแทก")
    st.caption(f"💡 แรงที่ต้องใช้ในการปลดแผ่นโลหะออกจากพั้นช์ (Stripping Force): {stripping_force_tons:.2f} Tons")

    # 3.2 ค่าชดเชยขนาด Springback (Radial) ของชิ้นงานตัด
    st.markdown(" ")
    st.subheader("📐 มิติแม่พิมพ์ชดเชยการสปริงตัว (Radial Elastic Recovery)")
    col_m1, col_m2 = st.columns(2)
    col_m1.metric("ขนาดพั้นช์เจาะรูในที่แนะนำ (Punch Size)", f"{recommended_punch:.3f} mm", delta=f"+{shrinkage:.3f} mm เผื่อรูหด")
    col_m2.metric("ขนาดดายตัดขอบนอกที่แนะนำ (Die Size)", f"{recommended_die:.3f} mm", delta=f"-{expansion:.3f} mm เผื่อแหวนขยาย")

    # 3.3 สเปกสปริงสำหรับแผ่นปลดชิ้นงาน
    st.markdown(" ")
    st.subheader("🔩 สเปกสปริงแผ่นปลดชิ้นงาน (Stripper Spring)")
    st.markdown(
        f"<div style='background-color:{color_code}; padding:12px; border-radius:6px; text-align:center; margin-bottom:15px.'>"
        f"<h3 style='color:white; margin:0px; font-weight:bold;'>สปริงแม่พิมพ์ที่แนะนำ: {color_label}</h3>"
        f"</div>", 
        unsafe_allow_html=True
    )
    st.info(f"💡 **เหตุผลอ้างอิงเชิงวิศวกรรม:** {reason_text}")
    st.success(f"📏 **ขนาดความยาวอิสระของสปริงปลด (Free Length - L0):** {calculated_L0:.2f} mm")

st.markdown("---")
st.caption("พัฒนาโดย: โปรเจกต์วิศวกรรมแอปพลิเคชันคำนวณแม่พิมพ์ปั๊มขึ้นรูปใช้งานได้จริงหน้างาน")
