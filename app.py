import streamlit as st

# --- ตั้งค่าหน้าตาแอปพลิเคชัน ---
st.set_page_config(
    page_title="Springback Suite Pro",
    page_icon="⚙️",
    layout="centered"
)

# --- ฐานข้อมูลวัสดุแผ่นโลหะ ---
MATERIAL_DATA = {
    "เหล็กแผ่นทั่วไป (Mild Steel / SS400)": {"E": 207000.0, "YS": 250.0},
    "เหล็กกล้ากำลังสูง (High-Strength Steel)": {"E": 210000.0, "YS": 550.0},
    "อลูมิเนียมแผ่น (Aluminum AL5052)": {"E": 70000.0, "YS": 195.0},
    "สแตนเลสแผ่น (Stainless SUS304)": {"E": 193000.0, "YS": 290.0}
}

# --- ส่วนหัวของแอปพลิเคชัน ---
st.caption("⚙️ โปรแกรมคำนวณงานวิศวกรรมแม่พิมพ์ (Die & Stamping Engineering App)")
st.title("Springback & Die Spring Calculator")
st.write("แอปพลิเคชันคำนวณการดีดกลับของผิวโลหะ และประเมินขนาดสปริงแม่พิมพ์หน้างาน")
st.markdown("---")

# --- โซนอินพุต 1: ข้อมูลชิ้นงาน ---
st.header("📋 1. ข้อมูลสเปกวัสดุชิ้นงาน")
mat_choice = st.selectbox("เลือกชนิดวัสดุ:", list(MATERIAL_DATA.keys()))
sheet_t = st.selectbox("เลือกความหนาของแผ่นชิ้นงาน, t (mm):", [0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 3.0, 4.0], index=5)

# ดึงข้อมูลภายในมาแสดง
modulus_E = MATERIAL_DATA[mat_choice]["E"]
yield_YS = MATERIAL_DATA[mat_choice]["YS"]
st.caption(f"พารามิเตอร์วัสดุ -> Elastic Modulus (E): {modulus_E} MPa | Yield Strength (σ_y): {yield_YS} MPa")

# --- โซนอินพุต 2: ขนาดแม่พิมพ์และระยะกดชัก ---
st.header("📐 2. พารามิเตอร์ขนาดแม่พิมพ์")
punch_R = st.number_input("รัศมีปลายพั้นช์ดัดงอ, R_i (mm):", min_value=0.1, value=4.0, step=0.1)

# ฟังก์ชันล็อกมุมมาตรฐาน 90 องศา (ผู้ใช้ไม่ต้องกรอกเอง)
lock_90 = st.checkbox("ใช้มุมพับมาตรฐาน 90 องศา (Standard 90° V-Bend)", value=True)

if lock_90:
    target_angle = 90.0
    st.info("🔒 ล็อกมุมดัดพับไว้ที่ 90.0 องศาสำเร็จ (ไม่ต้องระบุตัวเลขเพิ่ม)")
else:
    target_angle = st.number_input("ระบุมุมพับชิ้นงานที่ต้องการกำหนดเอง (องศา °):", min_value=1.0, max_value=180.0, value=90.0, step=1.0)

die_stroke = st.number_input("ระยะกดชักของแผ่นกดพิมพ์, Stroke (mm):", min_value=0.1, value=15.0, step=1.0)
st.markdown("---")

# --- โซนประมวลผลคำนวณ (Processing logic) ---
calc_factor = (punch_R * yield_YS) / (modulus_E * sheet_t)
springback_factor_Ks = 1 - 3 * calc_factor + 4 * (calc_factor ** 3)

if springback_factor_Ks > 1 or springback_factor_Ks < 0:
    st.error("⚠️ ข้อผิดพลาด: พารามิเตอร์อินพุตอยู่นอกขอบเขตการคำนวณตามทฤษฎี กรุณาตรวจสอบขนาดความหนาหรือรัศมีปลายพั้นช์อีกครั้ง")
else:
    # คำนวณค่ามุมชดเชย
    final_angle_tf = target_angle * springback_factor_Ks
    springback_diff = target_angle - final_angle_tf
    compensation_punch = target_angle * (2 - springback_factor_Ks)
    
    st.header("📊 3. ผลการวิเคราะห์และคำแนะนำการออกแบบ")
    
    # แสดงค่ามุมในลักษณะกล่องข้อมูล 3 คอลัมน์
    c1, c2, c3 = st.columns(3)
    c1.metric("สัมประสิทธิ์ Ks", f"{springback_factor_Ks:.3f}")
    c2.metric("มุมที่ได้จริงหลังดีดกลับ (θ_f)", f"{final_angle_tf:.2f} °")
    c3.metric("มุมพั้นช์ที่ต้องออกแบบเผื่อ", f"{compensation_punch:.2f} °")
    
    # ประเมินค่าความเหนียว/แรงต้าน เพื่อแมตช์คู่สีของสปริงแม่พิมพ์ (ISO Standard)
    load_index = sheet_t * yield_YS
    if load_index <= 250:
        color_label, color_code, compress_ratio = "สีเขียว (Light Load)", "#10B981", 0.40
        reason_text = "ภาระงานดัดพับค่อนข้างเบา ชิ้นงานบาง แรงสปริงแบ็คต่ำ สปริงยืดหยุ่นตัวได้ดี ช่วยเซฟโครงสร้างแม่พิมพ์"
    elif load_index <= 500:
        color_label, color_code, compress_ratio = "สีน้ำเงิน (Medium Load)", "#2563EB", 0.32
        reason_text = "ภาระงานระดับปานกลาง เหมาะสำหรับงานแผ่นเหล็กโครงสร้างทั่วไป สปริงทนรอบปั๊มสโตรกสูงได้ดีเยี่ยม"
    elif load_index <= 800:
        color_label, color_code, compress_ratio = "สีแดง (Heavy Load)", "#DC2626", 0.24
        reason_text = "ภาระงานหนัก ชิ้นงานเริ่มมีความหนาหรือแข็ง ต้องใช้แรงกดต้าน pad สูงเพื่อควบคุมขอบผิวชิ้นงานไม่ให้โก่งตัวดีดกลับ"
    else:
        color_label, color_code, compress_ratio = "สีเหลือง (Extra Heavy Load)", "#F59E0B", 0.20
        reason_text = "ภาระงานหนักพิเศษ สำหรับงานแผ่นเหล็กหนาหนืด หรือวัสดุกลุ่ม High-Strength Steel ทนแรงกดกระแทกสูงสุด"
        
    # คำนวณหาค่าความยาวอิสระขั้นต่ำของตัวสปริง (Free Length)
    calculated_L0 = die_stroke / compress_ratio
    
    # พ่นหน้าตาแถบสีและสเปกออกมาบนแอปพลิเคชันแบบคลีน ๆ
    st.markdown(
        f"<div style='background-color:{color_code}; padding:14px; border-radius:6px; text-align:center; margin-bottom:15px;'>"
        f"<h3 style='color:white; margin:0px; font-weight:bold;'>สปริงแม่พิมพ์ที่แนะนำ: {color_label}</h3>"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    st.info(f"💡 **เหตุผลอ้างอิงเชิงวิศวกรรม:** {reason_text}")
    st.success(f"📏 **ขนาดความยาวอิสระของสปริงที่ควรเลือกใช้ (Free Length - L0):** {calculated_L0:.2f} mm")

st.markdown("---")
st.caption("พัฒนาโดย: โปรเจกต์วิศวกรรมแอปพลิเคชันคำนวณแม่พิมพ์ปั๊มขึ้นรูปใช้งานได้จริงหน้างาน")
