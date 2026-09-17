import math
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ตั้งค่าหน้าเว็บให้แสดงผลเต็มหน้าจอ
st.set_page_config(
    page_title="เครื่องคำนวณสปริงสตริปเปอร์ — แม่พิมพ์กดตัด",
    page_icon="⚙️",
    layout="wide"
)

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
ODS =
