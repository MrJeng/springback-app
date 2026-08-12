import streamlit as st

# ตั้งค่าหน้าเว็บสไตล์แอปพลิเคชันมือถือ/คอมพิวเตอร์
st.set_page_config(page_title="Springback & Die Spring Calculator", page_icon="⚙️", layout="centered")

# ฐานข้อมูลพารามิเตอร์วัสดุทางวิศวกรรม
MATERIAL_DATABASE = {
    "เหล็กแผ่นทั่วไป (Mild Steel / SS400)": {"E": 207000.0, "YS": 250.0},
    "เหล็กกล้ากำลังสูง (High-Strength Steel)": {"E": 210000.0, "YS": 550.0},
    "อลูมิเนียมแผ่น (Aluminum AL5052)": {"E": 70000.0, "YS": 195.0},
    "สแตนเลสแผ่น (Stainless SUS304)": {"E": 193000.0, "YS": 290.0}
}

st.title("⚙️ Springback & Die Spring Calculator")
st.write("แอปพลิเคชันคำนวณการสปริงตัวกลับและแนะนำสเปกสปริงแม่พิมพ์เพื่อการใช้งานจริง")
st.markdown("---")

# --- โซนอินพุตเงื่อนไขชิ้นงาน ---
st.header("📋 1. เงื่อนไขวัสดุและชิ้นงาน")
selected_material = st.selectbox("เลือกชนิดของวัสดุแผ่น:", list(MATERIAL_DATABASE.keys()))
t = st.selectbox("เลือกความหนาชิ้นงาน, t (mm):", [0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0], index=5)

E = MATERIAL_DATABASE[selected_material]["E"]
sigma_y = MATERIAL_DATABASE[selected_material]["YS"]
st.caption(f"ดัชนีทางทฤษฎี -> Elastic Modulus (E): {E} MPa | Yield Strength (σ_y): {sigma_y} MPa")

# --- โซนขนาดพารามิเตอร์แม่พิมพ์ ---
st.header("📐 2. พารามิเตอร์แม่พิมพ์และระยะกด")
R_i = st.number_input("รัศมีปลายพั้นช์ดัด, R_i (mm):", min_value=0.1, value=4.0, step=0.1)
theta_i = st.number_input("มุมพับชิ้นงานที่ต้องการ (องศา °):", min_value=1.0, max_value=180.0, value=90.0, step=1.0)
stroke = st.number_input("ระยะกดพับของแม่พิมพ์, Stroke (mm):", min_value=0.1, value=15.0, step=1.0)

st.markdown("---")

# --- โซนโลจิสติกส์การประมวลผลคำนวณ ---
factor = (R_i * sigma_y) / (E * t)
K_s = 1 - 3 * factor + 4 * (factor ** 3)

# ตรวจสอบขอบเขตข้อผิดพลาดทางฟิสิกส์
if K_s > 1 or K_s < 0:
    st.error("⚠️ พารามิเตอร์อยู่นอกขอบเขตทฤษฎีพลาสติก กรุณาตรวจสอบสัดส่วนความหนาและรัศมีพั้นช์ดัด")
else:
    theta_f = theta_i * K_s
    springback_angle = theta_i - theta_f
    overbend_angle = theta_i * (2 - K_s)
    
    st.header("📊 3. ผลการคำนวณและคำแนะนำหน้างาน")
    
    # แสดงการคำนวณมุมแบบ Dashboard แถวเรียง 3 คอลัมน์
    col1, col2, col3 = st.columns(3)
    col1.metric("สัมประสิทธิ์ Ks", f"{K_s:.3f}")
    col2.metric("มุมหลังดีดกลับจริง (θ_f)", f"{theta_f:.2f} °")
    col3.metric("มุมพั้นช์ที่ต้องชดเชย", f"{overbend_angle:.2f} °")
    
    # คำนวณดัชนีภาระงานเพื่อเลือกคู่สีสปริงแม่พิมพ์ (Die Spring Standard)
    forming_index = t * sigma_y
    if forming_index <= 250:
        spring_color, color_hex, ratio = "สีเขียว (Light Load)", "#10B981", 0.40
        spring_desc = "ภาระงานเบา ชิ้นงานบาง แรงสปริงแบ็คต่ำ สปริงขยับตัวได้ดี ยืดอายุการใช้งานแม่พิมพ์"
    elif forming_index <= 500:
        spring_color, color_hex, ratio = "สีน้ำเงิน (Medium Load)", "#2563EB", 0.32
        spring_desc = "ภาระงานปานกลาง เหมาะสำหรับงานแผ่นเหล็กทั่วไป ทนรอบการปั๊มชดเชยได้สูง"
    elif forming_index <= 800:
        spring_color, color_hex, ratio = "สีแดง (Heavy Load)", "#DC2626", 0.24
        spring_desc = "ภาระงานหนัก วัสดุเริ่มหนาหรือแข็ง ต้องใช้แรงกด Pad สูงเพื่อต้านแรงดีดกลับ"
    else:
        spring_color, color_hex, ratio = "สีเหลือง (Extra Heavy Load)", "#F59E0B", 0.20
        spring_desc = "ภาระงานหนักพิเศษ สำหรับงานเหล็กหนาหรือโลหะ High-Strength ต้านแรงกดกระแทกสูงสุด"
        
    # คำนวณ Free Length ล่าสุด
    free_length = stroke / ratio
    
    # การแสดงผลการจัดสีสปริงและมิติขนาดสเปก
    st.markdown(f"<div style='background-color:{color_hex}; padding:12px; border-radius:6px; text-align:center;'><h3 style='color:white; margin:0px;'>สปริงแม่พิมพ์ที่แนะนำ: {spring_color}</h3></div>", unsafe_value_allowed=True)
    st.info(f"💡 **เหตุผลอ้างอิงทางวิศวกรรม:** {spring_desc}")
    st.success(f"📏 **ความยาวอิสระขั้นต่ำของสปริงที่ควรเลือกใช้ (Free Length - L0):** {free_length:.2f} mm")
