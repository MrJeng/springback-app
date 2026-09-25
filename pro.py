import math
import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

try:
    import joblib
except Exception:
    joblib = None

# ตั้งค่าหน้าเว็บให้แสดงผลเต็มหน้าจอ
st.set_page_config(
    page_title="เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด",
    page_icon="⚙️",
    layout="wide"
)

# ----------------------------------------------------------------------
# พื้นหลัง: สีกรม (navy) เข้ม พร้อมชิ้นส่วนวิศวกรรม (เฟือง สปริง น็อต ประแจ)
# จางๆ กระจายเต็มพื้นหลัง จัดวางเป็นกริดระยะห่างเท่ากันในภาพเดียว
# (ไม่ใช่ tile ที่ซ้ำแบบวอลเปเปอร์) วาดเป็น SVG ฝังในโค้ดเอง ไม่ต้องโหลดรูปจากอินเทอร์เน็ต
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] {
        background-color: #0d1b3e;
        background-image: url("data:image/svg+xml;utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='1920' height='1200' viewBox='0 0 1920 1200'%3E%3Cdefs%3E%3Cg id='gear1'%3E%3Ccircle r='26'/%3E%3Ccircle r='8' fill='%233c5a8a'/%3E%3Cg%3E%3Crect x='-4' y='-34' width='8' height='11'/%3E%3Crect x='-4' y='23' width='8' height='11'/%3E%3Crect x='-34' y='-4' width='11' height='8'/%3E%3Crect x='23' y='-4' width='11' height='8'/%3E%3Crect x='-4' y='-34' width='8' height='11' transform='rotate(45)'/%3E%3Crect x='-4' y='-34' width='8' height='11' transform='rotate(135)'/%3E%3Crect x='-4' y='-34' width='8' height='11' transform='rotate(225)'/%3E%3Crect x='-4' y='-34' width='8' height='11' transform='rotate(315)'/%3E%3C/g%3E%3C/g%3E%3Cg id='gear2'%3E%3Ccircle r='20'/%3E%3Ccircle r='6' fill='%233c5a8a'/%3E%3Cg%3E%3Crect x='-3' y='-27' width='6' height='9'/%3E%3Crect x='-3' y='18' width='6' height='9'/%3E%3Crect x='-27' y='-3' width='9' height='6'/%3E%3Crect x='18' y='-3' width='9' height='6'/%3E%3C/g%3E%3C/g%3E%3Cg id='spring1'%3E%3Cpath d='M-22 -30 L-8 -18 L-22 -6 L-8 6 L-22 18 L-8 30'/%3E%3Cline x1='-22' y1='-38' x2='-22' y2='-30'/%3E%3Cline x1='-8' y1='30' x2='-8' y2='38'/%3E%3C/g%3E%3Cg id='hex1'%3E%3Cpolygon points='0,-24 21,-12 21,12 0,24 -21,12 -21,-12'/%3E%3Ccircle r='8'/%3E%3C/g%3E%3Cg id='hex2'%3E%3Cpolygon points='0,-17 15,-8.5 15,8.5 0,17 -15,8.5 -15,-8.5'/%3E%3Ccircle r='6'/%3E%3C/g%3E%3Cg id='wave1'%3E%3Cpath d='M-30 0 q7.5 -18 15 0 q7.5 18 15 0 q7.5 -18 15 0'/%3E%3Ccircle cx='-30' cy='0' r='5' fill='%233c5a8a'/%3E%3Ccircle cx='30' cy='0' r='5' fill='%233c5a8a'/%3E%3C/g%3E%3Cg id='wrench1'%3E%3Cline x1='-24' y1='0' x2='24' y2='0'/%3E%3Ccircle cx='-24' cy='0' r='9'/%3E%3Cpath d='M18 -9 L30 -9 L30 9 L18 9'/%3E%3C/g%3E%3Cg id='bolt1'%3E%3Cline x1='-10' y1='0' x2='10' y2='0'/%3E%3Cline x1='0' y1='-10' x2='0' y2='10'/%3E%3C/g%3E%3C/defs%3E%3Cg fill='none' stroke='%233c5a8a' stroke-width='2' opacity='0.45'%3E%3Cuse href='%23gear1' x='160' y='140'/%3E%3Cuse href='%23spring1' x='500' y='110'/%3E%3Cuse href='%23hex1' x='860' y='150'/%3E%3Cuse href='%23wave1' x='1220' y='120'/%3E%3Cuse href='%23gear2' x='1580' y='150'/%3E%3Cuse href='%23wrench1' x='340' y='380'/%3E%3Cuse href='%23hex2' x='700' y='400'/%3E%3Cuse href='%23gear1' x='1060' y='370'/%3E%3Cuse href='%23spring1' x='1420' y='390'/%3E%3Cuse href='%23bolt1' x='1760' y='380'/%3E%3Cuse href='%23hex1' x='120' y='620'/%3E%3Cuse href='%23wave1' x='480' y='640'/%3E%3Cuse href='%23gear2' x='840' y='610'/%3E%3Cuse href='%23wrench1' x='1200' y='630'/%3E%3Cuse href='%23hex2' x='1560' y='620'/%3E%3Cuse href='%23spring1' x='260' y='860'/%3E%3Cuse href='%23gear1' x='620' y='880'/%3E%3Cuse href='%23bolt1' x='980' y='850'/%3E%3Cuse href='%23hex1' x='1340' y='870'/%3E%3Cuse href='%23wave1' x='1700' y='860'/%3E%3Cuse href='%23wrench1' x='180' y='1080'/%3E%3Cuse href='%23gear2' x='560' y='1100'/%3E%3Cuse href='%23hex2' x='920' y='1070'/%3E%3Cuse href='%23spring1' x='1280' y='1090'/%3E%3Cuse href='%23gear1' x='1640' y='1080'/%3E%3C/g%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: center top;
        background-size: 100% auto;
        background-attachment: fixed;
    }
    [data-testid="stHeader"] {
        background: rgba(0, 0, 0, 0);
    }
    /* ปรับสีตัวอักษรทั่วไปให้อ่านง่ายบนพื้นหลังสีกรมเข้ม */
    [data-testid="stAppViewContainer"] h1,
    [data-testid="stAppViewContainer"] h2,
    [data-testid="stAppViewContainer"] h3,
    [data-testid="stAppViewContainer"] h4,
    [data-testid="stAppViewContainer"] p,
    [data-testid="stAppViewContainer"] li,
    [data-testid="stAppViewContainer"] label,
    [data-testid="stAppViewContainer"] span,
    [data-testid="stMarkdownContainer"],
    [data-testid="stCaptionContainer"],
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        color: #eef2f5 !important;
    }
    /* กล่องแจ้งเตือน (success/warning/error) ให้ตัวอักษรพื้นฐานเป็นสีเดียวกันหมด (สว่าง อ่านง่ายบนพื้นกล่องสีเข้ม) */
    [data-testid="stAlert"],
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] span,
    [data-testid="stAlert"] li {
        color: #eef2f5 !important;
    }
    /* ส่วนที่เน้น (**...**) เช่น สเปกสปริงที่แนะนำ ให้เด่นด้วยสีทองและตัวหนา */
    [data-testid="stAlert"] strong {
        color: #ffce54 !important;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------
# ฝังฟอนต์ภาษาไทยไปกับแอป เพื่อให้ matplotlib วาดตัวอักษรไทยได้ถูกต้อง
# แม้เซิร์ฟเวอร์ที่ deploy (เช่น Streamlit Cloud) จะไม่มีฟอนต์ไทยติดตั้งไว้
# ----------------------------------------------------------------------
THAI_FONT_NAME = None
_FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "Loma.otf")
if os.path.exists(_FONT_PATH):
    try:
        fm.fontManager.addfont(_FONT_PATH)
        THAI_FONT_NAME = fm.FontProperties(fname=_FONT_PATH).get_name()
        plt.rcParams["font.family"] = THAI_FONT_NAME
        plt.rcParams["axes.unicode_minus"] = False
    except Exception:
        THAI_FONT_NAME = None

# ----------------------------------------------------------------------
# โหลดโมเดล Machine Learning (Neural Network) ที่ฝึกไว้ล่วงหน้าแล้ว
# (ฝึกจากสูตรวิศวกรรม/มาตรฐาน ISO 10243 เดิม ด้วยไฟล์ train_model.py)
# ใช้ทำนายผลคู่ขนานกับสูตรตรง เพื่อเปรียบเทียบให้เห็นว่า AI ทำนายใกล้เคียง
# สูตรจริงแค่ไหน — สูตรวิศวกรรมยังคงเป็นคำตอบหลักที่ใช้ในการออกแบบเสมอ
# ----------------------------------------------------------------------
_MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
ML_MODEL_A = None   # ทำนายระดับงานสปริง (Classification)
ML_MODEL_B = None   # ทำนายจำนวนสปริง (Regression)
ML_META = None
ML_FEATURES = ["tau", "thickness", "perimeter", "kstrip", "sf",
               "x_travel", "x_preload", "cap_springs", "f_design", "x_total"]

if joblib is not None:
    try:
        ML_MODEL_A = joblib.load(os.path.join(_MODELS_DIR, "pipe_duty.joblib"))
        ML_MODEL_B = joblib.load(os.path.join(_MODELS_DIR, "pipe_n.joblib"))
        ML_META = joblib.load(os.path.join(_MODELS_DIR, "meta.joblib"))
    except Exception:
        ML_MODEL_A = None
        ML_MODEL_B = None
        ML_META = None

# ----------------------------------------------------------------------
# ฐานข้อมูลมาตรฐานสปริง ISO 10243 และวัสดุ
# ----------------------------------------------------------------------
MATERIALS = [
    ("เหล็กเหนียวรีดเย็น (SPCC / Mild steel)", 350.0, 5.0),
    ("สแตนเลส (SUS304)",                        450.0, 8.0),
    ("อะลูมิเนียม (Al 5052)",                    170.0, 3.0),
    ("ทองแดง (Copper)",                          220.0, 4.0),
    ("ทองเหลือง (Brass)",                        280.0, 4.0),
]

# ขนาดเส้นผ่านศูนย์กลางภายนอกมาตรฐาน (Outer Diameter: mm)
ODS = [10, 13, 16, 20, 25, 32, 40, 50]

# ขนาดความยาวสปริงมาตรฐาน (Free Length: mm)
LENGTHS = [25, 32, 38, 51, 64, 76, 102, 127]

BASE_RATE_AT25 = {10: 60.0, 13: 90.0, 16: 140.0, 20: 220.0, 25: 340.0, 32: 520.0, 40: 780.0, 50: 1150.0}

DUTIES = [
    {"key": "L",  "name": "เบา (Light)",            "color_name": "เหลือง", "hex": "#c9a92a", "mult": 1.0, "max_pct": 0.45},
    {"key": "M",  "name": "กลาง (Medium)",           "color_name": "น้ำเงิน", "hex": "#3f7fc1", "mult": 1.6, "max_pct": 0.40},
    {"key": "H",  "name": "หนัก (Heavy)",            "color_name": "แดง",    "hex": "#c9503b", "mult": 2.4, "max_pct": 0.35},
    {"key": "XH", "name": "หนักพิเศษ (Extra Heavy)", "color_name": "เขียว",  "hex": "#3fb383", "mult": 3.4, "max_pct": 0.30},
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
                "duty": duty["name"], "color": duty["color_name"], "hex": duty["hex"],
                "od": od, "length": length,
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


def draw_spring_figure(spring):
    """วาดภาพประกอบสปริงคอยล์แบบง่าย ๆ ด้วย matplotlib ตามสเปกที่เลือก"""
    fp = fm.FontProperties(fname=_FONT_PATH) if THAI_FONT_NAME else None

    fig, ax = plt.subplots(figsize=(6, 3.2))
    color = spring["hex"]

    top_y, bottom_y = 0.9, 0.1
    body_r = 0.12 + spring["od"] * 0.006
    turns = 8
    seg = (top_y - bottom_y) / turns

    # ปลายสปริงบน-ล่าง (เส้นตรง)
    ax.plot([0.5 - body_r, 0.5 + body_r], [top_y, top_y], color=color, linewidth=4)
    ax.plot([0.5 - body_r, 0.5 + body_r], [bottom_y, bottom_y], color=color, linewidth=4)

    # เส้นซิกแซกแทนคอยล์สปริง
    xs, ys = [], []
    for i in range(turns + 1):
        x = 0.5 + body_r if i % 2 == 0 else 0.5 - body_r
        y = top_y - i * seg
        xs.append(x)
        ys.append(y)
    ax.plot(xs, ys, color=color, linewidth=4, solid_capstyle="round", solid_joinstyle="round")

    # เส้นบอกขนาด OD (แนวนอน ด้านบน)
    dim_y = top_y + 0.08
    ax.plot([0.5 - body_r, 0.5 + body_r], [dim_y, dim_y], color="#93a7ba", linewidth=1)
    ax.text(0.5, dim_y + 0.03, f"OD = Ø{spring['od']} mm", ha="center", fontsize=10,
            color="#4a5b6b", fontproperties=fp)

    # เส้นบอกความยาว L (แนวตั้ง ด้านซ้าย)
    dim_x = 0.5 - body_r - 0.12
    ax.plot([dim_x, dim_x], [top_y, bottom_y], color="#93a7ba", linewidth=1)
    ax.text(dim_x - 0.03, (top_y + bottom_y) / 2, f"L = {spring['length']} mm",
            ha="center", va="center", fontsize=10, color="#4a5b6b", rotation=90, fontproperties=fp)

    # สเปกด้านขวา
    info_x = 0.5 + body_r + 0.15
    specs = [
        f"เกรด: {spring['duty']}",
        f"k = {spring['k']:.1f} N/mm",
        f"ยุบสูงสุด = {spring['max_def']:.1f} mm",
        f"จำนวนที่ใช้ = {spring['n']} ตัว",
    ]
    for i, line in enumerate(specs):
        ax.text(info_x, 0.75 - i * 0.15, line, fontsize=10.5, color="#182430", fontproperties=fp)

    ax.set_xlim(0, 1.3)
    ax.set_ylim(0, 1.1)
    ax.axis("off")
    fig.tight_layout()
    return fig


# ========================================================================
# การจัดวางหน้าจอเว็บ (UI ของ Streamlit)
# ========================================================================
st.title("เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด ⚙️")
st.caption("คำนวณแรงตัด แรงสตริป แรงกดรวม และแนะนำสเปกสปริงมาตรฐาน (ISO 10243)")

if THAI_FONT_NAME is None:
    st.warning(
        "⚠️ ไม่พบไฟล์ฟอนต์ไทยที่ fonts/Loma.otf ภาพประกอบสปริงอาจแสดงตัวอักษรไทยไม่ถูกต้อง "
        "กรุณาตรวจสอบว่าอัปโหลดโฟลเดอร์ fonts/ ขึ้น GitHub ไปพร้อมกับไฟล์นี้ด้วย"
    )

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
        (ใช้ $F_{design}$ ที่เผื่อ Safety Factor แล้ว จึงเป็นค่าประมาณเชิงอนุรักษ์/ปลอดภัยไว้ก่อนสำหรับเลือกขนาดเครื่องปั๊ม)
    """)
    st.markdown("---")

    st.latex(r"7.\quad \text{Tons} = \frac{F_{machine}}{9806.65}")
    st.markdown("""
    *   $\\text{Tons}$ = ขนาดแรงรวมกดลงเครื่องปั๊มเมื่อแปลงหน่วยจาก นิวตัน (N) เป็น **ตันแรง (Metric Tons)**
    *   $9806.65$ = ค่าคงที่แรงโน้มถ่วงมาตรฐานเพื่อใช้ในการแปลงหน่วยแรง ($1\\text{ kgf} \\approx 9.80665\\text{ N}$)
    """)

st.markdown("---")

col_left, col_right = st.columns([1, 2.5], gap="medium")

# --- ฝั่งซ้าย: กล่องป้อนข้อมูลดิบ ---
with col_left:
    st.markdown("### **ค่าชิ้นงาน**")

    mat_names_only = [m[0] for m in MATERIALS] + ["กำหนดเอง..."]
    selected_mat = st.selectbox("วัสดุแผ่นงาน (workpiece)", mat_names_only, index=1)
    st.caption("💡 ชนิดของแผ่นโลหะที่จะนำมาปั๊มตัด ระบบจะดึงค่าแรงเฉือนมาตรฐานมาให้เบื้องต้น")

    if selected_mat != "กำหนดเอง...":
        mat_data = next(m for m in MATERIALS if m[0] == selected_mat)
        default_tau = float(mat_data[1])
        default_kstrip = float(mat_data[2])
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

    st.markdown("---")
    st.markdown("### **ขนาดแม่พิมพ์ (สำหรับพิจารณา)**")

    die_width = st.number_input("ความกว้างแม่พิมพ์ (mm)", value=300.0, step=10.0)
    st.caption("💡 Die Width: ความกว้างของแผ่นแม่พิมพ์ (die set) ที่จะใช้ออกแบบจริง")

    die_length = st.number_input("ความยาวแม่พิมพ์ (mm)", value=400.0, step=10.0)
    st.caption("💡 Die Length: ความยาวของแผ่นแม่พิมพ์ (die set) ที่จะใช้ออกแบบจริง")

# --- ฝั่งขวา: คำนวณสูตรและแสดงผลลัพธ์ ---
with col_right:
    st.markdown("### **ผลการคำนวณ**")

    f_cut = perimeter * thickness * tau
    f_strip_req = f_cut * (kstrip / 100.0)
    f_design = f_strip_req * sf
    x_total = x_travel + x_preload

    spring_options = calculate_spring_options(x_total, f_design, cap_springs)
    best_spring = spring_options[0] if spring_options else None

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
    else:
        st.error("ไม่พบสปริงที่รองรับระยะยุบที่ต้องการ ลองลดระยะยุบตัว (stroke/preload) ลง")

    st.markdown("### **ขนาดแม่พิมพ์เทียบกับพื้นที่ที่ต้องใช้วางสปริง**")

    die_area = die_width * die_length  # mm²
    d1, d2, d3 = st.columns(3)
    d1.metric("ขนาดแม่พิมพ์ (กว้าง×ยาว)", f"{die_width:,.0f} × {die_length:,.0f} mm")
    d2.metric("พื้นที่แม่พิมพ์ทั้งหมด", f"{die_area:,.0f} mm²")

    if best_spring:
        # ประมาณพื้นที่ที่ต้องเผื่อรอบสปริงแต่ละตัว (ระยะห่างขั้นต่ำ ~1.5 เท่าของ OD รอบรู)
        clearance = best_spring["od"] * 1.5
        area_per_spring = clearance * clearance
        required_area = best_spring["n"] * area_per_spring
        d3.metric("พื้นที่โดยประมาณที่สปริงต้องใช้", f"{required_area:,.0f} mm²")

        if required_area <= die_area:
            st.info(
                f"✅ พื้นที่แม่พิมพ์ {die_width:,.0f}×{die_length:,.0f} mm เพียงพอสำหรับวางสปริง "
                f"{best_spring['n']} ตัว (Ø{best_spring['od']} mm) โดยประมาณ "
                f"(ใช้พื้นที่ราว {required_area / die_area * 100:.1f}% ของแม่พิมพ์)"
            )
        else:
            st.warning(
                f"⚠️ พื้นที่แม่พิมพ์ {die_width:,.0f}×{die_length:,.0f} mm อาจไม่พอสำหรับวางสปริง "
                f"{best_spring['n']} ตัว (Ø{best_spring['od']} mm) — ต้องใช้พื้นที่ประมาณ {required_area:,.0f} mm² "
                f"ลองเพิ่มขนาดแม่พิมพ์ หรือเลือกสปริงขนาดเล็กลง/จำนวนน้อยลง"
            )
        st.caption(
            "หมายเหตุ: เป็นการประมาณพื้นที่คร่าวๆ เพื่อใช้พิจารณาเบื้องต้นเท่านั้น "
            "(สมมติเผื่อระยะห่างรอบสปริงแต่ละตัว ~1.5 เท่าของ OD) ตำแหน่งวางจริงต้องออกแบบ "
            "ร่วมกับตำแหน่ง punch/die และโครงสร้างแม่พิมพ์จริงเสมอ"
        )

    # --------------------------------------------------------------
    # เปรียบเทียบผลจากสูตรวิศวกรรม กับผลที่ทำนายจาก Machine Learning
    # (Neural Network ที่ฝึกไว้ล่วงหน้า) — ใช้เพื่อสาธิต/เปรียบเทียบเท่านั้น
    # สูตรวิศวกรรมยังคงเป็นคำตอบหลักที่ใช้ออกแบบจริงเสมอ
    # --------------------------------------------------------------
    st.markdown("### **🤖 เปรียบเทียบกับผลทำนายจาก Machine Learning (Neural Network)**")

    if ML_MODEL_A is not None and ML_MODEL_B is not None and best_spring:
        ml_input = pd.DataFrame([{
            "tau": tau, "thickness": thickness, "perimeter": perimeter,
            "kstrip": kstrip, "sf": sf, "x_travel": x_travel,
            "x_preload": x_preload, "cap_springs": cap_springs,
            "f_design": f_design, "x_total": x_total,
        }])[ML_FEATURES].values

        pred_duty_idx = int(ML_MODEL_A.predict(ml_input)[0])
        pred_duty_name = DUTIES[pred_duty_idx]["name"]
        pred_n = ML_MODEL_B.predict(ml_input)[0]
        pred_n_round = max(1, round(pred_n))

        m1, m2 = st.columns(2)
        m1.metric(
            "AI ทำนาย: ระดับงานสปริง",
            pred_duty_name,
            delta="ตรงกับสูตร ✓" if pred_duty_name == best_spring["duty"] else "ต่างจากสูตร",
            delta_color="normal" if pred_duty_name == best_spring["duty"] else "off",
        )
        m2.metric(
            "AI ทำนาย: จำนวนสปริง",
            f"{pred_n_round} ตัว",
            delta=f"สูตรคำนวณได้ {best_spring['n']} ตัว",
            delta_color="off",
        )

        acc_pct = ML_META["duty_accuracy"] * 100 if ML_META else None
        r2_val = ML_META["n_r2"] if ML_META else None
        acc_text = f"{acc_pct:.1f}%" if acc_pct is not None else "N/A"
        r2_text = f"{r2_val:.3f}" if r2_val is not None else "N/A"

        st.caption(
            f"โมเดลฝึกจากข้อมูลจำลอง {ML_META['n_samples']:,} ชุด (สร้างจากสูตรวิศวกรรมเดิม) "
            f"— ความแม่นยำโมเดลทำนายระดับงาน ≈ {acc_text}, ความแม่นยำโมเดลทำนายจำนวนสปริง (R²) ≈ {r2_text}. "
            "ผลจาก AI ใช้เพื่อเปรียบเทียบ/สาธิตการประยุกต์ Machine Learning เท่านั้น "
            "**คำตอบหลักที่ใช้ออกแบบจริงคือผลจากสูตรวิศวกรรมด้านบนเสมอ**"
            if ML_META else
            "ผลจาก AI ใช้เพื่อเปรียบเทียบ/สาธิตการประยุกต์ Machine Learning เท่านั้น "
            "คำตอบหลักที่ใช้ออกแบบจริงคือผลจากสูตรวิศวกรรมด้านบนเสมอ"
        )
    else:
        st.info(
            "ℹ️ ยังไม่พบไฟล์โมเดล Machine Learning (models/*.joblib) — "
            "รันไฟล์ train_model.py หนึ่งครั้งเพื่อฝึกและบันทึกโมเดลก่อนใช้งานส่วนนี้"
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
                "จำนวนที่ใช้ (ตัว)": s["n"],
                "แรงรวม (N)": f"{s['total']:,.0f}",
                "สถานะ": status,
            })

        df = pd.DataFrame(table_data)

        def highlight_row(row):
            idx = row.name
            spring = spring_options[idx]
            bg = spring["hex"] + "33"  # โปร่งแสงเล็กน้อย
            if spring is best_spring:
                return [f"background-color: {bg}; font-weight: 700;"] * len(row)
            return [f"background-color: {bg};"] * len(row)

        st.dataframe(
            df.style.apply(highlight_row, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "หมายเหตุ: ค่าอัตราสปริง (k) เป็นค่าประมาณเชิงวิศวกรรมเพื่อการศึกษา อ้างอิงมาตรฐานสี ISO 10243 "
            "(เหลือง=เบา, น้ำเงิน=กลาง, แดง=หนัก, เขียว=หนักพิเศษ) ก่อนสั่งซื้อจริงควรเทียบกับแคตตาล็อกผู้ผลิต "
            "เช่น Misumi, Raymond, Danly"
        )

        st.markdown("### **ภาพประกอบสปริงที่เลือก**")
        chosen_label = st.selectbox(
            "เลือกสปริงจากตารางด้านบนเพื่อดูภาพประกอบ",
            options=list(range(len(spring_options))),
            format_func=lambda i: f"{spring_options[i]['duty']} — Ø{spring_options[i]['od']}×{spring_options[i]['length']} mm",
            index=0,
        )
        fig = draw_spring_figure(spring_options[chosen_label])
        st.pyplot(fig)
        st.caption("ภาพประกอบตามสัดส่วนโดยประมาณ ไม่ใช่ภาพถ่ายสินค้าจริง")
    else:
        st.warning("ไม่มีตัวเลือกสปริงให้แสดง")
